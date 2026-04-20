from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.core.templates import render
from app.db.base import Base
from app.db.session import SessionLocal, engine, get_db
from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates

from app.models.user import User, UserRole
from app.models.grievance import Grievance

from app.routes import auth, dashboard, grievances

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    request.state.user = None

    user_id = request.cookies.get("user_id")

    if user_id:
        db = SessionLocal()
        try:
            stmt = select(User).where(User.id == int(user_id))
            user = db.execute(stmt).scalar_one_or_none()
            request.state.user = user
        finally:
            db.close()

    response = await call_next(request)
    return response

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(grievances.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if request.state.user:
        return RedirectResponse("/dashboard")
    return render(request, "landing.html")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return render(request, "auth/login.html")

    stmt = select(User).where(User.id == int(user_id))
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        return render(request, "auth/login.html")
    
    if user.role == UserRole.ADMIN:
        return RedirectResponse("/admin/dashboard")
    elif user.role == UserRole.OFFICER:
        return RedirectResponse("/officer/dashboard")
    else:
        return RedirectResponse("/user/dashboard")
