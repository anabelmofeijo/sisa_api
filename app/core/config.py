import os
import json
import importlib
import logging
from datetime import date, datetime
from enum import Enum
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.sqltypes import Date as SQLDate
from sqlalchemy.sql.sqltypes import DateTime as SQLDateTime
from sqlalchemy.sql.sqltypes import Enum as SQLEnum


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL nao definida no ambiente.")

# Ajusta URLs antigas
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

APP_ENV = os.getenv("APP_ENV", "development").lower()
IS_PROD = APP_ENV in {"prod", "production"} or bool(
    os.getenv("RENDER_SERVICE_ID") or os.getenv("RENDER_INSTANCE_ID") or os.getenv("RENDER")
)

LOCAL_DATABASE_URL = None
if not IS_PROD:
    LOCAL_DATABASE_URL = os.getenv(
        "LOCAL_DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:54322/postgres",
    )
    if LOCAL_DATABASE_URL.startswith("postgres://"):
        LOCAL_DATABASE_URL = LOCAL_DATABASE_URL.replace("postgres://", "postgresql://", 1)

logger = logging.getLogger(__name__)
SYNC_QUEUE_TABLE = "_offline_sync_queue"


def _is_local_postgres(url: str) -> bool:
    parsed = make_url(url)
    if not parsed.drivername.startswith("postgresql"):
        return False
    return parsed.host in {"localhost", "127.0.0.1"}


def _create_db_engine(url: str):
    connect_args = {"sslmode": "require"} if not _is_local_postgres(url) else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


# Engine principal (nuvem)
engine = _create_db_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# Engine secundário (local)
local_engine = _create_db_engine(LOCAL_DATABASE_URL) if LOCAL_DATABASE_URL else None
LocalSessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=local_engine, expire_on_commit=False)
    if local_engine is not None
    else None
)

Base = declarative_base()


def _ensure_sync_queue_table():
    if local_engine is None:
        return
    create_stmt = f"""
    CREATE TABLE IF NOT EXISTS {SYNC_QUEUE_TABLE} (
        id BIGSERIAL PRIMARY KEY,
        model_key TEXT NOT NULL,
        operation VARCHAR(10) NOT NULL,
        pk_values JSONB,
        payload JSONB,
        attempts INTEGER NOT NULL DEFAULT 0,
        last_error TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        synced_at TIMESTAMPTZ
    )
    """
    with local_engine.begin() as conn:
        conn.execute(text(create_stmt))


def _model_key(model_cls) -> str:
    return f"{model_cls.__module__}:{model_cls.__name__}"


def _resolve_model(model_key: str):
    module_name, class_name = model_key.rsplit(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def _serialize_for_column(value, column):
    if value is None:
        return None

    if isinstance(column.type, SQLEnum):
        if isinstance(value, Enum):
            return value.name
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return value


def _deserialize_for_column(value, column):
    if value is None:
        return None

    if isinstance(column.type, SQLEnum):
        enum_class = getattr(column.type, "enum_class", None)
        if enum_class is None:
            return value
        if isinstance(value, enum_class):
            return value
        try:
            return enum_class[value]
        except Exception:
            return enum_class(value)

    if isinstance(column.type, SQLDateTime) and isinstance(value, str):
        return datetime.fromisoformat(value)

    if isinstance(column.type, SQLDate) and isinstance(value, str):
        return date.fromisoformat(value)

    return value


def _pk_values_from_instance(instance, mapper):
    return [getattr(instance, col.key, None) for col in mapper.primary_key]


def _snapshot_operations(session):
    operations = []

    for obj in list(session.new) + list(session.dirty):
        mapper = inspect(obj).mapper
        payload = {
            col.key: _serialize_for_column(getattr(obj, col.key), col)
            for col in mapper.columns
        }
        operations.append(
            {
                "operation": "upsert",
                "model_class": obj.__class__,
                "model_key": _model_key(obj.__class__),
                "pk_values": _pk_values_from_instance(obj, mapper),
                "payload": payload,
                "source_obj": obj,
            }
        )

    for obj in list(session.deleted):
        mapper = inspect(obj).mapper
        operations.append(
            {
                "operation": "delete",
                "model_class": obj.__class__,
                "model_key": _model_key(obj.__class__),
                "pk_values": _pk_values_from_instance(obj, mapper),
                "payload": None,
                "source_obj": None,
            }
        )

    return operations


def _refresh_operations_from_source(operations):
    for op in operations:
        source_obj = op.get("source_obj")
        if source_obj is None or op["operation"] != "upsert":
            continue

        mapper = inspect(source_obj).mapper
        op["pk_values"] = _pk_values_from_instance(source_obj, mapper)
        op["payload"] = {
            col.key: _serialize_for_column(getattr(source_obj, col.key), col)
            for col in mapper.columns
        }


def _sync_source_object(source_obj, persisted_obj):
    mapper = inspect(source_obj).mapper
    for col in mapper.columns:
        setattr(source_obj, col.key, getattr(persisted_obj, col.key))


def _pk_identity(pk_values):
    if not pk_values:
        return None
    if any(value is None for value in pk_values):
        return None
    return pk_values[0] if len(pk_values) == 1 else tuple(pk_values)


def _apply_operations(session, operations, copy_back_to_source=False):
    persisted = []

    for op in operations:
        model_cls = op["model_class"]
        mapper = inspect(model_cls).mapper
        identity = _pk_identity(op["pk_values"])

        if op["operation"] == "upsert":
            target = session.get(model_cls, identity) if identity is not None else None
            if target is None:
                target = model_cls()
                session.add(target)

            for col in mapper.columns:
                if col.key in op["payload"]:
                    setattr(target, col.key, _deserialize_for_column(op["payload"][col.key], col))
            persisted.append((op, target))
            continue

        if op["operation"] == "delete" and identity is not None:
            target = session.get(model_cls, identity)
            if target is not None:
                session.delete(target)

    session.commit()

    for op, obj in persisted:
        mapper = inspect(obj).mapper
        op["pk_values"] = _pk_values_from_instance(obj, mapper)
        op["payload"] = {
            col.key: _serialize_for_column(getattr(obj, col.key), col)
            for col in mapper.columns
        }
        if copy_back_to_source and op.get("source_obj") is not None:
            _sync_source_object(op["source_obj"], obj)


def _queue_operations_for_sync(session, operations, last_error: str):
    insert_stmt = text(
        f"""
        INSERT INTO {SYNC_QUEUE_TABLE} (model_key, operation, pk_values, payload, attempts, last_error)
        VALUES (:model_key, :operation, CAST(:pk_values AS JSONB), CAST(:payload AS JSONB), 0, :last_error)
        """
    )
    for op in operations:
        session.execute(
            insert_stmt,
            {
                "model_key": op["model_key"],
                "operation": op["operation"],
                "pk_values": json.dumps(op["pk_values"]),
                "payload": json.dumps(op["payload"]) if op["payload"] is not None else None,
                "last_error": last_error[:1000],
            },
        )
    session.commit()


def _drain_sync_queue(primary_session, secondary_session, limit=100):
    if secondary_session is None:
        return

    rows = (
        secondary_session.execute(
            text(
                f"""
                SELECT id, model_key, operation, pk_values, payload, attempts
                FROM {SYNC_QUEUE_TABLE}
                WHERE synced_at IS NULL
                ORDER BY id ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        .mappings()
        .all()
    )

    for row in rows:
        try:
            model_cls = _resolve_model(row["model_key"])
            op = {
                "operation": row["operation"],
                "model_class": model_cls,
                "model_key": row["model_key"],
                "pk_values": row["pk_values"],
                "payload": row["payload"],
                "source_obj": None,
            }
            _apply_operations(primary_session, [op], copy_back_to_source=False)

            secondary_session.execute(
                text(
                    f"""
                    UPDATE {SYNC_QUEUE_TABLE}
                    SET synced_at = NOW(), last_error = NULL
                    WHERE id = :id
                    """
                ),
                {"id": row["id"]},
            )
            secondary_session.commit()
        except Exception as exc:
            primary_session.rollback()
            secondary_session.execute(
                text(
                    f"""
                    UPDATE {SYNC_QUEUE_TABLE}
                    SET attempts = :attempts, last_error = :last_error
                    WHERE id = :id
                    """
                ),
                {
                    "id": row["id"],
                    "attempts": int(row["attempts"]) + 1,
                    "last_error": str(exc)[:1000],
                },
            )
            secondary_session.commit()
            logger.exception("Falha ao sincronizar pendencia %s com a nuvem.", row["id"])
            break


try:
    _ensure_sync_queue_table()
except Exception:
    logger.exception("Nao foi possivel inicializar a fila de sincronizacao offline.")


class DualWriteSession:
    """
    Sessao que le no banco principal e replica escritas no banco local.
    """

    def __init__(self, primary, secondary=None):
        self.primary = primary
        self.secondary = secondary

    def add(self, instance):
        return self.primary.add(instance)

    def add_all(self, instances):
        return self.primary.add_all(instances)

    def delete(self, instance):
        return self.primary.delete(instance)

    def refresh(self, instance, *args, **kwargs):
        try:
            return self.primary.refresh(instance, *args, **kwargs)
        except Exception:
            if self.secondary is None:
                raise

            mapper = inspect(instance).mapper
            pk_values = _pk_values_from_instance(instance, mapper)
            identity = _pk_identity(pk_values)
            if identity is None:
                raise

            secondary_obj = self.secondary.get(instance.__class__, identity)
            if secondary_obj is None:
                raise

            _sync_source_object(instance, secondary_obj)
            return instance

    def rollback(self):
        self.primary.rollback()
        if self.secondary is not None:
            self.secondary.rollback()

    def close(self):
        self.primary.close()
        if self.secondary is not None:
            self.secondary.close()

    def commit(self):
        operations = _snapshot_operations(self.primary)
        try:
            self.primary.commit()
            _refresh_operations_from_source(operations)

            if self.secondary is not None:
                try:
                    _apply_operations(self.secondary, operations, copy_back_to_source=False)
                except Exception:
                    self.secondary.rollback()
                    logger.exception("Falha ao sincronizar escrita no banco local.")

                try:
                    _drain_sync_queue(self.primary, self.secondary)
                except Exception:
                    logger.exception("Falha ao processar fila de pendencias offline.")

        except Exception as cloud_error:
            self.primary.rollback()
            if self.secondary is None:
                raise

            try:
                _apply_operations(self.secondary, operations, copy_back_to_source=True)
                _queue_operations_for_sync(self.secondary, operations, str(cloud_error))
                logger.warning(
                    "Nuvem indisponivel. Escrita salva localmente e enfileirada para sincronizacao."
                )
            except Exception:
                self.secondary.rollback()
                raise

    def __getattr__(self, item):
        return getattr(self.primary, item)


def get_db():
    primary_db = SessionLocal()
    secondary_db = LocalSessionLocal() if LocalSessionLocal is not None else None
    db = DualWriteSession(primary=primary_db, secondary=secondary_db)
    try:
        yield db
    finally:
        db.close()
