"""
Authentication Service for AI Security Lab v4.0
JWT token generation and password hashing
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt

from ..models.auth import User, UserInDB, Token, TokenData, UserRole
from ..services.database import DatabaseService

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class AuthService:
    """Authentication service with JWT and password hashing."""
    
    def __init__(self, db: DatabaseService):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    
    def create_access_token(self, user: User) -> Token:
        """Create JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": user.id,
            "username": user.username,
            "role": user.role,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return Token(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            username = payload.get("username")
            role = payload.get("role")
            
            if user_id is None or username is None:
                return None
            
            return TokenData(user_id=user_id, username=username, role=role)
        except jwt.PyJWTError:
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        query = "SELECT * FROM users WHERE username = $1 AND is_active = TRUE"
        user_data = await self.db.fetch_one(query, username)
        
        if not user_data:
            return None
        
        if not self.verify_password(password, user_data['password_hash']):
            return None
        
        # Update last login
        await self.db.execute(
            "UPDATE users SET last_login = NOW() WHERE id = $1",
            user_data['id']
        )
        
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            role=UserRole(user_data['role']),
            is_active=user_data['is_active'],
            created_at=user_data.get('created_at'),
            last_login=datetime.utcnow()
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        query = "SELECT * FROM users WHERE id = $1 AND is_active = TRUE"
        user_data = await self.db.fetch_one(query, user_id)
        
        if not user_data:
            return None
        
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            role=UserRole(user_data['role']),
            is_active=user_data['is_active'],
            created_at=user_data.get('created_at'),
            last_login=user_data.get('last_login')
        )
