"""
Phase 4: Data Cleaning Pipeline
Produces clean dataset + Data Quality Report.
"""
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Project root is 3 levels up from src/data/data_cleaning.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "connecttel_churn_raw.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "connecttel_churn_clean.csv")
REPORT_PATH = os.path.join(PROJECT_ROOT, "data", "data_quality_report.json")


def generate_quality_report(df_raw, df_clean):
    report = {
        "generated_at": datetime.now().isoformat(),
        "original_shape": list(df_raw.shape),
        "cleaned_shape": list(df_clean.shape),
        "rows_removed": len(df_raw) - len(df_clean),
        "duplicates_removed": len(df_raw) - len(df_raw.drop_duplicates()),
        "missing_values_before": df_raw.isnull().sum().to_dict(),
        "missing_values_after": df_clean.isnull().sum().to_dict(),
        "data_types": df_clean.dtypes.astype(str).to_dict(),
        "numeric_summary": {},
        "outliers_detected": {},
    }

    for col in df_clean.select_dtypes(include=[np.number]).columns:
        series = df_clean[col]
        report["numeric_summary"][col] = {
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "std": round(float(series.std()), 2),
            "min": float(series.min()),
            "max": float(series.max()),
        }
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outlier_count = ((series < lower) | (series > upper)).sum()
        report["outliers_detected"][col] = int(outlier_count)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Data Quality Report saved to: {REPORT_PATH}")
    return report


def clean_data(df):
    print("=== Phase 4: Data Cleaning ===")
    original_len = len(df)

    # 1. Remove exact duplicates
    df = df.drop_duplicates()
    print(f"  Duplicates removed: {original_len - len(df)}")

    # 2. Fix data types
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["SeniorCitizen"] = df["SeniorCitizen"].astype(int)

    # 3. Handle missing values
    missing_before = df.isnull().sum().sum()
    print(f"  Missing values before imputation: {missing_before}")

    mask_tenure_zero = (df["TotalCharges"].isnull()) & (df["tenure"] == 0)
    df.loc[mask_tenure_zero, "TotalCharges"] = df.loc[mask_tenure_zero, "MonthlyCharges"]
    df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())

    missing_after = df.isnull().sum().sum()
    print(f"  Missing values after imputation: {missing_after}")

    # 4. Numeric consistency checks
    df = df[(df["MonthlyCharges"] > 0) & (df["TotalCharges"] > 0)]
    print(f"  Rows after removing invalid charges: {len(df)}")

    # 5. Outlier capping at 1st/99th percentile
    for col in ["MonthlyCharges", "TotalCharges"]:
        low = df[col].quantile(0.01)
        high = df[col].quantile(0.99)
        df[col] = df[col].clip(low, high)
        print(f"  {col}: capped at [{low:.2f}, {high:.2f}]")

    # 6. Service consistency: when InternetService == "No", services should be "No internet service"
    no_internet = df["InternetService"] == "No"
    service_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection",
                    "TechSupport", "StreamingTV", "StreamingMovies"]
    for col in service_cols:
        inconsistent = no_internet & (df[col] != "No internet service")
        if inconsistent.sum() > 0:
            df.loc[inconsistent, col] = "No internet service"
            print(f"  Fixed {inconsistent.sum()} inconsistent {col} records")

    # 7. MultipleLines consistency
    no_phone = df["PhoneService"] == "No"
    inconsistent = no_phone & (df["MultipleLines"] != "No phone service")
    if inconsistent.sum() > 0:
        df.loc[inconsistent, "MultipleLines"] = "No phone service"
        print(f"  Fixed {inconsistent.sum()} inconsistent MultipleLines records")

    print(f"\n  Original rows: {original_len}")
    print(f"  Final clean rows: {len(df)}")
    print(f"  Churn distribution: {df['Churn'].value_counts(normalize=True).to_dict()}")
    return df


def run_data_cleaning():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_raw = pd.read_csv(DATA_PATH)
    df_clean = clean_data(df_raw)
    df_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"\nClean dataset saved to: {OUTPUT_PATH}")
    report = generate_quality_report(df_raw, df_clean)
    print(f"\n  Shape: {report['original_shape']} -> {report['cleaned_shape']}")
    print(f"  Rows removed: {report['rows_removed']}")
    print(f"  Duplicates: {report['duplicates_removed']}")
    return df_clean


if __name__ == "__main__":
    run_data_cleaning()
