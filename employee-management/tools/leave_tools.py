import weaviate
from datetime import datetime, timedelta
from config.settings import settings
import numpy as np                                               

class LeaveTools:
    """Tools for leave-related operations"""
    
    def __init__(self):
        self.weaviate_client = weaviate.Client(url=settings.WEAVIATE_URL)
    
    def get_leaves_remaining(self, emp_id: str):
        """Get the number of leaves remaining for a particular employee by employee ID"""
        emp_id = str(emp_id).strip()
        
        try:
            result = (
                self.weaviate_client.query
                .get("EmployeeLeavesRemaining", ["employeeId", "casualLeave", "sickLeave", "compOff", "accuredLeave"])
                .with_where({
                    "path": ["employeeId"],
                    "operator": "Equal",
                    "valueText": emp_id
                })
                .with_limit(1)
                .do()
            )
            
            leaves_data = result.get("data", {}).get("Get", {}).get("EmployeeLeavesRemaining", [])
            
            if not leaves_data:
                
                return f"""
                **Employee Not Found:**
                - **Searched for Employee ID:** {emp_id}

                Please check if the employee ID exists in the system.
                """
            
            leave_record = leaves_data[0]
            employee_id = leave_record.get("employeeId")
            Casual_Leave = int(leave_record.get("casualLeave"))
            Sick_Leave = int(leave_record.get("sickLeave"))
            comp_Off = int(leave_record.get("compOff"))
            Accured_Leave = int(leave_record.get("accuredLeave"))
            

            return {
                    "Casual_Leaves":{Casual_Leave},
                    "Sick_Leaves": {Sick_Leave},
                    "Compensatory_Off_Leaves": {comp_Off},
                    "Accured_Leaves": {Accured_Leave}
            }
            
        except Exception as e:
            return f"Error retrieving leaves remaining: {str(e)}"
    
    def decrease_leaves_remaining(self, emp_id: str, decrement: int, leave_type : str) -> str:
        """Decrease leavesRemaining for a particular employee"""
        emp_id = emp_id.upper().strip()
        
        try:
            result = (
                self.weaviate_client.query
                .get("EmployeeLeavesRemaining", ["employeeId", leave_type])
                .with_additional(["id"])
                .with_where({
                    "path": ["employeeId"],
                    "operator": "Equal",
                    "valueText": emp_id
                })
                .with_limit(1)
                .do()
            )
            
            leaves_data = result.get("data", {}).get("Get", {}).get("EmployeeLeavesRemaining", [])
            
            if not leaves_data:
                return f"No leave record found for employee ID {emp_id}"
            
            leave_record = leaves_data[0]
            current_leaves = leave_record.get(leave_type, 0)
            new_leaves = current_leaves - decrement
            
            if new_leaves < 0:
                return [False,f"You do not have enough leaves"]
            
            obj_id = leave_record.get("_additional", {}).get("id")
            if not obj_id:
                return "Failed to get object ID for update"
            
            update_obj = {
                leave_type: new_leaves
            }
            
            self.weaviate_client.data_object.update(update_obj, "EmployeeLeavesRemaining", obj_id)
            
            return [True,f"""
                    **Leave Update Successful:**
                    - **Employee ID:** {emp_id}
                    - **Previous {leave_type} Leaves:** {current_leaves}
                    - **Decrement:** {decrement}
                    - **{leave_type} Leaves Remaining:** {new_leaves}
                    """]
            
        except Exception as e:
            return f"Error updating leaves remaining: {str(e)}"
    
    def check_duplicate_leaves(self, emp_id: str, start_date: datetime.date, end_date: datetime.date):
        """
        Checks if employee has already applied leave on that particular date or not

        Args:
        emp_id: Unique Employee Id

        Returns:
        Boolean variable if dates are correct or not.
        """
        try:
            query_builder = (
                self.weaviate_client.query
                .get("LeaveApplication", ["empId", "fromDate", "toDate"])
            )
            
            emp_id = emp_id.upper().strip()
            query_builder = query_builder.with_where({
                "path": ["empId"],
                "operator": "Equal",
                "valueText": emp_id
            })
            
            result = query_builder.do()
            applications = result.get("data", {}).get("Get", {}).get("LeaveApplication", [])
            
            for i, app in enumerate(applications, 1):
                prevStart = app.get('fromDate')
                prevEnd = app.get('toDate')
                prevStart = datetime.strptime(prevStart.split('T')[0], '%Y-%m-%d').date()
                prevEnd = datetime.strptime(prevEnd.split('T')[0], '%Y-%m-%d').date()
                if (start_date >= prevStart and start_date <= prevEnd) or (end_date >= prevStart and end_date <= prevEnd):
                    return False
            return True
        except Exception as e:
            return [e]


    def add_leave_application(self, emp_id: str,from_date: str, to_date: str, leave_type: int) -> str:
        """
        Add a new leave application record to the LeaveApplication schema
        
        Args:
            emp_id: Unique Employee Id (string)
            from_date: The start date (string)
            to_date: the end date (string)
            leave_type: The type of Leave (integer)
                - Casual Leave : 0, sick Leave: 1, Compensatory Off: 2, Accured Leave: 3
        Returns:
            The result if leaves are added to database or not.        
        """

        emp_id = emp_id.upper().strip()
        
        try:
            try:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                return "Error: Date format should be YYYY-MM-DD (e.g., 2025-06-15)"
            
            today = datetime.today().date()

            if from_date_obj.date() < today:
                return "Error: Please apply leave for upcoming days"
            if from_date_obj > to_date_obj:
                return "Error: Start date cannot be after end date"
            
            
            number_of_leaves = int(np.busday_count(from_date_obj.date(), to_date_obj.date() + timedelta(days=1)))
            if number_of_leaves <= 0:
                return "Error: There are no business days in the given range."
            
            if self.check_duplicate_leaves(emp_id=emp_id, start_date=from_date_obj.date(), end_date=to_date_obj.date()) == False:
                return f"Error: Employee Id {emp_id} have already applied leave on some of the dates."
            
            if leave_type == 0:
                leave_type = "casualLeave"
            elif leave_type == 1:
                leave_type = "sickLeave"
            elif leave_type == 2:
                leave_type = "compOff"
            elif leave_type == 3:
                leave_type = "accuredLeave"
            else:
                return f"Error: Please mention the type of leave."
            
            dec_resp = self.decrease_leaves_remaining(emp_id=emp_id, decrement=number_of_leaves, leave_type=leave_type)
            if dec_resp[0] == False:
                return dec_resp[1]
            
            from_date_rfc3339 = from_date_obj.strftime("%Y-%m-%dT00:00:00Z")
            to_date_rfc3339 = to_date_obj.strftime("%Y-%m-%dT00:00:00Z")
            
            leave_application = {
                "empId": emp_id,
                "numberOfLeavesApplied": number_of_leaves,
                "fromDate": from_date_rfc3339,
                "toDate": to_date_rfc3339,
                "leaveType": leave_type
            }

            result = self.weaviate_client.data_object.create(
                data_object=leave_application,
                class_name="LeaveApplication"
            )
            
            leave_duration = (to_date_obj - from_date_obj).days + 1
            
            return f"""
                    **Leave Applied Successfully:**
                    - **Employee ID:** {emp_id}
                    - **From Date:** {from_date}
                    - **To Date:** {to_date}
                    - **Number of business days in this duration:** {number_of_leaves}
                    - **Leave Type:** {leave_type}
                    """
            
        except Exception as e:
            return f"Error adding leave application: {str(e)}"
    
    def list_leave_applications(self, emp_id: str, limit: int = 10):
        """
        List applied leaves filtered on the basis of Employee Id
        
        Args:
            emp_id: Unique Employee Id (string)
            limit: The maximum number of entries to be retrieved (integer)

        Returns:
            The applied leave entries if exist.
        """
        try:
            emp_id = emp_id.upper().strip()
            query_builder = (
                self.weaviate_client.query
                .get("LeaveApplication", ["empId", "numberOfLeavesApplied", "fromDate", "toDate", "leaveType"])
                .with_where({
                "path": ["empId"],
                "operator": "Equal",
                "valueText": emp_id
                })
                .with_limit(limit)
            )
            
            result = query_builder.do()
            applications = result.get("data", {}).get("Get", {}).get("LeaveApplication", [])
            
            if not applications:
                return []
            return applications
            # formatted_results = []
            # for i, app in enumerate(applications, 1):
            #     app_info = f"""
            #                 **Application {i}:**
            #                 - **Employee ID:** {app.get('empId', 'N/A')}
            #                 - **Leaves Applied:** {app.get('numberOfLeavesApplied', 'N/A')}
            #                 - **From Date:** {app.get('fromDate', 'N/A')}
            #                 - **To Date:** {app.get('toDate', 'N/A')}
            #                 """
            #     formatted_results.append(app_info)
            
            # filter_msg = f" for employee {emp_id}"
            # return f"Found {len(applications)} leave applications{filter_msg}:\n\n" + "\n".join(formatted_results)
           
        except Exception as e:
            return f"Error listing leave applications: {str(e)}"
