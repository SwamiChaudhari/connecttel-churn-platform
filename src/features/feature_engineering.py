"""
Phase 5: Feature Engineering
Creates advanced business features for churn prediction.
"""
import pandas as pd
import numpy as np
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "connecttel_churn_clean.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "connecttel_churn_engineered.csv")


def engineer_features(df):
    """Create advanced business-driven features."""
    print("=== Phase 5: Feature Engineering ===")

    df = df.copy()

    # 1. Average Monthly Charge (TotalCharges / tenure, handling tenure=0)
    df["avg_monthly_charge"] = np.where(
        df["tenure"] == 0,
        df["MonthlyCharges"],
        df["TotalCharges"] / df["tenure"]
    ).round(2)

    print(f"  [1] avg_monthly_charge: avg spend per active month")

    # 2. Charge Tenure Ratio (Monthly vs Average)
    df["charge_tenure_ratio"] = (df["MonthlyCharges"] / (df["avg_monthly_charge"] + 1e-6)).round(3)
    print(f"  [2] charge_tenure_ratio: >1 means recent charges increased vs lifetime avg")

    # 3. Customer Lifetime Value (CLV) approximation
    df["customer_lifetime_value"] = (df["MonthlyCharges"] * df["tenure"]).round(2)
    print(f"  [3] customer_lifetime_value: total revenue generated so far")

    # 4. Engagement Score (0-100, based on services subscribed)
    binary_service_cols = [
        "PhoneService", "MultipleLines", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"
    ]

    def map_service(val):
        return 1 if val == "Yes" else 0

    service_matrix = df[binary_service_cols].apply(lambda col: col.map(map_service))
    df["internet_flag"] = (df["InternetService"] != "No").astype(int)
    service_total = service_matrix.sum(axis=1) + df["internet_flag"]
    max_services = len(binary_service_cols) + 1
    df["engagement_score"] = ((service_total / max_services) * 100).round(1)
    df.drop("internet_flag", axis=1, inplace=True)
    print(f"  [4] engagement_score: 0-100, based on number of services subscribed")

    # 5. Service Utilization Score (weighted)
    weights = {
        "PhoneService": 1, "MultipleLines": 1, "OnlineSecurity": 2,
        "OnlineBackup": 2, "DeviceProtection": 1, "TechSupport": 2,
        "StreamingTV": 1, "StreamingMovies": 1
    }
    weighted_sum = sum(
        df[col].apply(lambda x: weight if x == "Yes" else 0)
        for col, weight in weights.items()
    )
    internet_weight = 3
    weighted_sum += (df["InternetService"] != "No").astype(int) * internet_weight
    max_weighted = sum(weights.values()) + internet_weight
    df["service_utilization_score"] = ((weighted_sum / max_weighted) * 100).round(1)
    print(f"  [5] service_utilization_score: weighted score (premium services count more)")

    # 6. Contract Risk Score (0=low risk, 1=high risk)
    contract_risk = {"Month-to-month": 1.0, "One year": 0.3, "Two year": 0.1}
    df["contract_risk_score"] = df["Contract"].map(contract_risk).round(2)
    print(f"  [6] contract_risk_score: Month-to-month=1.0, Two year=0.1")

    # 7. Loyalty Score (based on tenure + contract + services)
    tenure_norm = np.clip(df["tenure"] / 72, 0, 1)
    contract_loyalty = 1 - df["contract_risk_score"]
    engagement_norm = df["engagement_score"] / 100
    df["loyalty_score"] = ((tenure_norm * 0.4 + contract_loyalty * 0.4 + engagement_norm * 0.2) * 100).round(1)
    print(f"  [7] loyalty_score: composite of tenure(40%) + contract(40%) + engagement(20%)")

    # 8. Churn Risk Index (heuristic composite)
    low_tenure = (df["tenure"] < 12).astype(float) * 30
    high_charges = (df["MonthlyCharges"] > df["MonthlyCharges"].quantile(0.75)).astype(float) * 20
    low_engagement = (df["engagement_score"] < 30).astype(float) * 25
    high_contract_risk = (df["contract_risk_score"] > 0.5).astype(float) * 25
    df["churn_risk_index"] = (low_tenure + high_charges + low_engagement + high_contract_risk).round(1)
    print(f"  [8] churn_risk_index: heuristic-based (0-100), pre-ML risk estimate")

    # 9. Tenure Group (categorical)
    df["tenure_group"] = pd.cut(
        df["tenure"],
        bins=[0, 6, 12, 24, 48, 72],
        labels=["0-6", "6-12", "12-24", "24-48", "48+"],
        include_lowest=True
    )
    print(f"  [9] tenure_group: categorical tenure bucket")

    # 10. Is New Customer (binary)
    df["is_new_customer"] = (df["tenure"] <= 3).astype(int)
    print(f"  [10] is_new_customer: 1 if tenure <= 3 months")

    # 11. AutoPay Flag
    df["has_autopay"] = df["PaymentMethod"].str.contains("automatic", case=False).astype(int)
    print(f"  [11] has_autopay: 1 if payment method is automatic")

    # 12. Fiber Flag
    df["has_fiber"] = (df["InternetService"] == "Fiber optic").astype(int)
    print(f"  [12] has_fiber: 1 if fiber optic internet")

    new_features = [
        "avg_monthly_charge", "charge_tenure_ratio", "customer_lifetime_value",
        "engagement_score", "service_utilization_score", "contract_risk_score",
        "loyalty_score", "churn_risk_index", "tenure_group", "is_new_customer",
        "has_autopay", "has_fiber"
    ]
    print(f"\n  Total new features: {len(new_features)}")
    print(f"  Final shape: {df.shape}")

    return df


def run_feature_engineering():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.read_csv(INPUT_PATH)
    df_engineered = engineer_features(df)
    df_engineered.to_csv(OUTPUT_PATH, index=False)
    print(f"\nEngineered dataset saved to: {OUTPUT_PATH}")
    return df_engineered


if __name__ == "__main__":
    run_feature_engineering()
