"""
Entrypoint of the `typer` app.
See the documentation in the `help` sections of every parameter for more information, or run ``python -m broken_access_control_scanner --help``.
"""
import os
import traceback
from pathlib import Path

import typer
from anthropic import Anthropic
from rich.console import Console
from rich.table import Table

from broken_access_control_scanner.analyzer import analyze_file
from broken_access_control_scanner.models import Severity

app = typer.Typer()

# Color mapping for severity levels
SEVERITY_COLORS = {
    Severity.NONE: "green",
    Severity.LOW: "blue",
    Severity.MEDIUM: "yellow",
    Severity.HIGH: "red",
    Severity.CRITICAL: "bold red",
}


def main(
    source_file: Path = typer.Argument(
        ...,
        help="Path to the source code file to analyze.",
        exists=True,
        readable=True,
    ),
    data_model: str = typer.Option(
        ...,
        "--data-model", "-d",
        help="Description of the data model and context for the endpoints.",
    ),
    model: str = typer.Option(
        "claude-sonnet-4-20250514",
        "--model", "-m",
        help="Anthropic model to use.",
    ),
):
    """
    Scan source code for broken access control vulnerabilities using AI.

    This tool analyzes source code for potential security issues related to
    access control, including missing authorization checks, IDOR vulnerabilities,
    and privilege escalation risks.

    Requires ANTHROPIC_API_KEY environment variable to be set.
    """
    console = Console()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY environment variable is required.[/red]")
        raise typer.Exit(code=1)

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)

    # Analyze file
    console.print(f"[blue]Analyzing:[/blue] {source_file}")
    try:
        results = analyze_file(client, source_file, data_model, model)
    except Exception:
        console.print(f"[red]Error: AI failed to parse the response.[/red]")
        traceback.print_exc()
        raise typer.Exit(code=1)

    if not results:
        console.print("[yellow]No endpoints found in the file.[/yellow]")
        raise typer.Exit(code=0)

    console.print(f"[blue]Found {len(results)} endpoint(s).[/blue]")
    console.print()

    # Create results table
    table = Table(title="Broken Access Control Vulnerability Scan Results")
    table.add_column("Endpoint", style="cyan", max_width=50)
    table.add_column("Severity", justify="center")
    table.add_column("Description", max_width=60)

    for result in results:
        severity_color = SEVERITY_COLORS[result.severity]
        table.add_row(
            result.endpoint,
            f"[{severity_color}]{result.severity.value}[/{severity_color}]",
            result.description
        )

    console.print(table)

    # Print summary
    console.print()
    severity_counts = {}
    for result in results:
        severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1

    console.print("[bold]Summary:[/bold]")
    for severity in Severity:
        count = severity_counts.get(severity, 0)
        if count > 0:
            color = SEVERITY_COLORS[severity]
            console.print(f"  [{color}]{severity.value}[/{color}]: {count}")
