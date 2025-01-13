import os
from llama_stack.distribution.library_client import LlamaStackAsLibraryClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client.types import Attachment
from termcolor import cprint
import toml
import streamlit as st

# from dotenv import load_dotenv
# with open(".streamlit/secrets.toml", "r") as f:
#     secrets = toml.load(f)
# os.environ['TOGETHER_API_KEY'] = secrets["TOGETHER_API_KEY"]
os.environ['TOGETHER_API_KEY'] = st.secrets["TOGETHER_API_KEY"]
model_id = "meta-llama/Llama-3.1-70B-Instruct"
# load_dotenv()

# def get_rag_responses(user_prompts, api_key):
def get_rag_responses(user_prompts):
    # os.environ['TOGETHER_API_KEY'] = api_key  # Set the API key from the user input
    # client = LlamaStackAsLibraryClient("together")
    # client = LlamaStackAsLibraryClient("/Library/anaconda3/lib/python3.12/site-packages/llama_stack/templates/together/run.yaml")
    client = LlamaStackAsLibraryClient("build/together/run.yaml")
    # _ = client.initialize()
    client.initialize()

    agent_config = AgentConfig(
        model=model_id,
        instructions="You are a helpful assistant",
        tools=[{"type": "memory"}],  # Enable Memory (RAG)
        enable_session_persistence=False,
    )
    rag_agent = Agent(client, agent_config)
    session_id = rag_agent.create_session("test-session")

    answerss = []
    for prompt, attachments in user_prompts:
        cprint(f'User> {prompt}', 'green')
        response = rag_agent.create_turn(
            messages=[{"role": "user", "content": prompt}],
            attachments=attachments,
            session_id=session_id,
        )
        for log in EventLogger().log(response):
            response_str = str(log)
            response_str = "\n".join(line for line in response_str.split("\n") if not line.startswith(("memory_retrieval", "inference")))
            answerss.append(response_str)
    return answerss


# def get_rag_responses(user_prompts):
#     for prompt, attachment in user_prompts:
#         response = rag_agent.create_turn(
#             messages=[{"role": "user", "content": prompt}],
#             attachments=attachments,
#             session_id=session_id,
#     )
#     for log in EventLogger().log(response):
#         log.print()
