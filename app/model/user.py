import enum
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..lib.database import Base
from sqlalchemy import Enum as SQLAlchemyEnum


#  make  the  table for  the  userrole
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEAM_LEAD = "team_lead"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    # Add New Columns
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    avatar_url = Column(String, nullable=True)

    # Relationships
    created_issues = relationship(
        "Issue", foreign_keys="[Issue.creator_id]", back_populates="creator"
    )
    assigned_issues = relationship(
        "Issue", foreign_keys="[Issue.assignee_id]", back_populates="assignee"
    )
    comments = relationship("Comment", back_populates="author")
    team = relationship("Team", back_populates="members")
