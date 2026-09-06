# NexaAgent

**Agentic Workplace & Food Assistant**

NexaAgent is an NLP-powered agentic chatbot that unifies workplace management and personalized food discovery within a single conversational interface. It understands natural-language requests, identifies intent, selects the right tools, and executes multi-step actions through an LLM-driven reasoning workflow powered by the Model Context Protocol (MCP).

---

## Features

### Workplace Assistant (WorkMate AI)
- Retrieve employee information and personal details
- Check and manage employee leave balances
- Apply for leaves via conversational interface
- Generate professional leave-request emails to managers
- Create, assign, and track Jira tickets
- Update Jira ticket statuses

### Food Assistant (MealMind AI)
- Recommend restaurants and dishes based on user preferences
- Semantic search over food and restaurant data using vector embeddings
- Supports queries involving calories, protein, price, and ingredients
- Combines semantic matching with structured numeric filtering
- Supports dietary preferences (low-calorie, high-protein, budget-friendly)
- Location-based restaurant recommendations
- Place food orders and track order history

### Agentic Reasoning
- Analyzes intent and context of user queries using LLM reasoning
- Dynamically selects appropriate tools based on query analysis
- Executes multi-step workflows across multiple MCP tools
- Continues reasoning loop until the task is complete
- Generates natural-language responses from structured tool outputs

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  STREAMLIT FRONTEND                     │
│                  (app/ - Port 8501)                     │
│                                                         │
│   Auth │ Chatbot │ Dashboard │ Leaves │ Food Orders     │
└───────────┬───────────────────────────┬─────────────────┘
            │                           │
            ▼                           ▼
┌─────────────────────┐     ┌──────────────────────────┐
│  EMPLOYEE BACKEND   │     │     FOOD BACKEND         │
│  FastAPI (5000)     │     │  FastAPI (7123)          │
│                     │     │                          │
│  ┌──────────────┐   │     │  ┌────────────────────┐  │
│  │  MCP Client  │   │     │  │    MCP Client      │  │
│  └──────┬───────┘   │     │  └─────────┬──────────┘  │
│         │           │     │            │              │
│  ┌──────▼───────┐   │     │  ┌─────────▼──────────┐  │
│  │   Qwen LLM   │   │     │  │    Qwen LLM        │  │
│  └──────┬───────┘   │     │  └─────────┬──────────┘  │
│         │           │     │            │              │
│  ┌──────▼───────┐   │     │  ┌─────────▼──────────┐  │
│  │  MCP Server  │   │     │  │   MCP Server       │  │
│  │  (8005 SSE)  │   │     │  │   (8123 SSE)       │  │
│  │              │   │     │  │                    │  │
│  │  - Employee  │   │     │  │  - Semantic Search │  │
│  │  - Leaves    │   │     │  │  - Food Details    │  │
│  │  - Jira      │   │     │  │  - Place Order     │  │
│  │  - Search    │   │     │  │  - Restaurant Info │  │
│  └──────┬───────┘   │     │  └─────────┬──────────┘  │
└─────────┼───────────┘     └────────────┼──────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────────────┐
│                     WEAVIATE DB                         │
│              (Vector Database - Port 8080)               │
│                                                         │
│  Classes:                                               │
│  ├── Employee            (profiles + Nomic embeddings)  │
│  ├── EmployeeLeavesRemaining  (leave balances)          │
│  ├── LeaveApplication    (leave history)                │
│  ├── JiraTicket          (ticket storage)               │
│  ├── Employeelogin       (bcrypt auth)                  │
│  ├── Foods               (food items + embeddings)      │
│  ├── EmployeeWallet      (wallet balances)              │
│  └── Orders              (food order records)           │
└─────────────────────────────────────────────────────────┘
          ▲                              ▲
          │                              │
┌─────────┴───────────┐     ┌───────────┴────────────────┐
│ FOOD FASTAPI APP    │     │                            │
│ (8000)              │     │                            │
│                     │     │                            │
│ - Food details      │     │                            │
│ - Restaurant info   │     │                            │
│ - Semantic search   │     │                            │
│ - Data ingestion    │     │                            │
└─────────────────────┘     │                            │
                            │                            │
┌───────────────────────────┘                            │
│ OLLAMA (Local)                                         │
│ - Qwen 2.5:3B (LLM reasoning + tool selection)        │
│ - Nomic Embed Text (768-dim embeddings)                │
└────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **LLM** | Qwen 2.5:3B (via Ollama) | Reasoning, intent analysis, tool selection |
| **Embeddings** | Nomic Embed Text (via Ollama) | 768-dim vector representations for semantic search |
| **Vector DB** | Weaviate | Store and query embeddings + structured data |
| **Agent Protocol** | MCP (Model Context Protocol) | Standardized tool interface between LLM and tools |
| **Backend** | FastAPI | REST API for employee and food services |
| **Frontend** | Streamlit | Conversational web interface |
| **Orchestration** | FastMCP | MCP server implementation |
| **Auth** | bcrypt | Password hashing for employee login |
| **Deployment** | Docker Compose | Multi-service container orchestration |

---

## Project Structure

```
NexaAgent/
├── employee-management/          # Employee management service
│   ├── config/settings.py        # Configuration (env vars)
│   ├── models/                   # Data models & Weaviate schemas
│   ├── services/                 # Weaviate, Nomic, data ingestion
│   ├── tools/                    # MCP tools (employee, leave, Jira, search)
│   ├── utils/                    # CSV parsing, validation
│   ├── scripts/server.py         # MCP Server (port 8005)
│   ├── scripts/fast_ingest.py    # Quick data ingestion script
│   ├── client/main.py            # MCP Client + FastAPI (port 5000)
│   ├── data/                     # Employee CSV data (1000 records)
│   └── Dockerfile
│
├── cafeteria_meal_service/       # Food recommendation service
│   ├── application/main.py       # FastAPI food app (port 8000)
│   ├── mcp_server/main.py        # MCP Server (port 8123)
│   ├── mcp_client/               # MCP Client + FastAPI (port 7123)
│   ├── requirements.txt
│   └── Dockerfiles
│
├── app/                          # Streamlit frontend
│   ├── main.py                   # Entry point
│   ├── auth/                     # Authentication, API calls, UI
│   ├── config/settings.py        # Frontend config
│   ├── utils/                    # Chat history
│   └── Dockerfile
│
├── docker-compose.yml            # All services orchestration
├── nginx.conf                    # Reverse proxy config
├── .env.example                  # Environment variables template
├── start.bat                     # One-click launcher (Windows)
├── setup-wsl.bat                 # WSL2 setup helper (Windows)
└── README.md
```

---

## Prerequisites

- **Docker** + **Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Ollama** - [Install Ollama](https://ollama.com)
- **Git** - [Install Git](https://git-scm.com/)
- **Python 3.10+**

---

## Quick Start

### 1. Install and start Ollama

```bash
# Install Ollama, then pull models
ollama pull qwen2.5:3b
ollama pull nomic-embed-text

# Start Ollama server
ollama serve
```

### 2. Start Weaviate

```bash
docker run -d -p 8080:8080 -p 50051:50051 --name weaviate semitechnologies/weaviate:latest
```

### 3. Install Python dependencies

```bash
# Employee service
cd employee-management
pip install fastmcp fastapi uvicorn bcrypt jira aiohttp pandas python-dotenv requests "weaviate-client==3.26.7"

# Frontend
cd ../app
pip install streamlit httpx requests aiohttp python-dotenv
```

### 4. Ingest data into Weaviate

```bash
cd employee-management
python scripts/fast_ingest.py
```

This creates 20 employee records with leave balances and login credentials.

### 5. Start all services

```bash
# Terminal 1 - MCP Server
cd employee-management
python scripts/server.py

# Terminal 2 - Employee Client
cd employee-management/client
python main.py

# Terminal 3 - Frontend
cd app
python -m streamlit run main.py --server.port 8501
```

Or on Windows, double-click **`start.bat`**.

### 6. Login

Navigate to **http://localhost:8501** and login with:

| Employee ID | Password |
|---|---|
| 101 | demo123 |
| 102 | demo123 |
| ... | ... |
| 120 | demo123 |

---

## How It Works

### User Query Flow

1. User types a message in the Streamlit chat interface
2. The frontend sends the query to the FastAPI backend
3. The LLM (Qwen 2.5) analyzes intent and determines which MCP tools to use
4. The MCP client invokes the selected tools via MCP SSE protocol
5. Tool results (from Weaviate) are returned to the LLM for reasoning
6. If multiple tools are needed, the agentic loop continues
7. A final natural-language response is generated and displayed

### Agentic Tool Selection

The system uses a prompt-engineered reasoning pipeline:

1. **Intent Classification** - LLM determines if the query is employee-related, food-related, or general
2. **Tool Selection** - Based on intent, the LLM selects the appropriate MCP tool(s)
3. **Parameter Extraction** - LLM extracts required parameters from the query
4. **Tool Execution** - MCP client calls the tool, which queries Weaviate
5. **Response Generation** - LLM synthesizes tool results into a natural response

### Semantic Search (Food)

1. User query is converted to a 768-dim vector embedding using Nomic
2. Weaviate performs near-vector similarity search
3. Results are filtered by structured attributes (price, calories, protein)
4. Matching food items are returned and formatted by the LLM

### MCP Protocol

The Model Context Protocol (MCP) provides a standardized interface between the LLM and external tools:

- **MCP Server** exposes tools with defined input/output schemas
- **MCP Client** discovers available tools and invokes them
- **LLM** decides which tools to call based on user intent
- Tool outputs feed back into the LLM for next-step reasoning

---

## Services

| Service | Port | Description |
|---|---|---|
| Weaviate | 8080, 50051 | Vector database |
| Ollama | 11434 | LLM + Embeddings |
| Employee MCP Server | 8005 | Employee, Leave, Jira tools |
| Employee Client | 5000 | Employee REST API |
| Food App | 8000 | Food search + ingestion |
| Food MCP Server | 8123 | Food semantic search tools |
| Food MCP Client | 7123 | Food agent API |
| Streamlit Frontend | 8501 | User interface |

---

## Example Queries

### Workplace
- "How many leaves do I have remaining?"
- "Apply for leave from Monday to Wednesday"
- "Draft an email to my manager requesting leave"
- "Show me my open Jira tickets"
- "What team am I on?"
- "Who is my manager?"

### Food
- "Find me a high-protein meal under 300 rupees"
- "Recommend low-calorie dishes near me"
- "I want something vegetarian with high protein"
- "Find a meal containing paneer under 250 rupees"
- "Show me restaurants nearby with budget-friendly meals"

---

## License

This project is for educational and demonstration purposes.
