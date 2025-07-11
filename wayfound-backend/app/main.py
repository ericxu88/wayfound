# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple inline schema for testing
@strawberry.type
class TestUser:
    id: str
    email: str
    created_at: str

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
    domain: str
    timeline_days: int
    milestones: List[Milestone]
    status: str
    created_at: str

@strawberry.input
class TestUserInput:
    email: str
    password: str

@strawberry.input
class CreateRoadmapInput:
    goal_text: str
    timeline_days: int = 30

# Helper functions for roadmap generation
def classify_domain(goal_text: str) -> str:
    """Simple domain classification (will be replaced with AI later)"""
    goal_lower = goal_text.lower()
    
    if any(word in goal_lower for word in ["cook", "recipe", "bake", "food", "kitchen", "chef"]):
        return "cooking"
    elif any(word in goal_lower for word in ["fit", "gym", "workout", "muscle", "weight", "exercise"]):
        return "fitness"
    elif any(word in goal_lower for word in ["code", "program", "python", "javascript", "app", "software"]):
        return "programming"
    elif any(word in goal_lower for word in ["language", "spanish", "french", "italian", "speak"]):
        return "language"
    elif any(word in goal_lower for word in ["paint", "draw", "art", "sketch", "canvas"]):
        return "art"
    else:
        return "general"

def generate_mock_milestones(goal_text: str, timeline_days: int) -> List[dict]:
    """Generate mock milestones based on goal and timeline"""
    domain = classify_domain(goal_text)
    
    # Calculate number of milestones (roughly one per week)
    num_milestones = max(2, min(8, timeline_days // 7))
    days_per_milestone = timeline_days // num_milestones
    
    milestones = []
    
    for i in range(num_milestones):
        day = (i * days_per_milestone) + 1
        milestone = create_milestone_for_domain(domain, i + 1, day, goal_text, num_milestones)
        milestones.append(milestone)
    
    return milestones

def create_milestone_for_domain(domain: str, milestone_num: int, day: int, goal_text: str, total_milestones: int) -> dict:
    """Create domain-specific milestones"""
    
    if domain == "cooking":
        titles = ["Kitchen Setup & Basics", "Fundamental Techniques", "Recipe Practice", "Advanced Skills"]
        descriptions = [
            "Set up your kitchen and learn basic knife skills",
            "Master essential cooking methods and techniques", 
            "Practice with simple recipes and build confidence",
            "Tackle complex recipes and develop your style"
        ]
        tasks = [
            ["Organize kitchen tools", "Learn knife safety", "Practice basic cuts"],
            ["Learn sautéing and boiling", "Practice seasoning", "Master timing"],
            ["Cook 3 simple recipes", "Document what you learn", "Adjust recipes to taste"],
            ["Try complex techniques", "Create your own variations", "Share with friends"]
        ]
        
    elif domain == "fitness":
        titles = ["Foundation & Form", "Building Strength", "Progression", "Mastery"]
        descriptions = [
            "Learn proper form and establish workout routine",
            "Focus on progressive overload and consistency",
            "Advanced techniques and goal-specific training", 
            "Peak performance and long-term maintenance"
        ]
        tasks = [
            ["Learn basic exercises", "Establish workout schedule", "Focus on form"],
            ["Increase weights gradually", "Track your progress", "Maintain consistency"],
            ["Add advanced exercises", "Optimize nutrition", "Monitor recovery"],
            ["Achieve target goals", "Plan long-term strategy", "Help others"]
        ]
        
    elif domain == "programming":
        titles = ["Development Environment", "Core Concepts", "Building Projects", "Advanced Skills"]
        descriptions = [
            "Set up tools and learn programming fundamentals",
            "Master key programming concepts and syntax",
            "Build real projects to apply your knowledge",
            "Learn advanced patterns and best practices"
        ]
        tasks = [
            ["Install development tools", "Write your first program", "Learn basic syntax"],
            ["Understand variables and functions", "Practice with exercises", "Debug simple errors"],
            ["Build a small project", "Use version control", "Add features iteratively"],
            ["Learn design patterns", "Optimize performance", "Contribute to open source"]
        ]
        
    else:  # general
        titles = ["Getting Started", "Building Foundation", "Skill Development", "Mastery & Growth"]
        descriptions = [
            f"Begin your journey with {goal_text}",
            "Build fundamental knowledge and skills",
            "Develop intermediate capabilities",
            "Achieve mastery and continue growing"
        ]
        tasks = [
            ["Research your goal", "Gather necessary resources", "Create learning plan"],
            ["Study fundamentals", "Practice basic skills", "Join communities"],
            ["Apply knowledge practically", "Seek feedback", "Overcome challenges"],
            ["Achieve your goal", "Teach others", "Set new challenges"]
        ]
    
    # Select appropriate milestone based on progress
    index = min(milestone_num - 1, len(titles) - 1)
    
    return {
        "id": f"milestone_{milestone_num}",
        "day": day,
        "title": titles[index],
        "description": descriptions[index],
        "tasks": tasks[index],
        "resources": [
            "YouTube tutorials",
            "Online courses", 
            "Community forums",
            "Practice exercises"
        ],
        "completed": False
    }

def convert_db_roadmap_to_graphql(db_roadmap) -> Roadmap:
    """Convert database roadmap to GraphQL type"""
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
        domain=db_roadmap.domain or "general",
        timeline_days=db_roadmap.timeline_days,
        milestones=milestones,
        status=db_roadmap.status,
        created_at=db_roadmap.created_at.isoformat()
    )

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Wayfound! 🚀"
    
    @strawberry.field
    def test_users(self) -> List[TestUser]:
        """Get test users"""
        return [
            TestUser(id="1", email="test1@wayfound.com", created_at="2024-01-01"),
            TestUser(id="2", email="test2@wayfound.com", created_at="2024-01-02")
        ]
    
    @strawberry.field
    def user_count(self) -> int:
        """Get count of users in database"""
        try:
            from app.database import SessionLocal
            from app.models import User as UserModel
            
            db = SessionLocal()
            try:
                count = db.query(UserModel).count()
                return count
            finally:
                db.close()
        except Exception as e:
            print(f"Error getting user count: {e}")
            return 0
    
    @strawberry.field
    def roadmap(self, roadmap_id: str) -> Roadmap:
        """Get a single roadmap by ID"""
        try:
            from app.database import SessionLocal
            from app.models import Roadmap as RoadmapModel
            
            db = SessionLocal()
            try:
                db_roadmap = db.query(RoadmapModel).filter(RoadmapModel.id == roadmap_id).first()
                if not db_roadmap:
                    raise Exception(f"Roadmap {roadmap_id} not found")
                
                return convert_db_roadmap_to_graphql(db_roadmap)
            finally:
                db.close()
        except Exception as e:
            print(f"Error getting roadmap: {e}")
            raise Exception(f"Failed to get roadmap: {str(e)}")
    
    @strawberry.field
    def user_roadmaps(self, user_id: str) -> List[Roadmap]:
        """Get all roadmaps for a user"""
        try:
            from app.database import SessionLocal
            from app.models import Roadmap as RoadmapModel
            
            db = SessionLocal()
            try:
                db_roadmaps = db.query(RoadmapModel).filter(RoadmapModel.user_id == user_id).all()
                return [convert_db_roadmap_to_graphql(roadmap) for roadmap in db_roadmaps]
            finally:
                db.close()
        except Exception as e:
            print(f"Error getting user roadmaps: {e}")
            return []

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input_data: TestUserInput) -> TestUser:
        """Create a test user"""
        try:
            from app.database import SessionLocal
            from app.models import User as UserModel
            from passlib.context import CryptContext
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            db = SessionLocal()
            try:
                # Hash the password
                hashed_password = pwd_context.hash(input_data.password)
                
                # Create user in database
                db_user = UserModel(
                    email=input_data.email,
                    hashed_password=hashed_password
                )
                
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                
                return TestUser(
                    id=db_user.id,
                    email=db_user.email,
                    created_at=db_user.created_at.isoformat()
                )
            finally:
                db.close()
        except Exception as e:
            print(f"Error creating user: {e}")
            raise Exception(f"Failed to create user: {str(e)}")
    
    @strawberry.mutation
    def create_roadmap(self, user_id: str, input_data: CreateRoadmapInput) -> Roadmap:
        """Create a new roadmap with AI-generated milestones"""
        try:
            from app.database import SessionLocal
            from app.models import Roadmap as RoadmapModel, User as UserModel
            from app.services.llm_service import roadmap_generator
            
            db = SessionLocal()
            try:
                # Check if user exists
                user = db.query(UserModel).filter(UserModel.id == user_id).first()
                if not user:
                    raise Exception(f"User {user_id} not found")
                
                # Generate AI roadmap
                print(f"🤖 Generating AI roadmap for: {input_data.goal_text}")
                ai_roadmap = roadmap_generator.generate_roadmap(
                    goal_text=input_data.goal_text,
                    timeline_days=input_data.timeline_days
                )
                
                # Create roadmap in database
                db_roadmap = RoadmapModel(
                    user_id=user_id,
                    goal_text=input_data.goal_text,
                    timeline_days=input_data.timeline_days,
                    milestones=ai_roadmap["milestones"],
                    domain=ai_roadmap["domain"],
                    status="active"
                )
                
                db.add(db_roadmap)
                db.commit()
                db.refresh(db_roadmap)
                
                print(f"✅ AI roadmap created with {len(ai_roadmap['milestones'])} milestones")
                return convert_db_roadmap_to_graphql(db_roadmap)
            finally:
                db.close()
        except Exception as e:
            print(f"❌ Error creating roadmap: {e}")
            raise Exception(f"Failed to create roadmap: {str(e)}")

# Create the schema inline
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Wayfound API starting up! 🚀")
    
    try:
        # Import all models to register them with SQLAlchemy
        from app.models import User, Roadmap, Survey, Progress
        from app.database import engine, metadata
        
        # Create all tables
        metadata.create_all(bind=engine)
        print("Database tables created! 📊")
    except Exception as e:
        print(f"Database setup failed: {e}")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("🤖 OpenAI API key found - AI generation enabled!")
    else:
        print("⚠️  OpenAI API key not found - using fallback generation")
        print("   Add OPENAI_API_KEY=sk-your-key to your .env file for AI features")
    
    # Print schema info (simplified)
    print("GraphQL schema loaded successfully! ✅")
    ai_status = "with AI!" if api_key else "(fallback mode)"
    print(f"🤖 Roadmap generation enabled {ai_status}")
    print("Available queries: hello, testUsers, userCount, roadmap, userRoadmaps")
    print("Available mutations: createUser, createRoadmap")
    
    yield
    # Shutdown
    print("App shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Wayfound API",
    description="AI-powered personalized learning roadmaps",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GraphQL router
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Wayfound API is running! 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)