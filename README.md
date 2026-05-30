# ConnectTel Churn Prediction & Retention Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![ML](https://img.shields.io/badge/Machine%20Learning-XGBoost%20%7C%20LightGBM%20%7C%20CatBoost-green.svg)
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)

A **complete, end-to-end AI-powered Customer Churn Prediction & Retention Intelligence Platform** built for a fictional telecom company — **ConnectTel**. This is not a college project. This is a **production-grade ML system** with explainability, business intelligence, and an executive dashboard.

---

## Table of Contents

| # | Section |
|---|---|
| 1 | [Business Problem](#-business-problem) |
| 2 | [Architecture](#-architecture) |
| 3 | [Project Structure](#-project-structure) |
| 4 | [Quick Start](#-quick-start) |
| 5 | [Phases & Deliverables](#-phases--deliverables) |
| 6 | [Models](#-models) |
| 7 | [Dashboard](#-dashboard) |
| 8 | [Results](#-results) |
| 9 | [Deployment](#-deployment) |
| 10 | [Interview Prep](#-interview-prep) |

---

## Business Problem

ConnectTel is a fast-growing Indian telecom operator with **100,000+ customers**. Every month, ~26% of customers churn (switch to competitors), costing the company an estimated **₹31.2 Crore annually** in lost revenue.

The **CEO's mandate**: Build a system that doesn't just analyze who left — but **predicts who will leave** and **recommends how to stop them**.

### Solution
An AI-powered platform that:
- Predicts churn risk for every customer (probability score)
- Explains WHY each customer is at risk (SHAP/XAI)
- Generates personalized retention recommendations
- Provides executive dashboards with business KPIs
- Monitors model health and triggers retraining

---

## Architecture

```
Data Generation → Cleaning → Feature Engineering → ML Pipeline (5 Models)
                                                           ↓
                                                  Model Selection + Tuning
                                                           ↓
                                              Explainable AI (SHAP Analysis)
                                                           ↓
                                         ┌─────────────────┴─────────────────┐
                                         ↓                                    ↓
                               Retention Engine                    SQL BI Layer
                                         ↓                                    ↓
                                    ┌────┴────┐                         KPI Reports
                                    ↓         ↓                          ↓
                              Streamlit    API Layer              Business Insights
                              Dashboard         ↓
                                            MLOps
                                        (Docker + CI/CD)
```

---

## Project Structure

```
connecttel-churn-platform/
├── README.md
├── requirements.txt
├── Dockerfile
├── run_all.py                    # Master pipeline runner
│
├── config/
│   ├── config.yaml               # Main configuration
│   ├── logging_config.yaml       # Logging setup
│   └── model_config.json         # Model hyperparameters
│
├── data/
│   ├── connecttel_churn_raw.csv
│   ├── connecttel_churn_clean.csv
│   └── connecttel_churn_engineered.csv
│
├── docs/
│   ├── phase1_business_requirements.md
│   ├── phase2_data_dictionary.md
│   ├── phase2_feature_catalog.md
│   ├── phase2_risk_assessment.md
│   ├── phase7_evaluation_report.md
│   └── phase8_executive_insights.md
│
├── models/
│   ├── best_model.joblib
│   ├── logistic_regression.joblib
│   ├── random_forest.joblib
│   ├── xgboost.joblib
│   ├── lightgbm.joblib
│   ├── catboost.joblib
│   └── label_encoders.joblib
│
├── notebooks/
│   ├── model_comparison.csv
│   └── figures/                  # All generated charts
│
├── sql/
│   └── bi_queries.sql            # 10 production SQL queries
│
├── src/
│   ├── data/
│   │   ├── generate_dataset.py
│   │   └── data_cleaning.py
│   ├── features/
│   │   └── feature_engineering.py
│   ├── models/
│   │   ├── ml_pipeline.py
│   │   ├── model_evaluation.py
│   │   ├── shap_analysis.py
│   │   └── retention_engine.py
│   ├── visualization/
│   │   └── eda.py
│   └── mlops/
│       └── production_utils.py
│
├── streamlit_app/
│   └── app.py                    # Interactive dashboard
│
├── tests/
│   ├── test_data_quality.py
│   └── test_model.py
│
├── deployment/
│   ├── Dockerfile
│   ├── deploy.sh
│   └── render.yaml
│
├── .github/
│   └── workflows/
│       └── ci_cd.yaml
│
└── logs/
    ├── connecttel_churn.log
    └── monitoring/
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Complete Pipeline
```bash
python run_all.py
```

This will:
- Generate synthetic dataset
- Clean and validate data
- Engineer 12 advanced features
- Train and evaluate 5 ML models
- Run SHAP explainability analysis
- Generate retention recommendations

### 3. Launch Dashboard
```bash
streamlit run streamlit_app/app.py
```

### 4. Open in Browser
Navigate to `http://localhost:8501`

---

## Phases & Deliverables

| Phase | Description | Output |
|---|---|---|
| 1 | Business Understanding | BRD, Revenue Impact Analysis |
| 2 | Data Understanding | Data Dictionary, Feature Catalog |
| 3 | EDA | 8 Visualizations, Executive Summary |
| 4 | Data Cleaning | Clean Dataset, Quality Report |
| 5 | Feature Engineering | 12 Business Features |
| 6 | ML Pipeline | 5 Trained + Tuned Models |
| 7 | Model Evaluation | ROC-AUC, Confusion Matrix, Report |
| 8 | Explainable AI | SHAP Analysis, Top Drivers |
| 9 | Retention Engine | Personalized Recommendations |
| 10 | SQL BI Layer | 10 Production Queries |
| 11 | Dashboard | Streamlit App (7 pages) |
| 12 | MLOps | Logging, Monitoring, Versioning |
| 13 | Deployment | Dockerfile, CI/CD, Guide |
| 14 | Portfolio Assets | Resume, LinkedIn, STAR Answers |
| 15 | Interview Prep | 150 Questions + Answers |

---

## Models

| Model | Strengths | Typical AUC |
|---|---|---|
| Logistic Regression | Interpretable baseline | ~0.82 |
| Random Forest | Robust, handles non-linearity | ~0.84 |
| XGBoost | Best overall performance | ~0.87 |
| LightGBM | Fast training, excellent on tabular | ~0.86 |
| CatBoost | Native categorical support | ~0.86 |

---

## Dashboard

The Streamlit dashboard has **7 pages**:

1. **Executive Overview** — KPIs, churn distribution, contract analysis
2. **Churn Analytics** — Deep-dive with filters, service analysis
3. **Revenue Analytics** — Revenue at risk, savings projections
4. **Customer Segmentation** — 3D scatter, engagement analysis
5. **AI Prediction Center** — Single customer prediction with gauge
6. **Retention Recommendations** — Top at-risk customers + CSV export
7. **Model Monitoring** — Model comparison, health checks

---

## Key Results

```
Overall Churn Rate: ~26%
Best Model: XGBoost (AUC ≈ 0.87)
Top Churn Drivers:
  1. Month-to-month contracts
  2. Low tenure (< 12 months)
  3. High monthly charges
  4. No online security
  5. Fiber optic internet

Estimated Annual Revenue at Risk: ₹31.2 Crore
Potential Savings (10% churn reduction): ₹3.54 Crore/year
```

---

## Deployment

### Docker
```bash
docker build -t connecttel-churn .
docker run -p 8501:8501 connecttel-churn
```

### Streamlit Cloud
1. Push to GitHub
2. Connect to streamlit.io
3. Deploy with one click

### Render
See `deployment/render.yaml` for Blueprint config.

---

## Technologies

| Layer | Technologies |
|---|---|
| **Language** | Python 3.9+ |
| **ML** | scikit-learn, XGBoost, LightGBM, CatBoost |
| **Explainability** | SHAP |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Dashboard** | Streamlit |
| **Data** | Pandas, NumPy, SQL |
| **MLOps** | Docker, GitHub Actions, Logging |
| **Deployment** | Docker, Streamlit Cloud, Render |

---

## Author

**Swami Chaudhari**
- B.E. Computer Engineering, Viva Institute of Technology
- Cisco Data Analytics Certified (Oct 2025)
- Skills: Python, SQL, Power BI, Tableau, ML, AWS, ETL, Web Scraping

---

## License

MIT License — free to use for learning, portfolios, and interviews.
