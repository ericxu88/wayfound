# app/schemas/graphql_schema.py
import strawberry
from typing import List, Optional
from datetime import datetime

# Simple types for testing
@strawberry.type
class SimpleUser:
    id: str
    email: str
    created_at: str

@strawberry.input
class SimpleUserInput:
    email: str
    password: str

@strawberry.type
class Query:
    
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Wayfound! 🚀"
    
    @strawberry.field
    def test_users(self) -> List[SimpleUser]:
        """Get test users"""
        return [
            SimpleUser(id="1", email="test1@wayfound.com", created_at="2024-01-01"),
            SimpleUser(id="2", email="test2@wayfound.com", created_at="2024-01-02")
        ]
    
    @strawberry.field
    def get_user_count(self) -> int:
        """Get count of users in database"""
        from app.database import SessionLocal
        from app.models import User as UserModel
        
        db = SessionLocal()
        try:
            count = db.query(UserModel).count()
            return count
        finally:
            db.close()

@strawberry.type
class Mutation:
    
    @strawberry.mutation
    def create_test_user(self, input_data: SimpleUserInput) -> SimpleUser:
        """Create a test user"""
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
            
            return SimpleUser(
                id=db_user.id,
                email=db_user.email,
                created_at=db_user.created_at.isoformat()
            )
        finally:
            db.close()

# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)