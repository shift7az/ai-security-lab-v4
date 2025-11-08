"""
Authentication API Endpoints for AI Security Lab v4.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..models.auth import LoginRequest, LoginResponse, Token, User, UserCreate
from ..services.auth_service import AuthService
from ..services.database import DatabaseService

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# Initialize services
auth_service: Optional[AuthService] = None
db_service: Optional[DatabaseService] = None


async def get_auth_service() -> AuthService:
    """Dependency to get auth service instance."""
    global auth_service
    if auth_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not initialized"
        )
    return auth_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_svc: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token
        auth_svc: Auth service instance
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    user = await auth_svc.get_current_user(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to verify current user has admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def init_auth_api(auth_svc: AuthService, db_svc: DatabaseService):
    """
    Initialize auth API with service instances.
    
    Args:
        auth_svc: Auth service instance
        db_svc: Database service instance
    """
    global auth_service, db_service
    auth_service = auth_svc
    db_service = db_svc


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_svc: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return JWT token.
    
    Args:
        request: Login credentials (username/password)
        auth_svc: Auth service instance
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = await auth_svc.authenticate_user(request.username, request.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    token = auth_svc.create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    # Update last login time
    if db_service:
        await db_service.execute(
            """
            UPDATE users 
            SET last_login = NOW() 
            WHERE id = $1
            """,
            user.id
        )
    
    return LoginResponse(
        token=token,
        user=user
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: For JWT tokens, logout is typically handled client-side by
    removing the token. Server-side blacklisting can be added if needed.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    return {
        "message": "Successfully logged out",
        "user_id": current_user.id
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    auth_svc: AuthService = Depends(get_auth_service)
):
    """
    Refresh JWT token for current user.
    
    Args:
        current_user: Current authenticated user
        auth_svc: Auth service instance
        
    Returns:
        New JWT token
    """
    # Generate new token
    token = auth_svc.create_access_token(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role
    )
    
    return token


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    auth_svc: AuthService = Depends(get_auth_service),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Register a new user (admin only).
    
    Args:
        user_data: User registration data
        auth_svc: Auth service instance
        current_admin: Current admin user
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username/email already exists
    """
    # Check if username exists
    existing_user = await db_service.fetchrow(
        "SELECT id FROM users WHERE username = $1",
        user_data.username
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = await db_service.fetchrow(
        "SELECT id FROM users WHERE email = $1",
        user_data.email
    )
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await auth_svc.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role
    )
    
    return user


@router.get("/users", response_model=list[User])
async def list_users(
    current_admin: User = Depends(get_current_active_admin)
):
    """
    List all users (admin only).
    
    Args:
        current_admin: Current admin user
        
    Returns:
        List of all users
    """
    rows = await db_service.fetch(
        """
        SELECT id, username, email, role, is_active, created_at, last_login
        FROM users
        ORDER BY created_at DESC
        """
    )
    
    return [User(**dict(row)) for row in rows]


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Delete a user (admin only).
    
    Args:
        user_id: User ID to delete
        current_admin: Current admin user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or trying to delete self
    """
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    result = await db_service.execute(
        "DELETE FROM users WHERE id = $1",
        user_id
    )
    
    if result == "DELETE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully", "user_id": user_id}
