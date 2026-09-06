import json
import os

class ChatHistory:
    def __init__(self, username):
        self.username = username
        self.filepath = os.path.join(os.path.dirname(__file__), f"chat_{username}.json")
    
    def load(self):
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r") as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save(self, messages):
        try:
            with open(self.filepath, "w") as f:
                json.dump(messages, f)
        except:
            pass
    
    def clear(self):
        self.save([])
