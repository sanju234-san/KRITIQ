"""
KRITIQ — Local Pipeline Playground Runner.
Performs a live review on local backend files (security.py, retry.py) using the actual
AI agents, saving steps and results in MongoDB, and printing a Rich terminal dashboard.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# Ensure app imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.orchestrator import run_pipeline
from app.services.github_service import FileContent
from app.schemas.webhook import WebhookPayload
from app.services.mongo_repository import mongo_repository

console = Console()


async def mock_fetch_local_files(repo_url, branch=None):
    """Scan local app/core folder and load security.py and retry.py for review."""
    files = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.join(base_dir, "app", "core")
    
    targets = ["security.py", "retry.py"]
    rprint("[cyan]   [Playground] Mocking GitHub fetch — loading local files:[/]")
    
    for filename in targets:
        path = os.path.join(core_dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            rprint(f"     - Loaded {filename} ({len(content)} chars)")
            files.append(
                FileContent(
                    path=f"app/core/{filename}",
                    content=content,
                    size=len(content),
                    sha=f"local_{filename}_sha",
                )
            )
    return files


async def mock_commit_local(repo_url, file_path, content, message, branch=None):
    """Simulate committing code fixes by printing them to terminal instead of pushing to GitHub."""
    rprint(f"\n[bold yellow]   [Playground Commit Simulation][/]")
    rprint(f"     File path: [cyan]{file_path}[/]")
    rprint(f"     Message:   [cyan]{message}[/]")
    rprint(f"     First 5 lines of resolved file:\n[dim]" + "\n".join(content.splitlines()[:5]) + "[/]")
    return "playground_commit_sha_9999"


async def run_playground():
    console.print(Panel("[bold purple]KRITIQ Playground Runner[/]\nRunning a live codebase review of backend files", expand=False))
    
    # 1. Initialize and Ping Database
    rprint("[bold cyan]1. Initializing MongoDB Connection...[/]")
    try:
        mongo_repository.connect()
        await mongo_repository.ping()
        rprint("[green][OK] Connected to MongoDB database successfully.[/]")
    except Exception as exc:
        rprint(f"[bold red][ERROR] Failed to connect to MongoDB:[/] {exc}")
        return

    # 2. Setup Payload
    payload = WebhookPayload(
        repo_url="https://github.com/sanju234-san/KRITIQ-playground",
        commit_sha="playground-main",
        live_url="http://localhost:8000/health"
    )

    # 3. Patch and execute the pipeline
    rprint("\n[bold cyan]2. Launching Autonomous Pipeline...[/]")
    
    with patch("app.services.github_service.github_service.fetch_files", side_effect=mock_fetch_local_files), \
         patch("app.services.github_service.github_service.commit_file", side_effect=mock_commit_local):
         
        try:
            # Execute pipeline and retrieve final DB report
            report = await run_pipeline(payload)
            
            # 4. Display Results Dashboard
            rprint("\n[bold green][SUCCESS] Pipeline Execution Complete![/]\n")
            console.print(Panel(f"[bold purple]Review Report Summary[/]\n[bold]Report ID:[/] {report.id}\n[bold]Status:[/] [green]{report.status.value}[/]\n[bold]Total Duration:[/] {report.duration_seconds}s", expand=False))
            
            # Step progress table
            step_table = Table(title="[bold cyan]Step Execution timings[/]")
            step_table.add_column("Step")
            step_table.add_column("Status")
            step_table.add_column("Duration")
            step_table.add_column("Details")
            
            for step in report.steps:
                st_color = "green" if step.status == "complete" else "red" if step.status == "failed" else "dim"
                step_table.add_row(
                    step.name,
                    f"[{st_color}]{step.status.value}[/]",
                    f"{step.duration_seconds}s" if step.duration_seconds is not None else "-",
                    step.error_message or ""
                )
            console.print(step_table)

            # Issues table
            if report.flags:
                issues_table = Table(title="[bold red]Flagged Issues[/]")
                issues_table.add_column("File")
                issues_table.add_column("Line", justify="right")
                issues_table.add_column("Severity")
                issues_table.add_column("Description")
                
                for issue in report.flags:
                    sev_color = "red" if issue.severity.value == "critical" else "orange3" if issue.severity.value == "high" else "yellow" if issue.severity.value == "medium" else "green"
                    issues_table.add_row(
                        issue.file_path,
                        str(issue.line_number),
                        f"[{sev_color}]{issue.severity.value}[/]",
                        issue.description
                    )
                console.print(issues_table)
            else:
                rprint("\n[bold green]No issues flagged in security.py or retry.py![/]")

            # Summary README content
            if report.summary:
                console.print("\n[bold cyan]Final Agent Summary Report:[/]")
                console.print(Panel(Markdown(report.summary), title="README.md Report Summary"))

        except Exception as exc:
            rprint(f"\n[bold red][ERROR] Pipeline execution failed:[/] {exc}")
            import traceback
            traceback.print_exc()
            
        finally:
            mongo_repository.close()


if __name__ == "__main__":
    asyncio.run(run_playground())
