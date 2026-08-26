from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.models.user import User, UserRole
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog


class AuthService:

    @staticmethod
    def register(
        db: Session,
        email: str,
        password: str,
        full_name: str,
        phone: str | None,
        ip_address: str | None = None,
    ) -> User:
        existing = db.scalar(
            select(User).where(
                User.email == email.lower().strip()
            )
        )

        if existing:
            raise ValueError(
                "Email already registered"
            )

        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            full_name=full_name.strip(),
            phone=phone.strip() if phone else None,
            role=UserRole.CITIZEN,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        AuthService.log_audit_event(
            db=db,
            user_id=user.id,
            action="USER_REGISTER",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            details=f"Registered citizen account: {user.email}",
        )

        return user

    @staticmethod
    def authenticate(
        db: Session,
        email: str,
        password: str,
        ip_address: str | None = None,
    ) -> User | None:
        user = db.scalar(
            select(User).where(
                User.email == email.lower().strip()
            )
        )

        if not user:
            AuthService.log_audit_event(
                db=db,
                user_id=None,
                action="LOGIN_FAILED",
                resource_type="auth",
                resource_id=email,
                ip_address=ip_address,
                details=f"Failed login attempt for non-existent or wrong email: {email}",
            )
            return None

        if not user.is_active:
            AuthService.log_audit_event(
                db=db,
                user_id=user.id,
                action="LOGIN_BLOCKED_INACTIVE",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=ip_address,
                details=f"Attempted login on deactivated account: {user.email}",
            )
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            AuthService.log_audit_event(
                db=db,
                user_id=user.id,
                action="LOGIN_FAILED_PASSWORD",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=ip_address,
                details=f"Failed password attempt for user: {user.email}",
            )
            return None

        AuthService.log_audit_event(
            db=db,
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            details=f"User logged in successfully with role {user.role.value}",
        )

        return user

    @staticmethod
    def issue_refresh_token(
        db: Session,
        user_id: int,
    ) -> str:
        raw_token, token_hash, expires = create_refresh_token(user_id)
        record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires,
        )
        db.add(record)
        db.commit()
        return raw_token

    @staticmethod
    def rotate_refresh_token(
        db: Session,
        raw_refresh_token: str,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        token_hashed = hash_token(raw_refresh_token)
        record = db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hashed,
                RefreshToken.revoked_at.is_(None),
            )
        )

        if not record:
            raise ValueError("Invalid refresh token")

        now = datetime.now(timezone.utc)
        # Handle naive or timezone-aware expiry
        expires = record.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if expires < now:
            record.revoked_at = now
            db.commit()
            raise ValueError("Refresh token has expired")

        # Invalidate old refresh token (Token Rotation)
        record.revoked_at = now

        user = db.scalar(
            select(User).where(User.id == record.user_id)
        )
        if not user or not user.is_active:
            db.commit()
            raise ValueError("User account is inactive or not found")

        # Issue new tokens
        new_access = create_access_token(user.id, user.role.value)
        new_refresh = AuthService.issue_refresh_token(db, user.id)

        AuthService.log_audit_event(
            db=db,
            user_id=user.id,
            action="TOKEN_ROTATED",
            resource_type="auth",
            resource_id=str(user.id),
            ip_address=ip_address,
            details="Refresh token rotated successfully",
        )

        return user, new_access, new_refresh

    @staticmethod
    def revoke_refresh_token(
        db: Session,
        raw_refresh_token: str,
        ip_address: str | None = None,
    ) -> bool:
        token_hashed = hash_token(raw_refresh_token)
        record = db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hashed,
                RefreshToken.revoked_at.is_(None),
            )
        )
        if record:
            record.revoked_at = datetime.now(timezone.utc)
            db.commit()
            AuthService.log_audit_event(
                db=db,
                user_id=record.user_id,
                action="LOGOUT",
                resource_type="auth",
                resource_id=str(record.user_id),
                ip_address=ip_address,
                details="Session logged out and refresh token revoked",
            )
            return True
        return False

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        return db.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def log_audit_event(
        db: Session,
        user_id: int | None,
        action: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        details: str | None = None,
    ) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details,
        )
        db.add(audit)
        try:
            db.commit()
        except Exception:
            db.rollback()
        return audit

    @staticmethod
    def list_audit_logs(
        db: Session,
        limit: int = 50,
    ) -> list[AuditLog]:
        return list(
            db.scalars(
                select(AuditLog)
                .order_by(desc(AuditLog.created_at))
                .limit(limit)
            ).all()
        )

