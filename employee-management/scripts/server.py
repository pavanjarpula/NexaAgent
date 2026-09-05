"""MCP Server with FastMCP for Weaviate semantic search"""
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from fastmcp import FastMCP                       # pyright: ignore[reportMissingImports]
# from mcp.server.fastmcp import FastMCP              # pyright: ignore[reportMissingImports]
from tools.employee_tools import EmployeeTools
from tools.leave_tools import LeaveTools
from tools.search_tools import SearchTools
from tools.jira_tools import JiraTools 

# Initialize FastMCP server
mcp = FastMCP("server")

# Initialize tool classes
employee_tools = EmployeeTools()
leave_tools = LeaveTools()
search_tools = SearchTools()
jira_tools = JiraTools()
# @mcp.tool()
# def semantic_search_employees(query: str, limit: int = 5, certainty: float = 0.7) -> str:
#     """Perform semantic search on employee data using natural language queries"""
#     return search_tools.semantic_search_employees(query, limit, certainty)

@mcp.tool()(
        name = "get_employee_details",
        description = """
            Get exact detailed information about a specific employee by ID
            Returns:
                {ID,Name, Email, Designation, Team:, Manager, Manager Email, Phone, Manager Id}
            """
    )
def get_employee_details(emp_id: str):
    return employee_tools.get_employee_details(emp_id)

@mcp.tool()(
        name = "get_leaves_remaining",
        description ="""
            Get the number of leaves remaining for a particular employee by employee ID
            Returns:
                {Employee ID, Casual Leaves Remaining, Sick Leaves Remaining, Compensatory off Leaves Remaining, Accured Leaves Remaining} 
            """
)
def get_leaves_remaining(emp_id: str) -> str:
    return leave_tools.get_leaves_remaining(emp_id)

@mcp.tool()(
        name = "list_leave_applications",
        description = 
            """
            List of previous leaves applied by employee emp_id
            Returns:
                List of leaves applied by employee emp_id, 
            """
)
def list_leave_applications(emp_id: str, limit: int = 10):
    return leave_tools.list_leave_applications(emp_id, limit)

@mcp.tool()(
        name = "add_leave_application",
        description = 
            """
            Apply the leave of the Employee, on the basis of Employee ID, start date, end date and leave type
            Returns:
                The result if leaves are applied or not.
            """
)
def add_leave_application(emp_id: str, from_date: str, to_date: str, leave_type: int = 4) -> str:
    return leave_tools.add_leave_application(emp_id, from_date, to_date, leave_type)


@mcp.tool()(
        name = "write_leave_mail",
        description =  
            """
            This tools will run only if you know employee name for signature purpose
            Writes mail to the employee manager, but it requires manager name for salutation purpose 
            mail template:
                - Subject: Request for [type] leave
                - Body structure:
                1. Polite opening
                2. Leave dates (from-to)
                3. Brief reason (Optional)
                4. Contact availability
                5. Appreciation
                - Tone: Formal but warm
            """
)
def write_leave_mail(subject: str, body: str, emp_id : str) -> str:
    return body
# New Jira ticket tools
@mcp.tool(
    name="get_employee_jira_tickets",
    description=
    """ 
     Get all Jira tickets assigned to a specific employee by employee ID
     Returns:
        List of Jira tickets for the specified employee
    """
)
def get_employee_jira_tickets(emp_id: str, limit: int = 10) :
    return jira_tools.get_employee_jira_tickets(emp_id, limit)
    
@mcp.tool(
    name="update_jira_ticket_status",
    description=
    """
     Update the status of a specific Jira ticket for an employee
      Returns:
        Confirmation message of the status update
    """
)
def update_jira_ticket_status(ticket_id: str, new_status: int=3) -> str:
    return jira_tools.update_jira_ticket_status(ticket_id, new_status)

# @mcp.tool(
#     name="get_tickets_by_status",
#     description=
#     """
#      Get all tickets with a specific status for specific employee identified by unique employee id
#      Returns:
#         List of tickets with the specified status
#     """
# )
# def get_tickets_by_status(status: str,emp_id: str ,limit: int = 20) -> str:
#     return jira_tools.get_tickets_by_status(status, limit)

@mcp.tool(
    name = "create_jira_ticket",
    description="""
    Generate a jira ticket with a specific title, description and status.
    Returns:
        Gives ouput if ticket is created or not.
    """
)
def create_jira_ticket(title: str, description: str, status: int=3):
    return jira_tools.create_ticket(title,description,status)

@mcp.tool(
    name="add_comment_to_ticket",
    description="""
    Add comment to any existing Jira ticket identified by its unique Jira ticket ID
    """
)
def add_comment_to_ticket(ticket_id: str, comment: str):
    return jira_tools.add_comment_to_ticket(ticket_id,comment)

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8005,transport = "sse")