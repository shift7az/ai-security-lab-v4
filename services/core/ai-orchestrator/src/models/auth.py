"""
Authentication Models for AI Security Lab v4.0
"""

from typing import Optional
from datetime import datetime
from enum import Enum

from .base import BaseModel


class UserRole(str, Enum):
    """User role types."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(BaseModel):
    """User model."""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserCreate(BaseModel):
    """User creation model."""
    username: str
    email: str
    password: str
    role: UserRole = UserRole.OPERATOR


class UserInDB(User):
    """User model with password hash (for database)."""
    password_hash: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class TokenData(BaseModel):
    """Data stored in JWT token."""
    user_id: str
    username: str
    role: str


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    token: Token
    user: User
