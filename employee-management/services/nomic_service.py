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
        """Generate embeddings using remote Nomic API"""
        if not texts:
            print("Warning: Empty input texts list")
            return []
            
        payload = {
            "input": texts,
            "model": settings.EMBEDDING_MODEL,
            "task_type": "search_document",
            "dimensionality": settings.EMBEDDING_DIMENSION
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            # Debug: Print response structure (first 500 chars)
            print("API response sample:", json.dumps(result, indent=2)[:500])

            # Extract all embeddings from response
            if "data" in result:
                embeddings = [item["embedding"] for item in result["data"]]
                print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0]) if embeddings else 0}")
                return embeddings
            else:
                print("Unexpected response format - missing 'data' field")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling Nomic API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error processing embeddings: {e}")
            return []
    
    def get_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using remote Nomic API"""
        payload = {
            "input": [text],
            "model": settings.EMBEDDING_MODEL,
            "task_type": "search_query",
            "dimensionality": settings.EMBEDDING_DIMENSION
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0]["embedding"]
            else:
                raise Exception("No embedding returned from Nomic API")
                
        except Exception as e:
            print(f"Error getting Nomic embedding: {e}")
            raise
