import weaviate
from typing import Optional
from config.settings import settings
import bcrypt
from fastapi import FastAPI, HTTPException

class EmployeeTools:
    """Tools for employee-related operations"""
    
    def __init__(self):
        self.weaviate_client = weaviate.Client(url=settings.WEAVIATE_URL)
    
    def get_employee_details(self, emp_id: str):
        """Get detailed information about a specific employee by ID"""
        emp_id = emp_id.upper().strip()
        
        try:
            result = (
                self.weaviate_client.query
                .get("Employee", [
                    "empId", "empName", "empEmail", "managerId",
                    "managerName", "managerEmail", "team",
                    "designation", "phoneNumber"
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
            emp_details = {
                            "EMP_ID":{emp.get('empId', 'N/A')},
                            "Name":{emp.get('empName', 'N/A')},
                            "Email":{emp.get('empEmail', 'N/A')},
                            "Designation":{emp.get('designation', 'N/A')},
                            "Team":{emp.get('team', 'N/A')},
                            "Manager":{emp.get('managerName', 'N/A')},
                            "ManagerID": ({emp.get('managerId', 'N/A')}),
                            "ManagerEmail":{emp.get('managerEmail', 'N/A')},
                            "Phone":{emp.get('phoneNumber', 'N/A')}
            }
            
            return emp_details
            
        except Exception as e:
            return f"Error retrieving employee details: {str(e)}"


    def register_employee(self, emp_id : str, password : str):
        """Registers user with its employee id and password"""
        try:
            result = (
                self.weaviate_client.query
                .get("Employeelogin", [
                    "employeeId"
                ])
                .with_where({
                    "path": ["employeeId"],
                    "operator": "Equal",
                    "valueText": emp_id
                })
                .with_limit(1)
                .do()
            )
            if result and result.get("data", {}).get("Get", {}).get("Employeelogin"):
                return False
            salt = bcrypt.gensalt()
            pswrd = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            emp_obj ={
                "employeeId": emp_id,
                "passwordHash": pswrd
            }
            result = self.weaviate_client.data_object.create(
                data_object=emp_obj,
                class_name="Employeelogin"
            )
            return True
        except Exception as e:
            return f"Error Registering Employee: {str(e)}"
        

    def login_employee(self, emp_id : str, password: str):
        """Logins  employee with employee id and password"""
        try:
            result = (
                self.weaviate_client.query
                .get("Employeelogin", [
                    "employeeId","passwordHash"
                ])
                .with_where({
                    "path": ["employeeId"],
                    "operator": "Equal",
                    "valueText": emp_id
                })
                .with_limit(1)
                .do()
            )
            if not result or (not result.get("data", {}).get("Get", {}).get("Employeelogin")):
                return False
            stored_pass = result.get("data", {}).get("Get", {}).get("Employeelogin")[0]
            return bcrypt.checkpw(password.encode('utf-8'), stored_pass["passwordHash"].encode('utf-8'))
        except Exception as e:
            return f"Error login Employee: {str(e)}"