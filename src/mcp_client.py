"""
Client connects to the weather MCP server and answers a question
using a Hugging Face-hosted chat model with tool calling.
"""
import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from src.constants import HF_MODEL_REPO
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_mcp_adapters.client import MultiServerMCPClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_hf_token() -> str:
    load_dotenv()
    token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise RuntimeError(
            "HUGGINGFACEHUB_API_TOKEN is not set. Add it to your .env file."
        )
    return token


async def build_agent(hf_token: str):
    client = MultiServerMCPClient(
        {
            "weather": {
                "command": "uv",
                "args": ["run", "-m", "src.mcp_server"],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()
    logger.info("Tools found: %s", [t.name for t in tools])

    llm = HuggingFaceEndpoint(
        repo_id=HF_MODEL_REPO,
        task="text-generation",
        max_new_tokens=512,
        huggingfacehub_api_token=hf_token,
    )
    chat_model = ChatHuggingFace(llm=llm)
    return create_agent(chat_model, tools)


async def main():
    hf_token = load_hf_token()
    agent = await build_agent(hf_token)

    response = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "What's the weather in Chennai right now?"}
            ]
        }
    )
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())