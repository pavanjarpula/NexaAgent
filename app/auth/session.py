from streamlit import session_state as st_session
from datetime import datetime, timedelta
import weaviate

class SessionManager:
    def __init__(self):
        if "auth" not in st_session:
            st_session.auth = {
                "authenticated": False,
                "username": None,
                "expires_at": None
            }
        if "backend_model" not in st_session:
            st_session["backend_model"] = "Qwen"
        st_session.history = []
        if "nav" not in st_session:
            st_session.nav = 0
        if "processed_buttons" not in st_session:
            st_session.processed_buttons = set()
        if "key" not in st_session:
            st_session.key = 1

    @property
    def is_authenticated(self):
        if not st_session.auth["authenticated"]:
            return False

        if st_session.auth["expires_at"]:
            return datetime.now() < st_session.auth["expires_at"]
        return True
    
    @property
    def username(self):
        return st_session.auth["username"] if self.is_authenticated else None
    
    
    def login(self, username, token=None):
        st_session.auth.update({
            "authenticated": True,
            "username": username,
            "expires_at": datetime.now() + timedelta(days=2) 
        })
    
    def logout(self):
        st_session.auth.update({
            "authenticated": False,
            "username": None,
            "expires_at": None
        })

        keys_to_keep = ['_streamlit_rerun_data']
        for key in list(st_session.keys()):
            if key not in keys_to_keep:
                del st_session[key]
