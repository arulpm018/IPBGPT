import streamlit as st
from document_processing import upload_pdf, get_related_documents
from chat_logic import process_pdf_chat, process_selected_documents_chat
import re

def initialize_session_state():
    defaults = {
        'messages': [{"role": "assistant", "content": "Can I assist you today?"}],
        'related_document': None,
        'selected_document': [],
        'document_chat': None,
        'number': 3,
        'prompt': None,
        'uploaded_file': None,
        'current_file': None,
        'mode': 'Search and Chat',
        'previous_mode': 'Search and Chat'
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_mode_toggle():
    col1, col2 = st.columns([9, 1])
    with col1:
        if st.button("Clear Chat"):
            st.session_state.clear_chat = True
            st.session_state.messages = [{"role": "assistant", "content": "Chat cleared. How can I assist you?"}]
    
    with col2:
        # Add a session state variable to track the checkbox status
        if 'mode_toggle' not in st.session_state:
            st.session_state['mode_toggle'] = st.session_state['mode'] == "Chat Mode"
        
        # Toggle between modes and update the session state correctly
        toggle = st.toggle("chat mode", key="mode_toggle", value=st.session_state['mode_toggle'])
        
        new_mode = "Chat Mode" if toggle else "Search and Chat"
        
        # Check if the mode has changed
        if new_mode != st.session_state['previous_mode']:
            st.session_state['mode'] = new_mode
            st.session_state['previous_mode'] = new_mode
            # Clear chat history when mode changes
            st.session_state.messages = [{"role": "assistant", "content": f"Mode changed to {new_mode}. How can I assist you?"}]


def display_sidebar():
    with st.sidebar:
        st.title("FIND RELATED RESEARCH📄")
        
        text_input = st.text_input("Enter your undergraduate thesis Title 👇")
        new_number = st.number_input('Insert a min number of the research', min_value=1, format='%i', value=st.session_state['number'])
        
        # Create a button to trigger the search
        search_button = st.button("Search for Related Documents")

        # Check if any input has changed or if the search button is pressed
        if search_button or new_number != st.session_state['number'] or text_input != st.session_state.get('prompt', ''):
            if text_input:
                st.session_state['number'] = new_number
                st.session_state['prompt'] = text_input
                
                with st.spinner("Searching for related documents..."):
                    related_docs = get_related_documents(text_input, new_number)
                    
                if 'error' in related_docs:
                    st.error(related_docs['error'])
                else:
                    st.session_state['related_document'] = related_docs
                    st.session_state['selected_document'] = []  # Reset selected documents
                    st.success(f"Found {len(related_docs.get('related_documents', []))} related documents!")
            else:
                st.warning("Please enter a thesis title before searching.")

        display_retrieved_documents()

    return text_input

def display_retrieved_documents():
    if st.session_state.get('related_document'):
        st.subheader("Retrieved Documents")
        for i, doc in enumerate(st.session_state['related_document']['related_documents']):
            st.markdown(f"**Document {i+1}**")
            st.markdown(f"**Judul**: {doc['judul']}")
            st.markdown(f"**URL**: [{doc['url']}]({doc['url']})")
            
            if st.session_state['uploaded_file'] is None:
                if st.checkbox(f"Select Document {i+1}", key=f"checkbox_{i}"):
                    if doc not in st.session_state['selected_document']:
                        st.session_state['selected_document'].append(doc)
                else:
                    if doc in st.session_state['selected_document']:
                        st.session_state['selected_document'].remove(doc)
            else:
                st.warning('Clear the PDF first before selecting Document')
            
            st.markdown("---")

def render_llm_response(response):
    # Split the response into segments based on code blocks
    segments = re.split(r'(```[\s\S]*?```)', response)
    
    for segment in segments:
        if segment.startswith('```') and segment.endswith('```'):
            # This is a code block
            code = segment.strip('`').split('\n')
            language = code[0] if code[0] else 'python'  # Default to python if no language specified
            code_content = '\n'.join(code[1:])
            st.code(code_content, language=language)
        else:
            # This is regular text
            st.markdown(segment)

def display_chat_interface():

    if not st.session_state['selected_document']:
        st.session_state['uploaded_file'] = st.file_uploader("Choose a PDF")
    
    if st.session_state.get('current_file') != st.session_state['uploaded_file']:
        if st.session_state['uploaded_file']:
            with st.spinner("Processing uploaded PDF. Please wait..."):
                result = upload_pdf(st.session_state['uploaded_file'])
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.session_state['current_file'] = st.session_state['uploaded_file']
                    st.success("PDF processed successfully!")

    chat_enabled = st.session_state['uploaded_file'] is not None or st.session_state['selected_document']

    if chat_enabled:
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Thinking..."):
                chat_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
                if st.session_state['uploaded_file']:
                    response = process_pdf_chat(prompt, chat_history)
                elif st.session_state['selected_document']:
                    response = process_selected_documents_chat(prompt, chat_history)
                
                if response.startswith("Failed to"):
                    st.error(response)
                else:
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_llm_response(message["content"])
            else:
                st.markdown(message["content"])

    if st.session_state['uploaded_file']:
        st.info("You are currently chatting with the uploaded PDF.")
    elif st.session_state['selected_document']:
        st.info("You are currently chatting with the selected documents from the search results.")
    elif st.session_state['mode'] == "Chat Mode":
        st.info("You are in Chat Mode mode.")

