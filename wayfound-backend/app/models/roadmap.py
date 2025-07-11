# app/models/roadmap.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Goal details
    goal_text = Column(Text, nullable=False)
    domain = Column(String(100), nullable=True)  # e.g., "cooking", "fitness", "coding"
    timeline_days = Column(Integer, nullable=False)  # Total days for the roadmap
    
    # Roadmap content (stored as JSON)
    milestones = Column(JSON, nullable=False)  # Array of milestone objects
    
    # Metadata
    status = Column(String(50), default="active")  # active, completed, paused, abandoned
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="roadmaps")
    progress_entries = relationship("Progress", back_populates="roadmap", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Roadmap(goal='{self.goal_text[:50]}...', timeline={self.timeline_days} days)>"