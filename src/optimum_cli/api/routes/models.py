"""Model management routes."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List

from optimum_cli.api.schemas import ModelInfo
from optimum_cli.core.optimizer import get_optimizer

router = APIRouter()


@router.get("/models/info/{model_id:path}", response_model=ModelInfo)
async def get_model_info(model_id: str):
    """
    Get information about a HuggingFace model.
    
    Returns model metadata including architecture, task type, and parameters.
    """
    try:
        optimizer = get_optimizer()
        info = optimizer.get_model_info(model_id)
        
        return ModelInfo(**info)
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to get model info: {str(e)}"
        )


@router.get("/models/optimized")
async def list_optimized_models():
    """
    List all optimized models in the output directory.
    
    Returns a list of available optimized models with metadata.
    """
    output_dir = Path("./optimized_models")
    
    if not output_dir.exists():
        return {"models": []}
    
    models = []
    for model_path in output_dir.iterdir():
        if model_path.is_dir():
            size = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
            size_mb = size / (1024 * 1024)
            
            models.append({
                "name": model_path.name,
                "path": str(model_path),
                "size_mb": round(size_mb, 2),
            })
    
    return {"models": models}


@router.get("/backends")
async def list_backends():
    """
    List all available optimization backends.
    
    Returns information about each backend including availability and requirements.
    """
    from optimum_cli.core.backend_manager import get_backend_manager
    
    backend_manager = get_backend_manager()
    backends = []
    
    for name in backend_manager.list_backends():
        try:
            info = backend_manager.get_backend_info(name)
            backends.append({
                "name": name,
                "available": info["available"],
                "requirements": info["requirements"],
            })
        except Exception as e:
            backends.append({
                "name": name,
                "available": False,
                "error": str(e),
            })
    
    return {"backends": backends}
