import streamlit as st
from ui_components import display_sidebar, display_chat_interface
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the API endpoint
API_URL = os.getenv("URL_BASE")
QUERY_ENDPOINT = f"{API_URL}/combined-query-chat/"

def display_search_and_chat_mode():
    display_sidebar()
    display_chat_interface()

def display_just_chat_interface():
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Prepare the chat history for the API request
        chat_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ]

        # Send user's question and chat history to the API
        with st.spinner("Thinking..."):
            response = requests.post(
                QUERY_ENDPOINT,
                json={"query": prompt, "chat_history": chat_history}
            )

        if response.status_code == 200:
            answer = response.json()["response"]

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(answer)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error(f"Error: {response.status_code} - {response.text}")

