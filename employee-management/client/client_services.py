import json
import aiohttp
from fastmcp import Client
from typing import Dict, List, Any, Optional
from prompt_builder import PromptBuilder

class CustomLLMMCPClient:
    def __init__(self, llm_url: str, mcp_server_path: str):
        self.llm_url = llm_url
        self.mcp_server_path = mcp_server_path
        self.available_tools = []
        self.MAXLENGTH = 10
        self.prompt_build = PromptBuilder()
        self.chat_history = []
        
    async def initialize_mcp_connection(self):
        """Initialize connection to MCP server and get available tools"""
        self.mcp_client = Client(self.mcp_server_path)
        await self.mcp_client.__aenter__()
        
        # Get available tools
        tools = await self.mcp_client.list_tools()
        self.available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": getattr(tool, 'inputSchema', {}).get('properties', {})
            }
            for tool in tools
        ]
        
    async def call_llm(self, prompt: str) -> str:
        """Call custom LLM API with the given prompt"""
        async with aiohttp.ClientSession() as session:
            payload = {
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
                    # Adjust according to your LLM's response schema
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    raise Exception(f"LLM API error: {response.status}")

    async def execute_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool call on the MCP server"""
        try:
            result = await self.mcp_client.call_tool(tool_name, parameters)
            return result[0].text if result else "No result returned"
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def extract_json_from_response(self, llm_response: str) -> Optional[Dict[str, Any]]:
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

    async def process_query(self, user_query: str, emp_id: str) -> str:
        """Process user query using custom LLM + MCP tools"""
        try:
            tool_prompt = self.prompt_build.create_tool_prompt(user_query, self.available_tools, self.chat_history, emp_id)            
            llm_response = await self.call_llm(tool_prompt)
            tool_plan = self.extract_json_from_response(llm_response)
            print("tool_plan", tool_plan)
            results = []
            for tool_call in tool_plan.get("tool_calls", []):
                tool_name = tool_call.get("tool_name")
                parameters = tool_call.get("parameters", {})
                if tool_name in [tool["name"] for tool in self.available_tools]:
                    result = await self.execute_tool_call(tool_name, parameters)
                    results.append(f"**{tool_name}**: {result}")
                else:
                    results.append(f"**Error**: Unknown tool '{tool_name}'")
            final_prompt = self.prompt_build.build_final_response_prompt(
                user_query,
                tool_plan.get('reasoning', 'No reasoning provided'),
                results,
                self.chat_history
            )
            final_response = await self.call_llm(final_prompt)
            self.chat_history.append({"User": user_query, "Response": final_response})
            print(f"**Query**: {user_query}\n\n**Database Results**:\n{chr(10).join(results)}\n\n**AI Response**: {final_response}")
            return f"{final_response}"
        except Exception as e:
            return f"Error processing query: {str(e)}"

    async def cleanup(self):
        """Clean up MCP connection"""
        if hasattr(self, 'mcp_client'):
            await self.mcp_client.__aexit__(None, None, None)
