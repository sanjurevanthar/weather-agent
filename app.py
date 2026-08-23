"""
Gradio front-end for the weather agent. Wraps build_agent() from
src.mcp_client so the same agent logic runs locally and on the Space.
"""
import asyncio
import gradio as gr
import spaces

from src.mcp_client import build_agent, load_hf_token


async def ask(question: str) -> str:
    hf_token = load_hf_token()
    agent = await build_agent(hf_token)
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    return response["messages"][-1].content

@spaces.GPU
def run(question: str) -> str:
    return asyncio.run(ask(question))


demo = gr.Interface(
    fn=run,
    inputs=gr.Textbox(
        label="Ask about the weather",
        placeholder="What's the weather in Chennai right now?",
    ),
    outputs=gr.Textbox(label="Agent's answer"),
    title="Revanth's Weather Agent",
    description="An MCP-powered agent that fetches live weather via Open-Meteo.",
)

if __name__ == "__main__":
    demo.launch()