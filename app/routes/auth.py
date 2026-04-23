from sqlalchemy import select
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.templates import render
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password

from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login/admin", response_class=HTMLResponse)
def login_admin_page(request: Request):
    return render(request, "auth/login_admin.html", {"title": "ADMIN LOGIN", "role": "Admin"})


@router.post("/login/admin")
def login_admin(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    stmt = select(User).where(User.email == email, User.role == UserRole.ADMIN)
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        return render(request, "auth/login_admin.html", {"title": "ADMIN LOGIN", "role": "Admin", "error": "Invalid admin email or password"})

    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(key="user_id", value=str(user.id))
    return response


@router.get("/login/officer", response_class=HTMLResponse)
def login_officer_page(request: Request):
    return render(request, "auth/login_officer.html", {"title": "OFFICER LOGIN", "role": "Officer"})


@router.post("/login/officer")
def login_officer(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    stmt = select(User).where(User.email == email, User.role == UserRole.OFFICER)
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        return render(request, "auth/login_officer.html", {"title": "OFFICER LOGIN", "role": "Officer", "error": "Invalid officer email or password"})

    response = RedirectResponse(url="/officer/dashboard", status_code=302)
    response.set_cookie(key="user_id", value=str(user.id))
    return response


@router.get("/login/user", response_class=HTMLResponse)
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render(request, "auth/login_user.html", {"title": "USER LOGIN", "role": "User"})


@router.post("/login/user")
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    stmt = select(User).where(User.email == email)
    user = db.execute(stmt).scalar_one_or_none()

    # Regular users shouldn't be admin/officer login via this if we want strict separation, 
    # but the request didn't specify that they can't login via the general user login.
    # However, to keep it simple and consistent:
    if not user or not verify_password(password, user.password):
        return render(request, "auth/login_user.html", {"title": "USER LOGIN", "role": "User", "error": "Invalid email or password"})

    if user.role == UserRole.ADMIN:
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
    elif user.role == UserRole.OFFICER:
        response = RedirectResponse(url="/officer/dashboard", status_code=302)
    else:
        response = RedirectResponse(url="/user/dashboard", status_code=302)

    response.set_cookie(key="user_id", value=str(user.id))
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return render(request, "auth/register.html")


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: UserRole = Form(...),
    db: Session = Depends(get_db),
):
    stmt = select(User).where(User.email == email)
    existing = db.execute(stmt).scalar_one_or_none()

    if existing:
        return render(request, "auth/register.html", {'error': "Email already exists"})

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
    )

    db.add(user)
    db.commit()

    return RedirectResponse(url="/login", status_code=302)


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_id")
    return response