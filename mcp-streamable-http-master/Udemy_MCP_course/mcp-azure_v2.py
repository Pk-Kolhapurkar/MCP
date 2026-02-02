import os
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv('/Users/kshitijjoy_1/opemai-test/.env')
async def run(mcp_server: MCPServerStdio):
    agent = Agent(
        name="Assistant", model="gpt-4o-mini" ,
        instructions="You are a helpful assistant. Use the available tools to answer the user's questions.",
        mcp_servers=[mcp_server]
    )

    conversation_history = []  # List to store the conversation history

    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ["exit", "quit"]:
            print("👋 Exiting chat!")
            break

        # Add the user's query to the conversation history
        conversation_history.append({"role": "user", "content": user_query})

        # Prepare the last three conversations as input
        last_three_conversations = conversation_history[-6:]  # Last 3 exchanges (user + assistant)

        # Format the input for the Runner
        formatted_input = "\n".join(
            f"{entry['role'].capitalize()}: {entry['content']}" for entry in last_three_conversations
        )

        # Get AI response
        result = await Runner.run(starting_agent=agent, input=formatted_input)
        conversation_history.append({"role": "assistant", "content": result.final_output})
        
        print(f"AI: {result.final_output}")

async def main():
    async with MCPServerStdio(
        name="Azure MCP Server",
        params={"command": "npx", "args": ["-y", "@azure/mcp@latest", "server", "start"]},
    ) as mcp_server:
        await run(mcp_server)

if __name__ == "__main__":
    asyncio.run(main())