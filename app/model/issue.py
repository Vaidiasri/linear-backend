from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..lib.database import Base


class Issue(Base):
    __tablename__ = "issues"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="backlog")
    priority = Column(Integer, default=0)

    # Foreign Keys
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("issues.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    team = relationship("Team", back_populates="issues")
    project = relationship("Project", back_populates="issues")
    comments = relationship("Comment", back_populates="issue")
    activities = relationship("Activity", back_populates="issue")