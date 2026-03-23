"""Benchmark command implementation."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from optimum_cli.core.benchmarking import (
    benchmark_model_inference,
    infer_backend_from_path,
    load_hf_baseline_model,
    load_runtime_model,
)
from optimum_cli.utils.exceptions import BenchmarkError

benchmark_app = typer.Typer(
    help=(
        "Benchmark optimized artifacts and compare optimized vs baseline models.\n\n"
        "Subcommands\n"
        "  model    Benchmark one or more optimized artifacts\n"
        "  compare  Compare two models (optimized or baseline Hugging Face model IDs)"
    )
)
console = Console()


@benchmark_app.command(name="model")
def benchmark_model(
    model_id: str = typer.Argument(..., help="Model ID or path to optimized model"),
    backends: str = typer.Option(
        "all",
        "--backends", "-b",
        help="Backends to benchmark for discovered artifacts: comma-separated list or 'all'"
    ),
    runs: int = typer.Option(
        50,
        "--runs", "-r",
        help="Number of measured runs per model"
    ),
    batch_size: int = typer.Option(
        1,
        "--batch-size",
        help="Inference batch size for each benchmark run"
    ),
    device: str = typer.Option(
        "auto",
        "--device",
        help="Execution device. Allowed values: auto, cpu, gpu"
    ),
    input_text: str = typer.Option(
        "The capital of France is [MASK].",
        "--input", "-i",
        help="Input text used for each inference run"
    ),
    models_dir: str = typer.Option(
        "./optimized_models",
        "--models-dir",
        help="Root directory used to discover optimized artifact folders"
    ),
):
    """Benchmark optimized model artifacts.

    Accepted Inputs:
      - `model_id` as a direct path to an optimized artifact folder
      - `model_id` as a Hugging Face model ID/name; artifacts are searched in --models-dir

    Common Variations:
      - Benchmark all discovered backends:
          optimum-pro benchmark model bert-base-uncased --backends all
      - Benchmark selected backends only:
          optimum-pro benchmark model bert-base-uncased --backends onnx,openvino
      - Increase statistical confidence:
          optimum-pro benchmark model bert-base-uncased --runs 200
      - Use custom input and batch size:
          optimum-pro benchmark model bert-base-uncased --input "Paris is [MASK]." --batch-size 4
      - Benchmark a direct optimized path:
          optimum-pro benchmark model ./optimized_models/bert-base-uncased_onnx
    """
    try:
        model_input_path = Path(model_id)
        model_paths: List[Dict[str, str]] = []

        if model_input_path.exists():
            backend_name = infer_backend_from_path(model_input_path)
            model_paths.append({
                "backend": backend_name,
                "path": str(model_input_path),
            })
        else:
            selected_backends = ["onnx", "openvino"] if backends.lower() == "all" else [
                backend.strip().lower() for backend in backends.split(",") if backend.strip()
            ]
            normalized_model = model_id.replace("/", "_")
            root = Path(models_dir)

            direct_named_candidate = root / normalized_model
            if direct_named_candidate.exists() and direct_named_candidate.is_dir():
                try:
                    backend_name = infer_backend_from_path(direct_named_candidate)
                    if backends.lower() == "all" or backend_name in selected_backends:
                        model_paths.append({
                            "backend": backend_name,
                            "path": str(direct_named_candidate),
                        })
                except Exception:
                    pass

            if root.exists() and root.is_dir() and not model_paths:
                try:
                    backend_name = infer_backend_from_path(root)
                    if backends.lower() == "all" or backend_name in selected_backends:
                        model_paths.append({
                            "backend": backend_name,
                            "path": str(root),
                        })
                except Exception:
                    pass

            for backend_name in selected_backends:
                candidate = root / f"{normalized_model}_{backend_name}"
                if candidate.exists() and candidate.is_dir():
                    model_paths.append({
                        "backend": backend_name,
                        "path": str(candidate),
                    })

        if not model_paths:
            console.print("\n[red]✗[/red] No benchmarkable optimized model artifacts found.")
            console.print("[dim]Provide a model directory path or ensure optimized artifacts exist in --models-dir.[/dim]\n")
            raise typer.Exit(code=1)

        console.print(f"\n[bold cyan]📊 Benchmarking:[/bold cyan] {model_id}")
        console.print(f"[dim]Runs: {runs} | Batch size: {batch_size} | Input: {input_text}[/dim]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Backend", style="cyan")
        table.add_column("Path")
        table.add_column("Avg (ms)", justify="right")
        table.add_column("P95 (ms)", justify="right")
        table.add_column("P99 (ms)", justify="right")
        table.add_column("Throughput (req/s)", justify="right")

        successful = 0
        for item in model_paths:
            backend_name = item["backend"]
            model_path = Path(item["path"])
            try:
                tokenizer, runtime_model = load_runtime_model(model_path, backend_name, base_model=model_id)
                metrics = benchmark_model_inference(
                    model=runtime_model,
                    tokenizer=tokenizer,
                    input_text=input_text,
                    runs=runs,
                    batch_size=batch_size,
                    device=device,
                )
                successful += 1
                table.add_row(
                    backend_name,
                    str(model_path),
                    f"{metrics['mean_latency_s'] * 1000:.2f}",
                    f"{metrics['p95_latency_s'] * 1000:.2f}",
                    f"{metrics['p99_latency_s'] * 1000:.2f}",
                    f"{metrics['throughput_rps']:.2f}",
                )
            except Exception as error:
                table.add_row(backend_name, str(model_path), "ERR", "ERR", "ERR", str(error))

        console.print(table)
        console.print()

        if successful == 0:
            raise typer.Exit(code=1)

    except BenchmarkError as error:
        console.print(f"\n[bold red]❌ Benchmark error:[/bold red] {error}\n")
        raise typer.Exit(code=1)
    except Exception as error:
        console.print(f"\n[bold red]❌ Benchmark failed:[/bold red] {error}\n")
        raise typer.Exit(code=1)


@benchmark_app.command(name="compare")
def compare_models(
    model_a: str = typer.Argument(..., help="First model path or Hugging Face model ID"),
    model_b: Optional[str] = typer.Argument(
        None,
        help="Second model path or Hugging Face model ID (optional if model_a is optimized artifact)",
    ),
    runs: int = typer.Option(50, "--runs", "-r", help="Number of benchmark runs"),
    batch_size: int = typer.Option(1, "--batch-size", help="Batch size for benchmarking"),
    device: str = typer.Option("auto", "--device", help="Execution device: auto, cpu, gpu"),
    models_dir: str = typer.Option(
        "./optimized_models",
        "--models-dir",
        help="Directory containing optimized model artifacts when passing model names"
    ),
    input_text: str = typer.Option(
        "The capital of France is [MASK].",
        "--input", "-i",
        help="Input text for inference benchmarking"
    ),
):
    """Compare two models side-by-side.

    Accepted Model References:
      - Optimized artifact directory path
      - Optimized artifact folder name in --models-dir (e.g., bert-base-uncased_onnx)
      - Hugging Face baseline model ID (loaded with PyTorch backend)

    Common Variations:
      - Optimized vs optimized:
          optimum-pro benchmark compare ./optimized_models/bert-base-uncased_onnx ./optimized_models/bert-base-uncased_openvino
      - Optimized vs inferred baseline (omit model_b):
          optimum-pro benchmark compare ./optimized_models/bert-base-uncased_onnx
      - Baseline vs baseline:
          optimum-pro benchmark compare bert-base-uncased distilbert-base-uncased
      - Tune benchmark shape:
          optimum-pro benchmark compare bert-base-uncased distilbert-base-uncased --runs 100 --batch-size 2 --device auto
    """
    try:
        root = Path(models_dir)

        def resolve_optimized_artifact(reference: str) -> Path | None:
            direct = Path(reference)
            if direct.exists() and direct.is_dir():
                try:
                    infer_backend_from_path(direct)
                    return direct
                except BenchmarkError:
                    return None

            normalized = reference.replace("/", "_")
            backend_hinted = normalized.endswith("_onnx") or normalized.endswith("_openvino")
            if not backend_hinted:
                return None

            candidates = [root / normalized]

            for candidate in candidates:
                if candidate.exists() and candidate.is_dir():
                    try:
                        infer_backend_from_path(candidate)
                        return candidate
                    except BenchmarkError:
                        continue

            return None

        def load_candidate(reference: str):
            optimized_path = resolve_optimized_artifact(reference)
            if optimized_path is not None:
                backend_name = infer_backend_from_path(optimized_path)
                tokenizer, runtime_model = load_runtime_model(optimized_path, backend_name, device=device)
                return tokenizer, runtime_model, backend_name, str(optimized_path), optimized_path

            tokenizer, baseline_model = load_hf_baseline_model(reference, device=device)
            return tokenizer, baseline_model, "pytorch", reference, None

        def infer_baseline_reference(optimized_path: Path) -> Optional[str]:
            config_path = optimized_path / "config.json"
            if config_path.exists():
                try:
                    with config_path.open("r", encoding="utf-8") as file:
                        config = json.load(file)
                    for key in ("_name_or_path", "name_or_path", "model_name_or_path", "base_model"):
                        value = config.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()
                except Exception:
                    pass

            name = optimized_path.name
            for suffix in ("_onnx", "_openvino"):
                if name.endswith(suffix):
                    return name[: -len(suffix)]
            return None

        tokenizer_a, runtime_a, backend_a, label_a, optimized_path_a = load_candidate(model_a)

        if model_b is None:
            if optimized_path_a is None:
                raise BenchmarkError(
                    "When model_b is omitted, model_a must be an optimized artifact path/name "
                    "so baseline can be inferred."
                )
            inferred_baseline = infer_baseline_reference(optimized_path_a)
            if not inferred_baseline:
                raise BenchmarkError(
                    "Could not infer baseline model from optimized artifact metadata. "
                    "Pass model_b explicitly."
                )
            model_b = inferred_baseline
            console.print(f"[dim]Auto-inferred baseline model: {model_b}[/dim]")

        tokenizer_b, runtime_b, backend_b, label_b, _ = load_candidate(model_b)

        metrics_a = benchmark_model_inference(
            runtime_a, tokenizer_a, input_text=input_text, runs=runs, batch_size=batch_size, device=device
        )
        metrics_b = benchmark_model_inference(
            runtime_b, tokenizer_b, input_text=input_text, runs=runs, batch_size=batch_size, device=device
        )

        table = Table(show_header=True, header_style="bold magenta", title="Model Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column("Model A", justify="right")
        table.add_column("Model B", justify="right")
        table.add_column("Winner", style="bold green")

        winner_latency = "A" if metrics_a["mean_latency_s"] < metrics_b["mean_latency_s"] else "B"
        winner_throughput = "A" if metrics_a["throughput_rps"] > metrics_b["throughput_rps"] else "B"

        table.add_row(
            "Avg Latency (ms)",
            f"{metrics_a['mean_latency_s'] * 1000:.2f}",
            f"{metrics_b['mean_latency_s'] * 1000:.2f}",
            winner_latency,
        )
        table.add_row(
            "P95 Latency (ms)",
            f"{metrics_a['p95_latency_s'] * 1000:.2f}",
            f"{metrics_b['p95_latency_s'] * 1000:.2f}",
            "A" if metrics_a["p95_latency_s"] < metrics_b["p95_latency_s"] else "B",
        )
        table.add_row(
            "Throughput (req/s)",
            f"{metrics_a['throughput_rps']:.2f}",
            f"{metrics_b['throughput_rps']:.2f}",
            winner_throughput,
        )

        console.print("\n[bold cyan]🔍 Comparing models[/bold cyan]\n")
        console.print(f"Model A: {label_a} ({backend_a})")
        console.print(f"Model B: {label_b} ({backend_b})\n")
        console.print(table)
        console.print()

    except BenchmarkError as error:
        console.print(f"\n[bold red]❌ Compare error:[/bold red] {error}\n")
        raise typer.Exit(code=1)
    except Exception as error:
        console.print(f"\n[bold red]❌ Comparison failed:[/bold red] {error}\n")
        raise typer.Exit(code=1)
