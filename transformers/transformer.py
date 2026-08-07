import pandas as pd


def transform_suppliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add supplier performance categories.
    """

    df = df.copy()

    def supplier_category(score):
        if score >= 90:
            return "High"

        elif score >= 80:
            return "Medium"

        else:
            return "Low"

    df["supplier_category"] = df["reliability_score"].apply(supplier_category)

    return df


def transform_logistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add logistics delay categories.
    """

    df = df.copy()

    def delay_category(days):

        if days == 0:
            return "On Time"

        elif days <= 2:
            return "Minor Delay"

        else:
            return "Major Delay"

    df["delay_category"] = df["delay_days"].apply(delay_category)

    return df