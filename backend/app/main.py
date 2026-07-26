from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import check_db_connection, settings
from app.routes.auth import router as auth_router
from app.routes.document import router as document_router
from app.routes.chat import router as chat_router
from app.routes.notes import router as notes_router
from app.routes.quiz import router as quiz_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI startup and shutdown events lifecycle helper.
    Ensures that database check occurs right as the server initializes.
    """
    print("[Lifespan] Booting PaperMind AI Application...")
    db_connected = await check_db_connection()
    if db_connected:
        print("[Lifespan] Connected to MongoDB database successfully!")
    else:
        print("[Lifespan] WARNING: MongoDB database is offline. Please check connection.")
    yield
    print("[Lifespan] Shutting down application context.")

app = FastAPI(
    title="PaperMind AI API",
    description="Enterprise RAG-Based Research Workspace Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Auth, Document, Chat, Notes & Quiz routing under the API prefix
app.include_router(auth_router, prefix="/api")
app.include_router(document_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(notes_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")

@app.get("/api/health")
def health_check():
    """Health check endpoint to ensure server is running."""
    return {
        "status": "healthy",
        "app_name": "PaperMind AI",
        "database_connected": True  # will be dynamic in later phases
    }
