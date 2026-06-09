"""
BaseAgent — abstract foundation for every KRITIQ pipeline agent.

All agents operate on a shared ``LangGraphState`` TypedDict that flows
through the LangGraph pipeline.  Each agent reads what it needs from
the state, does its work, and returns a *new* (or mutated) copy of the
state for the next node in the graph.
"""

from __future__ import annotations

import abc
import logging
from typing import Any, List, Optional, TypedDict


# ── Shared pipeline state ────────────────────────────────


class LangGraphState(TypedDict, total=False):
    """
    Canonical state dict shared by every agent in the LangGraph pipeline.

    Fields use ``total=False`` so each agent only needs to supply the
    keys it modifies — LangGraph merges updates automatically.
    """

    # ── Identity ─────────────────────────────────────────
    repo_url: str
    commit_sha: str
    report_id: str

    # ── Code ─────────────────────────────────────────────
    # List[dict] with keys: path, content, size, sha
    # (serialised from ``FileContent`` dataclass)
    files: List[dict[str, Any]]

    # ── Analysis results ─────────────────────────────────
    # List[dict] — serialised ``FlaggedIssue`` models
    flags: List[dict[str, Any]]

    # Parallel temporary storage to prevent overwriting during concurrent steps
    code_reviewer_flags: List[dict[str, Any]]
    security_flags: List[dict[str, Any]]

    # List[dict] — serialised ``Fix`` models
    fixes: List[dict[str, Any]]

    # ── Artefacts ────────────────────────────────────────
    screenshot_paths: List[str]
    uml_path: Optional[str]
    readme_content: Optional[str]


# ── Abstract base ────────────────────────────────────────


class BaseAgent(abc.ABC):
    """
    Every KRITIQ agent inherits from this class and implements
    :pymeth:`run`.

    Subclasses get:
    * A named ``logger`` derived from the class name.
    * A consistent ``__repr__``.
    * The contract that ``run`` receives the full pipeline state and
      returns the (possibly mutated) state.
    """

    def __init__(self) -> None:
        self.name: str = self.__class__.__name__
        self.logger: logging.Logger = logging.getLogger(
            f"kritiq.agents.{self.name}"
        )

    # ── Must override ────────────────────────────────────

    @abc.abstractmethod
    async def run(self, state: LangGraphState) -> LangGraphState:
        """
        Execute this agent's logic.

        Parameters
        ----------
        state : LangGraphState
            The current pipeline state (files, flags, fixes, …).

        Returns
        -------
        LangGraphState
            Updated state with this agent's contributions merged in.
        """
        ...

    # ── Helpers available to all agents ──────────────────

    def _log_start(self, state: LangGraphState) -> None:
        self.logger.info(
            "▶  %s  repo=%s  sha=%s  files=%d",
            self.name,
            state.get("repo_url", "?"),
            (state.get("commit_sha") or "?")[:8],
            len(state.get("files") or []),
        )

    def _log_done(self, label: str, count: int) -> None:
        self.logger.info("✔  %s  produced %d %s", self.name, count, label)

    def __repr__(self) -> str:
        return f"<{self.name}>"
