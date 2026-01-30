"""Model registry command implementation."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from optimum_cli.core.registry import ModelRegistry

registry_app = typer.Typer(help="Model registry commands")
console = Console()


@registry_app.command(name="list")
def list_models(name: str = typer.Option(None, "--name", "-n", help="Filter by model name")):
    """List all models in the registry."""
    async def _list():
        registry = ModelRegistry()
        await registry.initialize()
        models = await registry.list_models(name)
        
        console.print("\n[bold cyan]📦 Model Registry[/bold cyan]\n")
        
        if not models:
            console.print("[yellow]No models registered yet.[/yellow]")
            console.print("[dim]Use 'optimum-pro registry push' to register a model[/dim]\n")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Version")
        table.add_column("Backend")
        table.add_column("Size (MB)", justify="right")
        table.add_column("Created")
        
        for model in models:
            table.add_row(
                model["name"],
                model["version"],
                model["backend"],
                f"{model['size_mb']:.2f}",
                model["created_at"][:19],
            )
        
        console.print(table)
        console.print(f"\n[green]✓[/green] Total: {len(models)} model(s)\n")
    
    asyncio.run(_list())


@registry_app.command(name="push")
def push_model(
    name: str = typer.Argument(..., help="Model name"),
    path: str = typer.Argument(..., help="Path to optimized model"),
    version: str = typer.Option("1.0.0", "--version", "-v", help="Model version"),
    backend: str = typer.Option(..., "--backend", "-b", help="Backend used for optimization"),
    base_model: str = typer.Option(None, "--base-model", help="Original base model name"),
    task: str = typer.Option(None, "--task", help="Model task"),
):
    """Push a model to the registry."""
    async def _push():
        model_path = Path(path)
        if not model_path.exists():
            console.print(f"[red]✗[/red] Model path not found: {path}")
            raise typer.Exit(1)
        
        console.print(f"\n[bold cyan]📤 Registering model[/bold cyan]\n")
        console.print(f"Name: [cyan]{name}[/cyan]")
        console.print(f"Version: [yellow]{version}[/yellow]")
        console.print(f"Backend: [green]{backend}[/green]")
        console.print(f"Path: {path}\n")
        
        with console.status("[bold green]Copying model to registry..."):
            registry = ModelRegistry()
            await registry.initialize()
            model_id = await registry.register_model(
                name=name,
                version=version,
                backend=backend,
                model_path=model_path,
                base_model=base_model,
                task=task,
            )
        
        console.print(f"\n[green]✓[/green] Model registered successfully!")
        console.print(f"[dim]Model ID: {model_id}[/dim]\n")
    
    asyncio.run(_push())


@registry_app.command(name="pull")
def pull_model(
    name: str = typer.Argument(..., help="Model name"),
    version: str = typer.Option("latest", "--version", "-v", help="Model version"),
    output: str = typer.Option("./", "--output", "-o", help="Output directory"),
):
    """Pull a model from the registry."""
    console.print(f"\n[bold cyan]📥 Pulling model from registry[/bold cyan]\n")
    console.print(f"Name: {name}")
    console.print(f"Version: {version}")
    console.print(f"Output: {output}\n")
    console.print("[yellow]Registry pull feature coming soon![/yellow]\n")


@registry_app.command(name="delete")
def delete_model(
    name: str = typer.Argument(..., help="Model name"),
    version: str = typer.Option(None, "--version", "-v", help="Model version (deletes all if not specified)"),
):
    """Delete a model from the registry."""
    console.print(f"\n[bold cyan]🗑️  Deleting model from registry[/bold cyan]\n")
    console.print(f"Name: {name}")
    if version:
        console.print(f"Version: {version}")
    else:
        console.print("Version: [red]ALL VERSIONS[/red]")
    console.print("\n[yellow]Registry delete feature coming soon![/yellow]\n")


@registry_app.command(name="info")
def model_info_registry(
    name: str = typer.Argument(..., help="Model name"),
    version: str = typer.Option("latest", "--version", "-v", help="Model version"),
):
    """Show detailed information about a registered model."""
    async def _info():
        registry = ModelRegistry()
        await registry.initialize()
        model = await registry.get_model(name, version)
        
        if not model:
            console.print(f"[red]✗[/red] Model not found: {name}:{version}")
            raise typer.Exit(1)
        
        console.print(f"\n[bold cyan]ℹ️  Model Information[/bold cyan]\n")
        console.print(f"[cyan]Name:[/cyan] {model['name']}")
        console.print(f"[yellow]Version:[/yellow] {model['version']}")
        console.print(f"[green]Backend:[/green] {model['backend']}")
        console.print(f"[blue]Task:[/blue] {model['task'] or 'N/A'}")
        console.print(f"[magenta]Base Model:[/magenta] {model['base_model'] or 'N/A'}")
        console.print(f"[white]Size:[/white] {model['size_mb']:.2f} MB")
        console.print(f"[white]Path:[/white] {model['model_path']}")
        console.print(f"[dim]Created:[/dim] {model['created_at']}")
        console.print()
    
    asyncio.run(_info())


@registry_app.command(name="ab-test")
def create_ab_test(
    name: str = typer.Argument(..., help="Test name"),
    model_a: str = typer.Argument(..., help="Model A (format: name:version or name)"),
    model_b: str = typer.Argument(..., help="Model B (format: name:version or name)"),
):
    """Create an A/B test between two models."""
    async def _create_test():
        # Parse model names
        ma_parts = model_a.split(":")
        ma_name = ma_parts[0]
        ma_version = ma_parts[1] if len(ma_parts) > 1 else "latest"
        
        mb_parts = model_b.split(":")
        mb_name = mb_parts[0]
        mb_version = mb_parts[1] if len(mb_parts) > 1 else "latest"
        
        registry = ModelRegistry()
        await registry.initialize()
        
        # Get models
        model_a_data = await registry.get_model(ma_name, ma_version)
        model_b_data = await registry.get_model(mb_name, mb_version)
        
        if not model_a_data:
            console.print(f"[red]✗[/red] Model A not found: {model_a}")
            raise typer.Exit(1)
        if not model_b_data:
            console.print(f"[red]✗[/red] Model B not found: {model_b}")
            raise typer.Exit(1)
        
        console.print(f"\n[bold cyan]🔬 Creating A/B Test[/bold cyan]\n")
        console.print(f"Test Name: [cyan]{name}[/cyan]")
        console.print(f"Model A: [yellow]{model_a_data['name']}:{model_a_data['version']}[/yellow] ({model_a_data['backend']})")
        console.print(f"Model B: [yellow]{model_b_data['name']}:{model_b_data['version']}[/yellow] ({model_b_data['backend']})")
        
        test_id = await registry.create_ab_test(name, model_a_data["id"], model_b_data["id"])
        
        console.print(f"\n[green]✓[/green] A/B test created successfully!")
        console.print(f"[dim]Test ID: {test_id}[/dim]")
        console.print(f"\n[dim]Run: optimum-pro registry ab-compare {name}[/dim]\n")
    
    asyncio.run(_create_test())


@registry_app.command(name="ab-compare")
def compare_ab_test(
    name: str = typer.Argument(..., help="Test name"),
    input_text: str = typer.Option(
        "The capital of France is [MASK].", "--input", "-i", help="Input text for comparison"
    ),
):
    """Compare models in an A/B test."""
    async def _compare():
        registry = ModelRegistry()
        await registry.initialize()
        
        test = await registry.get_ab_test(name)
        if not test:
            console.print(f"[red]✗[/red] A/B test not found: {name}")
            raise typer.Exit(1)
        
        console.print(f"\n[bold cyan]🔬 A/B Test Comparison: {name}[/bold cyan]\n")
        
        # Get models
        model_a = await registry.get_model(test["model_a_name"], test["model_a_version"])
        model_b = await registry.get_model(test["model_b_name"], test["model_b_version"])
        
        table = Table(show_header=True, header_style="bold magenta", title="Model Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column(f"Model A\n{test['model_a_name']}:{test['model_a_version']}\n({model_a['backend']})", justify="right")
        table.add_column(f"Model B\n{test['model_b_name']}:{test['model_b_version']}\n({model_b['backend']})", justify="right")
        table.add_column("Winner", style="bold green")
        
        # Load and benchmark models
        import time
        from optimum.onnxruntime import ORTModelForMaskedLM
        from optimum.intel import OVModelForMaskedLM
        from transformers import AutoTokenizer
        
        console.print("[dim]Loading models...[/dim]")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            
            # Load models based on backend
            start = time.perf_counter()
            if model_a["backend"] == "onnx":
                model_a_loaded = ORTModelForMaskedLM.from_pretrained(model_a["model_path"])
            elif model_a["backend"] == "openvino":
                model_a_loaded = OVModelForMaskedLM.from_pretrained(model_a["model_path"])
            else:
                console.print(f"[red]✗[/red] Unsupported backend for Model A: {model_a['backend']}")
                raise typer.Exit(1)
            load_time_a = time.perf_counter() - start
            
            start = time.perf_counter()
            if model_b["backend"] == "onnx":
                model_b_loaded = ORTModelForMaskedLM.from_pretrained(model_b["model_path"])
            elif model_b["backend"] == "openvino":
                model_b_loaded = OVModelForMaskedLM.from_pretrained(model_b["model_path"])
            else:
                console.print(f"[red]✗[/red] Unsupported backend for Model B: {model_b['backend']}")
                raise typer.Exit(1)
            load_time_b = time.perf_counter() - start
            
            # Prepare inputs
            inputs = tokenizer(input_text, return_tensors="pt")
            
            # Warm-up runs
            console.print("[dim]Warming up models...[/dim]")
            for _ in range(3):
                _ = model_a_loaded(**inputs)
                _ = model_b_loaded(**inputs)
            
            # Inference speed (average of 10 runs)
            console.print("[dim]Running benchmarks...[/dim]")
            times_a = []
            times_b = []
            for _ in range(10):
                start = time.perf_counter()
                _ = model_a_loaded(**inputs)
                times_a.append(time.perf_counter() - start)
                
                start = time.perf_counter()
                _ = model_b_loaded(**inputs)
                times_b.append(time.perf_counter() - start)
            
            inference_a = sum(times_a) / len(times_a)
            inference_b = sum(times_b) / len(times_b)
            
            # Add metrics to table
            table.add_row(
                "Load Time (s)",
                f"{load_time_a:.3f}",
                f"{load_time_b:.3f}",
                "[green]A[/green]" if load_time_a < load_time_b else "[yellow]B[/yellow]",
            )
            table.add_row(
                "Avg Inference (s)",
                f"{inference_a:.4f}",
                f"{inference_b:.4f}",
                "[green]A[/green]" if inference_a < inference_b else "[yellow]B[/yellow]",
            )
            table.add_row(
                "Throughput (req/s)",
                f"{1/inference_a:.2f}",
                f"{1/inference_b:.2f}",
                "[green]A[/green]" if inference_a < inference_b else "[yellow]B[/yellow]",
            )
            table.add_row(
                "Model Size (MB)",
                f"{model_a['size_mb']:.2f}",
                f"{model_b['size_mb']:.2f}",
                "[green]A[/green]" if model_a["size_mb"] < model_b["size_mb"] else "[yellow]B[/yellow]",
            )
            
            console.print()
            console.print(table)
            console.print()
            
            # Calculate speedup
            speedup = inference_b / inference_a if inference_a < inference_b else inference_a / inference_b
            winner = "Model A" if inference_a < inference_b else "Model B"
            console.print(f"[bold green]Winner:[/bold green] {winner}")
            console.print(f"[bold]Speedup:[/bold] {speedup:.2f}x faster\n")
            
            # Record results
            await registry.record_ab_result(test["id"], model_a["id"], "load_time", load_time_a)
            await registry.record_ab_result(test["id"], model_b["id"], "load_time", load_time_b)
            await registry.record_ab_result(test["id"], model_a["id"], "inference_time", inference_a)
            await registry.record_ab_result(test["id"], model_b["id"], "inference_time", inference_b)
            
            console.print("[green]✓[/green] Results recorded to registry\n")
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error during comparison: {e}\n")
            import traceback
            traceback.print_exc()
            raise typer.Exit(1)
    
    asyncio.run(_compare())


@registry_app.command(name="ab-list")
def list_ab_tests():
    """List all A/B tests."""
    async def _list():
        registry = ModelRegistry()
        await registry.initialize()
        tests = await registry.list_ab_tests()
        
        console.print("\n[bold cyan]🔬 A/B Tests[/bold cyan]\n")
        
        if not tests:
            console.print("[yellow]No A/B tests found.[/yellow]")
            console.print("[dim]Use 'optimum-pro registry ab-test' to create one[/dim]\n")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Model A")
        table.add_column("Model B")
        table.add_column("Status")
        table.add_column("Created")
        
        for test in tests:
            table.add_row(
                test["name"],
                f"{test['model_a_name']}:{test['model_a_version']}",
                f"{test['model_b_name']}:{test['model_b_version']}",
                test["status"],
                test["created_at"][:19],
            )
        
        console.print(table)
        console.print(f"\n[green]✓[/green] Total: {len(tests)} test(s)\n")
    
    asyncio.run(_list())
