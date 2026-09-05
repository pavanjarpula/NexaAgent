from typing import Dict, Any

class EmployeeSchema:
    """Employee schema definition for Weaviate"""
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        return {
            "class": "Employee",
            "description": "Employee data in the organization",
            "vectorizer": "none",
            "properties": [ 
                {
                    "name": "empId",
                    "dataType": ["text"],
                    "description": "Employee ID",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "empName", 
                    "dataType": ["text"],
                    "description": "Employee name",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "empEmail",
                    "dataType": ["text"],
                    "description": "Employee email address",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "managerId",
                    "dataType": ["text"],
                    "description": "Manager ID",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "managerName",
                    "dataType": ["text"],
                    "description": "Manager name",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "managerEmail",
                    "dataType": ["text"],
                    "description": "Manager email address",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "team",
                    "dataType": ["text"],
                    "description": "Team name",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "designation",
                    "dataType": ["text"], 
                    "description": "Employee designation/role",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "phoneNumber",
                    "dataType": ["text"],
                    "description": "Employee phone number",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                }
            ]
        }

class EmployeeLeavesRemainingSchema:
    """Employee leaves remaining schema definition for Weaviate"""
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        return {
            "class": "EmployeeLeavesRemaining",
            "description": "Employee leaves remaining data",
            "vectorizer": "none",
            "properties": [
                {
                    "name": "employeeId",
                    "dataType": ["text"],
                    "description": "Employee ID",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "casualLeave",
                    "dataType": ["int"],
                    "indexFilterable": True,
                    "description": "Number of Casual leaves remaining",
                },
                {
                    "name": "sickLeave",
                    "dataType": ["int"],
                    "indexFilterable": True,
                    "description": "Number of Sick leaves remaining",
                },
                {
                    "name": "compOff",
                    "dataType": ["int"],
                    "indexFilterable": True,
                    "description": "Number of Compensatory Leaves remaining",
                },
                {
                    "name": "accuredLeave",
                    "dataType": ["int"],
                    "indexFilterable": True,
                    "description": "Number of Accired leaves remaining",
                }
            ]
        }

class LeaveApplicationSchema:
    """Leave application schema definition for Weaviate"""
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        return {
            "class": "LeaveApplication",
            "description": "Employee leave application data",
            "vectorizer": "none",
            "properties": [ 
                {
                    "name": "empId",
                    "dataType": ["text"],
                    "description": "Employee ID",
                    "tokenization": "field",
                    "indexFilterable": True,
                },
                {
                    "name": "numberOfLeavesApplied",
                    "dataType": ["int"],
                    "description": "Number of leaves applied for",
                    "indexFilterable": True,
                },
                {
                    "name": "fromDate",
                    "dataType": ["date"],
                    "description": "Leave start/from date",
                    "indexFilterable": True,
                },
                {
                    "name": "toDate",
                    "dataType": ["date"],
                    "description": "Leave end/to date",
                    "indexFilterable": True,
                },
                {
                    "name": "leaveType",
                    "dataType": ["text"],
                    "description": "Type of Leave Applied",
                    "indexFilterable": True
                }
            ]
        }

class JiraTicketSchema:
    """Jira ticket schema definition for Weaviate"""
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        return {
            "class": "JiraTicket",
            "description": "Jira ticket data for employees",
            "vectorizer": "none",
            "properties": [
                {
                    "name": "ticketId", 
                    "dataType": ["text"],
                    "description": "Unique Jira ticket ID",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "employeeId", 
                    "dataType": ["text"],
                    "description": "Employee ID assigned to ticket",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "title", 
                    "dataType": ["text"],
                    "description": "Ticket title/summary",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "description", 
                    "dataType": ["text"],
                    "description": "Detailed ticket description",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "status", 
                    "dataType": ["text"],
                    "description": "Current ticket status",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "priority", 
                    "dataType": ["text"],
                    "description": "Ticket priority level",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "assignedBy", 
                    "dataType": ["text"],
                    "description": "Who assigned the ticket",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "createdAt", 
                    "dataType": ["text"],
                    "description": "Ticket creation timestamp",
                    "indexFilterable": True
                },
                {
                    "name": "updatedAt", 
                    "dataType": ["text"],
                    "description": "Last update timestamp",
                    "indexFilterable": True
                }
            ]
        }

class EmployeeLoginSchema:
    """Employee login credentials schema definition for Weaviate"""
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        return {
            "class": "EmployeeLogin",
            "description": "Employee login credentials for frontend authentication",
            "vectorizer": "none",
            "properties": [
                {
                    "name": "employeeId",
                    "dataType": ["text"],
                    "description": "Employee ID used as username",
                    "tokenization": "field",
                    "indexFilterable": True,
                    "indexSearchable": True
                },
                {
                    "name": "passwordHash",
                    "dataType": ["text"],
                    "description": "Hashed password for security",
                    "tokenization": "field",
                    "indexFilterable": False,  # Don't index passwords for security
                    "indexSearchable": False   # Don't make passwords searchable
                }
            ]
        }
