from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass
class EmployeeData:
    """Data model for employee information"""
    empId: str
    empName: str
    empEmail: str
    managerId: str
    managerName: str
    managerEmail: str
    team: str
    designation: str
    phoneNumber: str
    
    @classmethod
    def from_series(cls, row: pd.Series) -> 'EmployeeData':
        """Create EmployeeData from pandas Series"""
        return cls(
            empId=str(row['empId']).strip().upper(),
            empName=str(row['empName']).strip(),
            empEmail=str(row['empEmail']).strip().lower(),
            managerId=str(row['managerId']).strip().upper(),
            managerName=str(row['managerName']).strip(),
            managerEmail=str(row['managerEmail']).strip().lower(),
            team=str(row['team']).strip(),
            designation=str(row['designation']).strip(),
            phoneNumber=str(row['phoneNumber']).strip()
        )

@dataclass
class LeaveApplicationData:
    """Data model for leave application"""
    empId: str
    numberOfLeavesApplied: int
    fromDate: str
    toDate: str
