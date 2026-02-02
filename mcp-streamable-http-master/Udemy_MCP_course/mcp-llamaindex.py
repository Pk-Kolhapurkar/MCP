import asyncio
import os
from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.agent.workflow import ReActAgent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from llama_index.tools.mcp.base import McpToolSpec
from llama_index.core.memory import ChatMemoryBuffer

load_dotenv('D:/Botangelos/LlamaBug/.env')
print ("🤖 Loading environment variables...")
# === Azure OpenAI Config ===
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Initialize Azure OpenAI LLM
llm = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
)

# Initialize MCP tools
server_params = StdioServerParameters(
    command="npx",
    args=[
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "D:\Botangelos\LlamaBug\llamaMCP_project\servers\src", 
    ],
)

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

async def main():
    # Initialize the MCP client
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tool_spec = McpToolSpec(client=session)
            mcp_tools = await mcp_tool_spec.to_tool_list_async()
            
            ## Initialize the ReAct agent with tools and memory
            agent = ReActAgent(
                tools=mcp_tools,
                llm=llm,
                memory=memory
            )
            
            ## Chat loop
            print("🤖 Chatbot is ready! Type /exit to quit anytime.")
            while True:
                user_query = input("\nYou: ")
                if user_query.lower() == "/exit":
                    print("👋 Exiting chat!")
                    break
                
                response = await agent.run(user_query)
                print(f"AI: {response}")
                

if __name__ == "__main__":
    asyncio.run(main())