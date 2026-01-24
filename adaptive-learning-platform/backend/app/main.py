from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.cache import cache_manager
from app.routes import auth, documents, questions, tests, analytics, reviews, notifications, comparisons, study_plans, security, question_management, websockets, data_export, teacher, predictions, experiments, session_recording
from app.core.monitoring import get_metrics
from app.db.indexes import create_indexes

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
    from app.core.database import get_database
    await connect_to_mongo()
    await cache_manager.connect()

    # Create database indexes
    try:
        db = get_database()
        if db is not None:
            await create_indexes(db)
    except Exception as e:
        print(f"Warning: Could not create indexes: {e}")

    print("🚀 Adaptive Learning Platform API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_mongo_connection()
    await cache_manager.disconnect()
    print("👋 Adaptive Learning Platform API shutdown")


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "message": "Adaptive Learning Platform API",
        "version": "1.0.0",
        "status": "running"
    }


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return await get_metrics()


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(tests.router, prefix="/api/tests", tags=["Tests"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(comparisons.router, prefix="/api/comparisons", tags=["Comparisons"])
app.include_router(study_plans.router, prefix="/api/study-plans", tags=["Study Plans"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(question_management.router, prefix="/api/question-management", tags=["Question Management"])
app.include_router(websockets.router, prefix="/ws", tags=["WebSockets"])
app.include_router(data_export.router, prefix="/api/data", tags=["Data Export"])
app.include_router(teacher.router, prefix="/api/teacher", tags=["Teacher Dashboard"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["ML Predictions"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["A/B Testing"])
app.include_router(session_recording.router, prefix="/api/sessions", tags=["Session Recording"])
