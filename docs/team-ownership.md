# Team Ownership Matrix

This document outlines the clear boundaries and expectations for each team member during implementation.

## 1. Member 1 — Dev (Frontend & API Integration)
* **Domain**: `kritiq-frontend/`
* **Responsibilities**:
  * Implement the React.js SPA pages and components.
  * Connect views using Axios to call backend APIs.
  * Integrate Monaco Editor for reading/editing files on-screen.
  * Implement frontend state management (AuthContext).
  * Design screens according to Tailwind CSS standards.

## 2. Member 2 — Sayeed (Backend & Database)
* **Domain**: `kritiq-backend/app/`
* **Responsibilities**:
  * Set up FastAPI base routing and dependency injection.
  * Implement JWT verification, user registration, and security logic.
  * Write MongoDB database repositories using PyMongo/document patterns.
  * Ensure correct request/response validations using Pydantic models.
  * Handle configuration, settings loading, and standard error handling.

## 3. Member 3 — Sanjeevni (AI Agent & Developer Tools)
* **Domain**: `kritiq-backend/` outside of `app/` (specifically: `ai_agent/`, `mcp_server/`, `rag_pipeline/`, `dataset/`, `repo_integration/`, `cli/`)
* **Responsibilities**:
  * Write the Gemini API client interface and manage review/translation/explanation prompts.
  * Build the Model Context Protocol (MCP) server for querying files/definitions.
  * Build the dataset retrieval RAG system (embeddings model integration and retriever).
  * Implement repository utility functions using GitPython/GitHub APIs.
  * Develop the CLI utility using Typer.
