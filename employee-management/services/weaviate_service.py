import weaviate
import json
from typing import List, Dict, Any, Optional
from config.settings import settings
from models.schemas import EmployeeSchema, EmployeeLeavesRemainingSchema, LeaveApplicationSchema

class WeaviateService:
    """Service for Weaviate operations"""
    
    def __init__(self):
        self.client = weaviate.Client(url=settings.WEAVIATE_URL)
        
    
    def create_weaviate_schema(self) -> bool:
        """Create Employee schema in Weaviate with vectorizer set to none"""
        try:
            existing_schema = self.client.schema.get()
            existing_classes = [cls["class"] for cls in existing_schema.get("classes", [])]
            
            if "Employee" in existing_classes:
                print("Employee class already exists. Deleting and recreating...")
                self.client.schema.delete_class("Employee")
            
            self.client.schema.create_class(EmployeeSchema.get_schema())
            print("Employee schema created successfully!")
            return True
        except Exception as e:
            print(f"Error creating schema: {e}")
            return False
    
    def create_schema2(self) -> bool:
        """Create schema and ingest 1000 employee leave records"""
        try:
            existing_schema = self.client.schema.get()
            existing_classes = [cls["class"] for cls in existing_schema.get("classes", [])]
            if "EmployeeLeavesRemaining" in existing_classes:
                print("EmployeeLeavesRemaining class already exists. Deleting and recreating...")
                self.client.schema.delete_class("EmployeeLeavesRemaining")
            
            self.client.schema.create_class(EmployeeLeavesRemainingSchema.get_schema())
            print("Schema created successfully!")
            
            # Generate 1000 records with employee IDs 1 to 1000 and leaves remaining as 20
            data = [{
                "employeeId": str(i),
                "casualLeave": 20,
                "sickLeave": 10,
                "compOff": 4,
                "accuredLeave": 6
            } for i in range(1, 1001)]
            
            print(f"Ingesting {len(data)} records...")
            
            success_count = 0
            with self.client.batch as batch:
                batch.batch_size = 100
                batch.dynamic = True
                
                for record in data:
                    batch.add_data_object(
                        data_object=record,
                        class_name="EmployeeLeavesRemaining",
                        uuid=weaviate.util.generate_uuid5(record["employeeId"])
                    )
                    success_count += 1
            
            print(f"Data ingestion completed successfully! {success_count} records added.")
            
            # Verify ingestion
            result = self.client.query.aggregate("EmployeeLeavesRemaining").with_meta_count().do()
            count = result['data']['Aggregate']['EmployeeLeavesRemaining'][0]['meta']['count']
            print(f"Total records in Weaviate: {count}")
            
            return True
            
        except Exception as e:
            print(f"Error during data ingestion: {e}")
            return False
    
    def create_schema3(self) -> bool:
        """Create LeaveApplication schema"""
        try:
            existing_schema = self.client.schema.get()
            existing_classes = [cls["class"] for cls in existing_schema.get("classes", [])]
            
            if "LeaveApplication" in existing_classes:
                print("LeaveApplication class already exists. Deleting and recreating...")
                self.client.schema.delete_class("LeaveApplication")
            
            self.client.schema.create_class(LeaveApplicationSchema.get_schema())
            print("LeaveApplication schema created successfully!")
            return True
        except Exception as e:
            print(f"Error creating schema: {e}")
            return False
    
    def verify_ingestion(self) -> bool:
        """Verify that data was ingested correctly"""
        try:
            result = self.client.query.aggregate("Employee").with_meta_count().do()
            count = result['data']['Aggregate']['Employee'][0]['meta']['count']
            print(f"Total Employee objects in Weaviate: {count}")
            
            sample = self.client.query.get("Employee", ["empId", "empName", "designation", "team", "empEmail", "managerId", "managerName"]).with_limit(1).do()
            if sample['data']['Get']['Employee']:
                print("Sample employee record:")
                print(json.dumps(sample['data']['Get']['Employee'][0], indent=2))
            
            print("\nData is now stored and optimized for employee ID searches!")
            return True
        except Exception as e:
            print(f"Error verifying ingestion: {e}")
            return False
            
    def create_and_ingest_jira_tickets(self) -> bool:
        """Create JiraTicket schema and bulk ingest diverse Jira tickets for all employees"""
        try:
            import datetime
            import weaviate
            now = datetime.datetime.now().isoformat()
            
            # Define the JiraTicket schema inline
            jira_ticket_schema = {
                "class": "JiraTicket",
                "vectorizer": "none",
                "properties": [
                    {"name": "ticketId", "dataType": ["string"]},
                    {"name": "employeeId", "dataType": ["string"]},
                    {"name": "title", "dataType": ["string"]},
                    {"name": "description", "dataType": ["string"]},
                    {"name": "status", "dataType": ["string"]},
                    {"name": "priority", "dataType": ["string"]},
                    {"name": "assignedBy", "dataType": ["string"]},
                    {"name": "createdAt", "dataType": ["string"]},
                    {"name": "updatedAt", "dataType": ["string"]}
                ]
            }
            
            # Check existing schema and delete if exists
            existing_schema = self.client.schema.get()
            existing_classes = [cls["class"] for cls in existing_schema.get("classes", [])]
            if "JiraTicket" in existing_classes:
                print("JiraTicket class already exists. Deleting and recreating...")
                self.client.schema.delete_class("JiraTicket")
            
            # Create the JiraTicket schema
            self.client.schema.create_class(jira_ticket_schema)
            print("JiraTicket schema created successfully!")
            
            # Create diverse tickets for each employee
            ticket_templates = [
                {
                    "title": "Complete quarterly compliance training",
                    "description": "All employees must complete the Q2 compliance training module by end of month.",
                    "priority": "Medium",
                    "assignedBy": "HR Team"
                },
                {
                    "title": "Update project documentation",
                    "description": "Review and update all project documentation to reflect recent changes.",
                    "priority": "Low",
                    "assignedBy": "Project Manager"
                },
                {
                    "title": "Security access review",
                    "description": "Review and validate current security access permissions for your role.",
                    "priority": "High",
                    "assignedBy": "Security Team"
                }
            ]
            
            data = []
            for i in range(1, 1001):
                template_index = (i - 1) % len(ticket_templates)
                template = ticket_templates[template_index]
                
                ticket = {
                    "ticketId": f"JIRA-{i:04d}",
                    "employeeId": str(i),
                    "title": template["title"],
                    "description": template["description"],
                    "status": "Open" if i % 3 == 0 else ("In Progress" if i % 3 == 1 else "Resolved"),
                    "priority": template["priority"],
                    "assignedBy": template["assignedBy"],
                    "createdAt": now,
                    "updatedAt": now
                }
                data.append(ticket)
            
            print(f"Ingesting {len(data)} Jira tickets...")
            
            success_count = 0
            with self.client.batch as batch:
                batch.batch_size = 100
                batch.dynamic = True
                
                for record in data:
                    batch.add_data_object(
                        data_object=record,
                        class_name="JiraTicket",
                        uuid=weaviate.util.generate_uuid5(record["ticketId"])
                    )
                    success_count += 1
            
            print(f"Jira ticket ingestion completed! {success_count} tickets added.")
            
            # Verify ingestion
            result = self.client.query.aggregate("JiraTicket").with_meta_count().do()
            count = result['data']['Aggregate']['JiraTicket'][0]['meta']['count']
            print(f"Total Jira tickets in Weaviate: {count}")
            
            return True
        except Exception as e:
            print(f"Error during Jira ticket schema creation and ingestion: {e}")
            return False
