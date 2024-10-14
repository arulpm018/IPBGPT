import streamlit as st
from ui_components import initialize_session_state, display_sidebar, display_chat_interface, display_mode_toggle
from app_modes import display_just_chat_interface

def main():

    st.set_page_config(
        page_title="IPB-GPT",
        page_icon="frontend/img/logo.png",
        layout="wide"
    )

    # Custom CSS to hide Streamlit's default menu and footer
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.title("💬 IPB-GPT")
    st.caption("🚀 A Repository Chatbot that helps you find related research about your undergraduate thesis")

    initialize_session_state()

    # Add mode toggle and Clear Chat button
    display_mode_toggle()

    if st.session_state['mode'] == "Just Chat":

        display_just_chat_interface()
    else:
        display_sidebar()
        display_chat_interface()

if __name__ == "__main__":
    main()
