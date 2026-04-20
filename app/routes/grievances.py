from fastapi import APIRouter, Depends, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime, UTC

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.grievance import Grievance, GrievancePriority, GrievanceStatus
from app.core.templates import render

router = APIRouter(prefix="/grievances")


@router.get("")
def list_grievances(
    request: Request,
    search: str = None,
    status: str = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user:
        return RedirectResponse("/login")

    query = select(Grievance)

    if user.role == UserRole.ADMIN:
        pass # All
    elif user.role == UserRole.OFFICER:
        query = query.where(Grievance.assigned_to == user.id)
    else:
        query = query.where(Grievance.created_by == user.id)

    # Filters
    if search:
        query = query.where(Grievance.title.ilike(f"%{search}%") | Grievance.description.ilike(f"%{search}%"))
    if status and status != "All Status":
        query = query.where(Grievance.status == status.lower().replace(" ", "_"))
    if category and category != "All Categories":
        query = query.where(Grievance.category == category)

    grievances = db.scalars(query.order_by(Grievance.created_at.desc())).all()

    return render(
        request,
        "grievances/list.html",
        {"grievances": grievances, "search": search, "status": status, "category": category},
    )


@router.get("/create")
def create_page(request: Request):
    if not request.state.user:
        return RedirectResponse("/login")
    return render(request, "grievances/create.html")


@router.post("/create")
async def create_grievance(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    priority: GrievancePriority = Form(...),
    document: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = request.state.user
    if not user:
        return RedirectResponse("/login")

    file_path = None
    if document and document.filename:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{datetime.now(UTC).timestamp()}_{document.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)

    grievance = Grievance(
        title=title,
        description=description,
        category=category,
        priority=priority,
        created_by=user.id,
        document_path=file_path
    )

    db.add(grievance)
    db.commit()

    return RedirectResponse("/dashboard", status_code=302)


@router.get("/{id}")
def detail(request: Request, id: int, db: Session = Depends(get_db)):
    user = request.state.user
    if not user:
        return RedirectResponse("/login")

    stmt = select(Grievance).where(Grievance.id == id)
    grievance = db.execute(stmt).scalar_one_or_none()

    if not grievance:
        return RedirectResponse("/dashboard")

    # Authorization check
    if user.role not in [UserRole.ADMIN, UserRole.OFFICER] and grievance.created_by != user.id:
        return RedirectResponse("/dashboard")

    # If admin, fetch officers for assignment
    officers = []
    if user.role == UserRole.ADMIN:
        officers = db.scalars(select(User).where(User.role == UserRole.OFFICER)).all()

    return render(
        request,
        "grievances/detail.html",
        {"g": grievance, "officers": officers},
    )


from app.models.notification import Notification

@router.post("/{id}/update")
def update_grievance(
    request: Request,
    id: int,
    status: GrievanceStatus = Form(...),
    resolution_note: str = Form(None),
    db: Session = Depends(get_db),
):
    user = request.state.user
    if not user or user.role not in [UserRole.ADMIN, UserRole.OFFICER]:
        return RedirectResponse("/dashboard")

    stmt = select(Grievance).where(Grievance.id == id)
    grievance = db.execute(stmt).scalar_one_or_none()

    if not grievance:
        return RedirectResponse("/dashboard")

    old_status = grievance.status
    grievance.status = status
    grievance.resolution_note = resolution_note
    if status == GrievanceStatus.RESOLVED:
        grievance.resolved_at = datetime.now(UTC)

    if old_status != status:
        notif = Notification(
            user_id=grievance.created_by,
            message=f"Your grievance '#{grievance.id}' status has been updated to {status.value}."
        )
        db.add(notif)

    db.commit()

    return RedirectResponse(f"/grievances/{id}", status_code=302)


@router.post("/{id}/assign")
def assign_grievance(
    request: Request,
    id: int,
    officer_id: int = Form(...),
    db: Session = Depends(get_db),
):
    user = request.state.user
    if not user or user.role != UserRole.ADMIN:
        return RedirectResponse("/dashboard")

    stmt = select(Grievance).where(Grievance.id == id)
    grievance = db.execute(stmt).scalar_one_or_none()

    if not grievance:
        return RedirectResponse("/dashboard")

    grievance.assigned_to = officer_id
    grievance.status = GrievanceStatus.IN_PROGRESS
    
    # Notify User
    db.add(Notification(
        user_id=grievance.created_by,
        message=f"Your grievance '#{grievance.id}' has been assigned to an officer."
    ))
    # Notify Officer
    db.add(Notification(
        user_id=officer_id,
        message=f"A new grievance '#{grievance.id}' has been assigned to you."
    ))

    db.commit()

    return RedirectResponse(f"/grievances/{id}", status_code=302)
