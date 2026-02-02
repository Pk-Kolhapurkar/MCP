from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


async def create_agent():
  """Gets tools from MCP Server."""
  tools, exit_stack = await MCPToolset.from_server(
      connection_params=StdioServerParameters(
      command="npx",
      args=[
        "mcp-remote",
        "https://mcp.paypal.com/sse"
      ]
    )
  )

  agent = LlmAgent(
      model='gemini-2.0-flash',
      name='paypal_assistant',
      instruction=(
          'You are a Paypal assistant that makes use of the Paylal MCP tools. '
          'You can answer questions about PayPal, help with transactions, and provide information about PayPal services. '
          'You can use the tools provided to you. '
      ),
      tools=tools,
  )
  return agent, exit_stack


root_agent = create_agent()