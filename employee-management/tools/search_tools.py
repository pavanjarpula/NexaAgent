import weaviate
from typing import List
from config.settings import settings
from services.nomic_service import NomicEmbeddingClient

class SearchTools:
    """Tools for search operations"""
    
    def __init__(self):
        self.weaviate_client = weaviate.Client(url=settings.WEAVIATE_URL)
        self.nomic_client = NomicEmbeddingClient()
    
    def semantic_search_employees(self, query: str, limit: int = 5, certainty: float = 0.7) -> str:
        """Perform semantic search on employee data using natural language queries"""
        try:
            query_vector = self.nomic_client.get_single_embedding(query)
            
            result = (
                self.weaviate_client.query
                .get("Employee", [
                    "empId", "empName", "empEmail", "managerId", 
                    "managerName", "managerEmail", "team", 
                    "designation", "phoneNumber"
                ])
                .with_near_vector({
                    "vector": query_vector,
                    "certainty": certainty
                })
                .with_limit(limit)
                .do()
            )
            
            employees = result.get("data", {}).get("Get", {}).get("Employee", [])
            
            if not employees:
                return f"No employees found matching query: '{query}' with certainty >= {certainty}"
            
            formatted_results = []
            for i, emp in enumerate(employees, 1):
                emp_info = f"""
                            **Employee {i}:**
                            - **ID:** {emp.get('empId', 'N/A')}
                            - **Name:** {emp.get('empName', 'N/A')}
                            - **Email:** {emp.get('empEmail', 'N/A')}
                            - **Designation:** {emp.get('designation', 'N/A')}
                            - **Team:** {emp.get('team', 'N/A')}
                            - **Manager:** {emp.get('managerName', 'N/A')} ({emp.get('managerId', 'N/A')})
                            - **Manager Email:** {emp.get('managerEmail', 'N/A')}
                            - **Phone:** {emp.get('phoneNumber', 'N/A')}
                            """
                formatted_results.append(emp_info)
            
            response_text = f"Found {len(employees)} employees matching '{query}':\n\n" + "\n".join(formatted_results)
            return response_text
            
        except Exception as e:
            return f"Error performing semantic search: {str(e)}"
