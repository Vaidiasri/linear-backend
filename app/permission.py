# app/permissions.py
from fastapi import HTTPException, status
from app.model.user import User, UserRole
from typing import Optional, Any

def check_permission(
    user: Optional[User], 
    resource_type: str, 
    action: str, 
    resource: Optional[Any] = None
) -> bool:
    """
    Check if user has permission to perform an action on a resource.
    
    Args:
        user: Authenticated user object
        resource_type: Type of resource ("issue", "project", etc.)
        action: Action to perform ("create", "read", "update", "delete")
        resource: The resource object being accessed (optional)
    
    Returns:
        bool: True if permission granted
    
    Raises:
        HTTPException: 403 Forbidden if permission denied
    
    Note:
        For TEAM_LEAD checks, ensure resource.project is eagerly loaded
    """
    
    # --- Input Validation ---
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User authentication required"
        )
    
    if not resource_type or not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource_type or action"
        )

    # --- ADMIN: God Mode ---
    if user.role == UserRole.ADMIN:
        return True

    # --- TEAM LEAD Logic ---
    if user.role == UserRole.TEAM_LEAD:
        if resource_type == "issue" and action in ["create", "update", "delete"]:
            # Check if issue belongs to a project assigned to user's team
            if resource:
                # Safely access nested attributes
                project = getattr(resource, "project", None)
                if project is None:
                    return False
                team_id = getattr(project, "team_id", None)
                if team_id == user.team_id:
                    return True
            return False

        # Team Leads CAN read issues from their team
        if resource_type == "issue" and action == "read":
            if resource:
                project = getattr(resource, "project", None)
                if project and getattr(project, "team_id", None) == user.team_id:
                    return True
            return False

        # Team Leads CANNOT create projects
        if resource_type == "project" and action == "create":
            return False

    # --- MEMBER Logic ---
    if user.role == UserRole.MEMBER:
        # Can create issues
        if resource_type == "issue" and action == "create":
            return True
        
        # Can read issues
        if resource_type == "issue" and action == "read":
            return True
        
        # Can update own issues
        if resource_type == "issue" and action == "update":
            if resource and getattr(resource, "created_by_id", None) == user.id:
                return True
            return False
        
        # Cannot delete issues
        if resource_type == "issue" and action == "delete":
            return False

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to perform this action"
    )