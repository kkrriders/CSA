from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, documents, questions, tests, analytics

settings = get_settings()

app = FastAPI(
    title="Adaptive Learning Platform API",
    description="AI-powered adaptive learning system with exam integrity",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await connect_to_mongo()
    print("🚀 Adaptive Learning Platform API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_mongo_connection()
    print("👋 Adaptive Learning Platform API shutdown")


@app.get("/")
async def root():
    return {
        "message": "Adaptive Learning Platform API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(tests.router, prefix="/api/tests", tags=["Tests"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
