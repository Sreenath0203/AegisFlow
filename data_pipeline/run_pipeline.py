import sys
import os

# Ensure project root is in python path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from data_pipeline.processing.pipeline_exporter import run_pipeline_ingestion

if __name__ == "__main__":
    print("Executing AegisFlow Data Pipeline Ingestion...")
    result = run_pipeline_ingestion()
    print(f"Pipeline Result: {result['status']} - {result['message']}")
    print(f"Suppliers Loaded: {result.get('suppliers_count', 0)}")
    print(f"Shipments Loaded: {result.get('shipments_count', 0)}")
