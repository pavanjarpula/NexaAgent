import pandas as pd
from typing import List, Tuple

def validate_employee_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate employee data and return validation status and errors"""
    errors = []
    
    required_columns = ['empId', 'empName', 'empEmail', 'managerId', 'managerName', 'managerEmail', 'team', 'designation', 'phoneNumber']
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
    
    # Check for empty employee IDs
    if df.empty:
        errors.append("DataFrame is empty")
    elif 'empId' in df.columns:
        empty_ids = df[df['empId'].isin(['', 'NAN', 'NONE', None])].index.tolist()
        if empty_ids:
            errors.append(f"Empty employee IDs found at rows: {empty_ids}")
    
    return len(errors) == 0, errors
