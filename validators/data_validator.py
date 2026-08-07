import pandas as pd


def validate_suppliers(df: pd.DataFrame):
    errors = []

    # Reliability score should be between 0 and 100
    invalid_scores = df[
        (df["reliability_score"] < 0) |
        (df["reliability_score"] > 100)
    ]

    if not invalid_scores.empty:
        errors.append("Invalid supplier reliability scores found.")

    # Delivery days should not be negative
    invalid_delivery = df[df["delivery_days"] < 0]

    if not invalid_delivery.empty:
        errors.append("Negative delivery days found.")

    return errors


def validate_logistics(df: pd.DataFrame):
    errors = []

    # Delay days should not be negative
    invalid_delay = df[df["delay_days"] < 0]

    if not invalid_delay.empty:
        errors.append("Negative delay days found.")

    valid_status = ["On Time", "Delayed"]

    invalid_status = df[~df["status"].isin(valid_status)]

    if not invalid_status.empty:
        errors.append("Invalid shipment status found.")

    return errors