# Kritiq — AI-Powered Code Review and Cross-Language Code Translation Agent

Kritiq is an AI-powered developer assistant designed to automate code review and cross-language code translation. It retrieves project context using a Model Context Protocol (MCP) server and couples it with a curated RAG (Retrieval-Augmented Generation) pipeline using Google Gemini API.

## Repository Layout & Component Division

The project is split into two major sub-projects:
1. `kritiq-frontend/` - React-based Single Page Application (SPA).
2. `kritiq-backend/` - FastAPI backend, AI services, MCP server, RAG pipelines, and database utilities.

### Team Ownership

| Team Member | Domain / Ownership | Primary Directories |
| :--- | :--- | :--- |
| **Dev** | Frontend & API Integration | `kritiq-frontend/` |
| **Sayeed** | Backend & Database Core | `kritiq-backend/app/` |
| **Sanjeevni** | AI Agent, MCP Server, RAG Pipeline, Dataset & Developer Tools (CLI) | `kritiq-backend/{ai_agent, mcp_server, rag_pipeline, dataset, repo_integration, cli}/` |

---

## High-Level Workflow

1. User interacts via **React Web App** or **CLI**.
2. **FastAPI Backend** handles auth, validates request, and coordinates workflow.
3. Backend fetches repository context via **MCP Server** and retrieves matching review examples using the **RAG Pipeline**.
4. Context & reference examples are combined into structured prompts and sent to the **Google Gemini API**.
5. The review or translation is returned to the user and persisted in **MongoDB Atlas**.

Refer to [docs/architecture.md](docs/architecture.md) for more details.
