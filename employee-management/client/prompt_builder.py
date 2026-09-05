from typing import Dict, List, Any
from datetime import datetime

class PromptBuilder:
    @staticmethod
    def create_tool_prompt(user_query: str, available_tools: List[Dict[str, Any]], chat_history: List[str], emp_id : str) -> str:
        """Create a structured prompt for Ollama to determine tool usage"""
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}:{tool['parameters']}"
            for tool in available_tools
        ])

        previous = ""
        if chat_history:
           previous += "Previous Conversations:\n"
           for i, entry in enumerate(reversed(chat_history)): 
               previous += f"Query{i+1}: {entry['User']}\nResponse{i+1}: {entry['Response']}\n\n"
           previous += ("="*60) + "\n"
        return f"""
                Chat History : {previous}
                You are an AI assistant that helps users query.
                you may or may not use the tools as per the requirements
                You must respond with a JSON object containing your reasoning and tool calls. 

                Available tools:
                {tools_description}
                leave_type: The type of Leave (integer), do not assume leave on your own
                    - 0 : Casual Leave, 1 : sick Leave, 2 : Compensatory Off, 3 : Accured Leave, 4 : Not mentioned
                new_status: The Status of Jira (integer)
                    -0 : To Do, 1: In Progress, 2: Done, 3: Not mentioned
                Today's Date : {datetime.today().strftime("%Y-%m-%d")} and Day : {datetime.today().strftime("%A")}
                Always use dates in (%Y-%m-%d) format
                If use has not specified the dates, change dates such that k business days are covered (which does not include saturday and sunday)

                User Query: {user_query}
                Emp_ID : {emp_id}
                
                Analyze the user's query and determine which tool to use or respond without tool. Respond ONLY with a JSON object in this exact format:
                {{
                    "reasoning": "Brief explanation of your approach",
                    "tool_calls": [
                        {{
                            "tool_name": "tool_name_here",
                            "parameters": {{"param1": "value1", "param2": "value2"}}
                        }}
                    ],
                    "needs_followup": true/false
                }}
                Examples:
                - For "What is the name of employee 24": Use get_employee_details with emp_id "24"
                - For "How many leaves does employee 123 have": Use get_leaves_remaining with emp_id "123"
                - For "Show recent leave applications": Use list_leave_applications
                - For "Apply Leave for employee 123 from 2025-07-01 to 2025-07-03": use add_leave_application with emp_id "123", then start date : "2025-07-01", end date : "2025-07-03", leave_type: as mentioned in proper format.
                - For "Apply Leave for employee 123 from 2025-07-01 upto 4 days": Calculate to_date by adding "4"-1 days to 2025-07-01 then use add_leave_application with emp_id "123", from_date : 2025-07-01 and to_date : to_date, leave_type: as mentioned in proper format
                - For "Show me leave history : use list_leave_applications
                - For "Apply leave for upcoming 3 days: use list_leave_applications and do not include today's date here.
                Important:
                    1.If the Conversation_history shows that the most recent previous query had some parameter missing and the current query provides the missing parameter. You may run the previous query with missing parameter value.
                    2.Respond with valid JSON only.
                 """
                # - For "apply leave for 2 days from tomorrow": find end date such that 2 business days are covered (which does not include saturday and sunday)
    
    @staticmethod
    def build_final_response_prompt(user_query: str, reasoning: str, results: List[str], chat_history: List[str]) -> str:
        """Build prompt for final response generation"""
        
        previous = ""
        if chat_history:
            previous += "Previous Conversations:\n"
            for i, entry in enumerate(reversed(chat_history)):  
               previous += f"Query{i+1}: {entry['User']}\nResponse{i+1}: {entry['Response']}\n\n"
            previous += ("="*60) + "\n"
        
        return f"""Based on the database query results below, provide a clear, helpful answer to the user's question.

        Chat History : {previous}
        User Question: {user_query}
        Reasoning: {reasoning}
        
        Database Results:
        {chr(10).join(results)}
        Important:
         1.Provide a natural language response that directly answers the user's question based on the database results.
         2.If the database results are empty simply respond that this task is beyond the scope of your abilities,
         3.Whenever you find '\n' in your database results it simply means write in next line.
         4.Be concise and helpful:"""