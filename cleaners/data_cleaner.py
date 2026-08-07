import pandas as pd
from pandas.api.types import is_numeric_dtype


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans a DataFrame by:
    1. Standardizing column names
    2. Removing duplicates
    3. Filling missing values
    """

    # Create a copy
    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Fill missing values
    for col in df.columns:

        if is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())

        else:
            df[col] = df[col].fillna("Unknown")

    return df