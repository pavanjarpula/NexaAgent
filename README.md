# WorkMate AI

An agentic AI based on Model Context Protocol which works on natural language queries, does the task and gives response in natural language.


## Follow these steps to run the whole project:

1. Run the backend 1 (employee-management):

    1. Run the MCP server by the command : uv run scripts/server.py

    2. Run the MCP Client by the command : uv run client/main.py

2. Run the backend 2 (cafeteria_meal_service):

    1. make a virtual environment and install all the dependencies given in the requirements.txt (if imports fail, manually install missing packages )

    2. Run the application server by the command : uvicorn application.main:app --port 8000

    3. Run the MCP server by the command: python3 mcp_server/main.py

    4. Run the MCP client by the command: uvicorn mcp_client/main.py --port 7123

3. Now Run the frontend (app) by the command: uv run streamlit run main.py




