from pathlib import Path
import pandas as pd

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "sample-data"

def load_suppliers():
    try:
        file_path = DATA_DIR / "suppliers.csv"

        suppliers = pd.read_csv(file_path)

        print(f"Loaded {len(suppliers)} supplier records.")

        return suppliers

    except Exception as e:
        print(f"Error loading suppliers: {e}")
        return None