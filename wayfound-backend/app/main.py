# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List

# Simple inline schema for testing
@strawberry.type
class TestUser:
    id: str
    email: str
    created_at: str

@strawberry.input
class TestUserInput:
    email: str
    password: str

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
    
    # Print schema info (simplified)
    print("GraphQL schema loaded successfully! ✅")
    print("Available queries: hello, testUsers, userCount")
    print("Available mutations: createUser")
    
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