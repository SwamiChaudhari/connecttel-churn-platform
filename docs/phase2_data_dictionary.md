# Phase 2: Data Dictionary
## ConnectTel Churn Prediction Platform
### Telco Customer Churn Dataset — Complete Column Reference

---

| # | Column Name | Data Type | Description | Business Importance | Expected Churn Impact | Values |
|---|---|---|---|---|---|---|
| 1 | customerID | String | Unique customer identifier | Primary key for tracking | None (identifier) | CUST-XXXXX |
| 2 | gender | Categorical | Customer gender | Minor demographic signal | Low | Male, Female |
| 3 | SeniorCitizen | Binary | Whether customer is 65+ | Seniors may have different usage | Medium (seniors churn slightly more) | 0, 1 |
| 4 | Partner | Categorical | Has a domestic partner | Partners add stickiness | Low-Medium | Yes, No |
| 5 | Dependents | Categorical | Has dependents (children) | Family plans increase stickiness | Low-Medium | Yes, No |
| 6 | tenure | Integer | Months with company | **#1 predictor** — low tenure = high risk | Very High | 0-72 months |
| 7 | PhoneService | Categorical | Has phone service | Basic service indicator | Low | Yes, No |
| 8 | MultipleLines | Categorical | Has multiple phone lines | Multi-line = higher engagement | Medium | Yes, No, No phone service |
| 9 | InternetService | Categorical | Internet type (DSL/Fiber/None) | **Key driver** — Fiber churns more | High | DSL, Fiber optic, No |
| 10 | OnlineSecurity | Categorical | Has online security add-on | Security = stickiness | Medium-High | Yes, No, No internet service |
| 11 | OnlineBackup | Categorical | Has online backup service | Backup = engagement | Medium | Yes, No, No internet service |
| 12 | DeviceProtection | Categorical | Has device protection plan | Protection = engagement | Medium | Yes, No, No internet service |
| 13 | TechSupport | Categorical | Has tech support add-on | **Major driver** — no support = churn | High | Yes, No, No internet service |
| 14 | StreamingTV | Categorical | Has streaming TV | Engagement signal | Low-Medium | Yes, No, No internet service |
| 15 | StreamingMovies | Categorical | Has streaming movies | Engagement signal | Low-Medium | Yes, No, No internet service |
| 16 | Contract | Categorical | Contract type | **#1 churn predictor** — month-to-month = high risk | **Critical** | Month-to-month, One year, Two year |
| 17 | PaperlessBilling | Categorical | Uses paperless billing | Digital customers — mixed signal | Low | Yes, No |
| 18 | PaymentMethod | Categorical | How customer pays | **Key driver** — electronic check = high risk | High | Electronic check, Mailed check, Bank transfer, Credit card |
| 19 | MonthlyCharges | Float | Monthly bill amount | **Major driver** — high charges = more churn | High | ₹18.25 - ₹118.75 |
| 20 | TotalCharges | Float | Total amount charged to date | Revenue signal, but correlated with tenure | Medium | ₹18 - ₹9,000+ |
| 21 | Churn | Categorical | Target — did customer leave? | What we're predicting | N/A (target) | Yes, No |

---

## Feature Categories

### Demographic (4 features)
gender, SeniorCitizen, Partner, Dependents

### Account (4 features)
tenure, Contract, PaperlessBilling, PaymentMethod

### Service Usage (8 features)
PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies

### Billing (2 features)
MonthlyCharges, TotalCharges

### Target (1 feature)
Churn

---

## Encoding Strategy

| Feature Type | Strategy |
|---|---|
| Binary (Yes/No) | Label encode: Yes=1, No=0 |
| Categorical (>2 values) | One-hot encoding for linear models; label encode for tree models |
| Ordinal (tenure) | Keep as integer or bin into groups |
| Continuous (charges) | StandardScaler for linear models; raw for tree models |

---

## Data Quality Notes

- TotalCharges has ~0.5% missing values (new customers with tenure=0)
- No duplicates expected (customerID is unique)
- Churn is imbalanced (~26% Yes, ~74% No) — requires stratified sampling
