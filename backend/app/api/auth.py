from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_token
from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    LogoutResponse,
    AuditLogResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        user_id = int(user_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
        )

    return user


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    request: RegisterRequest,
    req: Request,
    db: Session = Depends(get_db),
):
    client_ip = req.client.host if req.client else None
    try:
        user = AuthService.register(
            db=db,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone,
            ip_address=client_ip,
        )
        return user
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_db),
):
    client_ip = req.client.host if req.client else None
    user = AuthService.authenticate(
        db,
        request.email,
        request.password,
        ip_address=client_ip,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )
    refresh_token = AuthService.issue_refresh_token(
        db=db,
        user_id=user.id,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    request: RefreshTokenRequest,
    req: Request,
    db: Session = Depends(get_db),
):
    client_ip = req.client.host if req.client else None
    try:
        user, new_access, new_refresh = AuthService.rotate_refresh_token(
            db=db,
            raw_refresh_token=request.refresh_token,
            ip_address=client_ip,
        )
        return TokenResponse(
            access_token=new_access,
            token_type="bearer",
            refresh_token=new_refresh,
            user=UserResponse.model_validate(user),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
def logout(
    request: RefreshTokenRequest,
    req: Request,
    db: Session = Depends(get_db),
):
    client_ip = req.client.host if req.client else None
    AuthService.revoke_refresh_token(
        db=db,
        raw_refresh_token=request.refresh_token,
        ip_address=client_ip,
    )
    return LogoutResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/audit-logs",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only Admin or Registrar can view audit trails
    if current_user.role not in (UserRole.ADMIN, UserRole.REGISTRAR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators and Registrars may inspect audit logs",
        )
    return AuthService.list_audit_logs(db=db, limit=limit)

