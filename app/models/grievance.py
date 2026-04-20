import enum
from datetime import UTC, datetime
from sqlalchemy import String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GrievanceStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class GrievancePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Grievance(Base):
    __tablename__ = "grievances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text())

    category: Mapped[str] = mapped_column(String(100))
    priority: Mapped[GrievancePriority] = mapped_column(
        Enum(GrievancePriority), default=GrievancePriority.MEDIUM
    )

    status: Mapped[GrievanceStatus] = mapped_column(
        Enum(GrievanceStatus), default=GrievanceStatus.SUBMITTED
    )

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    resolution_note: Mapped[str | None] = mapped_column(Text(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    document_path: Mapped[str | None] = mapped_column(String(255), nullable=True)