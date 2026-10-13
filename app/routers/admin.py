from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_admin
from ..models import SecurityLog, User

router = APIRouter(
    prefix="/admin",
    tags=["Administração"],
)


@router.get("/security-logs")
def list_security_logs(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    logs = db.query(SecurityLog).order_by(SecurityLog.id.desc()).limit(200).all()

    return [
        {
            "id": log.id,
            "event": log.event,
            "user_id": log.user_id,
            "ip_address": log.ip_address,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
