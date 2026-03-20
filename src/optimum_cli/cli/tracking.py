"""Tracking command implementation."""

import typer
from rich.console import Console
from rich.table import Table

from optimum_cli.utils.tracking import get_tracking_log_path, read_local_tracking_events

tracking_app = typer.Typer(help="Tracking and run history commands")
console = Console()


@tracking_app.command(name="list")
def list_tracking_runs(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of most recent runs to show"),
    model_id: str = typer.Option(None, "--model-id", help="Filter by model ID"),
    success: str = typer.Option(
        "all",
        "--success",
        help="Filter by status: all, true, false",
    ),
):
    """List tracked optimization runs."""
    success_filter = None
    normalized = success.lower().strip()
    if normalized == "true":
        success_filter = True
    elif normalized == "false":
        success_filter = False

    events = read_local_tracking_events(limit=limit, model_id=model_id, success=success_filter)
    log_path = get_tracking_log_path()

    console.print("\n[bold cyan]📈 Optimization Tracking History[/bold cyan]")
    console.print(f"[dim]Log file: {log_path}[/dim]\n")

    if not events:
        console.print("[yellow]No tracking events found.[/yellow]\n")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Timestamp", style="cyan")
    table.add_column("Model")
    table.add_column("Status")
    table.add_column("Backend")
    table.add_column("Time (s)", justify="right")
    table.add_column("MLflow")
    table.add_column("W&B")

    for event in events:
        ok = event.get("success")
        status = "✅ success" if ok else "❌ failed"
        resolved_backend = event.get("resolved_backend") or "-"
        optimization_time = event.get("optimization_time_seconds")
        time_text = f"{optimization_time}" if optimization_time is not None else "-"

        table.add_row(
            str(event.get("timestamp", "-"))[:19],
            str(event.get("model_id", "-")),
            status,
            str(resolved_backend),
            time_text,
            str(event.get("mlflow_status", "-")),
            str(event.get("wandb_status", "-")),
        )

    console.print(table)
    console.print()


@tracking_app.command(name="path")
def show_tracking_path():
    """Show local tracking log path."""
    console.print(f"\n[bold]Tracking log file:[/bold] {get_tracking_log_path()}\n")
