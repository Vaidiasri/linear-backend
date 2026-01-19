from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..lib.database import Base
import uuid

class Attachment(Base): # Naam thoda professional 'Attachment' rakhte hain
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False) # Asli naam (e.g. bug.png)
    file_path = Column(String, nullable=False) # Storage path (e.g. static/uuid_bug.png)
    
    # Kiske liye hai? (Relationship with Issue)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    
    # Kisne kiya? (Relationship with User)
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    