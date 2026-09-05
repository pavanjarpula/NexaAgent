import os

class Setting:
    BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:5000")
    FOOD_API_URL = os.getenv("FOOD_API_URL", "http://localhost:7123/")
    LLM_URL = os.getenv("LLM_URL", "http://localhost:11434/v1/chat/completions")
    USER_AVATAR = "👤"
    BOT_AVATAR = "🤖"
