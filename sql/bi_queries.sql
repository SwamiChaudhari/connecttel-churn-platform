-- ============================================================
-- Phase 10: SQL Business Intelligence Layer
-- ConnectTel Churn Prediction Platform
-- Production-level SQL for business reporting & analytics
-- ============================================================

-- ============================================================
-- TABLE SETUP (SQLite/PostgreSQL compatible)
-- ============================================================

-- Main customer table
CREATE TABLE IF NOT EXISTS customers (
    customer_id         VARCHAR(20) PRIMARY KEY,
    gender              VARCHAR(10),
    senior_citizen      INTEGER,
    partner             VARCHAR(5),
    dependents          VARCHAR(5),
    tenure              INTEGER,
    phone_service       VARCHAR(5),
    multiple_lines      VARCHAR(30),
    internet_service    VARCHAR(20),
    online_security     VARCHAR(30),
    online_backup       VARCHAR(30),
    device_protection   VARCHAR(30),
    tech_support        VARCHAR(30),
    streaming_tv        VARCHAR(30),
    streaming_movies    VARCHAR(30),
    contract            VARCHAR(20),
    paperless_billing   VARCHAR(5),
    payment_method      VARCHAR(30),
    monthly_charges     DECIMAL(10,2),
    total_charges       DECIMAL(10,2),
    churn               VARCHAR(5),  -- 'Yes' or 'No'
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model predictions table
CREATE TABLE IF NOT EXISTS churn_predictions (
    prediction_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         VARCHAR(20) REFERENCES customers(customer_id),
    churn_probability   DECIMAL(5,4),
    risk_level          VARCHAR(20),  -- CRITICAL/HIGH/MODERATE/LOW
    prediction_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version       VARCHAR(20)
);

-- Retention actions table
CREATE TABLE IF NOT EXISTS retention_actions (
    action_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         VARCHAR(20) REFERENCES customers(customer_id),
    action_type         VARCHAR(50),
    action_description  TEXT,
    priority            VARCHAR(10),
    status              VARCHAR(20) DEFAULT 'PENDING',
    assigned_to         VARCHAR(100),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP,
    outcome             VARCHAR(20)  -- SUCCESS / FAILED / IN_PROGRESS
);


-- ============================================================
-- QUERY 1: Monthly Churn Rate
-- ============================================================
-- Tracks the overall churn rate segmented by month/year
SELECT
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*),
        2
    ) AS churn_rate_pct
FROM customers
GROUP BY strftime('%Y-%m', created_at)
ORDER BY month;

-- ============================================================
-- QUERY 2: Revenue Loss from Churn
-- ============================================================
-- Calculates total revenue lost due to churned customers
SELECT
    SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END) AS monthly_revenue_lost,
    SUM(CASE WHEN churn = 'Yes' THEN monthly_charges * 12 ELSE 0 END) AS annual_revenue_lost,
    SUM(CASE WHEN churn = 'Yes' THEN total_charges ELSE 0 END) AS total_revenue_lost,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS total_churned_customers,
    ROUND(AVG(CASE WHEN churn = 'Yes' THEN monthly_charges END), 2) AS avg_monthly_charges_churned
FROM customers;

-- ============================================================
-- QUERY 3: Churn by Customer Segment (Contract + Tenure)
-- ============================================================
-- Deep dive into which customer segments churn most
SELECT
    contract,
    CASE
        WHEN tenure <= 6   THEN '0-6 months'
        WHEN tenure <= 12  THEN '6-12 months'
        WHEN tenure <= 24  THEN '12-24 months'
        WHEN tenure <= 48  THEN '24-48 months'
        ELSE '48+ months'
    END AS tenure_segment,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(
        CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*),
        2
    ) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) AS revenue_lost
FROM customers
GROUP BY contract, tenure_segment
ORDER BY churn_rate_pct DESC;

-- ============================================================
-- QUERY 4: Customer Segmentation (RFM-style)
-- ============================================================
-- RFM: Recency (tenure), Frequency (engagement), Monetary (charges)
SELECT
    customer_id,
    tenure,
    monthly_charges,
    total_charges,
    CASE
        WHEN tenure >= 48 AND total_charges > 5000 THEN 'Champions'
        WHEN tenure >= 24 AND total_charges > 3000 THEN 'Loyal Customers'
        WHEN tenure >= 12 AND total_charges > 2000 THEN 'Potential Loyalists'
        WHEN tenure >= 6  THEN 'At Risk'
        ELSE 'New / Hibernating'
    END AS customer_segment,
    churn
FROM customers
ORDER BY total_charges DESC;

-- ============================================================
-- QUERY 5: Retention Performance by Action Type
-- ============================================================
-- Measures the effectiveness of retention actions
SELECT
    action_type,
    COUNT(*) AS total_actions,
    SUM(CASE WHEN outcome = 'SUCCESS' THEN 1 ELSE 0 END) AS successes,
    SUM(CASE WHEN outcome = 'FAILED' THEN 1 ELSE 0 END) AS failures,
    ROUND(
        CAST(SUM(CASE WHEN outcome = 'SUCCESS' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*),
        2
    ) AS success_rate_pct,
    AVG(julianday(completed_at) - julianday(created_at)) AS avg_days_to_complete
FROM retention_actions
GROUP BY action_type
ORDER BY success_rate_pct DESC;

-- ============================================================
-- QUERY 6: Top Churn Drivers (Service-Level Analysis)
-- ============================================================
-- Identifies which services are most associated with churn
SELECT 'OnlineSecurity' AS service, online_security AS status, COUNT(*) AS cnt,
    ROUND(CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) AS churn_rate
FROM customers GROUP BY online_security
UNION ALL
SELECT 'TechSupport', tech_support, COUNT(*),
    ROUND(CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2)
FROM customers GROUP BY tech_support
UNION ALL
SELECT 'InternetService', internet_service, COUNT(*),
    ROUND(CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2)
FROM customers GROUP BY internet_service
UNION ALL
SELECT 'PaymentMethod', payment_method, COUNT(*),
    ROUND(CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2)
FROM customers GROUP BY payment_method
ORDER BY churn_rate DESC;

-- ============================================================
-- QUERY 7: KPI Dashboard Query (Single-Row Summary)
-- ============================================================
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    SUM(CASE WHEN churn = 'No' THEN 1 ELSE 0 END) AS active_customers,
    ROUND(
        CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*),
        2
    ) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_revenue_per_user,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_revenue,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) AS revenue_at_risk_monthly,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    SUM(CASE WHEN tenure <= 3 THEN 1 ELSE 0 END) AS new_customers_3m,
    SUM(CASE WHEN contract = 'Month-to-month' THEN 1 ELSE 0 END) AS monthly_contract_count,
    SUM(CASE WHEN internet_service = 'Fiber optic' THEN 1 ELSE 0 END) AS fiber_customers
FROM customers;

-- ============================================================
-- QUERY 8: High-Risk Customer List (for Retention Team)
-- ============================================================
SELECT
    cp.customer_id,
    cp.churn_probability,
    cp.risk_level,
    c.contract,
    c.tenure,
    c.monthly_charges,
    c.internet_service,
    c.payment_method,
    c.total_charges,
    ROUND(c.monthly_charges * 12 * cp.churn_probability, 2) AS estimated_annual_revenue_at_risk
FROM churn_predictions cp
JOIN customers c ON cp.customer_id = c.customer_id
WHERE cp.risk_level IN ('CRITICAL', 'HIGH')
    AND cp.prediction_date = (
        SELECT MAX(prediction_date)
        FROM churn_predictions cp2
        WHERE cp2.customer_id = cp.customer_id
    )
ORDER BY cp.churn_probability DESC
LIMIT 100;

-- ============================================================
-- QUERY 9: Cohort Analysis — Retention by Tenure Cohort
-- ============================================================
WITH cohorts AS (
    SELECT
        customer_id,
        churn,
        monthly_charges,
        CASE
            WHEN tenure <= 6   THEN '0-6 months'
            WHEN tenure <= 12  THEN '6-12 months'
            WHEN tenure <= 24  THEN '12-24 months'
            WHEN tenure <= 36  THEN '24-36 months'
            WHEN tenure <= 48  THEN '36-48 months'
            ELSE '48+ months'
        END AS tenure_cohort
    FROM customers
)
SELECT
    tenure_cohort,
    COUNT(*) AS cohort_size,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(
        CAST(SUM(CASE WHEN churn = 'No' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*),
        2
    ) AS retention_rate_pct,
    SUM(monthly_charges) AS total_revenue
FROM cohorts
GROUP BY tenure_cohort
ORDER BY tenure_cohort;

-- ============================================================
-- QUERY 10: Monthly Revenue Forecast (With & Without Churn)
-- ============================================================
SELECT
    SUM(monthly_charges) AS current_monthly_revenue,
    SUM(CASE WHEN churn = 'No' THEN monthly_charges ELSE 0 END) AS retained_revenue,
    SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END) AS lost_revenue,
    ROUND(
        SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END) * 12,
        2
    ) AS projected_annual_loss,
    ROUND(
        SUM(CASE WHEN churn = 'No' THEN monthly_charges ELSE 0 END) * 12,
        2
    ) AS projected_annual_retained,
    -- If churn reduced by 10%:
    ROUND(
        SUM(CASE WHEN churn = 'Yes' THEN monthly_charges * 0.10 ELSE 0 END) * 12,
        2
    ) AS potential_savings_10pct_reduction
FROM customers;
