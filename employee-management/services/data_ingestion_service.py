import weaviate
import pandas as pd
from typing import List
from models.data_models import EmployeeData
from services.weaviate_service import WeaviateService
from services.nomic_service import NomicEmbeddingClient
from utils.csv_utils import read_csv_data

class DataIngestionService:
    """Service for data ingestion operations"""
    
    def __init__(self, weaviate_service: WeaviateService, nomic_client: NomicEmbeddingClient):
        self.weaviate_service = weaviate_service
        self.nomic_client = nomic_client
    
    def create_embedding_text(self, row: pd.Series) -> str:
        """Create a text representation for embedding generation"""
        return f"Employee: {row['empName']}, Designation: {row['designation']}, Team: {row['team']}, Email: {row['empEmail']}, Manager: {row['managerName']}, Manager ID: {row['managerId']}"
    
    def ingest_data_to_weaviate(self, df: pd.DataFrame) -> bool:
        """Ingest employee data with Nomic embeddings into Weaviate"""
        
        if df.empty:
            print("No data to ingest")
            return False
        
        # Prepare texts for embedding
        embedding_texts = [self.create_embedding_text(row) for _, row in df.iterrows()]
        
        print(f"Generating embeddings for {len(embedding_texts)} texts...")
        embeddings = self.nomic_client.get_embeddings(embedding_texts)
        
        if not embeddings:
            print("Failed to generate embeddings. Aborting ingestion.")
            return False
        
        if len(embeddings) != len(df):
            print(f"Mismatch: {len(embeddings)} embeddings for {len(df)} records")
            return False
        
        print(f"Generated {len(embeddings)} embeddings successfully")
        
        success_count = 0
        failed_count = 0
        
        with self.weaviate_service.client.batch as batch:
            batch.batch_size = 1
            batch.dynamic = True
            
            for idx, (_, row) in enumerate(df.iterrows()):
                try:
                    employee_data = EmployeeData.from_series(row)
                    data_object = {
                        "empId": employee_data.empId,
                        "empName": employee_data.empName,
                        "empEmail": employee_data.empEmail,
                        "managerId": employee_data.managerId,
                        "managerName": employee_data.managerName,
                        "managerEmail": employee_data.managerEmail,
                        "team": employee_data.team,
                        "designation": employee_data.designation,
                        "phoneNumber": employee_data.phoneNumber
                    }
                    
                    if not data_object["empId"] or data_object["empId"] in ["", "NAN", "NONE"]:
                        print(f"Skipping row {idx}: Empty employee ID")
                        continue
                    
                    batch.add_data_object(
                        data_object=data_object,
                        class_name="Employee",
                        vector=embeddings[idx],
                        uuid=weaviate.util.generate_uuid5(data_object["empId"])
                    )
                    success_count += 1
                    
                    if (idx + 1) % 50 == 0:
                        print(f"Processed {idx + 1} records...")
                    
                except Exception as e:
                    print(f"Error adding object {idx}: {e}")
                    failed_count += 1
        
        print(f"Ingestion completed: {success_count} successful, {failed_count} failed")
        return success_count > 0
