## SECOND VERSION
import streamlit as st
from llama_stack_client.types import Attachment
from PyPDF2 import PdfReader
from RAG import get_rag_responses_url
from RAG import get_rag_responses_pdf
# Title of the app
st.title("RAG Model Chatbot")

# Add a header
st.header("Ask me anything!")

# Option for the user to choose between URL or PDF input
input_type = st.radio("Choose input type:", ('Web URL', 'PDF'))

# Text input for user prompt
user_prompt = st.text_input("Enter your question:")

if input_type == 'Web URL':
    # Text area for user to enter URLs (one per line)
    st.write("Enter one or more URLs (one per line):")
    url_input = st.text_area("URLs", height=100)
else:
    # File uploader for PDF
    st.write("Upload a PDF file:")
    # pdf_file = st.file_uploader("PDF", type="pdf")
    pdf_files = st.file_uploader("PDF", type="pdf", accept_multiple_files=True)

# Button to submit the prompt
if st.button("Submit"):
    if user_prompt:
        if input_type == 'Web URL' and url_input:
            # Split the URLs by newlines and strip any extra whitespace
            urls = [url.strip() for url in url_input.split("\n") if url.strip()]
            # Create attachments from the user-provided URLs
            attachments = [
                {
                    "content": f"{url_input}",
                    "mime_type": "text/plain",
                }
                for url in urls
            ]

            user_prompts = [
                (
                    f"I am attaching documentation from the provided URLs. Help me answer questions I will ask next. {user_prompt}",
                    attachments,
                )
            ]

            # Get the RAG response
            respond = get_rag_responses_url(user_prompts)

        elif input_type == 'PDF' and pdf_files is not None:
            # Read the PDF file
            # pdf_content = pdf_file.read()
            # Create attachments from the uploaded PDF
            # attachments = [
            #     {
            #         "content": pdf_content,
            #         "mime_type": "application/pdf",
            #     }
            # ]
            attachments = [
                Attachment(
                    content=" ".join(PdfReader(file_path).pages[i].extract_text() for i in range(len(PdfReader(file_path).pages))),
                    mime_type="text/plain"
                )
                for file_path in pdf_files
            ]

            user_prompts = [
                (
                    f"I am attaching a PDF document. Help me answer questions I will ask next. {user_prompt}",
                    attachments,
                )
            ]

            # Get the RAG response
            respond = get_rag_responses_pdf(user_prompts)

        else:
            st.warning("Please provide the necessary input based on your selection.")
            respond = []

        if respond:
            st.write("### Response:")
            st.write(respond)
    else:
        st.warning("Please enter a question.")  
                