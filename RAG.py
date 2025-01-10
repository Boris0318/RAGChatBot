import os
from llama_stack.distribution.library_client import LlamaStackAsLibraryClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client.types import Attachment
from termcolor import cprint
# from dotenv import load_dotenv

# load_dotenv()

def initialize_client(api_key):
    os.environ['TOGETHER_API_KEY'] = api_key  # Set the API key from the user input
    client = LlamaStackAsLibraryClient("together")
    initialize_client = client.initialize()
    # _ = client.initialize()
    return initialize_client

model_id = "meta-llama/Llama-3.1-70B-Instruct"

def create_rag_agent(client):
    agent_config = AgentConfig(
        model=model_id,
        instructions="You are a helpful assistant",
        tools=[{"type": "memory"}],  # Enable Memory (RAG)
        enable_session_persistence=False,
    )
    rag_agent = Agent(client, agent_config)
    session_id = rag_agent.create_session("test-session")
    return rag_agent, session_id

def get_rag_responses(user_prompts, api_key):
    client = initialize_client(api_key)  # Initialize the client with the user's API key
    rag_agent, session_id = create_rag_agent(client)  # Create the RAG agent

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
