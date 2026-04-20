from fastapi import Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="app/templates")


from sqlalchemy import select, func
from app.db.session import SessionLocal
from app.models.notification import Notification

def render(request: Request, template_name: str, context: dict | None = None):
    context = context or {}
    
    user = request.state.user
    notification_count = 0
    if user:
        db = SessionLocal()
        try:
            notification_count = db.scalar(
                select(func.count(Notification.id))
                .where(Notification.user_id == user.id, Notification.is_read == False)
            )
        finally:
            db.close()

    base_context = {
        "request": request,
        "user": user,
        "notification_count": notification_count,
    }

    base_context.update(context)

    return templates.TemplateResponse(request, template_name, base_context)
