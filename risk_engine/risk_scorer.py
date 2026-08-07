import pandas as pd


def classify_supplier_risk(df: pd.DataFrame):

    df = df.copy()

    def risk(score):

        if score < 20:
            return "Low"

        elif score < 40:
            return "Medium"

        else:
            return "High"

    df["risk_level"] = df["risk_score"].apply(risk)

    return df


def classify_logistics_risk(df: pd.DataFrame):

    df = df.copy()

    def risk(score):

        if score == 0:
            return "Low"

        elif score <= 20:
            return "Medium"

        else:
            return "High"

    df["shipment_risk_level"] = df["shipment_risk"].apply(risk)

    return df