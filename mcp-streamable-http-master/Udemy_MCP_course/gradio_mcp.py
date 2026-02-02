import gradio as gr
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
import time, sys, dotenv, asyncio, threading, os


original_stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

# Load environment variables
dotenv.load_dotenv()


# Setup

model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")


server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/kshitijjoy_1/gradio-mcp"]
)

# Global variables
agent = None
loop = None
loop_ready = False
chat_history = InMemoryChatMessageHistory()

def start_background_loop():
    """Start background event loop"""
    global loop, loop_ready
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop_ready = True
    loop.run_forever()

async def setup_agent():
    """Initialize the agent"""
    global agent
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            print("Agent ready!")
            
            # Keep the connection alive
            await asyncio.Event().wait()

def chat(message, history):
    """Handle chat messages"""
    if not agent:
        return "Agent not ready yet!"
    
    try:
        # Add the user message to history
        chat_history.add_message(HumanMessage(content=message))
        
        future = asyncio.run_coroutine_threadsafe(
            agent.ainvoke({"messages": chat_history.messages}),
            loop
        )
        response = future.result(timeout=30)
        
        # Get the AI's response and add it to history
        ai_response = response["messages"][-1].content
        chat_history.add_message(response["messages"][-1])
        
        return ai_response
        
    except Exception as e:
        return f"Error: {str(e)}"

# Create chat interface
#demo = gr.ChatInterface(
#   title="File Assistant",
##    fn=chat,
#    description="Ask questions about your files",
#    type="messages"
#)

#demo=gr.Image(value="/Users/kshitijjoy_1/Documents/gradio_img.png", label="MCP-Gradio", show_label=False, height=200)  # <-- path to your image

demo = gr.Blocks()
with demo:
    gr.Image(value="/Users/kshitijjoy_1/Documents/gradio_img.png", label="MCP-Gradio", show_label=False, height=200)  # <-- path to your image
    gr.ChatInterface(
        title="📁 File Assistant",
        fn=chat,
        description="Ask questions about your files",
        type="messages"
    )

if __name__ == "__main__":
    print("Starting background loop...")
    loop_thread = threading.Thread(target=start_background_loop, daemon=True)
    loop_thread.start()
    while not loop_ready:
        time.sleep(0.1)
    asyncio.run_coroutine_threadsafe(setup_agent(), loop)
    time.sleep(3)
    demo.launch(server_port=7860)