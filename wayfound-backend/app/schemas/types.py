# app/schemas/types.py
import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class User:
    id: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

@strawberry.type
class Milestone:
    id: str
    day: int
    title: str
    description: str
    tasks: List[str]
    resources: List[str]
    completed: bool = False

@strawberry.type
class Roadmap:
    id: str
    user_id: str
    goal_text: str
    domain: Optional[str] = None
    timeline_days: int
    milestones: List[Milestone]
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

@strawberry.type
class Survey:
    id: str
    user_id: str
    responses: strawberry.scalars.JSON
    goal_domain: Optional[str] = None
    created_at: datetime

@strawberry.type
class Progress:
    id: str
    roadmap_id: str
    milestone_id: str
    milestone_day: int
    completed: bool
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Input types for mutations
@strawberry.input
class CreateUserInput:
    email: str
    password: str

@strawberry.input
class CreateRoadmapInput:
    goal_text: str
    survey_responses: strawberry.scalars.JSON
    timeline_days: Optional[int] = 30

@strawberry.input
class CreateSurveyInput:
    responses: strawberry.scalars.JSON
    goal_domain: Optional[str] = None

@strawberry.input
class UpdateProgressInput:
    milestone_id: str
    completed: bool
    notes: Optional[str] = None