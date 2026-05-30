"""
Phase 2: Synthetic Dataset Generator for ConnectTel Churn Platform
Generates a realistic telecom churn dataset with 10,000+ customers.
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)

# Project root: 3 levels up from src/data/generate_dataset.py → src/data/ → src/ → root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data")


def generate_dataset(n_customers: int = 10476) -> pd.DataFrame:
    """Generate a realistic telecom customer churn dataset."""

    customer_ids = [f"CUST-{i:05d}" for i in range(1, n_customers + 1)]

    # --- Demographics ---
    gender = np.random.choice(["Male", "Female"], n_customers)
    senior_citizen = np.random.choice([0, 1], n_customers, p=[0.84, 0.16])
    partner = np.random.choice(["Yes", "No"], n_customers, p=[0.48, 0.52])
    dependents = np.random.choice(["Yes", "No"], n_customers, p=[0.30, 0.70])

    # --- Account Info ---
    # Tenure: skewed toward lower values (newer customers churn more)
    tenure_probs = np.concatenate([np.full(12, 0.025), np.full(12, 0.018),
                                    np.full(12, 0.015), np.full(12, 0.012),
                                    np.full(12, 0.010), np.full(12, 0.008)])
    tenure_probs = tenure_probs / tenure_probs.sum()
    tenure = np.random.choice(range(1, 73), n_customers, p=tenure_probs)

    phone_service = np.random.choice(["Yes", "No"], n_customers, p=[0.90, 0.10])
    multiple_lines = np.where(
        phone_service == "Yes",
        np.random.choice(["Yes", "No"], n_customers, p=[0.42, 0.58]),
        "No phone service"
    )

    internet_service = np.random.choice(
        ["DSL", "Fiber optic", "No"], n_customers, p=[0.34, 0.44, 0.22]
    )

    # --- Services (depend on internet) ---
    def service_with_internet(n, yes_prob):
        result = []
        for i in range(n):
            if internet_service[i] == "No":
                result.append("No internet service")
            else:
                result.append("Yes" if np.random.random() < yes_prob else "No")
        return result

    online_security = service_with_internet(n_customers, 0.29)
    online_backup = service_with_internet(n_customers, 0.34)
    device_protection = service_with_internet(n_customers, 0.34)
    tech_support = service_with_internet(n_customers, 0.29)
    streaming_tv = service_with_internet(n_customers, 0.38)
    streaming_movies = service_with_internet(n_customers, 0.39)

    # --- Contract & Billing ---
    contract = np.random.choice(
        ["Month-to-month", "One year", "Two year"],
        n_customers, p=[0.55, 0.21, 0.24]
    )
    paperless_billing = np.random.choice(["Yes", "No"], n_customers, p=[0.59, 0.41])
    payment_method = np.random.choice(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        n_customers, p=[0.34, 0.23, 0.22, 0.21]
    )

    # --- Charges ---
    monthly_charges = np.round(np.random.uniform(18.25, 118.75, n_customers), 2)
    total_charges = np.round(
        np.where(
            tenure == 0,
            monthly_charges,
            monthly_charges * tenure * np.random.uniform(0.9, 1.1, n_customers)
        ), 2
    )

    # --- Churn (realistic: depends on features) ---
    churn_probability = np.zeros(n_customers)

    churn_probability += np.where(contract == "Month-to-month", 0.25, 0)
    churn_probability += np.where(contract == "One year", 0.05, 0)
    churn_probability += np.where(contract == "Two year", 0.02, 0)
    churn_probability += np.where(tenure < 12, 0.15, 0)
    churn_probability += np.where((tenure >= 12) & (tenure < 24), 0.08, 0)
    churn_probability += np.where(monthly_charges > 70, 0.10, 0)
    churn_probability += np.where(internet_service == "Fiber optic", 0.08, 0)
    churn_probability += np.where(payment_method == "Electronic check", 0.10, 0)
    churn_probability += np.where(np.array(online_security) == "Yes", -0.03, 0.05)
    churn_probability += np.where(np.array(tech_support) == "Yes", -0.03, 0.05)
    churn_probability += senior_citizen * 0.05
    churn_probability = np.clip(churn_probability, 0.05, 0.95)
    churn = np.where(np.random.random(n_customers) < churn_probability, "Yes", "No")

    total_charges_series = pd.Series(total_charges)
    missing_indices = np.random.choice(n_customers, size=int(n_customers * 0.005), replace=False)
    total_charges_series.iloc[missing_indices] = np.nan

    df = pd.DataFrame({
        "customerID": customer_ids,
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure.astype(int),
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges_series,
        "Churn": churn,
    })

    # Append a few duplicate rows
    dupes = df.sample(15, random_state=42)
    df = pd.concat([df, dupes], ignore_index=True)

    return df


def save_dataset(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "connecttel_churn_raw.csv")
    df.to_csv(path, index=False)
    print(f"Dataset saved: {len(df)} rows, {len(df.columns)} columns")
    print(f"Churn distribution:\n{df['Churn'].value_counts(normalize=True)}")
    print(f"Missing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")


if __name__ == "__main__":
    df = generate_dataset(10476)
    save_dataset(df)
