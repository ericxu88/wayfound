# app/resolvers/roadmap_resolver.py
import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User as UserModel, Roadmap as RoadmapModel
from app.schemas.types import Roadmap, CreateRoadmapInput
import json

class RoadmapResolver:
    
    @staticmethod
    def get_roadmap(roadmap_id: str, db: Session) -> Optional[Roadmap]:
        """Get a single roadmap by ID"""
        db_roadmap = db.query(RoadmapModel).filter(RoadmapModel.id == roadmap_id).first()
        if not db_roadmap:
            return None
            
        return RoadmapResolver._convert_db_to_graphql(db_roadmap)
    
    @staticmethod
    def get_user_roadmaps(user_id: str, db: Session) -> List[Roadmap]:
        """Get all roadmaps for a user"""
        db_roadmaps = db.query(RoadmapModel).filter(RoadmapModel.user_id == user_id).all()
        return [RoadmapResolver._convert_db_to_graphql(roadmap) for roadmap in db_roadmaps]
    
    @staticmethod
    def create_roadmap(user_id: str, input_data: CreateRoadmapInput, db: Session) -> Roadmap:
        """Create a new roadmap (we'll add AI generation later)"""
        
        # For now, create a simple mock roadmap
        # Later we'll replace this with AI-generated content
        mock_milestones = RoadmapResolver._generate_mock_milestones(
            input_data.goal_text, 
            input_data.timeline_days or 30
        )
        
        db_roadmap = RoadmapModel(
            user_id=user_id,
            goal_text=input_data.goal_text,
            timeline_days=input_data.timeline_days or 30,
            milestones=mock_milestones,
            domain="general",  # We'll add AI domain classification later
            status="active"
        )
        
        db.add(db_roadmap)
        db.commit()
        db.refresh(db_roadmap)
        
        return RoadmapResolver._convert_db_to_graphql(db_roadmap)
    
    @staticmethod
    def _convert_db_to_graphql(db_roadmap: RoadmapModel) -> Roadmap:
        """Convert database model to GraphQL type"""
        from app.schemas.types import Milestone
        
        # Convert JSON milestones to GraphQL Milestone objects
        milestones = []
        if db_roadmap.milestones:
            for milestone_data in db_roadmap.milestones:
                milestone = Milestone(
                    id=milestone_data.get("id", ""),
                    day=milestone_data.get("day", 1),
                    title=milestone_data.get("title", ""),
                    description=milestone_data.get("description", ""),
                    tasks=milestone_data.get("tasks", []),
                    resources=milestone_data.get("resources", []),
                    completed=milestone_data.get("completed", False)
                )
                milestones.append(milestone)
        
        return Roadmap(
            id=db_roadmap.id,
            user_id=db_roadmap.user_id,
            goal_text=db_roadmap.goal_text,
            domain=db_roadmap.domain,
            timeline_days=db_roadmap.timeline_days,
            milestones=milestones,
            status=db_roadmap.status,
            created_at=db_roadmap.created_at,
            updated_at=db_roadmap.updated_at,
            completed_at=db_roadmap.completed_at
        )
    
    @staticmethod
    def _generate_mock_milestones(goal_text: str, timeline_days: int) -> List[dict]:
        """Generate mock milestones (will be replaced with AI later)"""
        milestones = []
        
        # Generate simple milestones based on timeline
        weeks = max(1, timeline_days // 7)
        days_per_milestone = max(1, timeline_days // weeks)
        
        for week in range(weeks):
            day = (week * days_per_milestone) + 1
            milestone = {
                "id": f"milestone_{week + 1}",
                "day": day,
                "title": f"Week {week + 1}: Foundation",
                "description": f"Build basic skills for: {goal_text}",
                "tasks": [
                    f"Research basics of your goal",
                    f"Gather necessary materials/tools",
                    f"Practice fundamental skills"
                ],
                "resources": [
                    "YouTube tutorials",
                    "Online articles",
                    "Community forums"
                ],
                "completed": False
            }
            milestones.append(milestone)
        
        return milestones