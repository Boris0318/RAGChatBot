import os
from llama_stack.distribution.library_client import LlamaStackAsLibraryClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client.types import Attachment
from termcolor import cprint
import streamlit as st
from PyPDF2 import PdfReader
import io
import sys

api_key = st.secrets["TOGETHER_API_KEY"]
os.environ['TOGETHER_API_KEY'] = api_key
model_id = "meta-llama/Llama-3.1-70B-Instruct"
# load_dotenv()
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
def get_rag_responses_url(user_prompts):

    # client = LlamaStackAsLibraryClient("build/together/run.yaml")
    # # _ = client.initialize()
    # client.initialize()

    # agent_config = AgentConfig(
    #     model=model_id,
    #     instructions="You are a helpful assistant",
    #     tools=[{"type": "memory"}],  # Enable Memory (RAG)
    #     enable_session_persistence=False,
    # )
    # rag_agent = Agent(client, agent_config)
    # session_id = rag_agent.create_session("test-session")

    # answerss = []
    output_capture = io.StringIO()
    for prompt, attachments in user_prompts:
        cprint(f'User> {prompt}', 'green')
        response = rag_agent.create_turn(
            messages=[{"role": "user", "content": prompt}],
            attachments=attachments,
            session_id=session_id,
        )
        for log in EventLogger().log(response):
            # response_str = str(log)
            # response_str = "\n".join(line for line in response_str.split("\n") if not line.startswith(("memory_retrieval", "inference")))
            # answerss.append(response_str)
            original_stdout = sys.stdout  # Save the original sys.stdout
            sys.stdout = output_capture
            try:
                log.print() 
            finally:
                sys.stdout = original_stdout


    captured_output = output_capture.getvalue()

    first_newline_index = captured_output.find("\n")

    # If a newline exists, remove the first line
    if first_newline_index != -1:
        # Remove the first line
        captured_output = captured_output[first_newline_index + 1:]

        # Remove "inference>" from the beginning of the second line
        # if captured_output.startswith("inference>"):
        #     captured_output = captured_output[len("inference>"):].lstrip()
        if captured_output.startswith("inference>"):
            captured_output = captured_output[10:]

        # captured_output = remaining_output
        cleaned_output = captured_output
    else:
        # If there's no newline, return the output as is
        cleaned_output = captured_output

    # Join the lines back together
    return cleaned_output
    # lines = captured_output.splitlines()
    # cleaned_output = "\n".join(lines[2:])
    # return cleaned_output
    # return answerss

def get_rag_responses_pdf(user_prompts):
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

    # answerss = []
    
    output_capture = io.StringIO()
    for prompt, attachments in user_prompts:
        cprint(f'User> {prompt}', 'green')
        response = rag_agent.create_turn(
            messages=[{"role": "user", "content": prompt}],
            attachments=attachments,
            session_id=session_id,
        )
        for log in EventLogger().log(response):
            # response_str = str(log)
            # response_str = "\n".join(line for line in response_str.split("\n") if not line.startswith(("memory_retrieval", "inference")))
            # answerss.append(response_str)
            original_stdout = sys.stdout  # Save the original sys.stdout
            sys.stdout = output_capture
            try:
                log.print() 
            finally:
                sys.stdout = original_stdout
    captured_output = output_capture.getvalue()

    first_newline_index = captured_output.find("\n")
    # If a newline exists, remove the first line and the "inference>" prefix from the second line
    if first_newline_index != -1:
        # Remove the first line
        captured_output = captured_output[first_newline_index + 1:]

        # Remove "inference>" from the beginning of the second line
        # if captured_output.startswith("inference>"):
        #     captured_output = captured_output[len("inference>"):].lstrip()
        if captured_output.startswith("inference>"):
            captured_output = captured_output[10:]

        cleaned_output = captured_output
    else:
        # If there's no newline, return the output as is
        cleaned_output = captured_output


    # cleaned_output = re.sub(r"memory_retrieval>.*?inference>", "", captured_output_cleaned)
    # Optionally, clean any extra spaces or newlines
    # cleaned_output = " ".join(cleaned_output.split())
    # lines = captured_output.splitlines()
    # cleaned_output = "\n".join(lines[2:])
    return cleaned_output


