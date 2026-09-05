import shelve
from streamlit import error as st_error

class ChatHistory:
    def __init__(self, username):
        self.username = username
    
    def load(self):
        """Load user's chat history"""
        try:
            with shelve.open("chat_history") as db:
                return db.get(f"{self.username}_messages", [])
        except Exception as e:
            st_error(f"Error loading chat history: {e}")
            return []
    
    def save(self, messages):
        """Save user's chat history"""
        try:
            with shelve.open("chat_history") as db:
                db[f"{self.username}_messages"] = messages
        except Exception as e:
            st_error(f"Error saving chat history: {e}")
    
    def clear(self):
        """Clear user's chat history"""
        self.save([])