from fastapi import Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    stmt = select(User).where(User.id == int(user_id))
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user