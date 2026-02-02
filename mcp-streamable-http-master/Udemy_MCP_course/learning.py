from mcp.server.fastmcp import FastMCP  # Import FastMCP, the quickstart server base

mcp = FastMCP("Learning Info Server")  # Initialize an MCP server instance with a descriptive name

@mcp.tool()
def what_am_i_learning() -> str:
    """Responds with what the user is learning."""
    return "You are learning MCP Beginner to Pro with Kshitij Joy."

if __name__ == "__main__":
    mcp.run(transport="stdio")  # Run the server, using standard input/output for communication
