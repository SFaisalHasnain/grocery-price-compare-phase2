from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import timedelta

from models.user import User, UserCreate, UserLogin, UserInDB, Token
from services.auth_service import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_user_id_from_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from services.database import get_database

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    user_id = get_user_id_from_token(token)
    
    db = await get_database()
    user_dict = await db.users.find_one({"id": user_id})
    
    if user_dict is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(**user_dict)

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user by email"""
    db = await get_database()
    user_dict = await db.users.find_one({"email": email})
    
    if user_dict:
        return UserInDB(**user_dict)
    return None

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_create.password)
    user_dict = user_create.dict()
    user_dict.pop("password")
    
    user_in_db = UserInDB(**user_dict, hashed_password=hashed_password)
    
    # Save to database
    db = await get_database()
    await db.users.insert_one(user_in_db.dict())
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.id}, expires_delta=access_token_expires
    )
    
    # Return user data without password
    user = User(**user_dict, id=user_in_db.id, created_at=user_in_db.created_at)
    
    return Token(access_token=access_token, user=user)

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """Login user"""
    # Check if user exists
    user = await get_user_by_email(user_login.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # Return user data without password
    user_data = User(**{k: v for k, v in user.dict().items() if k != "hashed_password"})
    
    return Token(access_token=access_token, user=user_data)

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_user)
):
    """Update current user information"""
    db = await get_database()
    
    # Only allow updating certain fields
    allowed_fields = ["full_name", "location"]
    update_data = {k: v for k, v in user_update.items() if k in allowed_fields}
    
    if update_data:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
        
        # Return updated user
        updated_user_dict = await db.users.find_one({"id": current_user.id})
        return User(**updated_user_dict)
    
    return current_user
