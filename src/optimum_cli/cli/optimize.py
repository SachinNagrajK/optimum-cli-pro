"""Optimize command implementation."""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from optimum_cli.core.optimizer import get_optimizer
from optimum_cli.utils.logger import log

optimize_app = typer.Typer(help="Model optimization commands")
console = Console()


@optimize_app.command(name="model")
def optimize_model(
    model_id: str = typer.Argument(..., help="HuggingFace model ID or local path"),
    backend: str = typer.Option(
        "auto",
        "--backend", "-b",
        help="Backend to use: auto, onnx, openvino, bettertransformer"
    ),
    output: str = typer.Option(
        "./optimized_models",
        "--output", "-o",
        help="Output directory for optimized model"
    ),
    task: Optional[str] = typer.Option(
        None,
        "--task", "-t",
        help="Task type (auto-detected if not specified)"
    ),
    batch_size: Optional[int] = typer.Option(
        None,
        "--batch-size",
        help="Batch size for optimization"
    ),
    sequence_length: Optional[int] = typer.Option(
        None,
        "--sequence-length",
        help="Sequence length for optimization"
    ),
    quantization: bool = typer.Option(
        True,
        "--quantization/--no-quantization",
        help="Enable or disable quantization"
    ),
    track_mlflow: bool = typer.Option(
        False,
        "--track-mlflow",
        help="Track optimization with MLflow"
    ),
    track_wandb: bool = typer.Option(
        False,
        "--track-wandb",
        help="Track optimization with Weights & Biases"
    ),
):
    """
    Optimize a HuggingFace model.
    
    Examples:
        optimum-cli optimize model bert-base-uncased --backend onnx
        optimum-cli optimize model distilbert-base-uncased --backend auto
        optimum-cli optimize model roberta-base --backend openvino --quantization
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
            )
            
            progress.update(task_id, completed=True)
        
        # Display results
        console.print("\n[bold green]✨ Optimization Complete![/bold green]\n")
        console.print(f"[bold]Model ID:[/bold] {result['model_id']}")
        console.print(f"[bold]Backend:[/bold] {result['backend']}")
        console.print(f"[bold]Task:[/bold] {result['task']}")
        console.print(f"[bold]Output Path:[/bold] {result['output_path']}")
        console.print(f"[bold]Time:[/bold] {result['optimization_time_seconds']}s\n")
        
        # Track with MLOps if requested
        if track_mlflow:
            console.print("[yellow]MLflow tracking not yet implemented[/yellow]")
        
        if track_wandb:
            console.print("[yellow]Weights & Biases tracking not yet implemented[/yellow]")
        
        console.print("[green]✓[/green] Done!\n")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
        log.exception("Optimization failed")
        raise typer.Exit(code=1)


@optimize_app.command(name="info")
def model_info(
    model_id: str = typer.Argument(..., help="HuggingFace model ID"),
):
    """Get information about a model without optimizing it."""
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
    """List all optimized models in the output directory."""
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
