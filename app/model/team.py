from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..lib.database import Base


class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, index=True)

    # Relationships
    issues = relationship("Issue", back_populates="team")
    projects = relationship("Project", back_populates="team")
    members = relationship("User", back_populates="team")
    cycles = relationship("Cycle", back_populates="team")
