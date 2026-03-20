"""Tracking utilities for optimization runs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from optimum_cli.core.config import get_settings


def get_tracking_log_path() -> Path:
    """Get the local tracking JSONL file path."""
    settings = get_settings()
    log_path = Path(settings.logging.file_path).parent / "optimization_runs.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return log_path


def record_local_tracking_event(event: Dict[str, Any]) -> Path:
    """Append a tracking event to the local JSONL file."""
    log_path = get_tracking_log_path()
    payload = {
        "timestamp": datetime.now().isoformat(),
        **event,
    }

    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload) + "\n")

    return log_path


def read_local_tracking_events(
    limit: int = 50,
    model_id: Optional[str] = None,
    success: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Read optimization tracking events from local JSONL log."""
    log_path = get_tracking_log_path()
    if not log_path.exists():
        return []

    items: List[Dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            if model_id and payload.get("model_id") != model_id:
                continue
            if success is not None and payload.get("success") is not success:
                continue

            items.append(payload)

    items.sort(key=lambda entry: entry.get("timestamp", ""), reverse=True)
    return items[: max(1, limit)]


def record_local_tracking(
    result: Dict[str, Any],
    requested_backend: str,
    quantization: bool,
    requested_task: str | None,
) -> Path:
    """Backward-compatible wrapper for recording successful optimization metadata."""
    payload = {
        "success": True,
        "model_id": result.get("model_id"),
        "requested_backend": requested_backend,
        "resolved_backend": result.get("backend"),
        "task": result.get("task") or requested_task,
        "quantization": quantization,
        "optimization_time_seconds": result.get("optimization_time_seconds"),
        "output_path": result.get("output_path"),
        "source": "optimizer",
    }
    return record_local_tracking_event(payload)


def track_with_mlflow(result: Dict[str, Any], quantization: bool) -> Tuple[bool, str]:
    """Track optimization run in MLflow if available."""
    settings = get_settings()

    try:
        import mlflow
    except Exception:
        return False, "MLflow package not installed"

    try:
        mlflow.set_tracking_uri(settings.mlops.mlflow.tracking_uri)
        mlflow.set_experiment(settings.mlops.mlflow.experiment_name)

        run_name = f"{result.get('model_id', 'unknown')}:{result.get('backend', 'unknown')}"
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params(
                {
                    "model_id": result.get("model_id"),
                    "backend": result.get("backend"),
                    "task": result.get("task"),
                    "quantization": quantization,
                    "output_path": result.get("output_path"),
                }
            )
            optimization_time = result.get("optimization_time_seconds")
            if optimization_time is not None:
                mlflow.log_metric("optimization_time_seconds", float(optimization_time))

        return True, "Tracked run to MLflow"
    except Exception as error:
        return False, f"MLflow tracking failed: {error}"


def track_with_wandb(result: Dict[str, Any], quantization: bool) -> Tuple[bool, str]:
    """Track optimization run in Weights & Biases if available."""
    settings = get_settings()

    try:
        import wandb
    except Exception:
        return False, "wandb package not installed"

    try:
        run = wandb.init(
            project=settings.mlops.wandb.project,
            entity=settings.mlops.wandb.entity,
            config={
                "model_id": result.get("model_id"),
                "backend": result.get("backend"),
                "task": result.get("task"),
                "quantization": quantization,
                "output_path": result.get("output_path"),
            },
            reinit=True,
        )

        optimization_time = result.get("optimization_time_seconds")
        if optimization_time is not None:
            wandb.log({"optimization_time_seconds": float(optimization_time)})

        if run is not None:
            run.finish()

        return True, "Tracked run to Weights & Biases"
    except Exception as error:
        return False, f"Weights & Biases tracking failed: {error}"


def track_optimization_event(
    *,
    model_id: str,
    requested_backend: str,
    quantization: bool,
    requested_task: str | None,
    success: bool,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    track_mlflow: Optional[bool] = None,
    track_wandb: Optional[bool] = None,
    source: str = "optimizer",
) -> Dict[str, Any]:
    """Centralized tracking for optimization events across CLI/API/core."""
    settings = get_settings()
    result = result or {}

    mlflow_enabled = bool(track_mlflow) if track_mlflow is not None else bool(settings.mlops.mlflow.enabled)
    wandb_enabled = bool(track_wandb) if track_wandb is not None else bool(settings.mlops.wandb.enabled)

    mlflow_status = "skipped"
    wandb_status = "skipped"

    if success and mlflow_enabled:
        mlflow_ok, mlflow_msg = track_with_mlflow(result, quantization=quantization)
        mlflow_status = "ok" if mlflow_ok else f"error: {mlflow_msg}"
    elif not success and mlflow_enabled:
        mlflow_status = "skipped: failed optimization"

    if success and wandb_enabled:
        wandb_ok, wandb_msg = track_with_wandb(result, quantization=quantization)
        wandb_status = "ok" if wandb_ok else f"error: {wandb_msg}"
    elif not success and wandb_enabled:
        wandb_status = "skipped: failed optimization"

    event = {
        "success": success,
        "model_id": model_id,
        "requested_backend": requested_backend,
        "resolved_backend": result.get("backend"),
        "task": result.get("task") or requested_task,
        "quantization": quantization,
        "optimization_time_seconds": result.get("optimization_time_seconds"),
        "output_path": result.get("output_path"),
        "error": error,
        "mlflow_status": mlflow_status,
        "wandb_status": wandb_status,
        "source": source,
    }

    log_path = record_local_tracking_event(event)
    return {
        "local_log_path": str(log_path),
        "mlflow_status": mlflow_status,
        "wandb_status": wandb_status,
    }
