"""Main FastAPI application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from optimum_cli import __version__
from optimum_cli.api.routes import health, optimize, models, registry
from optimum_cli.utils.logger import log

# Create FastAPI app
app = FastAPI(
    title="Optimum CLI Pro API",
    description="Production-grade API for optimizing HuggingFace models",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(optimize.router, prefix="/api/v1", tags=["optimization"])
app.include_router(models.router, prefix="/api/v1", tags=["models"])
app.include_router(registry.router, prefix="/api/v1", tags=["registry"])

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    log.info("Starting Optimum CLI Pro API server")
    log.info(f"Version: {__version__}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    log.info("Shutting down Optimum CLI Pro API server")


@app.get("/")
async def root():
    """Root endpoint - serve the frontend."""
    static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        return FileResponse(str(static_path))
    return {
        "name": "Optimum CLI Pro API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
