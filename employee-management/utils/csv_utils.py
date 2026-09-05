import pandas as pd

def read_csv_data(file_path: str) -> pd.DataFrame:
    """Read employee data from CSV file"""
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
        
        print(f"Original CSV columns: {list(df.columns)}")
        
        column_mapping = {
            'Id': 'empId',
            'name': 'empName',
            'email': 'empEmail',
            'manager_id': 'managerId',
            'manager_name': 'managerName',
            'manager_email': 'managerEmail',
            'team': 'team',
            'designation': 'designation',
            'phone_number': 'phoneNumber'
        }
        
        df = df.rename(columns=column_mapping)
        
        required_columns = ['empId', 'empName', 'empEmail', 'managerId', 'managerName', 'managerEmail', 'team', 'designation', 'phoneNumber']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        df = df.fillna("")
        for col in required_columns:
            df[col] = df[col].astype(str).str.strip()
        
        df = df[df['empId'] != ""]
        df = df[df['empId'].str.upper() != "NAN"]
        
        print(f"Successfully read {len(df)} employee records from CSV")
        return df[required_columns]
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame()
