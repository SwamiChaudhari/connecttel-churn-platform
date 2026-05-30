# Phase 1: Business Requirements Document
## ConnectTel Customer Churn Prediction & Retention Intelligence Platform
### Classification: Internal — Confidential
### Version: 1.0 | Date: 2026

---

## 1. Executive Summary

ConnectTel is a fast-growing Indian telecom operator serving **100,000+ customers** across major metros. The company faces a critical business challenge: **customer churn is eroding revenue at an alarming rate**. Every month, thousands of subscribers switch to competitors, costing the company crores in lost revenue.

Unlike reactive approaches ("who already left"), the CEO has mandated a **predictive, proactive solution** — an AI-powered platform that identifies at-risk customers BEFORE they leave, enabling retention teams to intervene early.

This document lays out the complete business requirements for building a **production-grade Churn Prediction & Retention Intelligence Platform** using machine learning, explainable AI, and business intelligence.

---

## 2. Business Problem Definition

### 2.1 What is Customer Churn?

Customer churn occurs when a subscriber cancels their service or switches to a competitor. In telecom, churn is typically categorized as:

- **Voluntary Churn**: Customer actively cancels (dissatisfaction, better offers)
- **Involuntary Churn**: Service disconnected (payment failure, fraud)

### 2.2 Why Churn Matters

| Impact Area | Description |
|---|---|
| **Revenue Loss** | Lost Monthly Recurring Revenue (MRR) + replacement cost |
| **Acquisition Cost** | Acquiring new customers costs 5-7x more than retaining existing ones |
| **Competitive Intelligence** | Churn signals competitive weakness |
| **Brand Reputation** | Churning customers leave negative reviews |
| **Investor Confidence** | High churn reduces company valuation |

### 2.3 ConnectTel Specific Problem

```
Current State:
- Total Customers: 100,000+
- Monthly Churn Rate: ~26% (industry avg: 15-25%)
- Avg Revenue Per User (ARPU): ₹800/month
- Annual Revenue Base: ₹96,00,00,000 (₹96 Crore)
- Annual Churn Revenue Loss: ₹31,20,00,000 (₹31.2 Crore)
```

**The core business question:**
> "Can we predict which customers will churn in the next 30 days, understand WHY, and recommend actions to prevent it?"

---

## 3. Revenue Loss Estimation

### 3.1 Assumptions

| Parameter | Value | Source |
|---|---|---|
| Total Customers | 100,000 | Company data |
| Current Churn Rate | 26% | Industry benchmark |
| Avg Monthly Revenue Per User | ₹800 | Management estimate |
| Average Customer Lifetime (churned) | 8 months | Historical |
| Customer Acquisition Cost (CAC) | ₹4,000 | Marketing budget |

### 3.2 Calculation

```
Annual Churned Customers = 100,000 × 0.26 = 26,000 customers/year

Direct Revenue Loss:
  = 26,000 customers × ₹800/month × 12 months
  = ₹24.96 Crore/year

Opportunity Cost (if churned customers stayed 24 more months on average):
  = 26,000 × ₹800 × 24
  = ₹49.92 Crore/year

Replacement Acquisition Cost:
  = 26,000 × ₹4,000
  = ₹10.40 Crore/year

────────────────────────────────────────
TOTAL ANNUAL IMPACT = ₹35.36 Crore
(Direct Loss + Acquisition Cost)
```

### 3.3 ROI of Churn Reduction

| Churn Reduction | Revenue Saved (Annual) | Platform ROI |
|---|---|---|
| 10% improvement (26% → 23.4%) | ₹3.54 Crore | 3,540% |
| 25% improvement (26% → 19.5%) | ₹8.84 Crore | 8,840% |
| 50% improvement (26% → 13%) | ₹17.68 Crore | 17,680% |

---

## 4. Stakeholder Analysis

### 4.1 Stakeholder Map

| Stakeholder | Role | Key Concern | How Platform Helps |
|---|---|---|---|
| **CEO / Board** | Strategic decision maker | Revenue protection & growth | Executive dashboard with KPIs & projections |
| **VP Marketing** | Campaign planning | Reducing acquisition cost | Targeted retention campaigns |
| **Customer Success Lead** | Proactive outreach | Which customers to call | Risk-scored customer lists |
| **Sales Team Lead** | Offer optimization | Competitive offers | Feature importance & reason codes |
| **Finance Team** | Budget & forecasting | Revenue forecasting | Revenue loss projections & savings |
| **Data Science Lead** | Platform ownership | Model performance | Monitoring & retraining pipeline |
| **IT / DevOps** | Infrastructure | Deployment & uptime | Containerized, CI/CD-ready system |

### 4.2 Stakeholder Communication Plan

| Audience | Format | Frequency |
|---|---|---|
| CEO / Executives | Executive summary dashboard | Weekly |
| Marketing / Sales | Risk-segmented customer lists | Daily |
| Data Science Team | Model performance reports | Weekly |
| IT / DevOps | System health logs | Real-time |

---

## 5. Business Goals (SMART Format)

### Primary Goals

| ID | Goal | Metric | Target | Timeline |
|---|---|---|---|---|
| BG-01 | Predict churn with high accuracy | ROC-AUC Score | ≥ 0.85 | 8 weeks |
| BG-02 | Identify top churn risk drivers | Feature importance ranking | Top 10 drivers | 6 weeks |
| BG-03 | Reduce customer churn rate | Churn rate reduction | 10% improvement | 6 months (post-deployment) |
| BG-04 | Generate actionable retention plans | Recommendation coverage | 100% of high-risk | 8 weeks |
| BG-05 | Protect revenue | Revenue at risk identified | ₹5 Cr+/month | 8 weeks |

### Secondary Goals

| ID | Goal | Metric | Target |
|---|---|---|---|
| BG-06 | Deploy model to production | API uptime | 99.5% |
| BG-07 | Enable self-service analytics | Dashboard adoption | 50+ active users |
| BG-08 | Ensure model fairness | Bias audit pass | < 5% disparity |

---

## 6. Project Success Criteria

### 6.1 Technical Criteria
- ROC-AUC ≥ 0.85 on held-out test set
- Precision ≥ 0.80 for churn class (catch most actual churners)
- Recall ≥ 0.75 for churn class (don't miss churners)
- Model latency < 100ms per prediction
- Dashboard load < 3 seconds

### 6.2 Business Criteria
- Top 5 churn drivers validated by domain experts
- Retention team can generate risk lists within 1 click
- Marketing can launch targeted campaigns within 2 days
- Finance can forecast revenue impact monthly

### 6.3 Operational Criteria
- Automated retraining pipeline triggered monthly
- Model monitoring alerts within 5 min of drift detection
- Zero data leakage between train/test sets
- Full audit trail for all predictions

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Data quality issues (missing values, errors) | High | High | Data validation pipeline, quality reports |
| Class imbalance (more non-churn than churn) | Medium | High | SMOTE, class weights, stratified CV |
| Model drift over time | Medium | High | Monthly retraining, monitoring dashboard |
| Feature leakage | Low | Critical | Data audit, temporal validation |
| Stakeholder adoption resistance | Medium | Medium | User training, intuitive UI |
| Regulatory/compliance issues | Low | High | Data anonymization, consent tracking |
| Overfitting to training data | Medium | High | Cross-validation, regularization |

---

## 8. Timeline & Milestones

| Phase | Duration | Deliverables |
|---|---|---|
| Phase 1: Business Understanding | Week 1 | This document |
| Phase 2: Data Understanding | Week 1-2 | Data dictionary, feature catalog |
| Phase 3: EDA | Week 2-3 | EDA notebook, visualizations |
| Phase 4: Data Cleaning | Week 3 | Clean dataset, quality report |
| Phase 5: Feature Engineering | Week 3-4 | Engineered features |
| Phase 6: ML Pipeline | Week 4-6 | 5 trained models |
| Phase 7: Model Evaluation | Week 6 | Evaluation report |
| Phase 8: Explainable AI | Week 6-7 | SHAP analysis, insights |
| Phase 9: Retention Engine | Week 7-8 | Recommendation system |
| Phase 10: SQL BI Layer | Week 7-8 | SQL scripts, KPI reports |
| Phase 11: Dashboard | Week 8-10 | Streamlit app |
| Phase 12: MLOps | Week 10-11 | Monitoring, versioning |
| Phase 13: Deployment | Week 11-12 | Docker, CI/CD |
| Phase 14: Portfolio Assets | Week 12 | Resume, LinkedIn content |
| Phase 15: Interview Prep | Week 12 | 150 questions + answers |

---

## 9. Data Science Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ConnectTel Churn Platform                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌────────────────────────┐  │
│  │  Data     │──▶│ Feature  │──▶│  ML Pipeline           │  │
│  │  Ingestion│   │ Engineer │   │  (5 Models + Tuning)   │  │
│  └──────────┘   └──────────┘   └────────────────────────┘  │
│       │                               │                     │
│       │                        ┌──────▼──────┐              │
│       │                        │   Model     │              │
│       │                        │   Selection │              │
│       │                        └──────┬──────┘              │
│       │                               │                     │
│  ┌────▼─────┐   ┌──────────┐   ┌─────▼──────┐             │
│  │  SQL BI  │   │ SHAP /   │   │ Retention  │              │
│  │  Layer   │   │ XAI      │   │ Engine     │              │
│  └────┬─────┘   └────┬─────┘   └─────┬──────┘             │
│       │              │               │                     │
│       └──────────────┼───────────────┘                     │
│                      │                                     │
│               ┌──────▼──────┐                              │
│               │  Streamlit  │                              │
│               │  Dashboard  │                              │
│               └──────┬──────┘                              │
│                      │                                     │
│               ┌──────▼──────┐                              │
│               │   MLOps     │                              │
│               │ (Docker,CI) │                              │
│               └─────────────┘                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Document prepared by: Data Science Team*
*Reviewed by: VP Engineering, VP Marketing*
*Next Review: End of Phase 3*
