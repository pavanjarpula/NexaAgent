import streamlit as st
import requests
from typing import Dict, Any, Optional
from .api import AuthAPI
import json
from config.settings import Setting

def extract_json_from_response(llm_response: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from LLM response"""
        try:
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = llm_response[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            return f"Error parsing LLM response: {e}\nRaw response: {llm_response}"


def employee_llm(prompt : str):
    # Prepare the JSON payload for your backend
    payload = {
        "query": prompt,
        "id": st.session_state.auth["username"]
    }
    response = requests.post(
    f"{Setting.BACKEND_BASE_URL}/query",
    json=payload,
    headers={"Content-Type": "application/json"}
    )
    # Process the response
    if response.status_code == 200:
        backend_response = response.json()  # assuming JSON response
        full_response = backend_response.get("response", "No answer provided")
    else:
        full_response = f"Error: {response.status_code} - {response.text}"
    return full_response


def place_order(food_id, food_name, auth_api: AuthAPI):
    try:
        # Store the order in session state
        if "orders" not in st.session_state:
            st.session_state.orders = []
        
        st.session_state.orders.append({
            "food_id": food_id,
            "food_name": food_name,
            "user_id": st.session_state.auth["username"]
        })
        
        # Add to chat history immediately
        st.session_state.messages.append({
            "role": "user",
            "content": f"Place order for {food_name} (ID: {food_id})"
        })
        
        response = requests.post(
            f"{auth_api.food_api_url}order/",
            json={
                "user_id": st.session_state.auth["username"],
                "food_id": food_id
            },
            timeout=120
        )
        response.raise_for_status()
        
        # Add API response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": str(response.json())
        })
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Order failed: {str(e)}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Unexpected error: {str(e)}"
        })
def trigger_history(auth_api : AuthAPI):
    try:
        response = requests.post(
            f"{auth_api.food_api_url}/delete/",
            headers={"Content-Type": "application/json"}                
        )
        if response.status_code != 200:
            raise
        response = requests.post(
            f"{Setting.BACKEND_BASE_URL}/delete",
            json= {},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise
    except Exception as e:
        return f"Failed to clear chat history {e}"