import streamlit as st
from dotenv import load_dotenv
import os
import shelve
import requests

load_dotenv()
st.title("Employee Management Chatbot")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"


if "backend_model" not in st.session_state:
    st.session_state["backend_model"] = "Qwen"

# Load chat history from shelve file
def load_chat_history():
    try:
        with shelve.open("chat_history") as db:
            return db.get("messages", [])
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

# Save chat history to shelve file
def save_chat_history(messages):
    try:
        with shelve.open("chat_history") as db:
            db["messages"] = messages
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])
        st.success("Chat history cleared!")


# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)
    
    # Prepare the JSON payload for your backend
    payload = {
        "query": prompt,
        "context": st.session_state.messages  
    }
    
    # Show assistant response placeholder
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            response = requests.post(
                "http://0.0.0.0:5000/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Process the response
            if response.status_code == 200:
                backend_response = response.json()  # assuming JSON response
                full_response = backend_response.get("response", "No answer provided")
            else:
                full_response = f"Error: {response.status_code} - {response.text}"
            
            # Display the response
            message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"Failed to connect to backend: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Save chat history after each interaction
    save_chat_history(st.session_state.messages)