"""Tools for Jira ticket operations"""
from jira import JIRA
from jira.exceptions import JIRAError
from services.weaviate_service import WeaviateService

class JiraTools:
    def __init__(self):
        self.weaviate_service = WeaviateService()
        self.server_url = "https://vaibhavharit040503.atlassian.net"
        self.username = "vaibhavharit040503@gmail.com"
        self.api_token = "ATATT3xFfGF0r6qTTnPzKYoSJNui_-NW0aGue32jePTGd2SiM5kyxtlyM-ytMkkOW4ES1-aUx5MtY8BPhhQGmoPVtg4mcYQc-rxGpnp57OEkGhtMAXSBVBkVLmt4zQcNI59ylDR__etU0CacW4-CN7YrU09UveKW6ATyLtfwCWTfRLfNgp2fVVU=3E557199"
        self.project_key = "ETM"
        try:
            self.jira = JIRA(
                server=self.server_url,
                basic_auth=(self.username, self.api_token),
                timeout=10
            )
        except JIRAError as e:
            print(f"Failed to connect to Jira: {e.status_code} - {e.text}")
            raise


    def get_employee_jira_tickets(self, emp_id: str, limit: int = 10):
        """Get all Jira tickets for a specific employee"""
        try:
            result = (
                self.weaviate_service.client.query
                .get("Employee", [
                    "team"
                ])
                .with_where({
                    "path": ["empId"],
                    "operator": "Equal",
                    "valueText": emp_id
                })
                .with_limit(1)
                .do()
            )
            
            employees = result.get("data", {}).get("Get", {}).get("Employee", [])
            
            if not employees:
                return f"No employee found with ID: {emp_id}"
            
            emp = employees[0]
            try:
                jql_query = f'project = {self.project_key} ORDER BY created DESC'
                issues =  self.jira.search_issues(jql_query, maxResults=1000)
                tickets = []
                for issue_key in issues:        
                    issue =  self.jira.issue(issue_key)
                    ticket_data = {
                        "ticketId": issue.key,
                        "title": issue.fields.summary,
                        "description": issue.fields.description,
                        "status": issue.fields.status.name,
                        "assignedBy": emp["team"]
                    }
                    tickets.append(ticket_data)
                return tickets
            except JIRAError as e:
                return(f"Error getting issue {e}")
        except Exception as e:
            return f"Error retrieving Jira tickets: {str(e)}"

    def update_jira_ticket_status(self, ticket_id: str, new_status: int) -> str:
        """Update the status of a specific Jira ticket
            Args:
            emp_id: Unique Employee Id (string)
            ticket_id: Unique Ticket Id (string)
            new_status: The type of status (integer)
        Returns:
            The result if status has been updated or not """
        try:
            # Valid statuses
            if new_status == 0:
                new_status = "To Do"
            elif new_status == 1:
                new_status = "In Progress"
            elif new_status == 2:
                new_status = "Done"
            else:
                return f"Error: Please mention the new status."
            issue =  self.jira.issue(ticket_id)
            self.jira.transition_issue(issue= issue, transition=new_status)
            return f"Changed the status of {ticket_id} ticket to {new_status}"
        except Exception as e:
            return f"Error updating ticket status: {str(e)}"

    # def get_tickets_by_status(self, status: str, emp_id: str, limit: int = 20) -> str:
    #     """Get all tickets with a specific status for a specific employee"""
    #     try:
    #         result = self.weaviate_service.client.query.get(
    #             "JiraTicket", 
    #             ["ticketId", "employeeId", "title", "status", "priority", "assignedBy"]
    #         ).with_where({
    #             "operator": "And",
    #             "operands": [
    #                 {
    #                     "path": ["status"],
    #                     "operator": "Equal",
    #                     "valueString": status
    #                 },
    #                 {
    #                     "path": ["employeeId"],
    #                     "operator": "Equal",
    #                     "valueString": emp_id
    #                 }
    #             ]
    #         }).with_limit(limit).do()

    #         tickets = result.get('data', {}).get('Get', {}).get('JiraTicket', [])
            
    #         if not tickets:
    #             return f"No tickets found with status '{status}' for employee ID: {emp_id}"

    #         response = f"Tickets with status '{status}' for employee ID {emp_id}:\n\n"
    #         for ticket in tickets:
    #             response += f" {ticket['ticketId']} | Employee: {ticket['employeeId']} | {ticket['title']} | Priority: {ticket['priority']}\n"

    #         return response

    #     except Exception as e:
    #         return f"Error retrieving tickets by status and employee ID: {str(e)}"
    def create_ticket(self, title: str, description: str, status : int):
        """Creates a new jira ticket"""
        curr_status = ""
        if status == 0:
            curr_status = "To Do"
        elif status == 1:
            curr_status = "In Progress"
        elif status == 2:
            curr_status = "Done"
        else:
            return "Please provide the ticket status"
        
        issue_dict = {
            'project' : {'key': self.project_key},
            'summary' : title,
            'description' : description,
            'issuetype': {'name': 'Task'}
        }
        # issue_dict.update(kwargs)
            
        try:
            # First create the issue
            issue = self.jira.create_issue(fields=issue_dict)
            self.jira.transition_issue(
            issue=issue,
            transition=curr_status  
            )
            return {
                "key": issue.key,
                # "url": f"{self.jira.client_info()}/browse/{issue.key}",
                "title": issue.fields.summary,
                "summary": issue.fields.description
            }
        except JIRAError as e:
            return(f"Error creating issue: {e}")
    def add_comment_to_ticket(self, ticket_id: str, comment: str) -> str:
        """
        Add a new comment to a Jira ticket identified by ticket_id.

        Args:
            ticket_id (str): The unique ID of the Jira ticket.
            comment (str): The comment text to be added.

        Returns:
            str: Confirmation message or error details.
        """
        try:
            self.jira.add_comment(ticket_id, comment)
            return f"Comment added to ticket {ticket_id}."
        except JIRAError as e:
            return f"Error adding comment to ticket {ticket_id}: {e}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"