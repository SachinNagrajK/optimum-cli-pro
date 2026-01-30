"""Health check routes."""

from fastapi import APIRouter
from optimum_cli import __version__
from optimum_cli.api.schemas import HealthResponse
from optimum_cli.core.backend_manager import get_backend_manager

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    backend_manager = get_backend_manager()
    backends = backend_manager.list_backends()
    
    return {
        "status": "healthy",
        "version": __version__,
        "backends_available": backends,
    }


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with hardware info."""
    from optimum_cli.utils.hardware import get_hardware_detector
    from optimum_cli.core.backend_manager import get_backend_manager
    
    detector = get_hardware_detector()
    hardware = detector.detect_all()
    
    backend_manager = get_backend_manager()
    backends = {}
    for name in backend_manager.list_backends():
        try:
            info = backend_manager.get_backend_info(name)
            backends[name] = {
                "available": info["available"],
                "requirements": info["requirements"],
            }
        except Exception as e:
            backends[name] = {"available": False, "error": str(e)}
    
    return {
        "status": "healthy",
        "version": __version__,
        "hardware": hardware,
        "backends": backends,
    }
