from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from models.user import User, UserInDB
from services.auth_service import get_user_id_from_token
from services.database import get_database

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