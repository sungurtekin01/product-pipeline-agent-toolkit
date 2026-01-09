"""
Product Pipeline Toolkit API

FastAPI backend for executing the product pipeline (PRD → Design → Tickets)
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import pipeline, health, documents

app = FastAPI(
    title="Product Pipeline Toolkit API",
    description="API for executing AI-powered product development pipeline",
    version="1.0.0"
)

# Configure CORS - allow configurable origins for production
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(documents.router, prefix="/api", tags=["documents"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Product Pipeline Toolkit API",
        "docs": "/docs",
        "version": "1.0.0"
    }
