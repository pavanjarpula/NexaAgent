import os
from typing import Optional

class Settings:
    """Configuration settings for the application"""
    
    # Weaviate Configuration
    WEAVIATE_URL: str = "http://107.109.53.22:8080"
    # WEAVIATE_URL: str = "http://0.0.0.0:8080"
    
    # Nomic API Configuration
    NOMIC_API_URL: str = os.getenv("NOMIC_API_URL", "http://107.110.74.116/workspace_ashish_r1_itchatbot_infrence1/v1/embeddings")
    NOMIC_API_KEY: Optional[str] = os.getenv("NOMIC_API_KEY")
    
    # Data Configuration
    CSV_FILE_PATH: str = "../data/random_employee_data.csv"
    
    # Batch Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    
    # Embedding Configuration
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_MODEL: str = "nomic-embed-text-v1.5"

    # Ollama Configuration
    REMOTE_OLLAMA_HOST = "107.109.54.126"
    REMOTE_OLLAMA_PORT = 11434
    MCP_SERVER_PATH = "http://0.0.0.0:8123/sse"
   
    # New LLM
    LLM_URL="http://107.110.74.116/workspace_ashish_r1_itchatbot_infrence1/v1/chat/completions"
# Global settings instance
settings = Settings()
