from fastapi import Depends, HTTPException, status

from app.models.user import UserRole


def require_roles(*allowed_roles: UserRole):

    def checker(current_user):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return checker
