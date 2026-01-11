from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..lib.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_issues = relationship(
        "Issue", foreign_keys="[Issue.creator_id]", back_populates="creator"
    )
    assigned_issues = relationship(
        "Issue", foreign_keys="[Issue.assignee_id]", back_populates="assignee"
    )


class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    key = Column(
        String, unique=True, index=True
    )  # Example ticket kis ki hai let say 'Frontend'
    # make  the  relationship with issues
    issues = relationship("Issue", back_populates="team")
    projects = relationship("Project", back_populates="team")


class Issue(Base):
    __tablename__ = "issues"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ENG-1, ENG-2 banane ke liye ye identifier kaam aayega
    identifier = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="backlog")  # todo, in-progress, done
    priority = Column(Integer, default=0)  # 0 to 4

    # Relationships (Foreign Keys)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    creator = relationship(
        "User", foreign_keys=[creator_id]
    )  # user  aur  issue  ko connent  kar  liya hai
    assignee = relationship("User", foreign_keys=[assignee_id])
    team = relationship("Team", back_populates="issues")
    project = relationship("Project", back_populates="issues")

    # Self-reference for Sub-tasks (Advanced Logic)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("issues.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


#  projet  model
class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Ye Project kis Team ka hai?
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    team = relationship("Team", back_populates="projects")
    issues = relationship("Issue", back_populates="project")
