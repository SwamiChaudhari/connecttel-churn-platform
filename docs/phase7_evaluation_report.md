# Phase 7: Model Evaluation Report
**ConnectTel Churn Prediction Platform**
Generated: 2026-05-30 15:27

---

## Executive Summary

| Model | ROC-AUC | Accuracy | Precision | Recall | F1 Score | CV AUC (mean ± std) |
|---|---|---|---|---|---|---|
| Logistic Regression | 0.6663 | 0.6427 | 0.5733 | 0.3644 | 0.4456 | 0.6686 ± 0.0096 |
| CatBoost | 0.6584 | 0.6374 | 0.5554 | 0.4007 | 0.4655 | 0.6557 ± 0.0081 |
| Random Forest | 0.6583 | 0.6427 | 0.5756 | 0.3547 | 0.4390 | 0.6610 ± 0.0078 |
| LightGBM | 0.6477 | 0.6350 | 0.5477 | 0.4237 | 0.4778 | 0.6400 ± 0.0095 |
| XGBoost | 0.6454 | 0.6388 | 0.5532 | 0.4346 | 0.4868 | 0.6411 ± 0.0153 |

## Recommended Model: Logistic Regression

### Why Logistic Regression was selected:
1. **Highest ROC-AUC**: 0.6663 — best ability to distinguish churners from non-churners
2. **Strong cross-validation**: CV AUC = 0.6686 ± 0.0096
3. **Balanced Precision-Recall**: F1 = 0.4456

### Business Interpretation of Metrics:

| Metric | Value | What it means for ConnectTel |
|---|---|---|
| **ROC-AUC** | 0.6663 | The model correctly ranks a random churner higher than a non-churner 66.6% of the time |
| **Precision** | 0.5733 | When the model flags a customer as "likely to churn", it's correct 57.3% of the time |
| **Recall** | 0.3644 | The model catches 36.4% of all actual churners |
| **F1 Score** | 0.4456 | Harmonic mean of precision and recall — balanced measure |

### What This Means for Business:
- For every 100 customers the model flags as "at risk", 57 will actually churn — these are your priority targets
- Of all customers who will churn, the model catches 36% — minimizing missed opportunities
- The model enables targeted retention strategies instead of blanket discounts

---

## Visualizations
See `notebooks/figures/` for:
- `confusion_matrix.png` — Model prediction breakdown
- `roc_curve.png` — ROC curve with AUC
- `pr_curve.png` — Precision-Recall curve
- `model_evaluation.png` — All models comparison
