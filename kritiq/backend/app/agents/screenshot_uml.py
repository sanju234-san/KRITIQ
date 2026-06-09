"""
ScreenshotUMLAgent — Captures live page screenshots and generates codebase UML diagrams.
"""

from __future__ import annotations

import base64
import logging
import os
import re
import subprocess
import time
from typing import Any, List, Optional

import httpx
from playwright.async_api import async_playwright
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import BaseAgent, LangGraphState
from app.core.config import settings
from app.core.retry import retry_async

logger = logging.getLogger("kritiq.agents.ScreenshotUMLAgent")

_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
_TEMPERATURE = 0.1
_MAX_TOKENS = 2048

_UML_SYSTEM_PROMPT = """\
You are KRITIQ, an expert system architect.
Analyze the codebase structure (files and paths) provided by the user and generate a Mermaid flowchart mapping out the system's layout, directory relationships, and main execution paths.

You must return ONLY valid Mermaid syntax starting with either:
  flowchart TD
  flowchart LR
  graph TD
  graph LR

Rules:
  - Do NOT wrap the Mermaid syntax in markdown code fences or any other wrapping text.
  - Do NOT add explanations or comments outside the Mermaid code.
"""


class ScreenshotUMLAgent(BaseAgent):
    """
    Agent that captures webpage screenshots of a live deployment URL and
    generates codebase UML architecture diagrams using Mermaid rendering.
    """

    def __init__(self) -> None:
        super().__init__()
        self._llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=_MODEL,
            temperature=_TEMPERATURE,
            max_tokens=_MAX_TOKENS,
        )

    async def run(self, state: LangGraphState) -> LangGraphState:
        """Execute the screenshot capture and UML generation tasks."""
        self._log_start(state)

        # ── 1. Capture live URL screenshot ───────────────────
        # Retrieve live URL (check both direct state key and files homepages)
        live_url = state.get("live_url")
        if not live_url:
            # Fallback to repo or generic file structure metadata if possible
            files = state.get("files") or []
            for f in files:
                if f.get("path") == "package.json" or f.get("path") == "backend/app/main.py":
                    # Check settings homepage or dummy URLs
                    pass

        screenshot_path = await self.capture_screenshot(live_url)
        screenshot_paths = list(state.get("screenshot_paths") or [])
        if screenshot_path:
            screenshot_paths.append(screenshot_path)

        # ── 2. Generate and render Mermaid UML diagram ───────
        uml_path = None
        mermaid_code = await self.generate_mermaid(state)
        if mermaid_code:
            uml_path = await self.render_mermaid_cli(mermaid_code)

        self._log_done("UML & Screenshot files", 1 if uml_path or screenshot_path else 0)

        return {
            **state,
            "screenshot_paths": screenshot_paths,
            "uml_path": uml_path,
        }

    async def capture_screenshot(self, live_url: Optional[str]) -> Optional[str]:
        """Capture webpage using Playwright headless Chromium."""
        if not live_url:
            self.logger.info("No live URL provided — skipping screenshot.")
            return None

        self.logger.info("Capturing screenshot of: %s", live_url)
        os.makedirs("temp/screenshots", exist_ok=True)
        filename = f"temp/screenshots/screenshot_{int(time.time())}.png"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                # Set viewport size for clean visual layout
                await page.set_viewport_size({"width": 1280, "height": 800})
                await page.goto(live_url, timeout=30000, wait_until="networkidle")
                await page.screenshot(path=filename, full_page=True)
                await browser.close()
            self.logger.info("Screenshot successfully saved to %s", filename)
            return filename
        except Exception as exc:
            self.logger.error("Failed to capture webpage screenshot: %s", exc)
            return None

    @retry_async()
    async def generate_mermaid(self, state: LangGraphState) -> Optional[str]:
        """Query LLM to generate Mermaid flowchart code for file architecture."""
        files = state.get("files") or []
        if not files:
            self.logger.warning("No files found in state — skipping UML generation.")
            return None

        # Build list of file paths to send to the LLM
        file_paths = [f.get("path", "unknown") for f in files]
        file_structure = "\n".join(file_paths)

        user_prompt = f"Codebase File Structure:\n{file_structure}"
        messages = [
            SystemMessage(content=_UML_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            raw_text: str = response.content  # type: ignore[assignment]
            return self._clean_mermaid_code(raw_text)
        except Exception as exc:
            self.logger.error("LLM call failed for Mermaid diagram generation: %s", exc)
            return None

    def _clean_mermaid_code(self, text: str) -> str:
        """Strip markdown wraps and ensure Mermaid diagram starts correctly."""
        cleaned = text.strip()
        if "```" in cleaned:
            m = re.search(r"```(?:mermaid)?\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL)
            if m:
                cleaned = m.group(1).strip()

        # Enforce starts with flowchart or graph
        if not (cleaned.startswith("flowchart") or cleaned.startswith("graph")):
            cleaned = "flowchart TD\n" + cleaned

        return cleaned

    async def render_mermaid_cli(self, mermaid_code: str) -> Optional[str]:
        """Render Mermaid flowchart to PNG via mmdc subprocess with HTTP fallback."""
        os.makedirs("temp/uml", exist_ok=True)
        mmd_path = "temp/uml/uml.mmd"
        png_path = "temp/uml/uml.png"

        # Save raw Mermaid source
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(mermaid_code)

        try:
            # Call mmdc command
            subprocess.run(
                ["mmdc", "-i", mmd_path, "-o", png_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,
            )
            self.logger.info("Mermaid diagram successfully rendered via mmdc to %s", png_path)
            return png_path
        except Exception as exc:
            self.logger.warning(
                "mmdc subprocess call failed (%s). Falling back to mermaid.ink HTTP API...",
                exc,
            )
            return await self._render_mermaid_api_fallback(mermaid_code, png_path)

    async def _render_mermaid_api_fallback(self, mermaid_code: str, png_path: str) -> Optional[str]:
        """Download rendered PNG from mermaid.ink API."""
        try:
            # Base64 encode the flowchart text
            encoded_code = base64.b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
            url = f"https://mermaid.ink/img/{encoded_code}"

            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=15)
                if resp.status_code == 200:
                    with open(png_path, "wb") as f:
                        f.write(resp.content)
                    self.logger.info("Mermaid diagram successfully rendered via mermaid.ink to %s", png_path)
                    return png_path
                else:
                    self.logger.warning("mermaid.ink API returned non-200 status code: %d", resp.status_code)
        except Exception as exc:
            self.logger.error("Failed to render Mermaid diagram via HTTP fallback API: %s", exc)

        # Fallback to local .mmd text path if all rendering fails
        return "temp/uml/uml.mmd"
