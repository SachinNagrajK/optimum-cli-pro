"""Optimize command implementation."""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from optimum_cli.core.optimizer import get_optimizer
from optimum_cli.utils.logger import log

optimize_app = typer.Typer(
    help=(
        "Optimize model checkpoints with different acceleration backends.\n\n"
        "Subcommands\n"
        "  model  Optimize a model and write optimized artifacts\n"
        "  info   Inspect model metadata without optimization\n"
        "  list   List local optimized artifacts from ./optimized_models"
    )
)
console = Console()


@optimize_app.command(name="model")
def optimize_model(
    model_id: str = typer.Argument(..., help="HuggingFace model ID or local path"),
    backend: str = typer.Option(
        "auto",
        "--backend", "-b",
        help="Optimization backend. Allowed values: auto, onnx, openvino"
    ),
    output: str = typer.Option(
        "./optimized_models",
        "--output", "-o",
        help="Directory where optimized model artifacts are written"
    ),
    task: Optional[str] = typer.Option(
        None,
        "--task", "-t",
        help="Task override (auto-detected when omitted), e.g. fill-mask, text-classification"
    ),
    batch_size: Optional[int] = typer.Option(
        None,
        "--batch-size",
        help="Batch size used during optimization and calibration flows"
    ),
    sequence_length: Optional[int] = typer.Option(
        None,
        "--sequence-length",
        help="Maximum sequence length used for optimization-related processing"
    ),
    device: str = typer.Option(
        "auto",
        "--device",
        help="Execution device. Allowed values: auto, cpu, gpu"
    ),
    quantization: bool = typer.Option(
        True,
        "--quantization/--no-quantization",
        help="Toggle quantization on or off"
    ),
    track_mlflow: bool = typer.Option(
        False,
        "--track-mlflow",
        help="Track optimization run in MLflow"
    ),
    track_wandb: bool = typer.Option(
        False,
        "--track-wandb",
        help="Track optimization run in Weights & Biases"
    ),
):
    """Optimize a Hugging Face model checkpoint.

    Common Variations:
      - Auto backend selection:
          optimum-pro optimize model bert-base-uncased --backend auto
      - Explicit backend + output location:
          optimum-pro optimize model bert-base-uncased --backend onnx --output ./optimized_models
      - Disable quantization:
          optimum-pro optimize model roberta-base --backend onnx --no-quantization
      - Override task and tensor settings:
          optimum-pro optimize model gpt2 --task text-generation --batch-size 4 --sequence-length 256
      - Enable experiment tracking:
          optimum-pro optimize model bert-base-uncased --track-mlflow --track-wandb
    """
    try:
        console.print(f"\n[bold cyan]🚀 Optimizing model:[/bold cyan] {model_id}")
        console.print(f"[bold]Backend:[/bold] {backend}")
        console.print(f"[bold]Output:[/bold] {output}\n")
        
        optimizer = get_optimizer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_id = progress.add_task("Optimizing model...", total=None)
            
            result = optimizer.optimize(
                model_id=model_id,
                backend=backend,
                output_dir=output,
                task=task,
                batch_size=batch_size,
                sequence_length=sequence_length,
                quantization=quantization,
                device=device,
                track_mlflow=track_mlflow,
                track_wandb=track_wandb,
                tracking_source="cli",
            )
            
            progress.update(task_id, completed=True)
        
        # Display results
        console.print("\n[bold green]✨ Optimization Complete![/bold green]\n")
        console.print(f"[bold]Model ID:[/bold] {result['model_id']}")
        console.print(f"[bold]Backend:[/bold] {result['backend']}")
        console.print(f"[bold]Task:[/bold] {result['task']}")
        console.print(f"[bold]Output Path:[/bold] {result['output_path']}")
        console.print(f"[bold]Time:[/bold] {result['optimization_time_seconds']}s\n")

        tracking_info = result.get("tracking", {})
        if tracking_info:
            console.print(f"[dim]Local tracking: {tracking_info.get('local_log_path', 'N/A')}[/dim]")
            if track_mlflow or tracking_info.get("mlflow_status") not in (None, "skipped"):
                console.print(f"[dim]MLflow: {tracking_info.get('mlflow_status', 'skipped')}[/dim]")
            if track_wandb or tracking_info.get("wandb_status") not in (None, "skipped"):
                console.print(f"[dim]W&B: {tracking_info.get('wandb_status', 'skipped')}[/dim]")
        
        console.print("[green]✓[/green] Done!\n")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
        log.exception("Optimization failed")
        raise typer.Exit(code=1)


@optimize_app.command(name="info")
def model_info(
    model_id: str = typer.Argument(..., help="HuggingFace model ID"),
):
    """Inspect model metadata without running optimization.

    Example:
        optimum-pro optimize info bert-base-uncased
    """
    try:
        console.print(f"\n[bold cyan]📋 Model Information:[/bold cyan] {model_id}\n")
        
        optimizer = get_optimizer()
        info = optimizer.get_model_info(model_id)
        
        console.print(f"[bold]Model ID:[/bold] {info['model_id']}")
        console.print(f"[bold]Task:[/bold] {info['task']}")
        console.print(f"[bold]Model Type:[/bold] {info['model_type']}")
        console.print(f"[bold]Architectures:[/bold] {', '.join(info['architectures'])}")
        
        if info.get('num_parameters'):
            params_millions = info['num_parameters'] / 1_000_000
            console.print(f"[bold]Parameters (estimated):[/bold] {params_millions:.1f}M")
        
        if info.get('hidden_size'):
            console.print(f"[bold]Hidden Size:[/bold] {info['hidden_size']}")
        
        if info.get('num_layers'):
            console.print(f"[bold]Layers:[/bold] {info['num_layers']}")
        
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
        raise typer.Exit(code=1)


@optimize_app.command(name="list")
def list_optimized():
    """List optimized model artifacts discovered under ./optimized_models.

    Example:
        optimum-pro optimize list
    """
    output_dir = Path("./optimized_models")
    
    if not output_dir.exists():
        console.print("\n[yellow]No optimized models found.[/yellow]\n")
        return
    
    console.print("\n[bold cyan]📦 Optimized Models:[/bold cyan]\n")
    
    models = list(output_dir.iterdir())
    if not models:
        console.print("[yellow]No optimized models found.[/yellow]\n")
        return
    
    for model_path in models:
        if model_path.is_dir():
            size = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
            size_mb = size / (1024 * 1024)
            console.print(f"  • {model_path.name} ({size_mb:.1f} MB)")
    
    console.print()
