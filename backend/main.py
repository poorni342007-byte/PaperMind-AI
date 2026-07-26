from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import check_db_connection
from routers import auth_routes, pdf_routes, chat_routes, history_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect and verify MongoDB on startup
    connected = await check_db_connection()
    if connected:
        print("-------------------------------------------------")
        print("[Startup] Successfully connected to MongoDB!      ")
        print("-------------------------------------------------")
    else:
        print("-------------------------------------------------")
        print("[Startup] WARNING: Could not connect to MongoDB. ")
        print("Please check if your local database is running.  ")
        print("-------------------------------------------------")
    yield

app = FastAPI(
    title="PaperPal AI API",
    description="FastAPI backend for PaperPal AI - RAG Based Research Paper Simplifier",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configurations for frontend communication
# Vite React app defaults to port 5173, fallback to 3000
import os

frontend_url = os.getenv(
    "FRONTEND_URL",
    "https://papermind-ai-f2ed.onrender.com"
)

origins = [
    frontend_url,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router, prefix="/api")
app.include_router(pdf_routes.router, prefix="/api")
app.include_router(chat_routes.router, prefix="/api")
app.include_router(history_routes.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "PaperPal AI backend is running"}
