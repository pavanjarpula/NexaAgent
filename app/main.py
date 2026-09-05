import streamlit as st


from auth.api import AuthAPI
from auth.session import SessionManager
from dotenv import load_dotenv
from auth.ui import show_auth_interface, chat_interface, sidebar, display_ticket_card, display_home_page, applied_leaves, placed_orders
from config.settings import Setting
import asyncio



load_dotenv()
# Configuration
# Initialize services
auth_api = AuthAPI(Setting.BACKEND_BASE_URL)
session = SessionManager()

st.set_page_config(page_title="Employee Management", layout="wide", initial_sidebar_state="expanded", page_icon="👥")


st.markdown("<h1 style='text-align: center; color: white;'>WorkMate AI</h1>", unsafe_allow_html=True)

# Authentication check
if not session.is_authenticated:
    show_auth_interface(auth_api, session)
else:
    emp_data = auth_api.emp_initialize(session.username)
    food_data = auth_api.food_initialize(session.username)
    sidebar(session, auth_api, emp_data, food_data)
    
    if st.session_state.nav == 0:
        display_home_page(emp_data["Emp_Data"])
    elif st.session_state.nav == 1:
        st.markdown("<h2 style='text-align: center; color: white;'>ChatBot</h2>", unsafe_allow_html=True)
        st.markdown('---') 
        asyncio.run(chat_interface(session, auth_api))
    elif st.session_state.nav == 2:
        jira_data = auth_api.get_jira(session.username)
        st.markdown("<h2 style='text-align: center; color: white;'>Jira Tickets</h2>", unsafe_allow_html=True)
        st.markdown('---')
        cols = st.columns(2)
        for i, jira in enumerate(jira_data["Jira"]):
            with cols[i % 2]:
                display_ticket_card(jira)
    elif st.session_state.nav == 3:
        st.markdown("<h2 style='text-align: center; color: white;'>Order Placed</h2>", unsafe_allow_html=True)
        st.markdown('---')
        placed_orders(food_data["orders"])
    elif st.session_state.nav == 4:
        st.markdown("<h2 style='text-align: center; color: white;'>📅 Employee Leave Records</h2>", unsafe_allow_html=True)
        st.markdown('---')
        applied_leaves(emp_data["Applications"])