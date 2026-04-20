from sqlalchemy import func, select
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.templates import render
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.grievance import Grievance, GrievanceStatus
from app.models.notification import Notification

router = APIRouter()


@router.get("/user/dashboard", response_class=HTMLResponse)
def user_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user:
        return RedirectResponse("/login")
    
    total = db.scalar(select(func.count(Grievance.id)).where(Grievance.created_by == user.id))
    pending = db.scalar(select(func.count(Grievance.id)).where(Grievance.created_by == user.id, Grievance.status != GrievanceStatus.RESOLVED))
    resolved = db.scalar(select(func.count(Grievance.id)).where(Grievance.created_by == user.id, Grievance.status == GrievanceStatus.RESOLVED))
    
    recent = db.scalars(select(Grievance).where(Grievance.created_by == user.id).order_by(Grievance.created_at.desc()).limit(5)).all()

    return render(request, "dashboard/user.html", {
        "stats": {"total": total, "pending": pending, "resolved": resolved},
        "recent": recent
    })


@router.get("/officer/dashboard", response_class=HTMLResponse)
def officer_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user or user.role != UserRole.OFFICER:
        return RedirectResponse("/login")
        
    total = db.scalar(select(func.count(Grievance.id)).where(Grievance.assigned_to == user.id))
    pending = db.scalar(select(func.count(Grievance.id)).where(Grievance.assigned_to == user.id, Grievance.status != GrievanceStatus.RESOLVED))
    resolved = db.scalar(select(func.count(Grievance.id)).where(Grievance.assigned_to == user.id, Grievance.status == GrievanceStatus.RESOLVED))
    
    recent = db.scalars(select(Grievance).where(Grievance.assigned_to == user.id).order_by(Grievance.created_at.desc()).limit(5)).all()

    return render(request, "dashboard/officer.html", {
        "stats": {"total": total, "pending": pending, "resolved": resolved},
        "recent": recent
    })


@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user or user.role != UserRole.ADMIN:
        return RedirectResponse("/login")
        
    total = db.scalar(select(func.count(Grievance.id)))
    pending = db.scalar(select(func.count(Grievance.id)).where(Grievance.status != GrievanceStatus.RESOLVED))
    resolved = db.scalar(select(func.count(Grievance.id)).where(Grievance.status == GrievanceStatus.RESOLVED))
    
    users_count = db.scalar(select(func.count(User.id)))
    
    recent = db.scalars(select(Grievance).order_by(Grievance.created_at.desc()).limit(5)).all()

    return render(request, "dashboard/admin.html", {
        "stats": {"total": total, "pending": pending, "resolved": resolved, "users": users_count},
        "recent": recent
    })


@router.get("/admin/reports", response_class=HTMLResponse)
def admin_reports(
    request: Request,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user or user.role != UserRole.ADMIN:
        return RedirectResponse("/login")
        
    # Stats by category
    cat_stats = db.execute(
        select(Grievance.category, func.count(Grievance.id))
        .group_by(Grievance.category)
    ).all()
    
    # Stats by status
    status_stats = db.execute(
        select(Grievance.status, func.count(Grievance.id))
        .group_by(Grievance.status)
    ).all()

    return render(request, "dashboard/reports.html", {
        "cat_stats": cat_stats,
        "status_stats": status_stats
    })

@router.get("/notifications", response_class=HTMLResponse)
def list_notifications(
    request: Request,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user:
        return RedirectResponse("/login")
        
    notifications = db.scalars(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    ).all()
    
    # Mark as read
    for n in notifications:
        n.is_read = True
    db.commit()

    return render(request, "dashboard/notifications.html", {
        "notifications": notifications
    })

@router.get("/admin/users", response_class=HTMLResponse)
def admin_users(
    request: Request,
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user or user.role != UserRole.ADMIN:
        return RedirectResponse("/login")
        
    users = db.scalars(select(User).order_by(User.id.asc())).all()

    return render(request, "dashboard/users_list.html", {
        "users": users
    })
