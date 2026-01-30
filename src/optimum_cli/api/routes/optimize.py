"""Optimization routes."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from optimum_cli.api.schemas import OptimizeRequest, OptimizeResponse, ErrorResponse
from optimum_cli.core.optimizer import get_optimizer
from optimum_cli.utils.logger import log

router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_model(request: OptimizeRequest):
    """
    Optimize a HuggingFace model.
    
    This endpoint optimizes a model using the specified backend.
    The operation may take several minutes depending on model size.
    """
    try:
        log.info(f"API request: Optimize {request.model_id} with {request.backend}")
        
        optimizer = get_optimizer()
        
        result = optimizer.optimize(
            model_id=request.model_id,
            backend=request.backend,
            output_dir=request.output_dir,
            task=request.task,
            batch_size=request.batch_size,
            sequence_length=request.sequence_length,
            quantization=request.quantization,
        )
        
        return OptimizeResponse(
            success=result["success"],
            model_id=result["model_id"],
            backend=result["backend"],
            output_path=result["output_path"],
            task=result["task"],
            optimization_time_seconds=result["optimization_time_seconds"],
            message="Model optimization completed successfully"
        )
        
    except Exception as e:
        log.error(f"Optimization failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/optimize/async")
async def optimize_model_async(
    request: OptimizeRequest,
    background_tasks: BackgroundTasks
):
    """
    Optimize a model asynchronously.
    
    This endpoint starts optimization in the background and returns immediately.
    Use the returned task_id to check status.
    """
    import uuid
    
    task_id = str(uuid.uuid4())
    
    def run_optimization():
        try:
            optimizer = get_optimizer()
            optimizer.optimize(
                model_id=request.model_id,
                backend=request.backend,
                output_dir=request.output_dir,
                task=request.task,
                batch_size=request.batch_size,
                sequence_length=request.sequence_length,
                quantization=request.quantization,
            )
        except Exception as e:
            log.error(f"Async optimization failed: {e}")
    
    background_tasks.add_task(run_optimization)
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Optimization started in background"
    }
