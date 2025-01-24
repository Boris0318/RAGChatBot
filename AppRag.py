## SECOND VERSION
import streamlit as st
import datetime
from streamlit_gsheets import GSheetsConnection
from llama_stack_client.types import Attachment
from PyPDF2 import PdfReader
from RAG import get_rag_responses_url
from RAG import get_rag_responses_pdf

               
conn = st.connection("gsheets", type=GSheetsConnection)



# Print results.

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'input_submitted' not in st.session_state:
    st.session_state.input_submitted = False
if 'current_input_type' not in st.session_state:
    st.session_state.current_input_type = None
if 'url_input' not in st.session_state:
    st.session_state.url_input = None
if 'pdf_files' not in st.session_state:
    st.session_state.pdf_files = None


def add_files_to_sheet(user_id, files,query):
    # Read the existing data from the sheet
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet = "Files", usecols = list(range(4)),ttl=0)
    called_at = datetime.datetime.now()
    # df = conn.read(usecols = list(range(3)),ttl=5)
    df.loc[len(df)] = [user_id, files,query, called_at]
    conn.update(data= df)


def add_queries_to_sheet(user_id,files ,query):
    # df = conn.read(spreadsheet = "Queries")
    df = conn.read(usecols = list(range(3)))
    df.loc[len(df)] = [user_id, files,query]
    # df.loc[len(df)] = ["hello", 69]

    # conn.update(spreadsheet = "Queries", data= df)
    conn.update(data= df)

# Title of the app
st.title("RAG Model Chatbot")

with st.expander("ℹ️ How to use this chatbot"):
    st.write("""
    This chatbot can answer questions based on either web content or PDF documents you provide. 
    It's main purpose is to summrarize or find key information.
     Here's how to use it:
    
    1. **Choose your input type:**
        * **Web URL**: Enter a URL containing the content you want to ask about
        * **PDF**: Upload PDF files that contain the information you need
        
    2. **Ask your question:**
        * Type your question in the text box
        * Click 'Submit' to get your answer
             
    3. **Follow up the conversation! :**
        * Ask more questions about the file
        * Click on 'Send' to submit your new questions""")
# Initial setup (only shown before first submission)
if not st.session_state.input_submitted:
    st.header("Ask me anything!")
    
    # Option for the user to choose between URL or PDF input
    input_type = st.radio("Choose input type:", ('Web URL', 'PDF'))
    
    if input_type == 'Web URL':
        st.write("Enter one or more URLs (one per line):")
        url_input = st.text_area("URLs", height=100)
    else:
        st.write("Upload a PDF file:")
        pdf_files = st.file_uploader("PDF", type="pdf", accept_multiple_files=True)

    # Initial question
    user_prompt = st.text_input("Enter your question:")

    if st.button("Submit"):
        if user_prompt:
            # add_queries_to_sheet(st.session_state.session_id, user_prompt)
            if (input_type == 'Web URL' and url_input) or (input_type == 'PDF' and pdf_files is not None):
                # Store the input type and data
                st.session_state.current_input_type = input_type
                if input_type == 'Web URL':
                    st.session_state.url_input = url_input
                else:
                    st.session_state.pdf_files = pdf_files
                
                # Process the initial prompt
                if input_type == 'Web URL':
                    
                    urls = [url.strip() for url in url_input.split("\n") if url.strip()]
                    attachments = [{"content": url, "mime_type": "text/plain"} for url in urls]
                    user_prompts = [(f"I am attaching documentation from the provided URLs. Help me answer questions I will ask next. {user_prompt}", attachments)]
                    respond, session_id = get_rag_responses_url(user_prompts)
                    add_files_to_sheet(session_id, url_input,user_prompt)
                else:
                    
                    attachments = [Attachment(
                        content=" ".join(PdfReader(file_path).pages[i].extract_text() for i in range(len(PdfReader(file_path).pages))),
                        mime_type="text/plain"
                    ) for file_path in pdf_files]
                    user_prompts = [(f"I am attaching a PDF document. Help me answer questions I will ask next. {user_prompt}", attachments)]
                    respond, session_id = get_rag_responses_pdf(user_prompts)
                    add_files_to_sheet(st.session_state.session_id, pdf_files[0],user_prompt)

                if respond:
                    st.session_state.conversation_history.append(f"**👤 User:** {user_prompt}")
                    st.session_state.conversation_history.append(f"**🤖 Assistant:** {respond}")
                    st.session_state.input_submitted = True
                    st.rerun()
            else:
                st.warning("Please provide the necessary input based on your selection.")
        else:
            st.warning("Please enter a question.")

# After initial submission, show only conversation interface
else:
    # Display conversation history
    st.subheader("Conversation History:")
    for message in st.session_state.conversation_history:
        # st.write(message)
        st.markdown(message)

    # Single text input for continuing conversation
    new_prompt = st.text_input("Make another question:", key="continue_chat")
    
    if st.button("Send"):
        if new_prompt:
            # add_files_to_sheet(st.session_state.session_id, st.session_state.url_input ,new_prompt)
            if st.session_state.current_input_type == 'Web URL':
                
                urls = [url.strip() for url in st.session_state.url_input.split("\n") if url.strip()]
                attachments = [{"content": url, "mime_type": "text/plain"} for url in urls]
                user_prompts = [(f"Based on our previous conversation: {new_prompt}", attachments)]
                respond, session_id = get_rag_responses_url(user_prompts)
                add_files_to_sheet(session_id, st.session_state.url_input ,new_prompt)
            else:
                
                attachments = [Attachment(
                    content=" ".join(PdfReader(file_path).pages[i].extract_text() for i in range(len(PdfReader(file_path).pages))),
                    mime_type="text/plain"
                ) for file_path in st.session_state.pdf_files]
                user_prompts = [(f"Based on our previous conversation: {new_prompt}", attachments)]
                respond, session_id = get_rag_responses_pdf(user_prompts)
                add_files_to_sheet(session_id, st.session_state.pdf_files ,new_prompt)

            if respond:
                st.session_state.conversation_history.append(f"**👤 User:** {new_prompt}")
                st.session_state.conversation_history.append(f"**🤖 Assistant:** {respond}")
                st.rerun()

    # Add a clear conversation button
    if st.button("Start New Chat"):
        # Reset all session state
        if 'rag_agent' in st.session_state:
            del st.session_state.rag_agent
        if 'session_id' in st.session_state:
            del st.session_state.session_id
        st.session_state.conversation_history = []
        st.session_state.input_submitted = False
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()