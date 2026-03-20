"""Tracking routes."""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from optimum_cli.utils.tracking import get_tracking_log_path, read_local_tracking_events

router = APIRouter()


class TrackingEventResponse(BaseModel):
    """Tracking event response."""

    timestamp: str
    success: bool
    model_id: Optional[str] = None
    requested_backend: Optional[str] = None
    resolved_backend: Optional[str] = None
    task: Optional[str] = None
    quantization: Optional[bool] = None
    optimization_time_seconds: Optional[float] = None
    output_path: Optional[str] = None
    error: Optional[str] = None
    mlflow_status: Optional[str] = None
    wandb_status: Optional[str] = None
    source: Optional[str] = None


@router.get("/tracking/path")
async def get_tracking_path():
    """Get the local tracking log path."""
    return {"path": str(get_tracking_log_path())}


@router.get("/tracking/runs", response_model=List[TrackingEventResponse])
async def list_tracking_runs(
    limit: int = 50,
    model_id: Optional[str] = None,
    success: Optional[bool] = None,
):
    """List tracked optimization events."""
    return read_local_tracking_events(limit=limit, model_id=model_id, success=success)
