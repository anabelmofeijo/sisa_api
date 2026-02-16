from app import APIRouter, Depends, get_db, HTTPException
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from sqlalchemy.orm import Session
from app.crud.user import CRUDUser
from app.core.security import create_access_token, get_current_user, verify_password, hash_password

router = APIRouter()

@router.get("/")
async def running():
    """
    Health check endpoint.

    This endpoint is used to verify if the user service is running correctly.

    Returns:
        dict: A simple message confirming the service is active.
    """
    return {"message": "users is running"}

@router.post("/create_user", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    This endpoint receives user data and creates a new user in the database.

    Args:
        user (UserCreate): User data required for creation.
        db (Session): Database session dependency.

    Returns:
        UserResponse: The newly created user.
    """
    crud = CRUDUser()
    return crud.create_user(db, user)

@router.get("/list_users", response_model=list[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Retrieve all users.

    This endpoint returns a list of all registered users in the system.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[UserResponse]: A list containing all users.
    """
    crud = CRUDUser()
    return crud.list_users(db)

@router.delete("/delete_user/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete a user by ID.

    This endpoint removes a user from the database based on the provided user ID.

    Args:
        user_id (int): The ID of the user to be deleted.
        db (Session): Database session dependency.

    Returns:
        dict: A success or failure message.
    """
    crud = CRUDUser()
    success = crud.delete_user(db, user_id)

    if success:
        return {"message": "User deleted successfully"}

    return {"message": "User not found"}

@router.put("/update_user/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update an existing user.

    This endpoint updates the information of a user identified by the given ID.

    Args:
        user_id (int): The ID of the user to update.
        user_update (UserCreate): Updated user data.
        db (Session): Database session dependency.

    Returns:
        UserResponse: The updated user data.
    """
    crud = CRUDUser()
    updated_user = crud.update_user(db, user_id, user_update)

    if updated_user:
        return updated_user

    raise HTTPException(status_code=404, detail="User not found")

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.

    This endpoint is typically used for authentication purposes.
    It verifies if a user exists with the given email and password.

    Args:
        data (UserLogin): User credentials.
        db (Session): Database session dependency.

    Returns:
        TokenResponse: Access token for authenticated requests.

    Raises:
        HTTPException: If the user is not found or credentials are invalid.
    """
    crud = CRUDUser()
    user = crud.get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(data.password, user.password):
        # Compatibilidade: permite login de senhas antigas em texto puro e migra para hash.
        if user.password != data.password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        user.password = hash_password(data.password)
        db.commit()
        db.refresh(user)

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)
