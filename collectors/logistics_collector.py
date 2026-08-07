from pathlib import Path
import pandas as pd

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "sample-data"

def load_logistics():
    try:
        file_path = DATA_DIR / "logistics.csv"

        logistics = pd.read_csv(file_path)

        print(f"Loaded {len(logistics)} logistics records.")

        return logistics

    except Exception as e:
        print(f"Error loading logistics: {e}")
        return None