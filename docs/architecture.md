# System Architecture

Kritiq follows a layered architectural pattern to keep components decoupled, allowing individual layers to scale or be updated independently.

## Components Flow

```
[Presentation Layer]
   ├── React Web App (Dev)
   └── Typer CLI (Sanjeevni)
           │
           ▼
[Application Layer] (FastAPI Backend - Sayeed)
   ├── Routes, Authentication (JWT)
   └── Persistence Orchestration (MongoDB Atlas)
           │
           ▼
[AI, RAG, & Context Layer] (AI Services - Sanjeevni)
   ├── Gemini AI Agent & Prompt Engineering
   ├── MCP Server (Repository Access)
   └── RAG Pipeline (Custom Review Database)
```

## Description of Layers

1. **Presentation Layer**: Handles user interaction.
   * Web Frontend: Built with React.js, Tailwind CSS, Monaco Editor, and Axios.
   * Command Line Interface (CLI): Built with Python and Typer. Shares the backend REST endpoints.
2. **Application Layer**: Exposed as FastAPI endpoints. Handled in `kritiq-backend/app/`. Validates inputs using Pydantic, controls user sessions (JWT), and communicates with MongoDB Atlas.
3. **AI & Context Layer**: Performs the core reasoning. Handled in `kritiq-backend/ai_agent/`, `mcp_server/`, and `rag_pipeline/`. Coordinates retrieval of project files and dataset-driven examples to construct highly grounded prompts for the Gemini API.
