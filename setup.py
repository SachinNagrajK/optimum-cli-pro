"""
Optimum CLI Pro - Production-Grade Model Optimization Toolkit

This is a setuptools-based setup.py for backward compatibility.
The main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="optimum-cli-pro",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer[all]>=0.9.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "PyYAML>=6.0",
        "loguru>=0.7.0",
        "rich>=13.7.0",
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "transformers>=4.36.0",
        "torch>=2.1.0",
        "optimum>=1.16.0",
        "onnx>=1.15.0",
        "onnxruntime>=1.16.0",
        "datasets>=2.16.0",
        "evaluate>=0.4.1",
        "psutil>=5.9.0",
        "aiosqlite>=0.19.0",
        "httpx>=0.26.0",
        "plotly>=5.18.0",
        "pandas>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "optimum-cli=optimum_cli.__main__:main",
        ],
    },
    python_requires=">=3.9",
)
