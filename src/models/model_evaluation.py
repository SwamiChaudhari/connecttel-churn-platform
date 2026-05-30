"""
Phase 7: Model Evaluation Report
Generates comprehensive evaluation metrics and visualizations.
"""
import pandas as pd
import numpy as np
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc,
    precision_recall_curve, average_precision_score
)
import joblib

MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "notebooks")
FIG_DIR = os.path.join(PROJECT_ROOT, "notebooks", "figures")
REPORT_DIR = os.path.join(PROJECT_ROOT, "docs")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")


def save_fig(fig, name):
    fig.savefig(os.path.join(FIG_DIR, f"{name}.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_evaluation_report():
    print("=== Phase 7: Model Evaluation ===")

    # Load comparison results
    results_path = os.path.join(RESULTS_DIR, "model_comparison.json")
    if not os.path.exists(results_path):
        print("  ERROR: Run ml_pipeline.py first!")
        return

    with open(results_path) as f:
        results = json.load(f)

    # --- Model Comparison Bar Chart ---
    df = pd.DataFrame(results).T
    df = df.sort_values("roc_auc", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # AUC comparison
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df)))
    axes[0].barh(df.index, df["roc_auc"], color=colors, edgecolor="white")
    axes[0].set_xlabel("ROC-AUC Score")
    axes[0].set_title("Model ROC-AUC Comparison", fontweight="bold")
    axes[0].axvline(x=0.85, color="red", linestyle="--", label="Target (0.85)")
    axes[0].legend()
    for i, (_, row) in enumerate(df.iterrows()):
        axes[0].text(row["roc_auc"] + 0.002, i, f'{row["roc_auc"]:.4f}', va="center")

    # Multi-metric comparison
    metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    df_metrics = df[metrics]
    df_metrics.plot(kind="barh", ax=axes[1], edgecolor="white", width=0.8)
    axes[1].set_title("Multi-Metric Comparison", fontweight="bold")
    axes[1].set_xlabel("Score")
    axes[1].legend(loc="lower right", fontsize=8)

    fig.suptitle("ConnectTel Churn Model Evaluation", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "model_evaluation")

    # --- Confusion Matrix for Best Model ---
    best_model_name = max(results, key=lambda k: results[k]["roc_auc"])
    safe_name = best_model_name.lower().replace(" ", "_")
    model_path = os.path.join(MODEL_DIR, f"{safe_name}.joblib")

    if os.path.exists(model_path):
        model = joblib.load(model_path)

        # Load test data
        df_data = pd.read_csv("data/connecttel_churn_engineered.csv")
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder

        df_ml = df_data.copy()
        df_ml.drop(columns=["customerID"], inplace=True, errors="ignore")
        y = (df_ml["Churn"] == "Yes").astype(int)
        X = df_ml.drop(columns=["Churn"])
        for col in X.select_dtypes(include=["object", "category"]).columns:
            X[col] = LabelEncoder().fit_transform(X[col].astype(str))

        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        # Confusion Matrix
        fig, ax = plt.subplots(figsize=(8, 6))
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                    xticklabels=["No Churn", "Churn"],
                    yticklabels=["No Churn", "Churn"])
        ax.set_ylabel("Actual")
        ax.set_xlabel("Predicted")
        ax.set_title(f"Confusion Matrix — {best_model_name}", fontweight="bold")
        fig.tight_layout()
        save_fig(fig, "confusion_matrix")

        # ROC Curve
        fig, ax = plt.subplots(figsize=(8, 6))
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc_val = auc(fpr, tpr)
        ax.plot(fpr, tpr, color="#e74c3c", lw=2,
                label=f"{best_model_name} (AUC = {roc_auc_val:.4f})")
        ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random Classifier")
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("ROC Curve", fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        save_fig(fig, "roc_curve")

        # Precision-Recall Curve
        fig, ax = plt.subplots(figsize=(8, 6))
        precision, recall, _ = precision_recall_curve(y_test, y_proba)
        ap = average_precision_score(y_test, y_proba)
        ax.plot(recall, precision, color="#3498db", lw=2,
                label=f"AP = {ap:.4f}")
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.set_title("Precision-Recall Curve", fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        save_fig(fig, "pr_curve")

        # Classification Report
        from sklearn.metrics import classification_report
        report = classification_report(y_test, y_pred, target_names=["No Churn", "Churn"])
        print(f"\nClassification Report:\n{report}")

    # --- Generate Markdown Report ---
    report = f"""# Phase 7: Model Evaluation Report
**ConnectTel Churn Prediction Platform**
Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}

---

## Executive Summary

| Model | ROC-AUC | Accuracy | Precision | Recall | F1 Score | CV AUC (mean ± std) |
|---|---|---|---|---|---|---|
"""
    for name, metrics in sorted(results.items(), key=lambda x: -x[1]["roc_auc"]):
        report += (f"| {name} | {metrics['roc_auc']:.4f} | {metrics['accuracy']:.4f} | "
                   f"{metrics['precision']:.4f} | {metrics['recall']:.4f} | "
                   f"{metrics['f1_score']:.4f} | {metrics['cv_auc_mean']:.4f} ± {metrics['cv_auc_std']:.4f} |\n")

    report += f"""
## Recommended Model: {best_model_name}

### Why {best_model_name} was selected:
1. **Highest ROC-AUC**: {results[best_model_name]['roc_auc']:.4f} — best ability to distinguish churners from non-churners
2. **Strong cross-validation**: CV AUC = {results[best_model_name]['cv_auc_mean']:.4f} ± {results[best_model_name]['cv_auc_std']:.4f}
3. **Balanced Precision-Recall**: F1 = {results[best_model_name]['f1_score']:.4f}

### Business Interpretation of Metrics:

| Metric | Value | What it means for ConnectTel |
|---|---|---|
| **ROC-AUC** | {results[best_model_name]['roc_auc']:.4f} | The model correctly ranks a random churner higher than a non-churner {(results[best_model_name]['roc_auc']*100):.1f}% of the time |
| **Precision** | {results[best_model_name]['precision']:.4f} | When the model flags a customer as "likely to churn", it's correct {(results[best_model_name]['precision']*100):.1f}% of the time |
| **Recall** | {results[best_model_name]['recall']:.4f} | The model catches {(results[best_model_name]['recall']*100):.1f}% of all actual churners |
| **F1 Score** | {results[best_model_name]['f1_score']:.4f} | Harmonic mean of precision and recall — balanced measure |

### What This Means for Business:
- For every 100 customers the model flags as "at risk", {(results[best_model_name]['precision']*100):.0f} will actually churn — these are your priority targets
- Of all customers who will churn, the model catches {(results[best_model_name]['recall']*100):.0f}% — minimizing missed opportunities
- The model enables targeted retention strategies instead of blanket discounts

---

## Visualizations
See `notebooks/figures/` for:
- `confusion_matrix.png` — Model prediction breakdown
- `roc_curve.png` — ROC curve with AUC
- `pr_curve.png` — Precision-Recall curve
- `model_evaluation.png` — All models comparison
"""

    report_path = os.path.join(REPORT_DIR, "phase7_evaluation_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    print("\nBest model: {} (AUC={:.4f})".format(best_model_name, results[best_model_name]["roc_auc"]))


if __name__ == "__main__":
    generate_evaluation_report()
