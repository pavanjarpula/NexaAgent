import asyncio
from client_services import OllamaMCPClient
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from config.settings import Settings


async def main():
    # Initialize client
    client = OllamaMCPClient(Settings.REMOTE_OLLAMA_HOST, Settings.REMOTE_OLLAMA_PORT, Settings.MCP_SERVER_PATH)
    
    try:
        # Initialize MCP connection
        await client.initialize_mcp_connection()
        print("Connected to MCP server and Ollama")
        print(f"Available tools: {[tool['name'] for tool in client.available_tools]}\n")
        
        # Test queries
        test_queries = [
            # "Find all software engineers with employee ID 33",
            # "Who are the managers in the company?",
            # "Get details for employee ID 1",
            # "How many leaves does employee 33 have remaining?",
            # "Show me recent leave applications for employee ID 33",
            # "Who works in the engineering department?",
            # "Find all interns and their details",
            # "Apply leave for employee ID 33 from_date: 2025-06-17 to_date: 2025-06-23",
            "how many trophies rcb has won"
        ]
        
        for query in test_queries:
            print(f"Processing: {query}")
            print("=" * 60)
            response = await client.process_query(query)
            print(response)
            print("\n" + "=" * 60 + "\n")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
