# Grievance Redressal Management System (GRMS)

A centralized, web-based platform designed to streamline the process of submitting, tracking, and resolving grievances with transparency and accountability.

## 🚀 Problem Statement
Traditional grievance handling often suffers from a lack of transparency, delayed response times, and poor record management. Manual paperwork and fragmented communication lead to accountability issues, leaving users frustrated and administrators overwhelmed by disorganized data.

### How GRMS Solves the Problem
GRMS centralizes the entire lifecycle of a grievance into a single digital platform:
- **Transparency:** Users can track the status of their grievances in real-time.
- **Accountability:** Role-based access ensures cases are assigned to specific officers and tracked through resolution.
- **Efficiency:** Digital submission forms with document uploads and automated notifications reduce processing time.
- **Data-Driven Insights:** Administrators gain a system-wide view through visualized reports and analytics.

---

## 🛠 Tech Stack
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13+)
- **Database:** [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite by default)
- **Security:** Argon2 hashing (Passlib), Cookie-based sessions
- **Frontend:** Jinja2 Templates, [Tailwind CSS](https://tailwindcss.com/), [Lucide Icons](https://lucide.dev/)
- **Package Management:** [uv](https://github.com/astral-sh/uv)

---

## 🛣 Routes & Navigation

### Authentication & Core
| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing Page (Unauth) / Redirect to Dashboard (Auth) |
| `/login` | GET/POST | User authentication with remember-me support |
| `/register` | GET/POST | Account creation (Role: Student, Faculty, Staff, Officer, Admin) |
| `/logout` | GET | Securely end session and delete cookies |
| `/dashboard` | GET | Role-based router (Redirects to specific dashboard) |
| `/notifications` | GET | Personal alert center (Marks as read on view) |

### Grievance Management
| Route | Method | Description |
|---|---|---|
| `/grievances` | GET | List grievances with Search, Status, and Category filters |
| `/grievances/create` | GET/POST | Submit new grievance with multipart/form-data support |
| `/grievances/{id}` | GET | Detailed view of a case including status timeline |
| `/grievances/{id}/update` | POST | Officer action: Update status and add resolution notes |
| `/grievances/{id}/assign` | POST | Admin action: Assign unassigned cases to specific officers |

### Administration & Reporting
| Route | Method | Description |
|---|---|---|
| `/admin/users` | GET | List and manage all registered system users |
| `/admin/reports` | GET | Visual analytics of grievance distribution and status |
| `/uploads/{file}` | GET | Static file server for supporting documents |

---

## 🏗 System Design
The system follows a modular **FastAPI + Jinja2** architecture:
1.  **Model Layer:** SQLAlchemy ORM handles the database schema (Users, Grievances, Notifications).
2.  **Service Layer:** Business logic for document uploads (to `/uploads`), status tracking, and notification triggers is encapsulated in route handlers.
3.  **Authentication Middleware:** A custom middleware `add_user_to_request` in `main.py` intercepts requests to verify user state via cookies, ensuring secure role-based access control (RBAC).
4.  **Notification Engine:** Event-based triggers generate notifications for users when their cases are assigned or updated.
5.  **Frontend View Engine:** Jinja2 templates are used to render dynamic HTML, styled with Tailwind CSS for a modern, responsive "Dark Theme" experience.

---

## ⚙️ Setup Instructions

This project uses `uv` for lightning-fast Python package management.

### 1. Prerequisites
Ensure you have `uv` installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installation
Clone the repository and sync the dependencies:
```bash
# Clone the repo
git clone 
cd grms

# Sync dependencies and create virtual environment
uv sync
```

### 3. Database Seeding (Optional)
Populate the system with realistic dummy data (Admins, Officers, Users, and Grievances):
```bash
uv run python seed_data.py
```

### 4. Running the Application
Start the development server:
```bash
uv run fastapi dev app/main.py
```
The application will be available at `http://localhost:8000`.

---

## 🔑 Default Credentials (from `seed_data.py`)
- **Admin:** `admin@grms.com` / `admin123`
- **Officer:** `officer1@grms.com` / `officer123`
- **Standard User:** `user1@grms.com` / `user123`
