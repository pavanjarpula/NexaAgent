import streamlit as st
from .api import AuthAPI
from .session import SessionManager
from datetime import datetime
from config.settings import  Setting
from utils.history import ChatHistory
from .call_llm import employee_llm, extract_json_from_response, place_order, trigger_history
from streamlit.components.v1 import html


def render_buttons(button_infos, auth_api: AuthAPI):
    """Helper function to render buttons in a 3-column layout"""
    if button_infos:
        cols = st.columns(3)
        for idx, btn_info in enumerate(button_infos):
            if cols[idx % 3].button(
                btn_info["label"],
                key=f"btn_{btn_info['food_id']}_{idx}",  # Unique key
                help=f"Click to order {btn_info['food_name']}"
            ):
                place_order(btn_info["food_id"], btn_info["food_name"],auth_api)

def show_auth_interface(api: AuthAPI, session: SessionManager):
    """Render login/register interface"""
    
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            height: 100vh !important;
            min-height: 100vh !important;
            max-height: 100vh !important;
        }
        [data-testid="stSidebar"], .block-container {
            height: 100vh !important;
            min-height: 100vh !important;
            max-height: 100vh !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1, 2])
    with col1:

        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            with st.form("Login"):
                username = st.text_input("Employee ID", key="login_id")
                password = st.text_input("Password", type="password", key="login_pass")
                
                if st.form_submit_button("Login"):
                    if not (username and password):
                        st.error("Please enter both username and password")
                        return
                    
                    try:
                        response = api.login(username, password)
                    except:
                        response = True
                    
                    if response:
                        session.login(username)
                        st.success("Login Successful")
                        st.rerun()
                    else:
                        st.error("Login failed - check your credentials")
        
        with tab2:
            st.subheader("Register")
            with st.form("Register"):
                new_username = st.text_input("Employee ID", key="reg_id")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Register"):
                    if not (new_username and new_password):
                        st.error("Please enter both username and password")
                        return
                    
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                        return
                    
                    if api.register(new_username, new_password):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Registration failed")

    with col2:
        st.image(
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c",
            caption="Empowering Teams, Simplifying Management",
            use_container_width=True
        )



def sidebar(session : SessionManager, auth_api : AuthAPI, emp_data, food_data):
    chat_history = ChatHistory(session.username)
    with st.sidebar:
        st.markdown("""
        <style> 
            div.stButton > button:first-child {
                height: 3em;
            }
        </style>
        """, unsafe_allow_html=True)
        if st.button("HOME", use_container_width=True):
            st.session_state.nav = 0
            st.rerun()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ChatBot", use_container_width=True):
                st.session_state.nav = 1
                st.rerun()

        with col2:
            if st.button("Jira Tickets", use_container_width=True):
                st.session_state.nav = 2
                st.rerun()

        col3, col4 = st.columns(2)
        with col3:
            if st.button("Order Placed", use_container_width=True):
                st.session_state.nav = 3
                st.rerun()

        with col4:
            if st.button("Applied Leaves", use_container_width=True):
                st.session_state.nav = 4
                st.rerun()

        col5, col6 = st.columns(2)
        with col5:
            if st.button("Delete Chat History", use_container_width=True):
                st.session_state.messages = []
                trigger_history(auth_api)
                chat_history.save([])
                st.success("History cleared!")

        with col6:
            if st.button("Logout", use_container_width=True):
                st.session_state.nav = 0
                session.logout()
                st.rerun()

        st.markdown("---")
        st.write(f"Casual Leaves Remaining : {emp_data['Leaves']['Casual_Leaves'][0]}")
        st.write(f"Sick Leaves Remaining : {emp_data['Leaves']['Sick_Leaves'][0]}")
        st.write(f"Compensatory Off Leaves Remaining : {emp_data['Leaves']['Compensatory_Off_Leaves'][0]}")
        st.write(f"Accured Leaves Remaining : {emp_data['Leaves']['Accured_Leaves'][0]}")

        st.markdown("---")
        wallet = food_data.get('balance', 0) if food_data else 0
        st.write(f"Wallet Balance : {wallet}")
        st.markdown("---")
        if st.button("Update"):
            emp_data = auth_api.emp_initialize(session.username)
            try:
                result = auth_api.food_initialize(session.username)
                if result:
                    food_data = result
            except:
                pass
        


async def chat_interface(session: SessionManager, auth_api : AuthAPI):
    """Chat bot interface"""

    
    chat_history = ChatHistory(session.username)
    
    check_prompt = """
                You are an intelligent query classifier. Your task is to analyze the user's input and determine which backend agent should handle it. You have two options:

                Food Agent: Handles queries related to food, restaurants, recipes, food delivery, or dining recommendations.
                Examples:
                "Find me a pizza place nearby"
                "Find me some foods with high protien"
                "Find me some foods with low calories"
                "Find me details about paneer"
                "Find all the details about this restaurent"
                "Place order for ID : F298"
                ""
                "How to make pasta?"

                "Order burger from McDonalds"

                Employee Agent: Handles queries related to employee HR matters, leave requests, Jira tickets, or employee details.
                Examples:
                "How many leaves do I have left?"
                "Show recent leave applications"
                "Apply Leave from 2025-07-01 to 2025-07-03"
                "Show me leave history"

                Instructions:
                1. Read the user's query carefully.
                2. Identify the key topic (food/restaurants OR employee/Jira).
                3.Respond only with:
                    {"agent": "Food"} if it's food-related.
                    {"agent": "Employee"} if it's Jira/employee-related.
                4.If unsure,send {"agent": "I am not able to answer these kind of questions "}.
                """

    if "messages" not in st.session_state:
        st.session_state.messages = chat_history.load()

    # Display chat messages
    for message in st.session_state.messages:
        avatar = Setting.USER_AVATAR if message["role"] == "user" else Setting.BOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "button_infos" in message:
                render_buttons(message["button_infos"], auth_api)
    # Main chat interface
    if prompt := st.chat_input("How can I help?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=Setting.USER_AVATAR):
            st.markdown(prompt)
        
        check_prompt += f"\nUser Query : {prompt}\n"
        # Show assistant response placeholder
        with st.chat_message("assistant", avatar=Setting.BOT_AVATAR):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            try:
                response = await auth_api.call_llm(check_prompt)
                json_response = extract_json_from_response(llm_response=response)
                full_response = "I am unable to handle such queries, sorry for inconvenience"
                if json_response["agent"] == "Employee":
                    full_response = employee_llm(prompt)
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                elif json_response["agent"] == "Food":
                    food_list= await auth_api.get_bot_response(prompt)
                    assistant_message = {
                        "role": "assistant",
                        "content": food_list[0],  # The text response
                        "button_infos": food_list[1]  # The button data
                    }
                    st.session_state.messages.append(assistant_message)
                    message_placeholder.markdown(food_list[0])
                    if food_list[1]:  # If there are buttons
                            cols = st.columns(3)
                            for idx, btn_info in enumerate(food_list[1]):
                                if cols[idx % 3].button(
                                    btn_info["label"],
                                    key=f"food_btn_{btn_info['food_id']}",
                                    help=f"Click to order {btn_info['food_name']}"
                                ):
                                    place_order(btn_info["food_id"], btn_info["food_name"],auth_api)
                else:
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

                
                
            except Exception as e:
                error_msg = f"Failed to connect to backend: {str(e)}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        chat_history.save(st.session_state.messages)
    
def display_ticket_card(ticket):
    """Render a single Jira ticket card with backend data"""
    status_colors = {
        "To Do": "#FF5630",
        "Done": "#0052CC",
        "In Progress": "#36B37E",
        "default": "#97A0AF"
    }
    
    color = status_colors.get(ticket.get("status"), status_colors["default"])
    
    card = f"""
    <div style="
        border-left: 4px solid {color};
        padding: 12px;
        margin: 8px 0;
        background: white;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 250px
    ">
        <div style="display: flex; justify-content: space-between;">
            <h4 style="margin: 0; color: {color};">{ticket.get('ticketId', '')}</h4>
            <span style="
                background: {color};
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8em;
            ">{ticket.get('status', '')}</span>
        </div>
        <h3 style="margin: 8px 0; color:black;">{ticket.get('title', '')}</h3>
        <p style="color: black; margin: 8px 0;">{ticket.get('description', '')}</p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <small style = "color: black;">Assigned by: {ticket.get('assignedBy', '')}</small>
        </div> 
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)


def display_home_page(emp_details):
    """Employee dashboard showing profile and approved leaves"""
    
    # Page header
    st.markdown(f"""
    <h1 style='text-align: center; padding-bottom: 10px;'>
        Welcome, {emp_details["Name"][0]}!
    </h1>
    """, unsafe_allow_html=True)

    # Employee Profile Card
    st.markdown(f"""
    <style>
        .profile-card {{
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            color: black;
            background-color: white;
        }}
        .profile-header {{
            color: #2563eb;
            border-bottom: 1px solid black;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        table {{l
            width: 100%;
            border-collapse: collapse;
        }}
        td {{
            padding: 8px 0;
            border: 1px solid black !important;
        }}
        td:first-child {{
            font-weight: 600;
            color : black !important;
            width: 40%;
        }}
    </style>

    <div class="profile-card">
        <h3 class="profile-header">🧑‍💼 Employee Profile</h3>
        <table>
            <tr><td>ID</td><td>{emp_details["EMP_ID"][0]}</td></tr>
            <tr><td>Name</td><td>{emp_details["Name"][0]}</td></tr>
            <tr><td>Designation</td><td>{emp_details["Designation"][0]}</td></tr>
            <tr><td>Team</td><td>{emp_details["Team"][0]}</td></tr>
            <tr><td>Email</td><td>{emp_details["Email"][0]}</td></tr>
            <tr><td>Phone</td><td>{emp_details["Phone"][0]}</td></tr>
        </table>
        
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown(f"""
    <style>
        .profile-card {{
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .profile-header {{
            color: #2563eb;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        td {{
            padding: 8px 0;
            border: 1px solid black !important;
        }}
        td:first-child {{
            font-weight: 600;
            color : black !important;
            width: 40%;
        }}
    </style>

    <div class="profile-card">
        <h4 class="profile-header" style="margin-top:20px">👥 Reporting To</h4>
        <table>
            <tr><td>Manager</td><td>{emp_details["Manager"][0]}</td></tr>
            <tr><td>Manager ID</td><td>{emp_details["ManagerID"][0]}</td></tr>
            <tr><td>Manager Email</td><td>{emp_details["ManagerEmail"][0]}</td></tr>
        </table>
        
    </div>
    """, unsafe_allow_html=True)


def applied_leaves(leave_records):

    styles = """
    <style>
    .leave-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        font-family: Arial, sans-serif;
        color: white;
    }
    .leave-table th {
        background-color: #2563eb;
        color: white;
        padding: 10px;
        text-align: left;
    }
    .leave-table td {
        padding: 10px;
        border: 1px solid #ddd;
    }
    .sick-leave { color: #dc2626; }
    .casual-leave { color: #059669; }
    .compensatory-leave { color: #d97706; }
    .accured-leave { color: #7c3aed; }
    </style>
    """

    # Table header
    header = """
    <table class="leave-table">
        <thead>
            <tr>
                <th>Employee ID</th>
                <th>Days</th>
                <th>From</th>
                <th>To</th>
                <th>Leave Type</th>
            </tr>
        </thead>
        <tbody>
    """

    table_rows = []
    for record in leave_records:
        leave_class = ""
        if record["leaveType"] == "sickLeave":
            leave_class = "sick-leave"
        elif record["leaveType"] == "casualLeave":
            leave_class = "casual-leave"
        elif record["leaveType"] == "compOff":
            leave_class = "compensatory-leave"
        elif record["leaveType"] == "accuredLeave":
            leave_class = "accured-leave"
        
        start = datetime.strptime(record['fromDate'], "%Y-%m-%dT%H:%M:%SZ")
        start =  start.strftime("%b %d, %Y")  
        end = datetime.strptime(record['toDate'], "%Y-%m-%dT%H:%M:%SZ")
        end =  end.strftime("%b %d, %Y")  
        
        row = f"""
        <tr>
            <td>{record['empId']}</td>
            <td>{record['numberOfLeavesApplied']}</td>
            <td>{start}</td>
            <td>{end}</td>
            <td class="{leave_class}">{leave_class}</td>
        </tr>
        """
        table_rows.append(row)

    # Table footer
    footer = """
        </tbody>
    </table>
    """

    # Combine all parts
    html_content = f"{styles}{header}{''.join(table_rows)}{footer}"

    # Display using components.v1.html for more reliable rendering
    html(html_content, height=800)

def placed_orders(leave_records):

    styles = """
    <style>
    .order-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        color: white;
    }
    .order-table th {
        background-color: #2563eb;
        color: white;
        padding: 10px;
        text-align: left;
    }
    .order-table td {
        padding: 10px;
        border: 1px solid #ddd;
    }
    </style>
    """

    # Table header
    header = """
    <table class="order-table">
        <thead>
            <tr>
                <th>Employee ID</th>
                <th>Food ID</th>
                <th>Restaurant</th>
                <th>Food Name</th>
                <th>Price</th>
            </tr>
        </thead>
        <tbody>
    """

    table_rows = []
    for record in leave_records:
        
        row = f"""
        <tr>
            <td>{record['user_id']}</td>
            <td>{record['food_id']}</td>
            <td>{record['Restaurant_name']}</td>
            <td>{record['Food_name']}</td>
            <td>₹ {record['price']}</td>
        </tr>
        """
        table_rows.append(row)

    # Table footer
    footer = """
        </tbody>
    </table>
    """

    # Combine all parts
    html_content = f"{styles}{header}{''.join(table_rows)}{footer}"

    # Display using components.v1.html for more reliable rendering
    html(html_content, height=800)