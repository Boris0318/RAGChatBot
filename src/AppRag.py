import streamlit as st
from src.RAG import get_rag_responses

# Title of the app
st.title("RAG Model Chatbot")

# Add a header
st.header("Ask me anything!")

# Text input for user prompt
user_prompt = st.text_input("Enter your question:")

# Text area for user to enter URLs (one per line)
st.write("Enter one or more URLs (one per line):")
url_input = st.text_area("URLs", height=100)

# Button to submit the prompt
if st.button("Submit"):
    if user_prompt and url_input:
        # Split the URLs by newlines and strip any extra whitespace
        urls = [url.strip() for url in url_input.split("\n") if url.strip()]

        # Create attachments from the user-provided URLs
        attachments = [
            {
                "content": f"https://raw.githubusercontent.com/pytorch/torchtune/main/docs/source/tutorials/{url}",
                "mime_type": "text/plain",
            }
            for url in urls
        ]

        # Define the user prompts with the dynamic attachments
        user_prompts = [
            (
                "I am attaching documentation from the provided URLs. Help me answer questions I will ask next.",
                attachments,
            ),
            (
                user_prompt,  # Use the user's question here
                None,
            ),
        ]

        # Get the RAG response
        # response = get_rag_responses(user_prompts)
        respond = get_rag_responses(user_prompts)
        sentences = []
        sentence = []
        new_sentence_triggered = False  # Flag to indicate if a new sentence should be started
        
        for word in respond:
            if word == '' and sentence:  # Check if the word is empty and if the sentence is not empty
                sentences.append(' '.join(sentence))  # Join the sentence words with spaces
                sentence = []  # Reset the sentence
                new_sentence_triggered = False
            elif word == ':\n\n':  # Special case for the ":\n\n" which indicates a line break but also has content before it
                sentences.append(' '.join(sentence) + word)  # Include the ":\n\n" in the sentence
                sentence = []
                new_sentence_triggered = True
            elif word in ['\n']:  # Check for newline indicator
                new_sentence_triggered = True
            elif word == '' and new_sentence_triggered:  # Ignore empty strings after a newline
                continue
            elif word == '•' and new_sentence_triggered:  # If '•' comes after a newline, start a new sentence
                if sentence:  # Check if sentence is not empty before appending
                    sentences.append(' '.join(sentence))
                sentence = [word]  # Start the new sentence with '•'
                new_sentence_triggered = False
            else:
                if new_sentence_triggered:  # If a new sentence was triggered, append the current sentence and start fresh
                    if sentence:
                        sentences.append(' '.join(sentence))
                    sentence = [word]
                    new_sentence_triggered = False
                else:
                    sentence.append(word)  # Add the word to the current sentence
        
        # Append the last sentence if it's not empty
        if sentence:
            sentences.append(' '.join(sentence))
            
        st.write("### Response:")
        # Print the sentences
        for i, sentence in enumerate(sentences):
            # print(f"{sentence}")
            # Display the response
            st.write(" ")

            st.write(sentence)
        else:
            st.warning("Please enter a question and at least one URL.")
                
        
                