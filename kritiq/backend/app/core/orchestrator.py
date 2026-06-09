"""
Orchestrator — full 5-agent LangGraph review & fix state machine pipeline.
Tracks execution states in MongoDB (pending -> running -> complete/failed).
"""

import logging
import time
from uuid import uuid4
from typing import Any, List

from langgraph.graph import StateGraph, START, END

from app.agents.base import LangGraphState
from app.agents.code_reviewer import CodeReviewerAgent
from app.agents.security_auditor import SecurityAuditorAgent
from app.agents.auto_fixer import AutoFixerAgent
from app.agents.screenshot_uml import ScreenshotUMLAgent
from app.agents.readme_writer import ReadmeWriterAgent

from app.schemas.webhook import WebhookPayload
from app.schemas.report import ReviewReport, StatusEnum, PipelineStep, StepStatusEnum
from app.schemas.issue import FlaggedIssue, Fix
from app.services.github_service import github_service
from app.services.mongo_repository import mongo_repository

logger = logging.getLogger("kritiq.orchestrator")

# ── Agent Instances ──────────────────────────────────────

reviewer = CodeReviewerAgent()
auditor = SecurityAuditorAgent()
fixer = AutoFixerAgent()
uml_agent = ScreenshotUMLAgent()
readme_agent = ReadmeWriterAgent()

# ── Helper for status updates ────────────────────────────


async def update_step_status(
    report_id: str,
    step_name: str,
    status: StepStatusEnum,
    duration_seconds: float = None,
    error_message: str = None,
) -> None:
    """Updates MongoDB with the status of a specific step in the pipeline."""
    try:
        report = await mongo_repository.get_report(report_id)
        if report:
            updated = False
            for step in report.steps:
                if step.name == step_name:
                    step.status = status
                    if duration_seconds is not None:
                        step.duration_seconds = round(duration_seconds, 2)
                    if error_message is not None:
                        step.error_message = error_message
                    updated = True
                    break
            
            # If the step wasn't in the list for some reason, append it
            if not updated:
                report.steps.append(
                    PipelineStep(
                        name=step_name,
                        status=status,
                        duration_seconds=round(duration_seconds, 2) if duration_seconds is not None else None,
                        error_message=error_message,
                    )
                )
            await mongo_repository.save_report(report)
    except Exception as exc:
        logger.warning(
            "Failed to update step status for %s to %s in MongoDB: %s",
            step_name,
            status,
            exc,
        )


# ── Node Functions ───────────────────────────────────────


async def fetch_source_files(state: LangGraphState) -> dict:
    """Fetch codebase files from GitHub repository and set state status to running."""
    repo_url = state.get("repo_url")
    commit_sha = state.get("commit_sha")
    report_id = state.get("report_id")

    logger.info("Node [fetch_files]: Updating DB status to running for report=%s", report_id)
    try:
        report = await mongo_repository.get_report(report_id)
        if report:
            report.status = StatusEnum.running
            await mongo_repository.save_report(report)
    except Exception as db_err:
        logger.warning("Failed to update status to running in MongoDB: %s", db_err)

    start_time = time.time()
    await update_step_status(report_id, "clone_repo", StepStatusEnum.running)

    try:
        files = await github_service.fetch_files(repo_url, branch=commit_sha)
        serialized_files = [
            {
                "path": f.path,
                "content": f.content,
                "size": f.size,
                "sha": f.sha,
            }
            for f in files
        ]
        duration = time.time() - start_time
        await update_step_status(report_id, "clone_repo", StepStatusEnum.complete, duration_seconds=duration)
        logger.info("Node [fetch_files]: Fetched %d files", len(serialized_files))
        return {"files": serialized_files}
    except Exception as exc:
        duration = time.time() - start_time
        logger.error("Node [fetch_files] failed to get codebase: %s", exc)
        await update_step_status(
            report_id,
            "clone_repo",
            StepStatusEnum.failed,
            duration_seconds=duration,
            error_message=str(exc),
        )
        # Error recovery: Return empty files list but keep going
        return {"files": []}


async def code_review_node(state: LangGraphState) -> dict:
    """Execute CodeReviewerAgent."""
    report_id = state.get("report_id")
    logger.info("Node [code_reviewer]: Running review.")
    start_time = time.time()
    await update_step_status(report_id, "code_review", StepStatusEnum.running)

    try:
        res = await reviewer.run(state)
        duration = time.time() - start_time
        await update_step_status(report_id, "code_review", StepStatusEnum.complete, duration_seconds=duration)
        return {"flags": res.get("flags", [])}
    except Exception as exc:
        duration = time.time() - start_time
        logger.error("Node [code_reviewer] failed: %s", exc)
        await update_step_status(
            report_id,
            "code_review",
            StepStatusEnum.failed,
            duration_seconds=duration,
            error_message=str(exc),
        )
        return {"flags": []}


async def security_audit_node(state: LangGraphState) -> dict:
    """Execute SecurityAuditorAgent."""
    report_id = state.get("report_id")
    logger.info("Node [security_auditor]: Running security audit.")
    start_time = time.time()
    await update_step_status(report_id, "security_audit", StepStatusEnum.running)

    try:
        res = await auditor.run(state)
        duration = time.time() - start_time
        await update_step_status(report_id, "security_audit", StepStatusEnum.complete, duration_seconds=duration)
        return {"security_flags": res.get("security_flags", [])}
    except Exception as exc:
        duration = time.time() - start_time
        logger.error("Node [security_auditor] failed: %s", exc)
        await update_step_status(
            report_id,
            "security_audit",
            StepStatusEnum.failed,
            duration_seconds=duration,
            error_message=str(exc),
        )
        return {"security_flags": []}


def merge_results_node(state: LangGraphState) -> dict:
    """Join parallel code reviewer and security auditor flags, then deduplicate."""
    logger.info("Node [merge_results]: Merging audit findings.")
    cr_flags = state.get("flags") or []
    sec_flags = state.get("security_flags") or []

    combined = list(cr_flags) + list(sec_flags)

    # Deduplicate
    seen = set()
    deduped = []
    for f in combined:
        key = (
            f.get("file_path"),
            f.get("line_number"),
            f.get("category"),
            f.get("description"),
        )
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    logger.info("Node [merge_results]: Total flags merged = %d", len(deduped))
    return {
        "flags": deduped,
        "security_flags": [],
    }


async def auto_fixer_node(state: LangGraphState) -> dict:
    """Execute AutoFixerAgent."""
    report_id = state.get("report_id")
    logger.info("Node [auto_fixer]: Attempting auto-fixes.")
    start_time = time.time()
    await update_step_status(report_id, "auto_fix", StepStatusEnum.running)

    try:
        res = await fixer.run(state)
        duration = time.time() - start_time
        await update_step_status(report_id, "auto_fix", StepStatusEnum.complete, duration_seconds=duration)
        return {
            "files": res.get("files", []),
            "fixes": res.get("fixes", []),
        }
    except Exception as exc:
        duration = time.time() - start_time
        logger.error("Node [auto_fixer] failed: %s", exc)
        await update_step_status(
            report_id,
            "auto_fix",
            StepStatusEnum.failed,
            duration_seconds=duration,
            error_message=str(exc),
        )
        return {
            "files": state.get("files") or [],
            "fixes": [],
        }


async def screenshot_uml_node(state: LangGraphState) -> dict:
    """Execute ScreenshotUMLAgent."""
    report_id = state.get("report_id")
    logger.info("Node [screenshot_uml]: Capturing UI and UML.")
    start_time = time.time()
    await update_step_status(report_id, "screenshot_uml", StepStatusEnum.running)

    try:
        res = await uml_agent.run(state)
        duration = time.time() - start_time
        await update_step_status(report_id, "screenshot_uml", StepStatusEnum.complete, duration_seconds=duration)
        return {
            "screenshot_paths": res.get("screenshot_paths", []),
            "uml_path": res.get("uml_path"),
        }
    except Exception as exc:
        duration = time.time() - start_time
        logger.error("Node [screenshot_uml] failed: %s", exc)
        await update_step_status(
            report_id,
            "screenshot_uml",
            StepStatusEnum.failed,
            duration_seconds=duration,
            error_message=str(exc),
        )
        return {
            "screenshot_paths": state.get("screenshot_paths") or [],
            "uml_path": None,
        }


async def readme_writer_node(state: LangGraphState) -> dict:
    """Execute ReadmeWriterAgent."""
    report_id = state.get("report_id")
    logger.info("Node [readme_writer]: Creating review summary markdown.")
    start_time = time.time()
    await update_step_status(report_id, "readme_writer", StepStatusEnum.running)

    try:
        res = await readme_agent.run(state)
        duration = time.time() - start_time
        await update_step_status(report_id, "readme_writer", StepStatusEnum.complete, duration_seconds=duration)
        return {"readme_content": res.get("readme_content")}
    except Exception as exc:
        duration = time.time() - start_time
        logger.error("Node [readme_writer] failed: %s", exc)
        await update_step_status(
            report_id,
            "readme_writer",
            StepStatusEnum.failed,
            duration_seconds=duration,
            error_message=str(exc),
        )
        return {"readme_content": None}


async def save_report_node(state: LangGraphState) -> dict:
    """Commit report to database and update status to complete."""
    report_id = state.get("report_id")
    logger.info("Node [save_report]: Saving final report=%s to MongoDB", report_id)

    start_time = state.get("pipeline_start_time")
    duration = time.time() - start_time if start_time else None

    # Retrieve intermediate steps status
    steps = []
    try:
        existing = await mongo_repository.get_report(report_id)
        if existing:
            steps = existing.steps
    except Exception as exc:
        logger.warning("Failed to fetch existing steps in save_report_node: %s", exc)

    try:
        report = ReviewReport(
            id=report_id,
            repo_url=state.get("repo_url", ""),
            commit_sha=state.get("commit_sha", ""),
            flags=[FlaggedIssue.model_validate(f) for f in state.get("flags", [])],
            fixes=[Fix.model_validate(f) for f in state.get("fixes", [])],
            readme_path=None,
            screenshot_paths=state.get("screenshot_paths") or [],
            uml_path=state.get("uml_path"),
            summary=state.get("readme_content"),
            status=StatusEnum.complete,
            steps=steps,
            duration_seconds=round(duration, 2) if duration is not None else None,
        )
        await mongo_repository.save_report(report)
    except Exception as exc:
        logger.error("Node [save_report] failed: %s", exc)

    return {}


# ── Conditional Routing logic ───────────────────────────


async def route_after_review(state: LangGraphState) -> str:
    """Route conditionally based on whether any issues are flagged."""
    flags = state.get("flags") or []
    if len(flags) > 0:
        logger.info("Routing: Flags found -> auto_fixer")
        return "auto_fixer"
    else:
        logger.info("Routing: No flags found -> skipping auto_fixer -> screenshot_uml")
        
        # If we skipped auto_fixer, mark it as complete/skipped with 0 duration
        report_id = state.get("report_id")
        if report_id:
            await update_step_status(
                report_id,
                "auto_fix",
                StepStatusEnum.complete,
                duration_seconds=0.0,
                error_message="Skipped (no review issues flagged)",
            )
            
        return "screenshot_uml"


# ── Graph Construction ───────────────────────────────────

workflow = StateGraph(LangGraphState)

# Add all 5 agents + support nodes
workflow.add_node("fetch_files", fetch_source_files)
workflow.add_node("code_reviewer", code_review_node)
workflow.add_node("security_auditor", security_audit_node)
workflow.add_node("merge_results", merge_results_node)
workflow.add_node("auto_fixer", auto_fixer_node)
workflow.add_node("screenshot_uml", screenshot_uml_node)
workflow.add_node("readme_writer", readme_writer_node)
workflow.add_node("save_report", save_report_node)

# Set starting entry point
workflow.add_edge(START, "fetch_files")

# Fan-out to Code Reviewer and Security Auditor concurrently
workflow.add_edge("fetch_files", "code_reviewer")
workflow.add_edge("fetch_files", "security_auditor")

# Fan-in: join code review and security audits
workflow.add_edge("code_reviewer", "merge_results")
workflow.add_edge("security_auditor", "merge_results")

# Conditional Router from merge node
workflow.add_conditional_edges(
    "merge_results",
    route_after_review,
    {
        "auto_fixer": "auto_fixer",
        "screenshot_uml": "screenshot_uml",
    },
)

# Connect fixer to screenshot
workflow.add_edge("auto_fixer", "screenshot_uml")

# Connect screenshot to README compiler
workflow.add_edge("screenshot_uml", "readme_writer")

# Connect README compiler to DB persistence step
workflow.add_edge("readme_writer", "save_report")

# Set completion point
workflow.add_edge("save_report", END)

# Compile pipeline
pipeline = workflow.compile()


# ── Pipeline Runner ──────────────────────────────────────


async def run_pipeline(payload: WebhookPayload, report_id: str = None) -> ReviewReport:
    """
    Entry point to trigger the codebase audit and auto-fix pipeline.
    Tracks state updates in MongoDB (pending -> running -> complete/failed).
    """
    if not report_id:
        report_id = str(uuid4())
    repo_url = payload.repo_url
    commit_sha = payload.commit_sha
    live_url = payload.live_url
    start_time = time.time()

    # Initialize all step entities with pending status
    initial_steps = [
        PipelineStep(name="clone_repo", status=StepStatusEnum.pending),
        PipelineStep(name="code_review", status=StepStatusEnum.pending),
        PipelineStep(name="security_audit", status=StepStatusEnum.pending),
        PipelineStep(name="auto_fix", status=StepStatusEnum.pending),
        PipelineStep(name="screenshot_uml", status=StepStatusEnum.pending),
        PipelineStep(name="readme_writer", status=StepStatusEnum.pending),
    ]

    # 1. Create and save initial report in DB as pending if not already present
    logger.info("Initializing pipeline run for report_id=%s, repo_url=%s", report_id, repo_url)
    existing_report = None
    try:
        existing_report = await mongo_repository.get_report(report_id)
    except Exception:
        pass

    if not existing_report:
        report = ReviewReport(
            id=report_id,
            repo_url=repo_url,
            commit_sha=commit_sha,
            status=StatusEnum.pending,
            flags=[],
            fixes=[],
            screenshot_paths=[],
            steps=initial_steps,
        )
        try:
            await mongo_repository.save_report(report)
        except Exception as db_err:
            logger.error("Failed to create initial database report record: %s", db_err)
    else:
        report = existing_report
        # Initialize steps if they aren't there yet
        if not report.steps:
            report.steps = initial_steps
            try:
                await mongo_repository.save_report(report)
            except Exception as db_err:
                logger.error("Failed to update initial report steps: %s", db_err)

    # 2. Invoke state machine
    initial_state = LangGraphState(
        repo_url=repo_url,
        commit_sha=commit_sha,
        report_id=report_id,
        live_url=live_url,
        files=[],
        flags=[],
        fixes=[],
        screenshot_paths=[],
        uml_path=None,
        readme_content=None,
        pipeline_start_time=start_time,  # Track start time in state
    )

    try:
        await pipeline.ainvoke(initial_state)
        
        # 3. Retrieve and return the final report from database
        final_report = await mongo_repository.get_report(report_id)
        if final_report:
            return final_report
        return report
    except Exception as exc:
        logger.error("Review pipeline failed for report_id=%s: %s", report_id, exc)
        # Update status to failed
        try:
            failed_report = await mongo_repository.get_report(report_id)
            if failed_report:
                failed_report.status = StatusEnum.failed
                failed_report.error_message = str(exc)
                failed_report.duration_seconds = round(time.time() - start_time, 2)
                await mongo_repository.save_report(failed_report)
        except Exception as db_err:
            logger.error("Failed to update status to failed in DB: %s", db_err)
        raise exc
