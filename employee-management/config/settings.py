import os
from typing import Optional

class Settings:
    """Configuration settings for the application"""
    
    # Weaviate Configuration
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    
    # Ollama Embedding Configuration
    NOMIC_API_URL: str = os.getenv("NOMIC_API_URL", "http://localhost:11434/api/embeddings")
    NOMIC_API_KEY: Optional[str] = None
    
    # Data Configuration
    CSV_FILE_PATH: str = "../data/random_employee_data.csv"
    
    # Batch Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    
    # Embedding Configuration
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # Ollama Configuration
    REMOTE_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
    REMOTE_OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
    MCP_SERVER_PATH = os.getenv("MCP_SERVER_URL", "http://localhost:8005/sse")
   
    # LLM
    LLM_URL = os.getenv("LLM_URL", "http://localhost:11434/v1/chat/completions")

# Global settings instance
settings = Settings()
