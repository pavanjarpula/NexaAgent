import requests
import json
from typing import List
from config.settings import settings

class NomicEmbeddingClient:
    """Client for Nomic embedding API"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or settings.NOMIC_API_URL
        self.headers = {"Content-Type": "application/json"}
        if api_key or settings.NOMIC_API_KEY:
            self.headers["Authorization"] = f"Bearer {api_key or settings.NOMIC_API_KEY}"
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama local API"""
        if not texts:
            print("Warning: Empty input texts list")
            return []
            
        embeddings = []
        for text in texts:
            payload = {
                "model": settings.EMBEDDING_MODEL,
                "prompt": text
            }
            try:
                response = requests.post(self.api_url, json=payload, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                embeddings.append(result["embedding"])
            except requests.exceptions.RequestException as e:
                print(f"Error calling Ollama API: {e}")
                return []
            except Exception as e:
                print(f"Unexpected error processing embeddings: {e}")
                return []
        
        print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0]) if embeddings else 0}")
        return embeddings
    
    def get_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using Ollama local API"""
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "prompt": text
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result["embedding"]
                
        except Exception as e:
            print(f"Error getting Ollama embedding: {e}")
            raise
