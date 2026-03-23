"""Main CLI application using Typer."""

import typer
from rich.console import Console
from rich.table import Table

from optimum_cli import __version__
from optimum_cli.cli.optimize import optimize_app
from optimum_cli.cli.benchmark import benchmark_app
from optimum_cli.cli.registry import registry_app
from optimum_cli.cli.serve import serve_app
from optimum_cli.cli.tracking import tracking_app

# Create main app
app = typer.Typer(
    name="optimum-pro",
    help=(
        "🚀 Production-grade CLI for optimizing, benchmarking, serving, and tracking Hugging Face models.\n\n"
        "Command Groups\n"
        "  optimize   Optimize models, inspect model metadata, and list optimized artifacts\n"
        "  benchmark  Benchmark optimized artifacts and compare optimized vs baseline models\n"
        "  registry   Register, pull, inspect, delete, and A/B test optimized models\n"
        "  serve      Start the FastAPI server for model serving and web UI\n"
        "  tracking   View local optimization run history and tracking log location\n\n"
        "Top-Level Commands\n"
        "  version        Show installed CLI version\n"
        "  info           Show system hardware and backend readiness\n"
        "  list-backends  Show backend availability and requirements\n\n"
        "Quick Examples\n"
        "  optimum-pro optimize model bert-base-uncased --backend onnx --quantization\n"
        "  optimum-pro benchmark model bert-base-uncased --backends onnx,openvino --runs 100\n"
        "  optimum-pro registry push bert-opt-v1 ./optimized_models/bert-base-uncased --backend onnx\n"
        "  optimum-pro registry ab-compare backend-comparison --runs 50 --device auto\n"
        "  optimum-pro serve start --host 0.0.0.0 --port 8000 --workers 2\n"
        "  optimum-pro tracking list --limit 50 --success true"
    ),
    add_completion=True,
    rich_markup_mode="rich",
)

# Create console for rich output
console = Console()

# Add sub-commands
app.add_typer(optimize_app, name="optimize", help="Optimize models and inspect optimization artifacts")
app.add_typer(benchmark_app, name="benchmark", help="Benchmark optimized models and compare variants")
app.add_typer(registry_app, name="registry", help="Register, fetch, inspect, and compare stored models")
app.add_typer(serve_app, name="serve", help="Run the FastAPI serving API and web UI")
app.add_typer(tracking_app, name="tracking", help="Inspect local optimization tracking history")


@app.command()
def version():
    """Show installed CLI version.

    Example:
        optimum-pro version
    """
    console.print(f"[bold green]Optimum CLI Pro[/bold green] version [bold]{__version__}[/bold]")


@app.command()
def info():
    """Show system hardware details and backend recommendations.

    Includes CPU, memory, GPU detection, backend availability, and recommended
    backend for your current environment.

    Example:
        optimum-pro info
    """
    from optimum_cli.utils.hardware import get_hardware_detector
    from optimum_cli.core.backend_manager import get_backend_manager
    
    console.print("\n[bold cyan]🖥️  System Information[/bold cyan]\n")
    
    # Hardware info
    detector = get_hardware_detector()
    hw_info = detector.detect_all()
    
    # CPU info
    cpu = hw_info["cpu"]
    console.print(f"[bold]CPU:[/bold] {cpu.get('brand', 'Unknown')}")
    console.print(f"  Vendor: {cpu.get('vendor', 'unknown')}")
    console.print(f"  Cores: {cpu.get('cores_physical')} physical, {cpu.get('cores_logical')} logical")
    
    # Memory info
    mem = hw_info["memory"]
    console.print(f"\n[bold]Memory:[/bold] {mem.get('total_gb')}GB total, {mem.get('available_gb')}GB available")
    
    # GPU info
    gpu = hw_info["gpu"]
    if gpu.get("available"):
        console.print(f"\n[bold]GPU:[/bold] {gpu.get('backend', 'N/A')}")
        for device in gpu.get("devices", []):
            console.print(f"  {device['id']}: {device['name']} ({device['memory_gb']}GB)")
    else:
        console.print("\n[bold]GPU:[/bold] Not available")
    
    # Platform info
    platform = hw_info["platform"]
    console.print(f"\n[bold]Platform:[/bold] {platform['system']} {platform['release']}")
    console.print(f"[bold]Python:[/bold] {platform['python_version']}")
    
    # Backend info
    console.print("\n[bold cyan]🔧 Available Backends[/bold cyan]\n")
    
    backend_manager = get_backend_manager()
    backends_table = Table(show_header=True, header_style="bold magenta")
    backends_table.add_column("Backend", style="cyan")
    backends_table.add_column("Status", style="green")
    backends_table.add_column("Requirements")
    
    for backend_name in backend_manager.list_backends():
        try:
            backend_info = backend_manager.get_backend_info(backend_name)
            status = "✅ Available" if backend_info["available"] else "❌ Missing dependencies"
            reqs = ", ".join(backend_info["requirements"][:2]) + "..."
            backends_table.add_row(backend_name, status, reqs)
        except Exception:
            backends_table.add_row(backend_name, "❌ Error", "N/A")
    
    console.print(backends_table)
    
    # Recommended backend with availability check
    console.print("\n[bold cyan]💡 Recommendations[/bold cyan]\n")
    
    # Get ideal backend based on hardware
    ideal = detector.recommend_backend(check_availability=False)
    recommended = detector.recommend_backend(check_availability=True)
    
    if ideal == recommended:
        console.print(f"[bold]Best backend for your hardware:[/bold] [green]{recommended}[/green] ✅")
    else:
        console.print(f"[bold]Best backend for your hardware:[/bold] [yellow]{ideal}[/yellow] ⚠️  (not installed)")
        console.print(f"[bold]Available fallback:[/bold] [green]{recommended}[/green]")
        console.print(f"\n[dim]💡 To install {ideal}: pip install optimum[{ideal}][/dim]")
    
    console.print()


@app.command()
def list_backends():
    """List optimization backends with readiness status and requirements.

    Example:
        optimum-pro list-backends
    """
    from optimum_cli.core.backend_manager import get_backend_manager
    
    console.print("\n[bold cyan]Available Backends:[/bold cyan]\n")
    
    backend_manager = get_backend_manager()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Backend", style="cyan", width=20)
    table.add_column("Status", style="green", width=15)
    table.add_column("Description", width=50)
    
    for name in backend_manager.list_backends():
        try:
            info = backend_manager.get_backend_info(name)
            status = "✅ Ready" if info["available"] else "❌ Not Ready"
            description = f"Requirements: {', '.join(info['requirements'][:2])}"
            table.add_row(name, status, description)
        except Exception as e:
            table.add_row(name, "❌ Error", str(e))
    
    console.print(table)
    console.print()


if __name__ == "__main__":
    app()
