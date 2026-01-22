# RBAC Implementation Roadmap 🛡️

Follow these steps to implement the **Admin -> Team Lead -> User** hierarchy.

## Phase 1: Database & Models Change

### Step 1: Update `app/model/user.py`

Add `role` and `team_id` to the User model.

```python
# app/model/user.py
import enum
from sqlalchemy import Enum as SQLAlchemyEnum

# 1. Define Enum
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEAM_LEAD = "team_lead"
    MEMBER = "member"

class User(Base):
    # ... existing fields ...

    # 2. Add New Columns
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)

    # 3. Add Relationship
    team = relationship("Team", back_populates="members")
```

### Step 2: Update `app/model/team.py`

Add the reverse relationship for members.

```python
# app/model/team.py
class Team(Base):
    # ... existing fields ...

    members = relationship("User", back_populates="team")
```

### Step 3: Run Migrations

Run Alembic to apply these changes to the database.

```bash
alembic revision --autogenerate -m "add_role_and_team_to_user"
alembic upgrade head
```

---

## Phase 2: Authorization Logic (The Core)

### Step 4: Create `app/permissions.py`

This is your "Policy Engine".

```python
# app/permissions.py
from fastapi import HTTPException, status
from app.model.user import User, UserRole

def check_permission(user: User, resource_type: str, action: str, resource=None):
    # --- ADMIN: God Mode ---
    if user.role == UserRole.ADMIN:
        return True

    # --- TEAM LEAD Logic ---
    if user.role == UserRole.TEAM_LEAD:
        # Can only manage issues if they allow to the team's project
        if resource_type == "issue" and action in ["create", "update", "delete"]:
            # Check if issue belongs to a project assigned to user's team
            if resource and resource.project.team_id == user.team_id:
                return True
            return False

        # Team Leads CANNOT create projects
        if resource_type == "project" and action == "create":
            return False

    # --- MEMBER Logic ---
    if user.role == UserRole.MEMBER:
        if resource_type == "issue" and action == "create":
            return True # Can create issues
        # Add more logic...

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to perform this action"
    )
```

---

## Phase 3: Update Routers

### Step 5: Protect Project Routes

Only Admin can create projects.

```python
# app/routers/project.py
@router.post("/")
async def create_project(..., current_user = Depends(get_current_user)):
    # Strict Check
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admins can create projects")

    # ... proceed ...
```

### Step 6: Protect Issue Routes

Use the permission checker.

```python
# app/routers/issue.py
from app.permissions import check_permission

@router.delete("/{id}")
async def delete_issue(id: UUID, ..., current_user = Depends(get_current_user)):
    issue = await service.get(id)

    # Use the centralized logic
    check_permission(current_user, "issue", "delete", resource=issue)

    await service.delete(id)
```

---

## Phase 4: User Management (Admin Dashboard)

### Step 7: Create APIs to Assign Roles

You need a way to promote a user to Team Lead or assign them to a team.

```python
# app/routers/user.py
class UserUpdateRole(BaseModel):
    role: UserRole
    team_id: UUID | None

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    data: UserUpdateRole,
    admin_user = Depends(get_current_user)
):
    # Only Admin can do this
    if admin_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admins can assign roles")

    # ... update logic ...
```
