"""Serve command implementation."""

import typer
from rich.console import Console

serve_app = typer.Typer(
    help=(
        "Run the FastAPI serving API and web UI for optimized models.\n\n"
        "Subcommands\n"
        "  start  Start the API server"
    )
)
console = Console()


@serve_app.command()
def start(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of workers"),
):
    """Start the FastAPI server for API + web interface.

    Variations:
      - Default host/port:
          optimum-pro serve start
      - Development mode with reload:
          optimum-pro serve start --port 8080 --reload
      - Bind explicit host and worker count:
          optimum-pro serve start --host 0.0.0.0 --port 8000 --workers 4

    Notes:
      - When --reload is enabled, workers are forced to 1 by design.
      - API docs are available at /docs when server is running.
    """
    console.print("\n[bold cyan]🚀 Starting API server[/bold cyan]\n")
    console.print(f"Host: {host}")
    console.print(f"Port: {port}")
    console.print(f"Workers: {workers}")
    console.print(f"Reload: {reload}\n")
    
    try:
        import uvicorn
        
        console.print("[green]Server starting...[/green]")
        console.print(f"[dim]API docs available at: http://{host}:{port}/docs[/dim]\n")
        
        uvicorn.run(
            "optimum_cli.api.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
        )
        
    except ImportError:
        console.print("[bold red]Error:[/bold red] FastAPI not installed")
        console.print("Install with: pip install fastapi uvicorn\n")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"\n[bold red]Error starting server:[/bold red] {e}\n")
        raise typer.Exit(code=1)
