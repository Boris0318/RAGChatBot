import os
from llama_stack.distribution.library_client import LlamaStackAsLibraryClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client.types import Attachment
from termcolor import cprint
from dotenv import load_dotenv

load_dotenv()


# Initialize the LlamaStack client
# os.environ['TOGETHER_API_KEY'] = os.getenv('API_KEY')
os.environ['TOGETHER_API_KEY'] = '8c416c1d37fba4cd88428e8ba5a7f0cd4a599c22e8d3207eec3482fbed1f7d00'

client = LlamaStackAsLibraryClient("together")
_ = client.initialize()

# Define the model ID
model_id = "meta-llama/Llama-3.1-70B-Instruct"

# Define URLs for attachments
urls = ["chat.rst", "llama3.rst", "datasets.rst", "lora_finetune.rst"]
attachments = [
    Attachment(
        content=f"https://raw.githubusercontent.com/pytorch/torchtune/main/docs/source/tutorials/{url}",
        mime_type="text/plain",
    )
    for url in urls
]
user_prompt = [
    (
        "I am attaching documentation for Torchtune. Help me answer questions I will ask next.",
        attachments,
    ),
    (
        "What are the top 5 topics that were explained? Only list succinct bullet points.",
        None,
    ),
]

# Configure the RAG agent
agent_config = AgentConfig(
    model=model_id,
    instructions="You are a helpful assistant",
    tools=[{"type": "memory"}],  # Enable Memory (RAG)
    enable_session_persistence=False,
)

# Create the RAG agent
rag_agent = Agent(client, agent_config)
session_id = rag_agent.create_session("test-session")

def get_rag_responses(user_prompts):
    answerss = []
    for prompt, attachments in user_prompts:
        cprint(f'User> {prompt}', 'green')
        response = rag_agent.create_turn(
            messages=[{"role": "user", "content": prompt}],
            attachments=attachments,
            session_id=session_id,
        )
        for log in EventLogger().log(response):
            # answerss = log.print()
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
