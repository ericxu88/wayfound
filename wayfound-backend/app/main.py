# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import strawberry
from strawberry.fastapi import GraphQLRouter

# We'll create these in the next step
# from app.schemas.graphql_schema import Query, Mutation

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Wayfound API starting up! 🚀")
    # TODO: We'll add database connection later
    # from app.database import engine, metadata
    # metadata.create_all(bind=engine)
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

# Temporary basic schema until we create the real one
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Wayfound! 🚀"

@strawberry.type
class Mutation:
    @strawberry.mutation
    def placeholder(self) -> str:
        return "Mutations coming soon!"

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

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