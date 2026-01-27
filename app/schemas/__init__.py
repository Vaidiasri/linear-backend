"""
Schemas package - Pydantic models for request/response validation
"""

from .user import UserBase, UserCreate, UserOut, UserUpdateRole
from .team import TeamCreate, TeamOut
from .project import ProjectCreate, ProjectOut
from .issue import (
    IssueStatus,
    IssuePriority,
    IssueBase,
    IssueCreate,
    IssueOut,
    IssueDetailOut,
    IssueStats,
)
from .comment import CommentCreate, CommentOut
from .activity import ActivityOut
from .attached import AttachmentOut
from .dashboard import DashboardOut

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserOut",
    "UserUpdateRole",
    # Team
    "TeamCreate",
    "TeamOut",
    # Project
    "ProjectCreate",
    "ProjectOut",
    # Issue
    "IssueStatus",
    "IssuePriority",
    "IssueBase",
    "IssueCreate",
    "IssueOut",
    "IssueDetailOut",
    # Comment
    "CommentCreate",
    "CommentOut",
    # Activity
    "ActivityOut",
    # Attachmet
    "AttachmentOut",
    # Dashboard
    "DashboardOut",
]
