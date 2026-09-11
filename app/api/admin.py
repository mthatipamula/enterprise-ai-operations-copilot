from fastapi import APIRouter, Depends

from app.core.security import require_role

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
)


@router.get("/status")
def admin_status(
    current_user: dict = Depends(require_role("admin")),
):
    return {
        "message": "Admin access granted",
        "user": current_user["username"],
        "roles": current_user["roles"],
    }