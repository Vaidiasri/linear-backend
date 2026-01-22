from typing import Any, Optional
from app.model.user import User, UserRole

# --- Condition Functions ---


def is_admin(user: User, resource: Any = None) -> bool:
    return user.role == UserRole.ADMIN


def is_member(user: User, resource: Any = None) -> bool:
    return user.role == UserRole.MEMBER


def is_team_lead(user: User, resource: Any = None) -> bool:
    return user.role == UserRole.TEAM_LEAD


def is_creator(user: User, resource: Any) -> bool:
    if not resource:
        return False
    return getattr(resource, "created_by_id", None) == user.id


def is_team_resource(user: User, resource: Any) -> bool:
    if not resource:
        return False

    # If resource is Project
    if hasattr(resource, "team_id"):
        if resource.team_id == user.team_id:
            return True

    # If resource is Issue (has project relationship)
    project = getattr(resource, "project", None)
    if project and getattr(project, "team_id", None) == user.team_id:
        return True

    return False


# --- Policy Definitions ---

POLICIES = [
    # 1. Admin: God Mode
    {
        "name": "admin_access",
        "action": "*",  # Matches ANY action on ANY resource
        "condition": is_admin,
    },
    # 2. Team Lead: Manage Team Issues
    {
        "name": "team_lead_manage_team_issues",
        "action": "issue:create",
        "condition": lambda u, r: is_team_lead(u) and is_team_resource(u, r),
    },
    {
        "name": "team_lead_update_team_issues",
        "action": "issue:update",
        "condition": lambda u, r: is_team_lead(u) and is_team_resource(u, r),
    },
    {
        "name": "team_lead_delete_team_issues",
        "action": "issue:delete",
        "condition": lambda u, r: is_team_lead(u) and is_team_resource(u, r),
    },
    {
        "name": "team_lead_read_team_issues",
        "action": "issue:read",
        "condition": lambda u, r: is_team_lead(u) and is_team_resource(u, r),
    },
    # 3. Member: Create & Read All
    {
        "name": "member_create_issue",
        "action": "issue:create",
        "condition": lambda u, r: is_member(u),  # Can create generally
    },
    {
        "name": "member_read_issue",
        "action": "issue:read",
        "condition": lambda u, r: is_member(u),  # Can read generally
    },
    # 4. Member: Update Own
    {
        "name": "member_update_own_issue",
        "action": "issue:update",
        "condition": lambda u, r: is_member(u) and is_creator(u, r),
    },
]
