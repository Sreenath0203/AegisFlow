import pandas as pd


def engineer_supplier_features(df: pd.DataFrame):
    df = df.copy()

    df["risk_score"] = (
        100
        - df["reliability_score"]
        + (df["delivery_days"] * 2)
    )

    return df


def engineer_logistics_features(df: pd.DataFrame):
    df = df.copy()

    df["shipment_risk"] = df["delay_days"] * 10

    return df