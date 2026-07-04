# Kritiq Backend & AI Services

This directory contains the FastAPI app (Application/Data Layer) and the AI/MCP/RAG system logic.

## Ownership Split

### Sayeed (`app/`)
* **Core API Routing**: Auth, Reviews, Translation, Explanations, History.
* **Database Repositories**: Users, repos, reviews, translations, activity history.
* **Security**: Password hashing, JWT token creation, token dependencies.
* **Application Core**: Config files and error handlers.

### Sanjeevni (`ai_agent/`, `mcp_server/`, `rag_pipeline/`, `dataset/`, `repo_integration/`, `cli/`, `tests/`)
* **AI Agent & Prompting**: Gemini client, review/translation/explanation services, prompts.
* **Model Context Protocol (MCP)**: Server, tools, GitHub client connection.
* **RAG Pipeline**: Vector embeddings client, RAG retriever/formatter.
* **Dataset**: Dataset builder, JSON schema, category documents.
* **Repo Integration**: Local repository cloning with GitPython and GitHub REST API calls.
* **CLI**: Command Line Tool built on Typer.
* **Tests**: Test suites for all layers.
