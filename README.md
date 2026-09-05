# NexaAgent

**Agentic Workplace & Food Assistant**

NexaAgent is an NLP-powered agentic chatbot that unifies workplace management and personalized food discovery within a single conversational interface. It understands natural-language requests, identifies intent, selects the right tools, and executes multi-step actions through an LLM-driven reasoning workflow.

---

## Features

### Workplace Assistant (WorkMate AI)
- Retrieve employee information and personal details
- Check employee leave balances
- Handle leave applications on behalf of the user
- Generate professional leave-request emails
- Create and assign Jira tickets
- Retrieve and track Jira ticket information
- Update the status of existing Jira tickets

### Food Assistant (MealMind AI)
- Recommend restaurants and dishes based on user preferences
- Semantic search over food and restaurant data
- Supports queries involving calories, protein, price, ingredients
- Combines semantic matching with structured/numeric filtering
- Supports dietary preferences (low-calorie, high-protein, budget-friendly)
- Location-based restaurant recommendations
- Place food orders and track order history

### Agentic Reasoning
- Analyzes intent and context of user queries
- Determines which tools are needed
- Executes multi-step workflows across multiple tools
- Continues reasoning loop until the task is complete
- Generates natural-language responses from tool outputs

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
│  ├── Employee          (profiles + Nomic embeddings)    │
│  ├── EmployeeLeavesRemaining  (leave balances)          │
│  ├── LeaveApplication  (leave history)                  │
│  ├── JiraTicket        (ticket storage)                 │
│  ├── EmployeeLogin     (bcrypt auth)                    │
│  ├── Foods             (food items + embeddings)        │
│  ├── EmployeeWallet    (wallet balances)                │
│  └── Orders            (food order records)             │
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
│ - Qwen 2.5 (LLM reasoning)                            │
│ - Nomic Embed Text (embeddings)                        │
└────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **LLM** | Qwen 2.5 (via Ollama) | Reasoning, intent analysis, tool selection |
| **Embeddings** | Nomic Embed Text (via Ollama) | Vector representations for semantic search |
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
└── README.md
```

---

## Prerequisites

- **Docker** + **Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Ollama** - [Install Ollama](https://ollama.com)
- **Git** - [Install Git](https://git-scm.com/)

---

## Quick Start (Docker)

### 1. Start Ollama on your machine

```bash
ollama serve
```

In a separate terminal, pull the required models:

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### 2. Clone and start services

```bash
git clone https://github.com/pavanjarpula/NexaAgent.git
cd NexaAgent
docker-compose up -d
```

### 3. Open the application

Navigate to **http://localhost:8501** in your browser.

### 4. Data Ingestion (First Time Only)

After Weaviate is running, ingest the employee data:

```bash
docker exec -it nexaagent-employee-mcp-server-1 uv run scripts/ingest.py
```

---

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.13 (employee service, frontend)
- Python 3.10 (food service)
- Ollama running locally
- Weaviate running locally

### Step 1: Start Infrastructure

```bash
# Start Ollama
ollama serve

# Start Weaviate
docker run -d -p 8080:8080 -p 50051:50051 semitechnologies/weaviate:latest
```

### Step 2: Employee Management Backend

```bash
cd employee-management

# Install dependencies
uv sync

# Run MCP Server (Terminal 1)
uv run scripts/server.py

# Run MCP Client (Terminal 2)
cd client && uv run main.py
```

### Step 3: Food Service

```bash
cd cafeteria_meal_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install "weaviate-client>=4.0.0" httpx

# Run FastAPI App (Terminal 3)
uvicorn application.main:app --port 8000

# Run MCP Server (Terminal 4)
python mcp_server/main.py

# Run MCP Client (Terminal 5)
uvicorn mcp_client.qwin_helper_main:app --port 7123
```

### Step 4: Frontend

```bash
cd app

# Install dependencies
uv sync

# Run Streamlit (Terminal 6)
uv run streamlit run main.py
```

### Step 5: Open

Navigate to **http://localhost:8501**

---

## Environment Variables

All configuration is done via environment variables. See `.env.example` for the full list.

| Variable | Default | Description |
|---|---|---|
| `WEAVIATE_URL` | `http://localhost:8080` | Weaviate server URL |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_URL` | `http://localhost:11434/v1/chat/completions` | LLM API endpoint |
| `NOMIC_API_URL` | `http://localhost:11434/api/embeddings` | Embedding API endpoint |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `BACKEND_BASE_URL` | `http://localhost:5000` | Employee backend URL |
| `FOOD_API_URL` | `http://localhost:7123/` | Food backend URL |

---

## How It Works

### User Query Flow

1. User types a message in the Streamlit chat interface
2. The query reaches the FastAPI backend
3. The LLM (Qwen) analyzes the intent and determines which tools to use
4. The MCP client invokes the selected tools via MCP protocol
5. Tool results are returned to the LLM for reasoning
6. If multiple tools are needed, the loop continues
7. A final natural-language response is generated and displayed

### Semantic Search Flow

1. User query is converted to a vector embedding using Nomic
2. Weaviate performs vector similarity search
3. Results are filtered by structured attributes (price, calories, etc.)
4. Matching food items are returned and formatted

### MCP Protocol

The Model Context Protocol (MCP) provides a standardized interface between the LLM and external tools:

- **MCP Server** exposes tools with defined inputs/outputs
- **MCP Client** discovers and invokes tools
- **LLM** decides which tools to call based on user intent
- Tool outputs feed back into the LLM for next-step reasoning

---

## Docker Services

| Service | Port | Description |
|---|---|---|
| `weaviate` | 8080, 50051 | Vector database |
| `employee-mcp-server` | 8005 | Employee MCP tools |
| `employee-mcp-client` | 5000 | Employee REST API |
| `food-app` | 8000 | Food search API |
| `food-mcp-server` | 8123 | Food MCP tools |
| `food-mcp-client` | 7123 | Food agent API |
| `frontend` | 8501 | Streamlit UI |
| `frontend-proxy` | 5000 | Nginx reverse proxy |

---

## Example Queries

### Workplace
- "How many leaves do I have remaining?"
- "Apply for leave from Monday to Wednesday"
- "Draft an email to my manager requesting leave tomorrow"
- "Show me my open Jira tickets"
- "Change the status of my Jira ticket to Done"

### Food
- "Find me a high-protein meal under 300 rupees"
- "Recommend low-calorie dishes near me"
- "I want something vegetarian with high protein"
- "Find a meal containing paneer under 250 rupees"
- "Show me restaurants nearby with budget-friendly meals"

---

## Useful Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f employee-mcp-server
```

---

## License

This project is for educational and demonstration purposes.
