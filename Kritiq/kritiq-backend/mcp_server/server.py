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

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    print("Starting MCP server...", file=sys.stderr)
    asyncio.run(main())
