# app/models/survey.py
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Survey responses (stored as JSON for flexibility)
    responses = Column(JSON, nullable=False)
    # Example structure:
    # {
    #   "skill_level": "Beginner",
    #   "time_per_day": "30 minutes", 
    #   "learning_style": "Visual",
    #   "timeline_preference": "Flexible",
    #   "specific_interests": ["Italian cooking", "Pasta making"]
    # }
    
    # Goal context
    goal_domain = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="surveys")

    def __repr__(self):
        return f"<Survey(user_id='{self.user_id}', domain='{self.goal_domain}')>"