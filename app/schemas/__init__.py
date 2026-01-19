"""
Schemas package - Pydantic models for request/response validation
"""

from .user import UserBase, UserCreate, UserOut
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

# Update IssueDetailOut with proper types now that imports are available
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    IssueDetailOut.model_rebuild()

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserOut",
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
]
