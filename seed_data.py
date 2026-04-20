from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.grievance import Grievance, GrievanceStatus, GrievancePriority
from app.models.notification import Notification
from app.core.security import hash_password
from datetime import datetime, timedelta, UTC
import random
import os

def seed():
    # Recreate tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Ensure uploads dir exists
    os.makedirs("uploads", exist_ok=True)
    
    db = SessionLocal()
    
    print("Seeding database...")
    
    # 1. Create Admins
    admin = User(
        name="System Admin",
        email="admin@grms.com",
        password=hash_password("admin123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    
    # 2. Create Officers
    officers = []
    for i in range(1, 4):
        officer = User(
            name=f"Officer {i}",
            email=f"officer{i}@grms.com",
            password=hash_password("officer123"),
            role=UserRole.OFFICER
        )
        db.add(officer)
        officers.append(officer)
    
    # 3. Create Users
    users = []
    roles = [UserRole.STUDENT, UserRole.FACULTY, UserRole.STAFF]
    for i in range(1, 11):
        role = random.choice(roles)
        user = User(
            name=f"User {i} ({role.value})",
            email=f"user{i}@grms.com",
            password=hash_password("user123"),
            role=role
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    
    # 4. Create Grievances
    categories = ["Academic", "Administrative", "Facilities", "Hostel", "Other"]
    titles = [
        "Issue with Exam Schedule", "Delayed Salary Payment", "Water Leak in Hostel",
        "WiFi Connectivity Problems", "Library Books Unavailable", "Mess Food Quality",
        "Late Grade Submission", "Parking Space Shortage", "Classroom AC Not Working",
        "ID Card Replacement Delay", "Scholarship Application Issue", "Lab Equipment Broken"
    ]
    
    for i in range(25):
        creator = random.choice(users)
        status = random.choice(list(GrievanceStatus))
        priority = random.choice(list(GrievancePriority))
        category = random.choice(categories)
        
        created_at = datetime.now(UTC) - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        g = Grievance(
            title=random.choice(titles),
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            category=category,
            priority=priority,
            status=status,
            created_by=creator.id,
            created_at=created_at
        )
        
        # Assignment and Resolution based on status
        if status in [GrievanceStatus.IN_PROGRESS, GrievanceStatus.RESOLVED]:
            g.assigned_to = random.choice(officers).id
            
        if status == GrievanceStatus.RESOLVED:
            g.resolution_note = "This issue has been successfully resolved after investigation."
            g.resolved_at = created_at + timedelta(days=random.randint(1, 5))
            
        db.add(g)
        db.flush() # Get ID
        
        # Add a notification for each
        db.add(Notification(
            user_id=creator.id,
            message=f"Grievance '#{g.id}' has been {status.value}.",
            created_at=created_at + timedelta(minutes=5)
        ))
    
    db.commit()
    print("Seeding completed successfully!")
    db.close()

if __name__ == "__main__":
    seed()
