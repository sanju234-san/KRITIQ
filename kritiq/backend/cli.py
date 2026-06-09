"""
KRITIQ — Command Line Interface (CLI) Agent Tool.
Allows running reviews, viewing reports, checking status, config, and system health.
"""

import asyncio
from datetime import datetime
from functools import wraps
import os
import sys
from typing import Optional
from uuid import uuid4

import click
from rich import print as rprint
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add current directory to path if running directly to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.orchestrator import run_pipeline
from app.schemas.webhook import WebhookPayload
from app.schemas.report import ReviewReport, StatusEnum, StepStatusEnum
from app.services.mongo_repository import mongo_repository

console = Console()


def async_command(f):
    """Decorator to run click commands in an asyncio event loop."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


async def init_db():
    """Connect to database and check connection."""
    mongo_repository.connect()
    await mongo_repository.ping()


async def close_db():
    """Safely close database connection."""
    mongo_repository.close()


@click.group()
def cli():
    """KRITIQ: The Autonomous AI Code-Review & Fixer Agent CLI."""
    pass


# ── Command: Health ──────────────────────────────────────


@cli.command()
@async_command
async def health():
    """Check connectivity to MongoDB, Groq LLM, and GitHub."""
    console.print(Panel("[bold purple]KRITIQ Health Check[/]", expand=False))
    
    # 1. MongoDB Check
    try:
        await init_db()
        mongo_status = "[bold green]OK[/]"
    except Exception as e:
        mongo_status = f"[bold red]FAIL[/] ({e})"
    finally:
        await close_db()

    # 2. Groq LLM Check
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("mock_") or len(settings.GROQ_API_KEY) < 10:
        groq_status = "[bold red]FAIL[/] (Missing or invalid GROQ_API_KEY)"
    else:
        try:
            # Simple direct API call to check key
            import httpx
            headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
            async with httpx.AsyncClient() as client:
                res = await client.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5.0)
                if res.status_code == 200:
                    groq_status = "[bold green]OK[/]"
                else:
                    groq_status = f"[bold red]FAIL[/] (API returned {res.status_code})"
        except Exception as e:
            groq_status = f"[bold red]FAIL[/] ({e})"

    # 3. GitHub Check
    if not settings.GITHUB_TOKEN or settings.GITHUB_TOKEN.startswith("mock_") or len(settings.GITHUB_TOKEN) < 10:
        github_status = "[bold red]FAIL[/] (Missing or invalid GITHUB_TOKEN)"
    else:
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json"
            }
            async with httpx.AsyncClient() as client:
                res = await client.get("https://api.github.com/user", headers=headers, timeout=5.0)
                if res.status_code == 200:
                    github_status = "[bold green]OK[/]"
                else:
                    github_status = f"[bold red]FAIL[/] (API returned {res.status_code})"
        except Exception as e:
            github_status = f"[bold red]FAIL[/] ({e})"

    table = Table(box=None)
    table.add_column("Service", style="bold cyan")
    table.add_column("Status")
    
    table.add_row("MongoDB Database", mongo_status)
    table.add_row("Groq LLM Service", groq_status)
    table.add_row("GitHub API Gateway", github_status)
    
    console.print(table)


# ── Command: Config ──────────────────────────────────────


@cli.command()
def config():
    """Display loaded configuration parameters (safely masked)."""
    console.print(Panel("[bold purple]KRITIQ Environment Configuration[/]", expand=False))
    
    def mask(val: str) -> str:
        if not val:
            return "[red]Not Configured[/]"
        if val.startswith("mock_") or len(val) < 8:
            return f"{val} [yellow](Mock/Insecure)[/]"
        return f"{val[:4]}...{val[-4:]} [green](Configured)[/]"

    table = Table(box=None)
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value")
    
    table.add_row("App Environment", settings.APP_ENV)
    table.add_row("Groq API Key", mask(settings.GROQ_API_KEY))
    table.add_row("GitHub PAT Token", mask(settings.GITHUB_TOKEN))
    table.add_row("MongoDB Connection URI", mask(settings.MONGODB_URI))
    table.add_row("MongoDB DB Name", settings.MONGODB_DB_NAME)
    table.add_row("GitHub Webhook Secret", mask(settings.GITHUB_WEBHOOK_SECRET))
    
    console.print(table)


# ── Command: List ────────────────────────────────────────


@cli.command(name="list")
@click.option("--limit", default=20, help="Number of reports to fetch.")
@async_command
async def list_reports(limit):
    """List recent codebase audit reports stored in the database."""
    try:
        await init_db()
    except Exception as e:
        console.print(f"[bold red]Database connection failed:[/] {e}")
        return

    reports = await mongo_repository.list_all_reports(limit=limit)
    await close_db()

    if not reports:
        console.print("[yellow]No reports found in the database.[/]")
        return

    table = Table(title="[bold purple]Recent KRITIQ Reviews[/]")
    table.add_column("Report ID", style="dim", width=36)
    table.add_column("Repository URL", style="cyan")
    table.add_column("Branch/SHA", style="magenta")
    table.add_column("Status")
    table.add_column("Flags", justify="right")
    table.add_column("Fixes", justify="right")
    table.add_column("Created At")

    for r in reports:
        status_color = "green" if r.status == StatusEnum.complete else "yellow" if r.status == StatusEnum.running else "red" if r.status == StatusEnum.failed else "dim"
        status_text = f"[{status_color}]{r.status.value}[/]"
        
        created_str = r.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(r.created_at, datetime) else str(r.created_at)

        table.add_row(
            r.id,
            r.repo_url,
            r.commit_sha[:8] if r.commit_sha else "main",
            status_text,
            str(len(r.flags)),
            str(len(r.fixes)),
            created_str
        )

    console.print(table)


# ── Command: Status ──────────────────────────────────────


@cli.command()
@click.argument("report_id")
@async_command
async def status(report_id):
    """Retrieve detailed status of a specific review pipeline."""
    try:
        await init_db()
        report = await mongo_repository.get_report(report_id)
    except Exception as e:
        console.print(f"[bold red]Database query failed:[/] {e}")
        return
    finally:
        await close_db()

    if not report:
        console.print(f"[bold red]Error:[/] Report '{report_id}' not found.")
        return

    console.print(Panel(f"[bold purple]Review Status:[/] {report_id}", expand=False))
    console.print(f"[bold]Repo URL:[/] {report.repo_url}")
    console.print(f"[bold]Commit SHA:[/] {report.commit_sha}")
    
    status_color = "green" if report.status == StatusEnum.complete else "cyan" if report.status == StatusEnum.running else "red" if report.status == StatusEnum.failed else "dim"
    console.print(f"[bold]Overall Status:[/] [{status_color}]{report.status.value}[/]")
    if report.duration_seconds:
        console.print(f"[bold]Duration:[/] {report.duration_seconds}s")
    if report.error_message:
        console.print(f"[bold red]Error:[/] {report.error_message}")

    if report.steps:
        console.print("\n[bold]Step Progress:[/]")
        step_table = Table(box=None)
        step_table.add_column("Step Name")
        step_table.add_column("Status")
        step_table.add_column("Duration")
        step_table.add_column("Details")
        
        for step in report.steps:
            st_color = "green" if step.status == StepStatusEnum.complete else "cyan" if step.status == StepStatusEnum.running else "red" if step.status == StepStatusEnum.failed else "dim"
            st_text = f"[{st_color}]{step.status.value}[/]"
            
            dur = f"{step.duration_seconds}s" if step.duration_seconds is not None else "-"
            err = f"[red]{step.error_message}[/]" if step.error_message else ""
            
            step_table.add_row(step.name, st_text, dur, err)
        
        console.print(step_table)


# ── Command: Report ──────────────────────────────────────


@cli.command()
@click.argument("report_id")
@click.option("--output", "-o", default=None, help="Save report summary to this file.")
@async_command
async def report(report_id, output):
    """View and format a completed review report in the terminal."""
    try:
        await init_db()
        report_data = await mongo_repository.get_report(report_id)
    except Exception as e:
        console.print(f"[bold red]Database query failed:[/] {e}")
        return
    finally:
        await close_db()

    if not report_data:
        console.print(f"[bold red]Error:[/] Report '{report_id}' not found.")
        return

    if report_data.status != StatusEnum.complete:
        console.print(f"[yellow]This report is currently '{report_data.status.value}'. Please wait for completion.[/]")
        return

    # Print Summary Markdown
    if report_data.summary:
        console.print("\n" + "=" * 80)
        console.print(Markdown(report_data.summary))
        console.print("=" * 80 + "\n")
        
        if output:
            try:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(report_data.summary)
                console.print(f"[green]Saved markdown summary to {output}[/]")
            except Exception as e:
                console.print(f"[bold red]Failed to save output file:[/] {e}")
    else:
        console.print("[yellow]No report summary details found for this review.[/]")

    # Print Issues Table
    if report_data.flags:
        table = Table(title="[bold red]Flagged Code Issues[/]")
        table.add_column("File", style="cyan")
        table.add_column("Line", style="dim", justify="right")
        table.add_column("Severity")
        table.add_column("Category", style="magenta")
        table.add_column("Description")
        
        for issue in report_data.flags:
            sev_color = "red" if issue.severity.value == "critical" else "orange3" if issue.severity.value == "high" else "yellow" if issue.severity.value == "medium" else "green"
            sev_text = f"[{sev_color}]{issue.severity.value}[/]"
            
            table.add_row(
                issue.file_path,
                str(issue.line_number),
                sev_text,
                issue.category.value,
                issue.description
            )
        
        console.print(table)
    else:
        console.print("[green]No code issues were flagged in this review! Code looks great.[/]")


# ── Command: Review ──────────────────────────────────────


@cli.command()
@click.argument("repo_url")
@click.option("--live-url", default=None, help="Live application URL for screenshots.")
@click.option("--branch", default="main", help="Branch or commit SHA to audit.")
@async_command
async def review(repo_url, live_url, branch):
    """Trigger a new codebase review pipeline and track progress live."""
    try:
        await init_db()
    except Exception as e:
        console.print(f"[bold red]Database connection failed:[/] {e}")
        return

    report_id = str(uuid4())
    payload = WebhookPayload(
        repo_url=repo_url,
        live_url=live_url,
        commit_sha=branch,
    )

    console.print(Panel(f"[bold purple]Initializing KRITIQ Review Pipeline[/]\n[bold]Repo URL:[/] {repo_url}\n[bold]Branch:[/] {branch}\n[bold]Report ID:[/] {report_id}"))

    # Spawn the pipeline runner in background
    pipeline_task = asyncio.create_task(run_pipeline(payload, report_id))

    # Live UI update loop
    step_layout = {}
    
    with Live(Text("Starting execution pipeline...", style="cyan"), refresh_per_second=2) as live:
        while not pipeline_task.done():
            await asyncio.sleep(1.0)
            
            # Retrieve latest step states
            report = await mongo_repository.get_report(report_id)
            if not report:
                continue
            
            # Print table
            table = Table(title=f"Pipeline Progress [bold cyan]({report.status.value})[/]", box=None)
            table.add_column("Step")
            table.add_column("Status")
            table.add_column("Duration")
            table.add_column("Message/Error")

            for step in report.steps:
                st_color = "green" if step.status == StepStatusEnum.complete else "cyan" if step.status == StepStatusEnum.running else "red" if step.status == StepStatusEnum.failed else "dim"
                
                # Format spinner/status icon
                st_icon = "pending"
                if step.status == StepStatusEnum.running:
                    st_icon = "running"
                elif step.status == StepStatusEnum.complete:
                    st_icon = "complete"
                elif step.status == StepStatusEnum.failed:
                    st_icon = "failed"
                
                dur_str = f"{step.duration_seconds}s" if step.duration_seconds is not None else "-"
                err_str = f"[red]{step.error_message}[/]" if step.error_message else ""
                
                table.add_row(
                    step.name,
                    f"[{st_color}]{st_icon}[/]",
                    dur_str,
                    err_str
                )
            
            live.update(table)

    await close_db()

    # Get final result or handle failure
    try:
        final_report = await pipeline_task
        console.print(f"\n[bold green][SUCCESS] Review pipeline completed successfully![/]")
        console.print(f"[bold]Flags Found:[/] {len(final_report.flags)}")
        console.print(f"[bold]Fixes Committed:[/] {len(final_report.fixes)}")
        console.print(f"\nRun the following command to view details: [bold]python cli.py report {report_id}[/]")
    except Exception as exc:
        console.print(f"\n[bold red][ERROR] Pipeline run failed overall:[/] {exc}")


if __name__ == "__main__":
    cli()
