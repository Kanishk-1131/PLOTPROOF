from enum import Enum
from fastapi import HTTPException, status

from app.models.user import UserRole, User


class Permission(str, Enum):
    VERIFICATION_VIEW = "VERIFICATION_VIEW"
    VERIFICATION_APPROVE = "VERIFICATION_APPROVE"
    VERIFICATION_REJECT = "VERIFICATION_REJECT"
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"
    DOCUMENT_VIEW = "DOCUMENT_VIEW"
    DOCUMENT_DELETE = "DOCUMENT_DELETE"
    USER_MANAGE = "USER_MANAGE"
    AUDIT_VIEW = "AUDIT_VIEW"
    BLOCKCHAIN_ANCHOR = "BLOCKCHAIN_ANCHOR"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.CITIZEN: {
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_VIEW,
        Permission.VERIFICATION_VIEW,
    },
    UserRole.REGISTRAR: {
        Permission.DOCUMENT_VIEW,
        Permission.VERIFICATION_VIEW,
        Permission.VERIFICATION_APPROVE,
        Permission.VERIFICATION_REJECT,
        Permission.BLOCKCHAIN_ANCHOR,
        Permission.AUDIT_VIEW,
    },
    UserRole.BANK_OFFICER: {
        Permission.DOCUMENT_VIEW,
        Permission.VERIFICATION_VIEW,
    },
    UserRole.ADMIN: {
        Permission.VERIFICATION_VIEW,
        Permission.VERIFICATION_APPROVE,
        Permission.VERIFICATION_REJECT,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_VIEW,
        Permission.DOCUMENT_DELETE,
        Permission.USER_MANAGE,
        Permission.AUDIT_VIEW,
        Permission.BLOCKCHAIN_ANCHOR,
    },
}


def has_permission(user: User, permission: Permission) -> bool:
    user_perms = ROLE_PERMISSIONS.get(user.role, set())
    return permission in user_perms


def require_permissions(*required_perms: Permission):
    def checker(current_user: User):
        user_perms = ROLE_PERMISSIONS.get(current_user.role, set())
        for perm in required_perms:
            if perm not in user_perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: requires {perm.value}",
                )
        return current_user

    return checker


def require_roles(*allowed_roles: UserRole):
    def checker(current_user: User):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return checker

