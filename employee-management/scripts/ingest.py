"""Main execution script for data ingestion"""
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from config.settings import settings
from services.weaviate_service import WeaviateService
from services.nomic_service import NomicEmbeddingClient
from services.data_ingestion_service import DataIngestionService
from utils.csv_utils import read_csv_data

def main():
    """Main execution function"""
    print("Starting Employee Data Ingestion Process from CSV...")
    
    try:
        weaviate_service = WeaviateService()
        print("Connected to Weaviate successfully!")
    except Exception as e:
        print(f"Failed to connect to Weaviate: {e}")
        return
    
    nomic_client = NomicEmbeddingClient()
    data_ingestion_service = DataIngestionService(weaviate_service, nomic_client)
    
    if not weaviate_service.create_weaviate_schema():
        print("Failed to create schema. Exiting.")
        return
    
    df = read_csv_data(settings.CSV_FILE_PATH)
    if df.empty:
        print("No data to process. Exiting.")
        return
    
    if data_ingestion_service.ingest_data_to_weaviate(df):
        print("Data ingestion completed successfully!")
        weaviate_service.verify_ingestion()
    else:
        print("Data ingestion failed.")
    
    weaviate_service.create_schema2()
    weaviate_service.create_schema3()
    weaviate_service.create_and_ingest_jira_tickets()
if __name__ == "__main__":
    main()
