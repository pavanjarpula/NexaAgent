import streamlit as st
import requests

from auth.api import AuthAPI
from auth.session import SessionManager
from dotenv import load_dotenv
from auth.ui import show_auth_interface, chat_interface, sidebar, display_ticket_card, display_home_page, applied_leaves, placed_orders
from config.settings import Setting
import asyncio

load_dotenv()
auth_api = AuthAPI(Setting.BACKEND_BASE_URL)
session = SessionManager()

st.set_page_config(page_title="WorkMate AI", layout="wide", initial_sidebar_state="expanded", page_icon="🤖")
st.markdown("<h1 style='text-align: center; color: white;'>WorkMate AI</h1>", unsafe_allow_html=True)

def get_demo_emp_data(username):
    return {
        "Emp_Data": {
            "empId": username.upper(),
            "empName": username.replace("_", " ").title(),
            "empEmail": f"{username}@company.com",
            "designation": "Software Engineer",
            "team": "Software Engineering",
            "managerName": "Rajesh Kumar",
            "managerId": "501",
            "managerEmail": "rajesh.kumar@company.com",
            "phoneNumber": "+91-9876543210"
        },
        "Leaves": {
            "Casual_Leaves": [12],
            "Sick_Leaves": [8],
            "Compensatory_Off_Leaves": [4],
            "Accured_Leaves": [15]
        },
        "Applications": []
    }

def get_demo_food_data(username):
    return {
        "balance": 2500.0,
        "orders": []
    }

def check_backend_available():
    try:
        r = requests.post(f"{Setting.BACKEND_BASE_URL}/login", json={"username": "test", "password": "test"}, timeout=2)
        return True
    except:
        return False

if not session.is_authenticated:
    show_auth_interface(auth_api, session)
else:
    backend_available = check_backend_available()

    emp_data = None
    food_data = get_demo_food_data(session.username)

    if backend_available:
        try:
            emp_data = auth_api.emp_initialize(session.username)
        except:
            emp_data = None
        try:
            result = auth_api.food_initialize(session.username)
            if result:
                food_data = result
        except:
            pass

    if not emp_data:
        emp_data = get_demo_emp_data(session.username)

    sidebar(session, auth_api, emp_data, food_data)

    if st.session_state.nav == 0:
        display_home_page(emp_data["Emp_Data"])
    elif st.session_state.nav == 1:
        st.markdown("<h2 style='text-align: center; color: white;'>ChatBot</h2>", unsafe_allow_html=True)
        st.markdown('---')
        asyncio.run(chat_interface(session, auth_api))
    elif st.session_state.nav == 2:
        st.markdown("<h2 style='text-align: center; color: white;'>Jira Tickets</h2>", unsafe_allow_html=True)
        st.markdown('---')
        st.info("Jira service not available")
    elif st.session_state.nav == 3:
        st.markdown("<h2 style='text-align: center; color: white;'>Order Placed</h2>", unsafe_allow_html=True)
        st.markdown('---')
        placed_orders(food_data.get("orders", []))
    elif st.session_state.nav == 4:
        st.markdown("<h2 style='text-align: center; color: white;'>Employee Leave Records</h2>", unsafe_allow_html=True)
        st.markdown('---')
        applied_leaves(emp_data.get("Applications", []))
