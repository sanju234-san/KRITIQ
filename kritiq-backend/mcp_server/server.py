import asyncio
import sys
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp_server.tools import list_local_files, list_github_repo_files

# Initialize the MCP Server
app = Server("kritiq-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="list_local_files",
            description="List files and directories inside a local filesystem directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The local directory path to list. Defaults to the current directory ('.').",
                        "default": "."
                    }
                }
            }
        ),
        Tool(
            name="list_github_repo_files",
            description="List files and directories at a given path inside a public GitHub repository, using the GitHub REST API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "The GitHub username or organisation that owns the repository (e.g. 'octocat')."
                    },
                    "repo": {
                        "type": "string",
                        "description": "The name of the repository (e.g. 'Hello-World')."
                    },
                    "path": {
                        "type": "string",
                        "description": "The path inside the repository to list. Defaults to the root ('').",
                        "default": ""
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        Tool(
            name="review_code",
            description="Review source code for bugs, security vulnerabilities, and code smells using Kritiq's Gemini + RAG + MCP pipeline.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Source code to review."},
                    "language": {"type": "string", "description": "Programming language (e.g. python, javascript, java).", "default": "python"},
                    "file_path": {"type": "string", "description": "Optional file path for sibling context."},
                    "repo_owner": {"type": "string", "description": "Optional GitHub repo owner."},
                    "repo_name": {"type": "string", "description": "Optional GitHub repo name."}
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="translate_code",
            description="Translate source code from one programming language to another using Kritiq's Gemini + RAG pipeline.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Source code to translate."},
                    "source_language": {"type": "string", "description": "Source language (e.g. python).", "default": "python"},
                    "target_language": {"type": "string", "description": "Target language (e.g. java, go, typescript)."},
                    "file_path": {"type": "string", "description": "Optional file path for context."}
                },
                "required": ["code", "target_language"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution requests."""
    if name == "list_local_files":
        directory = arguments.get("directory", ".")
        files = list_local_files(directory)
        return [TextContent(type="text", text="\n".join(files))]

    if name == "list_github_repo_files":
        owner = arguments["owner"]
        repo = arguments["repo"]
        path = arguments.get("path", "")
        files = list_github_repo_files(owner, repo, path)
        return [TextContent(type="text", text="\n".join(files))]

    if name == "review_code":
        import anyio
        from ai_agent.review_service import review_code
        result = await anyio.to_thread.run_sync(
            review_code,
            arguments["code"],
            arguments.get("language", "python"),
            arguments.get("file_path"),
            arguments.get("repo_owner"),
            arguments.get("repo_name"),
        )
        return [TextContent(type="text", text=str(result))]

    if name == "translate_code":
        import anyio
        from ai_agent.translation_service import translate_code
        result = await anyio.to_thread.run_sync(
            translate_code,
            arguments["code"],
            arguments.get("source_language", "python"),
            arguments["target_language"],
            arguments.get("file_path"),
        )
        return [TextContent(type="text", text=str(result))]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def create_mcp_sse_app():
    """Creates a Starlette ASGI app exposing this MCP server over SSE (/sse & /messages/)."""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.responses import Response

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
        return Response()

    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=sse.handle_post_message),
        ]
    )

if __name__ == "__main__":
    print("Starting MCP server...", file=sys.stderr)
    asyncio.run(main())
