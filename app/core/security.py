from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

SECRET_KEY = "enterprise-ai-demo-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security_scheme = HTTPBearer()


# Demo users for the local portfolio application.
# In production these would come from an enterprise
# identity provider such as Azure AD/Entra ID, Okta, etc.
DEMO_USERS = {
    "operations_user": {
        "password": "operations123",
        "user_id": "user-001",
        "roles": ["operations"],
        "department": "payments",
    },
    "support_user": {
        "password": "support123",
        "user_id": "user-002",
        "roles": ["support"],
        "department": "customer-support",
    },
    "admin_user": {
        "password": "admin123",
        "user_id": "user-003",
        "roles": ["admin"],
        "department": "platform",
    },
}


def create_access_token(
    username: str,
    user: dict[str, Any],
) -> str:
    """Create a signed JWT containing the user's authorization claims."""

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user["user_id"],
        "username": username,
        "roles": user["roles"],
        "department": user["department"],
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def authenticate_user(
    username: str,
    password: str,
) -> dict[str, Any] | None:
    """Authenticate a demo user."""

    user = DEMO_USERS.get(username)

    if not user:
        return None

    if user["password"] != password:
        return None

    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict[str, Any]:
    """Validate JWT and return the authenticated user's claims."""

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        username = payload.get("username")
        roles = payload.get("roles", [])
        department = payload.get("department")

        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        return {
            "user_id": user_id,
            "username": username,
            "roles": roles,
            "department": department,
        }

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
        ) from exc

    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc

def require_role(required_role: str):
    def role_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        if required_role not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' is required",
            )

        return current_user

    return role_checker