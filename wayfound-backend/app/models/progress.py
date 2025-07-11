# app/models/progress.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Progress(Base):
    __tablename__ = "progress"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    roadmap_id = Column(String, ForeignKey("roadmaps.id"), nullable=False)
    
    # Milestone tracking
    milestone_id = Column(String(100), nullable=False)  # References milestone in roadmap JSON
    milestone_day = Column(Integer, nullable=False)  # Which day this milestone is for
    
    # Progress status
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Optional user notes
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="progress_entries")

    def __repr__(self):
        status = "✅" if self.completed else "⏳"
        return f"<Progress({status} Day {self.milestone_day}, milestone: {self.milestone_id})>"