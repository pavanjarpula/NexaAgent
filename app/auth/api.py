import os
import requests
import aiohttp
import streamlit as st
from streamlit import error as st_error
import httpx

class AuthAPI:
    def __init__(self, base_url):
        self.emp_base_url = base_url
        self.llm_url = os.getenv("LLM_URL", "http://localhost:11434/v1/chat/completions")
        self.food_api_url = os.getenv("FOOD_API_URL", "http://localhost:7123/")
    
    def login(self, username, password):
        """Authenticate user with backend"""
        try:
            response = requests.post(
                f"{self.emp_base_url}/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200
        except Exception as e:
            st_error(f"Login failed: {str(e)}")
            return None
    
    def register(self, username, password):
        """Register new user with backend"""
        try:
            response = requests.post(
                f"{self.emp_base_url}/register",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200
        except Exception as e:
            st_error(f"Registration failed: {str(e)}")
            return False
        
    def emp_initialize(self,username):
        try:
            response = requests.post(
                f"{self.emp_base_url}/initialize",
                json={"id": username},
                headers={"Content-Type": "application/json"}                
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    def food_initialize(self,username):
        try:
            response = requests.post(
                f"{self.food_api_url}ordered/",
                json={"user_id":username},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None


    def get_jira(self,username):
        try:
            response = requests.post(
                f"{self.emp_base_url}/jira",
                json={"id": username},
                headers={"Content-Type": "application/json"}                
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st_error(f"Failed to Initiaize: {str(e)}")
            return False        
        
    async def call_llm(self, prompt: str) -> str:
        """Call custom LLM API with the given prompt"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "qwen2.5:3b",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            headers = {
                "Content-Type": "application/json"
            }
            async with session.post(self.llm_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    raise Exception(f"LLM API error: {response.status}")

    async def get_bot_response(self,prompt : str):
        try:
            payload = {
                "prompt": prompt,
                "user_location": "Sector 135, Noida",
                "user_id": st.session_state.auth["username"]
            }
            response = requests.post(
                f"{self.food_api_url}chat/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()  
        except Exception as e:
            st_error(f"Failed to generate response: {str(e)}")
            return {f"Error:{e}"}
