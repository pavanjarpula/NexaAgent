"""Fast ingestion - creates 20 employees directly in Weaviate (no embeddings needed)"""
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import weaviate
import datetime
from config.settings import settings

client = weaviate.Client(url=settings.WEAVIATE_URL)
print("Connected to Weaviate!")

# Drop and recreate all schemas
for cls in ["Employee", "EmployeeLeavesRemaining", "LeaveApplication", "JiraTicket", "Employeelogin"]:
    try:
        client.schema.delete_class(cls)
    except:
        pass

# Schema definitions
employee_schema = {
    "class": "Employee", "vectorizer": "none",
    "properties": [
        {"name": "empId", "dataType": ["string"]},
        {"name": "empName", "dataType": ["string"]},
        {"name": "empEmail", "dataType": ["string"]},
        {"name": "managerId", "dataType": ["string"]},
        {"name": "managerName", "dataType": ["string"]},
        {"name": "managerEmail", "dataType": ["string"]},
        {"name": "team", "dataType": ["string"]},
        {"name": "designation", "dataType": ["string"]},
        {"name": "phoneNumber", "dataType": ["string"]},
    ]
}

leaves_schema = {
    "class": "EmployeeLeavesRemaining", "vectorizer": "none",
    "properties": [
        {"name": "employeeId", "dataType": ["string"]},
        {"name": "casualLeave", "dataType": ["int"]},
        {"name": "sickLeave", "dataType": ["int"]},
        {"name": "compOff", "dataType": ["int"]},
        {"name": "accuredLeave", "dataType": ["int"]},
    ]
}

leave_app_schema = {
    "class": "LeaveApplication", "vectorizer": "none",
    "properties": [
        {"name": "employeeId", "dataType": ["string"]},
        {"name": "leaveType", "dataType": ["string"]},
        {"name": "startDate", "dataType": ["string"]},
        {"name": "endDate", "dataType": ["string"]},
        {"name": "status", "dataType": ["string"]},
        {"name": "reason", "dataType": ["string"]},
    ]
}

login_schema = {
    "class": "Employeelogin", "vectorizer": "none",
    "properties": [
        {"name": "employeeId", "dataType": ["string"]},
        {"name": "passwordHash", "dataType": ["string"]},
    ]
}

for s in [employee_schema, leaves_schema, leave_app_schema, login_schema]:
    client.schema.create_class(s)
print("All schemas created!")

import bcrypt

employees = [
    {"empId": "101", "empName": "Pavan Jarpula", "empEmail": "pavan.jarpula@company.com", "managerId": "501", "managerName": "Rajesh Kumar", "managerEmail": "rajesh.kumar@company.com", "team": "Software Engineering", "designation": "Software Engineer", "phoneNumber": "+91-9876543210"},
    {"empId": "102", "empName": "Aashi Manne", "empEmail": "aashi.manne@company.com", "managerId": "501", "managerName": "Rajesh Kumar", "managerEmail": "rajesh.kumar@company.com", "team": "Software Engineering", "designation": "Senior Engineer", "phoneNumber": "+91-9876543211"},
    {"empId": "103", "empName": "Shaurya Tailor", "empEmail": "shaurya.tailor@company.com", "managerId": "502", "managerName": "Priya Sharma", "managerEmail": "priya.sharma@company.com", "team": "Cloud", "designation": "Cloud Architect", "phoneNumber": "+91-9876543212"},
    {"empId": "104", "empName": "Vanya Mukhopadhyay", "empEmail": "vanya.m@company.com", "managerId": "502", "managerName": "Priya Sharma", "managerEmail": "priya.sharma@company.com", "team": "Cloud", "designation": "DevOps Engineer", "phoneNumber": "+91-9876543213"},
    {"empId": "105", "empName": "Tanveer Manne", "empEmail": "tanveer.m@company.com", "managerId": "503", "managerName": "Amit Patel", "managerEmail": "amit.patel@company.com", "team": "Framework", "designation": "Framework Developer", "phoneNumber": "+91-9876543214"},
    {"empId": "106", "empName": "Falguni Kannan", "empEmail": "falguni.k@company.com", "managerId": "503", "managerName": "Amit Patel", "managerEmail": "amit.patel@company.com", "team": "Framework", "designation": "UI Developer", "phoneNumber": "+91-9876543215"},
    {"empId": "107", "empName": "Zayan Bhakta", "empEmail": "zayan.b@company.com", "managerId": "501", "managerName": "Rajesh Kumar", "managerEmail": "rajesh.kumar@company.com", "team": "Software Engineering", "designation": "Backend Developer", "phoneNumber": "+91-9876543216"},
    {"empId": "108", "empName": "Harinakshi Deep", "empEmail": "harinakshi.d@company.com", "managerId": "504", "managerName": "Neha Gupta", "managerEmail": "neha.gupta@company.com", "team": "B2B", "designation": "Business Analyst", "phoneNumber": "+91-9876543217"},
    {"empId": "109", "empName": "Anika Khosla", "empEmail": "anika.k@company.com", "managerId": "504", "managerName": "Neha Gupta", "managerEmail": "neha.gupta@company.com", "team": "B2B", "designation": "Product Manager", "phoneNumber": "+91-9876543218"},
    {"empId": "110", "empName": "Lakshit Gole", "empEmail": "lakshit.g@company.com", "managerId": "505", "managerName": "Suresh Reddy", "managerEmail": "suresh.reddy@company.com", "team": "System", "designation": "System Engineer", "phoneNumber": "+91-9876543219"},
    {"empId": "111", "empName": "Rishi Sehgal", "empEmail": "rishi.s@company.com", "managerId": "505", "managerName": "Suresh Reddy", "managerEmail": "suresh.reddy@company.com", "team": "System", "designation": "Infrastructure Engineer", "phoneNumber": "+91-9876543220"},
    {"empId": "112", "empName": "Devansh Parekh", "empEmail": "devansh.p@company.com", "managerId": "501", "managerName": "Rajesh Kumar", "managerEmail": "rajesh.kumar@company.com", "team": "Software Engineering", "designation": "Full Stack Developer", "phoneNumber": "+91-9876543221"},
    {"empId": "113", "empName": "Madhavi Pau", "empEmail": "madhavi.p@company.com", "managerId": "503", "managerName": "Amit Patel", "managerEmail": "amit.patel@company.com", "team": "Framework", "designation": "QA Engineer", "phoneNumber": "+91-9876543222"},
    {"empId": "114", "empName": "Brinda Raghavan", "empEmail": "brinda.r@company.com", "managerId": "502", "managerName": "Priya Sharma", "managerEmail": "priya.sharma@company.com", "team": "Cloud", "designation": "SRE", "phoneNumber": "+91-9876543223"},
    {"empId": "115", "empName": "Ikbal Misra", "empEmail": "ikbal.m@company.com", "managerId": "504", "managerName": "Neha Gupta", "managerEmail": "neha.gupta@company.com", "team": "Digital Health", "designation": "Data Analyst", "phoneNumber": "+91-9876543224"},
    {"empId": "116", "empName": "Sai Pandit", "empEmail": "sai.p@company.com", "managerId": "505", "managerName": "Suresh Reddy", "managerEmail": "suresh.reddy@company.com", "team": "Visual Solution", "designation": "UI/UX Designer", "phoneNumber": "+91-9876543225"},
    {"empId": "117", "empName": "Zinal Ramesh", "empEmail": "zinal.r@company.com", "managerId": "501", "managerName": "Rajesh Kumar", "managerEmail": "rajesh.kumar@company.com", "team": "Software Engineering", "designation": "Tech Lead", "phoneNumber": "+91-9876543226"},
    {"empId": "118", "empName": "Falguni Kala", "empEmail": "falguni.kala@company.com", "managerId": "503", "managerName": "Amit Patel", "managerEmail": "amit.patel@company.com", "team": "Framework", "designation": "ML Engineer", "phoneNumber": "+91-9876543227"},
    {"empId": "119", "empName": "Yachana Gour", "empEmail": "yachana.g@company.com", "managerId": "502", "managerName": "Priya Sharma", "managerEmail": "priya.sharma@company.com", "team": "Cloud", "designation": "Cloud Engineer", "phoneNumber": "+91-9876543228"},
    {"empId": "120", "empName": "Niharika Tella", "empEmail": "niharika.t@company.com", "managerId": "504", "managerName": "Neha Gupta", "managerEmail": "neha.gupta@company.com", "team": "People Group", "designation": "HR Manager", "phoneNumber": "+91-9876543229"},
]

with client.batch as batch:
    batch.batch_size = 50
    for emp in employees:
        batch.add_data_object(data_object=emp, class_name="Employee")
print(f"Ingested {len(employees)} employees!")

# Leaves
with client.batch as batch:
    batch.batch_size = 50
    for emp in employees:
        leaves = {
            "employeeId": emp["empId"],
            "casualLeave": 12,
            "sickLeave": 8,
            "compOff": 4,
            "accuredLeave": 15,
        }
        batch.add_data_object(data_object=leaves, class_name="EmployeeLeavesRemaining")
print("Ingested leave records!")

# Login credentials (demo / demo123)
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw("demo123".encode('utf-8'), salt).decode('utf-8')

with client.batch as batch:
    batch.batch_size = 50
    for emp in employees:
        cred = {"employeeId": emp["empId"], "passwordHash": hashed}
        batch.add_data_object(data_object=cred, class_name="Employeelogin")
print("Ingested login credentials!")

# Verify
result = client.query.aggregate("Employee").with_meta_count().do()
count = result['data']['Aggregate']['Employee'][0]['meta']['count']
print(f"\nTotal employees in Weaviate: {count}")
print("Done! Use Employee ID 101-120 with password 'demo123' to login.")
