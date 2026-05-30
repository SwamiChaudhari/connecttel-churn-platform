"""
Phase 3: Exploratory Data Analysis
Professional EDA with executive-level insights.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings
warnings.filterwarnings("ignore")

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "connecttel_churn_raw.csv")
REPORT_DIR = os.path.join(PROJECT_ROOT, "notebooks")
FIG_DIR = os.path.join(PROJECT_ROOT, "notebooks", "figures")

os.makedirs(FIG_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="husl")


def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df


def save_fig(fig, name):
    fig.savefig(os.path.join(FIG_DIR, f"{name}.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def churn_distribution(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    counts = df["Churn"].value_counts()
    axes[0].pie(counts.values, labels=counts.index, autopct="%1.1f%%",
                colors=["#2ecc71", "#e74c3c"], startangle=90, textprops={"fontsize": 12})
    axes[0].set_title("Churn Distribution", fontsize=14, fontweight="bold")

    sns.countplot(data=df, x="Churn", palette=["#2ecc71", "#e74c3c"], ax=axes[1])
    axes[1].set_title("Churn Count", fontsize=14, fontweight="bold")
    for p in axes[1].patches:
        axes[1].annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha="center", va="bottom", fontsize=12)
    fig.suptitle("Customer Churn Overview — ConnectTel", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "churn_distribution")
    churn_rate = (df["Churn"] == "Yes").mean()
    print(f"  Churn Rate: {churn_rate:.2%}")
    return churn_rate


def demographics_analysis(df):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for ax, col in zip(axes.flatten(), ["gender", "SeniorCitizen", "Partner", "Dependents"]):
        ct = pd.crosstab(df[col], df["Churn"], normalize="index")
        ct.plot(kind="bar", ax=ax, color=["#2ecc71", "#e74c3c"], edgecolor="white")
        ax.set_title(f"Churn by {col}", fontsize=12, fontweight="bold")
        ax.set_ylabel("Proportion")
        ax.legend(title="Churn")
        ax.tick_params(axis="x", rotation=0)
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", fontsize=8)

    fig.suptitle("Demographics Churn Analysis", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "demographics_analysis")
    print("  Demographics analysis saved")


def contract_tenure_analysis(df):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Contract type
    ct = pd.crosstab(df["Contract"], df["Churn"], normalize="index")
    ct.plot(kind="bar", ax=axes[0], color=["#2ecc71", "#e74c3c"], edgecolor="white")
    axes[0].set_title("Churn by Contract Type", fontweight="bold")
    axes[0].tick_params(axis="x", rotation=0)

    # Tenure distribution by churn
    for churn_val, color in [("No", "#2ecc71"), ("Yes", "#e74c3c")]:
        subset = df[df["Churn"] == churn_val]["tenure"]
        axes[1].hist(subset, bins=30, alpha=0.6, label=churn_val, color=color, edgecolor="white")
    axes[1].set_title("Tenure Distribution by Churn", fontweight="bold")
    axes[1].set_xlabel("Tenure (months)")
    axes[1].legend()

    # Monthly Charges distribution by churn
    for churn_val, color in [("No", "#2ecc71"), ("Yes", "#e74c3c")]:
        subset = df[df["Churn"] == churn_val]["MonthlyCharges"]
        axes[2].hist(subset, bins=30, alpha=0.6, label=churn_val, color=color, edgecolor="white")
    axes[2].set_title("Monthly Charges by Churn", fontweight="bold")
    axes[2].set_xlabel("Monthly Charges (₹)")
    axes[2].legend()

    fig.suptitle("Contract & Charges Analysis", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "contract_tenure_analysis")
    print("  Contract & tenure analysis saved")


def service_usage_analysis(df):
    service_cols = ["InternetService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    for i, col in enumerate(service_cols):
        ax = axes.flatten()[i]
        ct = pd.crosstab(df[col], df["Churn"], normalize="index")
        ct.plot(kind="bar", ax=ax, color=["#2ecc71", "#e74c3c"], edgecolor="white")
        ax.set_title(col, fontsize=10, fontweight="bold")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        ax.legend(fontsize=8)
    # Hide unused subplot
    axes.flatten()[7].set_visible(False)
    fig.suptitle("Service Usage & Churn", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "service_usage_analysis")
    print("  Service usage analysis saved")


def payment_analysis(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ct = pd.crosstab(df["PaymentMethod"], df["Churn"], normalize="index")
    ct.plot(kind="bar", ax=axes[0], color=["#2ecc71", "#e74c3c"], edgecolor="white")
    axes[0].set_title("Churn by Payment Method", fontweight="bold")
    axes[0].tick_params(axis="x", rotation=45)

    sns.boxplot(data=df, x="Churn", y="MonthlyCharges", ax=axes[1],
                palette=["#2ecc71", "#e74c3c"])
    axes[1].set_title("Monthly Charges by Churn", fontweight="bold")

    fig.suptitle("Payment & Charges Analysis", fontsize = 16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "payment_analysis")
    print("  Payment analysis saved")


def correlation_heatmap(df):
    numeric_df = df.select_dtypes(include=[np.number]).copy()
    numeric_df["Churn_Binary"] = (df["Churn"] == "Yes").astype(int)
    corr = numeric_df.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                square=True, linewidths=0.5, ax=ax,
                cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Heatmap", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "correlation_heatmap")
    print("  Correlation heatmap saved")


def revenue_analysis(df):
    df["RevenueLost"] = np.where(df["Churn"] == "Yes", df["MonthlyCharges"], 0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Revenue by contract
    contract_revenue = df.groupby("Contract")["RevenueLost"].sum()
    contract_revenue.plot(kind="bar", ax=axes[0], color="#e74c3c", edgecolor="white")
    axes[0].set_title("Revenue Lost by Contract Type", fontweight="bold")
    axes[0].set_ylabel("₹ Revenue Lost")
    axes[0].tick_params(axis="x", rotation=45)

    # Tenure group revenue
    df["TenureGroup"] = pd.cut(df["tenure"], bins=[0, 12, 24, 36, 72],
                               labels=["0-12", "12-24", "24-36", "36+"])
    tenure_revenue = df.groupby("TenureGroup", observed=True)["RevenueLost"].sum()
    tenure_revenue.plot(kind="bar", ax=axes[1], color="#3498db", edgecolor="white")
    axes[1].set_title("Revenue Lost by Tenure Group", fontweight="bold")
    axes[1].set_ylabel("₹ Revenue Lost")
    axes[1].tick_params(axis="x", rotation=0)

    fig.suptitle("Revenue Impact Analysis", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "revenue_analysis")
    print("  Revenue analysis saved")


def run_full_eda():
    print("=" * 60)
    print("PHASE 3: EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    df = load_data()
    print(f"\nDataset: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Data types:\n{df.dtypes}\n")

    print("\n--- Churn Distribution ---")
    churn_rate = churn_distribution(df)

    print("\n--- Demographics Analysis ---")
    demographics_analysis(df)

    print("\n--- Contract & Tenure Analysis ---")
    contract_tenure_analysis(df)

    print("\n--- Service Usage Analysis ---")
    service_usage_analysis(df)

    print("\n--- Payment Analysis ---")
    payment_analysis(df)

    print("\n--- Correlation Analysis ---")
    correlation_heatmap(df)

    print("\n--- Revenue Impact ---")
    revenue_analysis(df)

    print(f"\nAll figures saved to: {FIG_DIR}/")
    print("\n--- KEY FINDINGS FOR EXECUTIVES ---")
    print(f"1. Overall churn rate: {churn_rate:.2%}")
    print(f"2. Avg tenure (churned): {df[df['Churn']=='Yes']['tenure'].mean():.1f} months")
    print(f"3. Avg tenure (retained): {df[df['Churn']=='No']['tenure'].mean():.1f} months")
    print(f"4. Avg monthly charges (churned): ₹{df[df['Churn']=='Yes']['MonthlyCharges'].mean():.2f}")
    print(f"5. Avg monthly charges (retained): ₹{df[df['Churn']=='No']['MonthlyCharges'].mean():.2f}")
    print(f"6. Total monthly revenue at risk: ₹{df[df['Churn']=='Yes']['MonthlyCharges'].sum():,.2f}")
    return df


if __name__ == "__main__":
    run_full_eda()
