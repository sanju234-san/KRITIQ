"""
GitHubService — async-compatible wrapper around PyGithub.

Provides:
  • fetch_files()  — recursively pull every text file, honouring .gitignore
  • commit_file()  — push a single file change back to the repo

All PyGithub calls are synchronous under the hood; we wrap them with
``asyncio.to_thread`` so the FastAPI event loop is never blocked.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import re
from dataclasses import dataclass
from typing import List, Optional

import pathspec
from github import Github, GithubException
from github.ContentFile import ContentFile
from github.Repository import Repository

from app.core.config import settings

logger = logging.getLogger("kritiq.github_service")

# ── Data containers ──────────────────────────────────────


@dataclass(frozen=True, slots=True)
class FileContent:
    """Lightweight container returned by ``fetch_files``."""

    path: str
    content: str
    size: int = 0
    sha: str = ""


# ── Helpers ──────────────────────────────────────────────

_REPO_URL_RE = re.compile(
    r"github\.com[:/](?P<owner>[^/]+)/(?P<name>[^/.]+?)(?:\.git)?/?$"
)

# Files that should always be skipped regardless of .gitignore
_ALWAYS_SKIP: set[str] = {
    ".git",
    ".DS_Store",
    "Thumbs.db",
    "__pycache__",
    "node_modules",
    ".env",
}

# Maximum single-file size we'll try to decode (500 KB)
_MAX_FILE_BYTES = 512_000


# Simple owner/repo shorthand pattern (e.g. "sanju234-san/KRITIQ")
_SHORTHAND_RE = re.compile(r"^(?P<owner>[\w.-]+)/(?P<name>[\w.-]+)$")


def _parse_owner_repo(repo_url: str) -> tuple[str, str]:
    """
    Extract ``(owner, name)`` from a GitHub URL or shorthand.

    Supports:
      - owner/repo                       (shorthand)
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      - git@github.com:owner/repo.git
    """
    # Try shorthand first (e.g. "sanju234-san/KRITIQ")
    m = _SHORTHAND_RE.match(repo_url.strip())
    if m:
        return m.group("owner"), m.group("name")

    # Try full URL
    m = _REPO_URL_RE.search(repo_url)
    if m:
        return m.group("owner"), m.group("name")

    raise ValueError(f"Cannot parse GitHub owner/repo from URL: {repo_url}")


def _build_gitignore_spec(repo: Repository) -> Optional[pathspec.PathSpec]:
    """
    Try to read ``.gitignore`` from the repo root and compile it
    into a ``pathspec.PathSpec`` matcher.  Returns ``None`` when the
    repo has no ``.gitignore``.
    """
    try:
        gitignore_file: ContentFile = repo.get_contents(".gitignore")  # type: ignore[assignment]
        raw = base64.b64decode(gitignore_file.content).decode("utf-8", errors="replace")
        patterns = [
            line.strip()
            for line in raw.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    except GithubException:
        logger.debug("No .gitignore found — skipping pattern filter")
        return None


def _is_text_decodable(raw: bytes) -> bool:
    """Cheap heuristic: reject files with null bytes (likely binary)."""
    return b"\x00" not in raw[:8192]


# ── Service class ────────────────────────────────────────


class GitHubService:
    """
    Stateless service that wraps PyGithub operations.

    Instantiated once at app startup and shared across requests.
    """

    def __init__(self, token: Optional[str] = None) -> None:
        self._token = token or settings.GITHUB_TOKEN
        self._client = Github(self._token, per_page=100)

    # ── public async API ─────────────────────────────────

    async def fetch_files(
        self,
        repo_url: str,
        branch: Optional[str] = None,
    ) -> List[FileContent]:
        """
        Recursively fetch every text file from ``repo_url``,
        filtering out paths matched by ``.gitignore``.

        Parameters
        ----------
        repo_url : str
            Full GitHub URL (https://github.com/owner/repo).
        branch : str | None
            Branch / ref to read.  Defaults to the repo's default branch.

        Returns
        -------
        List[FileContent]
            Decoded file path + content pairs.
        """
        return await asyncio.to_thread(
            self._fetch_files_sync, repo_url, branch
        )

    async def commit_file(
        self,
        repo_url: str,
        file_path: str,
        content: str,
        message: str,
        branch: Optional[str] = None,
    ) -> str:
        """
        Create or update ``file_path`` in the repo and return the
        resulting commit SHA.

        Parameters
        ----------
        message : str
            Conventional-commit message, e.g.
            ``"fix(auth): patch XSS vulnerability in login form"``
        """
        return await asyncio.to_thread(
            self._commit_file_sync, repo_url, file_path, content, message, branch
        )

    # ── private sync implementations ─────────────────────

    def _get_repo(self, repo_url: str) -> Repository:
        owner, name = _parse_owner_repo(repo_url)
        return self._client.get_repo(f"{owner}/{name}")

    def _fetch_files_sync(
        self,
        repo_url: str,
        branch: Optional[str],
    ) -> List[FileContent]:
        repo = self._get_repo(repo_url)
        ref = branch or repo.default_branch

        ignore_spec = _build_gitignore_spec(repo)

        results: List[FileContent] = []
        stack: list[ContentFile] = list(repo.get_contents("", ref=ref))  # type: ignore[arg-type]

        while stack:
            item = stack.pop()

            # Skip always-ignored paths
            if any(part in _ALWAYS_SKIP for part in item.path.split("/")):
                continue

            # Skip .gitignore-matched paths
            if ignore_spec and ignore_spec.match_file(item.path):
                logger.debug("Skipped (gitignore): %s", item.path)
                continue

            if item.type == "dir":
                children = repo.get_contents(item.path, ref=ref)
                stack.extend(children)  # type: ignore[arg-type]
                continue

            # ── It's a file ──────────────────────────────
            if item.size and item.size > _MAX_FILE_BYTES:
                logger.debug("Skipped (too large: %d B): %s", item.size, item.path)
                continue

            try:
                raw = base64.b64decode(item.content) if item.content else b""
            except Exception:
                logger.warning("Decode error: %s", item.path)
                continue

            if not _is_text_decodable(raw):
                logger.debug("Skipped (binary): %s", item.path)
                continue

            results.append(
                FileContent(
                    path=item.path,
                    content=raw.decode("utf-8", errors="replace"),
                    size=item.size or len(raw),
                    sha=item.sha,
                )
            )

        logger.info(
            "Fetched %d text files from %s @ %s", len(results), repo_url, ref
        )
        return results

    def _commit_file_sync(
        self,
        repo_url: str,
        file_path: str,
        content: str,
        message: str,
        branch: Optional[str],
    ) -> str:
        repo = self._get_repo(repo_url)
        ref = branch or repo.default_branch

        # Ensure the message follows conventional-commit format
        if not re.match(r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(\(.+\))?:", message):
            message = f"fix(kritiq): {message}"

        try:
            # File already exists — update it
            existing: ContentFile = repo.get_contents(file_path, ref=ref)  # type: ignore[assignment]
            result = repo.update_file(
                path=file_path,
                message=message,
                content=content,
                sha=existing.sha,
                branch=ref,
            )
            commit_sha = result["commit"].sha
            logger.info("Updated %s → %s", file_path, commit_sha[:8])
        except GithubException as exc:
            if exc.status == 404:
                # File doesn't exist yet — create it
                result = repo.create_file(
                    path=file_path,
                    message=message,
                    content=content,
                    branch=ref,
                )
                commit_sha = result["commit"].sha
                logger.info("Created %s → %s", file_path, commit_sha[:8])
            else:
                raise

        return commit_sha


# ── Module-level singleton ───────────────────────────────

github_service = GitHubService()
