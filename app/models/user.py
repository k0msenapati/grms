import enum
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"
    OFFICER = "officer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)