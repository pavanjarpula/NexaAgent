from client_services import CustomLLMMCPClient
import sys
import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import Dict, Any


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from config.settings import Settings
from tools.employee_tools import EmployeeTools
from tools.leave_tools import LeaveTools
from tools.jira_tools import JiraTools

employee_tools = EmployeeTools()
leave_tools = LeaveTools()
jira_tools = JiraTools()

client = CustomLLMMCPClient(Settings.LLM_URL, Settings.MCP_SERVER_PATH)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing MCP client...")
    
    # Initialize MCP connection
    await client.initialize_mcp_connection()
    print("Connected to MCP server and Ollama")
    print(f"Available tools: {[tool['name'] for tool in client.available_tools]}\n")
    yield

    #Code to run on shutdow
    print("Cleaning up MCP client...")
    await client.cleanup()


app = FastAPI(lifespan=lifespan)

# CORS and routes remain the same
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
)

@app.post("/query")
async def handle_query(data: Dict[str, Any] = Body(...)):
    try:
        query = data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query missing in request")
        response = await client.process_query(query, data.get("id"))
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/login")
async def user_login(data : Dict[str, Any] = Body(...)):
    try:
        t =  employee_tools.login_employee(data.get("username"), data.get("password"))    
        print(t)
        if t:
            return "Employee Login"
        raise HTTPException(status_code=409, detail="Check Credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register")
async def user_register(data : Dict[str, Any] = Body(...)):
    try:
        t = employee_tools.register_employee(data.get("username"), data.get("password"))
        print(t)
        if t:
            return "Employee Registered!!"
        raise HTTPException(status_code=409, detai="Employee Already registered ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/initialize")
async def user_initialize(data : Dict[str, Any] = Body(...)):
    try:
        return {"Emp_Data":employee_tools.get_employee_details(data.get("id")),  
                "Leaves":leave_tools.get_leaves_remaining(data.get("id")),
                "Applications": leave_tools.list_leave_applications(data.get("id"))
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jira")
async def retreive_jira(data : Dict[str, Any] = Body(...)):
    try:
        return {"Jira": jira_tools.get_employee_jira_tickets(data.get("id"))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_chat_history():
    try:
        client.chat_history = []
        return True
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="107.109.54.27", port=5000, reload=True)
