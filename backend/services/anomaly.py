
def detect_anomalies(df):
    df["anomaly"] = ((df["mq"] > 550) | (df["dust"] > 45)).astype(int)
    return df
