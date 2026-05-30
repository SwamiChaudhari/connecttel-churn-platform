# Phase 15: Interview Preparation Guide
## 150 Questions & Answers Based on ConnectTel Churn Project

---

# SECTION A: DATA ANALYST QUESTIONS (50)

## A1. SQL & Data Querying

**Q1. Write a query to find the monthly churn rate.**
```sql
SELECT
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS total,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
    ROUND(CAST(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY month ORDER BY month;
```

**Q2. How would you find the top 10 highest-risk customers?**
```sql
SELECT customer_id, churn_probability, risk_level,
       monthly_charges * 12 * churn_probability AS revenue_at_risk
FROM churn_predictions cp
WHERE prediction_date = (SELECT MAX(prediction_date) FROM churn_predictions WHERE customer_id = cp.customer_id)
  AND risk_level IN ('CRITICAL', 'HIGH')
ORDER BY churn_probability DESC LIMIT 10;
```

**Q3. What's the difference between WHERE and HAVING?**
WHERE filters rows before grouping; HAVING filters groups after aggregation.
Example: `WHERE tenure > 12` filters individual rows. `HAVING AVG(MonthlyCharges) > 75` filters groups.

**Q4. How do you handle NULL values in SQL?**
Use COALESCE(column, default), IS NULL / IS NOT NULL checks, or conditional aggregation.
In our project: `COALESCE(total_charges, monthly_charges * tenure) AS imputed_total`.

**Q5. Explain a CTE and when you'd use one.**
A Common Table Expression (CTE) is a named temporary result set. Used for readability and recursive queries.
We used CTEs for cohort analysis:
```sql
WITH cohorts AS (
    SELECT *, CASE WHEN tenure <= 6 THEN '0-6' ELSE '6+' END AS cohort FROM customers
) SELECT cohort, AVG(CASE WHEN churn='Yes' THEN 1.0 ELSE 0.0 END) FROM cohorts GROUP BY cohort;
```

**Q6. How would you calculate year-over-year revenue growth?**
```sql
WITH yearly AS (
    SELECT strftime('%Y', created_at) AS year, SUM(monthly_charge) AS revenue FROM customers GROUP BY year
)
SELECT year, revenue, LAG(revenue) OVER (ORDER BY year) AS prev_year,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY year)) * 100.0 / LAG(revenue) OVER (ORDER BY year), 2) AS yoy_growth
FROM yearly;
```

**Q7. What window functions have you used?**
ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, SUM() OVER, AVG() OVER.
Used LAG for revenue growth trends and ROW_NUMBER for ranking customers by churn risk.

**Q8. How do you optimize a slow SQL query?**
Add indexes on JOIN/WHERE columns, avoid SELECT *, use EXPLAIN to analyze query plan, avoid subqueries in WHERE (use JOINs), partition large tables.

**Q9. What's the difference between INNER JOIN and LEFT JOIN?**
INNER JOIN returns only matching rows from both tables. LEFT JOIN returns all rows from the left + matching from right (NULL if no match).

**Q10. How would you find customers who churned within 3 months of joining?**
```sql
SELECT * FROM customers
WHERE churn = 'Yes' AND tenure <= 3;
-- Result: These are "early churners" — critical for onboarding improvement.
```

## A2. Data Analysis Concepts

**Q11. What KPIs would you track for churn?**
- Monthly Churn Rate, Revenue Churn Rate, Customer Lifetime Value (CLV), Net Revenue Retention, Average Revenue Per User (ARPU), Time-to-Churn, Reactivation Rate.

**Q12. How do you calculate Customer Lifetime Value?**
CLV = (Average Revenue Per User × Gross Margin) / Churn Rate
Or: CLV = Monthly Charges × Expected Lifespan (1/churn_rate)
In our project: CLV = MonthlyCharges × tenure (historical) and predicted CLV using survival analysis.

**Q13. What's the difference between median and average revenue?**
Mean is affected by outliers (a few high-value customers skew it). Median is robust — it represents the typical customer. In churn analysis, median is often more informative because revenue distributions are right-skewed.

**Q14. How do you handle seasonality in churn data?**
Decompose time series into trend + seasonal + residual. Use moving averages, or include month/quarter as a feature in the model. Compare YoY rather than MoM for seasonal businesses.

**Q15. What's cohort analysis and why is it useful?**
Grouping customers by acquisition period and tracking behavior over time. Reveals if newer customers churn faster (onboarding issues) or if retention improvements work.

**Q16. How do you identify outliers in customer data?**
IQR method (Q1 - 1.5*IQR to Q3 + 1.5*IQR), Z-score (>3), visual inspection (box plots, scatter plots). In our project, we capped at 1st/99th percentile.

**Q17. What's the 80/20 rule in business analytics?**
80% of revenue often comes from 20% of customers. In churn context: 20% of customers may be at 80% of total risk. Focus retention efforts on high-value at-risk customers.

**Q18. How would you segment customers?**
RFM analysis (Recency, Frequency, Monetary), behavioral segmentation (service usage), demographic (age/region), value-based (high/medium/low CLV).

**Q19. What's the difference between descriptive and predictive analytics?**
Descriptive: "What happened?" (churn rate was 26% last month). Predictive: "What will happen?" (2,000 customers will churn next month). Our project is predictive.

**Q20. How do you present data to non-technical stakeholders?**
Focus on business impact, not methodology. Use dashboards with KPIs, color-coded risk levels, simple charts, and actionable summaries. Avoid jargon — say "this customer is very likely to leave" instead of "churn probability = 0.92".

## A3. Power BI / Tableau (Conceptual)

**Q21. How would you visualize churn data in Power BI?**
KPI cards for churn rate and revenue at risk, pie chart for churn distribution, bar chart for churn by segment, trend line for monthly churn, heatmap for contract × internet service churn rates.

**Q22. What's a calculated column vs. measure in Power BI?**
Calculated column: computed row-by-row during refresh, stored in the model. Measure: computed dynamically based on filter context. Use measures for aggregations like churn rate.

**Q23. How do you create a churn dashboard drill-down?**
Hierarchy: Company → Region → City → Individual Customer. Use bookmarks for navigation, slicers for filters, and drill-through pages.

**Q24. What's the star schema and why use it?**
Central fact table (transactions/predictions) connected to dimension tables (customers, time, products). Optimizes query performance and simplifies business logic.

**Q25. How do you handle many-to-many relationships in Power BI?**
Use bridge tables or bidirectional filtering. In our case, customer-to-services is many-to-many, resolved via a service mapping table.

## A4. Excel / Spreadsheet Analysis

**Q26. How do you calculate churn rate in Excel?**
=COUNTIF(ChurnRange, "Yes") / COUNTA(CustomerIDRange) × 100

**Q27. How would you use VLOOKUP/INDEX-MATCH for churn analysis?**
=XLOOKUP(customerID, ID_column, Revenue_column) to pull customer revenue into the prediction table for at-risk revenue calculations.

**Q28. When would you use a pivot table over a formula?**
Pivot tables for quick aggregation, grouping, and cross-tabulation. In churn analysis: pivot by Contract Type (rows) and Churn (columns) with COUNT of customers (values).

## A5. Statistical Analysis for Analysts

**Q29. What statistical test would you use to compare churn between two groups?**
Chi-square test for categorical variables (e.g., churn by contract type). T-test for continuous variables (e.g., mean tenure of churned vs retained).

**Q30. What's correlation vs. causation in churn analysis?**
Correlation: customers with high charges churn more. Causation: high charges CAUSE churn (needs experimentation to prove). Always be careful — fiber customers may churn because of service quality, not the fiber itself.

**Q31. What's a confidence interval and why does it matter?**
A range in which the true value likely falls. "Churn rate is 26% ± 2%" means the true rate is between 24-28%. Important for setting realistic targets.

**Q32. How do you interpret a correlation matrix?**
Values range from -1 to +1. In our project: tenure negatively correlated with churn (longer tenure = less churn), MonthlyCharges positively correlated (higher charges = more churn).

## A6. Business Analysis

**Q33. How do you calculate ROI of a retention program?**
ROI = (Revenued Saved - Program Cost) / Program Cost × 100
If retention program costs ₹50L and saves ₹3.5 Cr: ROI = (3.5 - 0.5) / 0.5 × 100 = 600%.

**Q34. What's the cost of customer acquisition vs. retention?**
Acquisition costs 5-7x more than retention. It costs ₹4,000 to acquire a new customer but only ₹500-800 to retain an existing one through loyalty programs.

**Q35. How would you prioritize which customers to target for retention?**
Score by: Revenue at Risk = MonthlyCharges × ChurnProbability. Target high-probability, high-value customers first. A customer paying ₹100/month with 90% churn risk (₹1,080 annual risk) is more valuable to target than one paying ₹30 with 95% risk (₹342).

**Q36. What's Net Promoter Score (NPS) and how does it relate to churn?**
NPS measures likelihood to recommend. Detractors (0-6 score) are high churn risk. Promoters (9-10) are loyal. NPS is a leading indicator of churn.

**Q37. How do you define "at risk" vs "churned"?**
"At risk" = predicted to churn soon (probability > threshold). "Churned" = already left. The distinction is critical — our model predicts risk before it happens.

**Q38. What's the customer journey in churn context?**
Awareness → Onboarding → Active Usage → Signs of Dissatisfaction → Churn Risk → Churn. Our model catches customers at the "Churn Risk" stage.

## A7. Python for Analysis

**Q39. How do you handle missing values in pandas?**
```python
df.isnull().sum()  # check
df['col'].fillna(df['col'].median(), inplace=True)  # impute
df.dropna(subset=['critical_col'], inplace=True)  # drop if critical
```

**Q40. How do you merge customer and prediction data?**
```python
merged = pd.merge(customers, predictions, on='customer_id', how='inner')
```

**Q41. How do you create a new calculated column?**
```python
df['revenue_at_risk'] = df['monthly_charges'] * df['churn_probability']
```

**Q42. How do you group and aggregate data?**
```python
df.groupby('contract').agg(
    churn_rate=('churn', lambda x: (x == 'Yes').mean()),
    avg_revenue=('monthly_charges', 'mean'),
    count=('customer_id', 'count')
)
```

## A8. EDA & Visualization

**Q43. What chart type best shows churn distribution?**
Pie chart or donut chart for proportions, bar chart for counts with labels.

**Q44. How do you show churn trend over time?**
Line chart with markers. Add a trendline and annotate key events (e.g., "Price increase in March").

**Q45. How do you visualize the relationship between two continuous variables?**
Scatter plot. Color by churn status. Add transparency (alpha) to handle overlapping points.

**Q46. How do you show churn across multiple segments?**
Stacked bar chart or grouped bar chart. X-axis = segment, Y-axis = proportion, stacked by churn status.

**Q47. What is a heatmap useful for showing?**
Correlation between features, or churn rates across two dimensions (e.g., contract type × internet service).

**Q48. How do you deal with skewed distributions?**
Log transformation, square root transformation, or show on a log scale. Revenue distributions are typically right-skewed.

**Q49. How do you choose between matplotlib and plotly?**
Matplotlib for static reports, publication-ready figures. Plotly for interactive dashboards, web apps, and exploratory analysis.

**Q50. How do you make visualizations accessible?**
Use colorblind-friendly palettes, add text labels, ensure sufficient contrast, provide alt text/patterns, and don't rely solely on color.

---

# SECTION B: DATA SCIENCE QUESTIONS (50)

## B1. Machine Learning Fundamentals

**Q51. What is supervised vs. unsupervised learning?**
Supervised: labeled data, predict target (our churn model — predict "Yes"/"No"). Unsupervised: no labels, find patterns (e.g., customer segmentation using K-Means).

**Q52. What type of problem is churn prediction?**
Binary classification — predicting one of two classes: Churn (Yes) or No Churn (No). Output is a probability between 0 and 1.

**Q53. What's the bias-variance tradeoff?**
High bias = underfitting (model too simple, misses patterns). High variance = overfitting (model too complex, memorizes noise). We balance with regularization and cross-validation.

**Q54. How does cross-validation work?**
Split data into K folds, train on K-1 folds, test on the held-out fold. Repeat K times. Average the results. We use 5-fold stratified CV to maintain class balance in each fold.

**Q55. What's the difference between L1 and L2 regularization?**
L1 (Lasso): adds penalty proportional to absolute value. Can zero out coefficients → feature selection. L2 (Ridge): adds penalty proportional to squared value. Shrinks coefficients but keeps all features. We use L2 for Logistic Regression.

**Q56. Why use multiple models instead of just one?**
Different models capture different patterns. Ensemble approaches combine strengths. Also, the "best" model depends on the metric — one may optimize AUC while another optimizes F1. Having options lets business stakeholders choose.

**Q57. What's ensemble learning?**
Combining multiple models for better performance. Bagging (Random Forest) reduces variance. Boosting (XGBoost, LightGBM) reduces bias by sequentially correcting errors.

**Q58. How do you handle categorical features in ML models?**
One-hot encoding (for tree models), label encoding (for ordinal), target encoding (for high cardinality), ordinal encoding. In our pipeline, we use label encoding for tree-based models and one-hot for linear models.

**Q59. What is feature scaling and when is it needed?**
Normalizing features to similar ranges. Required for Logistic Regression (gradient descent), SVM, KNN. NOT required for tree-based models (XGBoost, RF) since they split on thresholds.

**Q60. What's a pipeline in scikit-learn?**
Chains preprocessing and modeling steps. Ensures transformations are applied consistently to train and test data, preventing data leakage.

## B2. Model-Specific Questions

**Q61. How does Logistic Regression work?**
Fits a sigmoid curve to predict probability. P(churn=1) = 1/(1+e^-(β₀+β₁x₁+...)). Coefficients represent log-odds change per unit increase in feature.

**Q62. Explain Random Forest to a non-technical person.**
Imagine asking 200 experts for their opinion, then taking a vote. Each expert (decision tree) looks at a slightly different subset of the data and features. The majority vote wins. This prevents any single expert's bias from dominating.

**Q63. How does XGBoost differ from Random Forest?**
RF trains trees in parallel (bagging). XGBoost trains trees sequentially (boosting) — each tree corrects the errors of previous ones. XGBoost also has built-in regularization. XGBoost usually performs better on tabular data.

**Q64. What makes LightGBM faster than XGBoost?**
Uses leaf-wise tree growth (vs level-wise), histogram-based binning for faster split finding, and GOSS (Gradient-based One-Side Sampling) to focus on hard examples. Typically 2-10x faster with similar accuracy.

**Q65. What makes CatBoost special?**
Handles categorical features natively without preprocessing. Uses ordered boosting to prevent overfitting. Less hyperparameter tuning needed. Excellent with datasets that have many categorical features (like ours).

**Q66. What are the key hyperparameters in XGBoost?**
- n_estimators: number of trees (more = better fit, more overfitting risk)
- max_depth: depth of each tree (deeper = more complex patterns)
- learning_rate: step size (smaller = more precise, needs more trees)
- subsample/colsample_bytree: randomness (prevents overfitting)

**Q67. What is early stopping in gradient boosting?**
Stop training when validation performance stops improving for N rounds (e.g., 50). Prevents overfitting and saves computation time.

**Q68. How does hyperparameter tuning work with GridSearchCV?**
Tries every combination of specified parameter values, evaluates each via cross-validation, and returns the combination with the best score. Comprehensive but computationally expensive.

**Q69. What's the difference between GridSearchCV and RandomizedSearchCV?**
GridSearch tries all combinations (exhaustive). RandomSearch samples random combinations (faster, often near-optimal). Use RandomSearch for large parameter spaces.

**Q70. How do you prevent overfitting in tree-based models?**
Limit max_depth, increase min_samples_split/min_samples_split, use subsampling (subsample < 1), add regularization (lambda/alpha), use early stopping, reduce n_estimators.

## B3. Evaluation Metrics

**Q71. Explain Accuracy in business terms.**
"Of all customers, what percentage did we predict correctly?" Misleading with imbalanced data — 76% accuracy is trivial by predicting "No Churn" for everyone.

**Q72. What's Precision and why does it matter?**
"Of all customers we flagged as 'will churn', how many actually churned?" High precision means our retention efforts won't waste budgets on customers who wouldn't have left.

**Q73. What's Recall and why does it matter?**
"Of all customers who actually churned, how many did we catch?" High recall means we're not missing churners who could have been saved.

**Q74. When would you prioritize precision over recall?**
When retention actions are expensive. If each retention call costs ₹500 and you have a limited budget, you want to be sure you're targeting actual churners (high precision).

**Q75. When would you prioritize recall over precision?**
When the cost of missing a churner is high. VIP customers or high-value accounts — you'd rather over-target than miss someone important.

**Q76. What is the F1 Score?**
Harmonic mean of precision and recall. F1 = 2 × (Precision × Recall) / (Precision + Recall). Balances both metrics — useful when you need a single number.

**Q77. Explain ROC-AUC in simple terms.**
"If I pick a random churner and random non-churner, what's the probability my model ranks the churner higher?" 0.87 means 87% of the time, the model correctly ranks churners above non-churners.

**Q78. What's the difference between ROC-AUC and PR-AUC?**
ROC-AUC evaluates across all thresholds, considering both classes. PR-AUC (Precision-Recall) focuses on the positive class only. PR-AUC is more informative for imbalanced datasets where the positive class is rare.

**Q79. How do you interpret a confusion matrix?**
- True Positives: correctly predicted churners → target these!
- True Negatives: correctly predicted retained → leave them alone
- False Positives: flagged as churner but won't churn → wasted resources
- False Negatives: missed churners → lost revenue

**Q80. What threshold do you use for classification?**
Default is 0.5. But you can adjust based on business needs. Increase threshold to reduce false positives (higher precision, lower recall). Decrease to catch more churners (higher recall, lower precision).

## B4. Feature Engineering

**Q81. What features did you engineer and why?**
- avg_monthly_charge: captures spending pattern independent of tenure
- charge_tenure_ratio: >1 means recent charges increased — risk signal
- customer_lifetime_value: identifies high-value customers to prioritize
- engagement_score: bundled services = stickier customers
- loyalty_score: composite of tenure + contract + engagement
- churn_risk_index: heuristic risk score from known patterns

**Q82. How do you know if a feature is useful?**
Domain knowledge + statistical analysis (correlation with target) + model-based importance (feature importances) + SHAP analysis. A feature is useful if removing it hurts model performance.

**Q83. What's feature leakage?**
Using information that won't be available at prediction time. Example: using "total complaints in last 30 days" when you only know complaints after they happen. We ensure all features are known at prediction time.

**Q84. How do you handle multicollinearity?**
Remove highly correlated features, use regularization (L1/L2), use PCA, or keep both (tree models handle it fine). In our case, MonthlyCharges and TotalCharges are correlated — we engineer ratio features instead.

**Q85. What's the difference between feature selection and feature extraction?**
Selection: choosing a subset of existing features (remove unimportant ones). Extraction: creating new features from existing ones (PCA, polynomial features). We did both.

## B5. Data Science Process

**Q86. Walk me through your DS project lifecycle.**
1. Business Understanding: define problem, stakeholders, success criteria
2. Data Understanding: explore, audit, document
3. EDA: visualizations, patterns, hypotheses
4. Data Cleaning: handle missing, outliers, consistency
5. Feature Engineering: create business-meaningful features
6. Modeling: train multiple models, tune hyperparameters
7. Evaluation: compare metrics, select best model
8. Explainability: SHAP, feature importance for business
9. Deployment: dashboard, API, monitoring
10. Communication: reports, presentations for stakeholders

**Q87. How do you validate that data is representative?**
Compare distributions across segments, check for selection bias, verify sample size adequacy, compare with external benchmarks (industry churn rates).

**Q88. What would you do if model performance degrades in production?**
1. Check for data drift (feature distributions changed?)
2. Check for concept drift (relationship between features and target changed?)
3. Retrain with recent data
4. If persistent, redesign features or try different model
5. Set up automated monitoring to catch this early

**Q89. How do you ensure reproducibility?**
Set random seeds, pin dependencies (requirements.txt), use version control, log all experiments, use pipelines (scikit-learn), document decisions.

**Q90. What's A/B testing and how does it relate to churn?**
Test retention strategies by randomly assigning customers to treatment/control groups. E.g., Group A gets 10% discount, Group B gets nothing. Compare churn rates after 3 months to measure effectiveness.

## B6. Advanced Concepts

**Q91. What is SHAP and how does it work?**
SHapley Additive exPlanations — based on game theory. Calculates each feature's contribution to a prediction by comparing predictions with and without each feature, across all possible combinations.

**Q92. How do you handle class imbalance?**
- Resampling: SMOTE (oversample minority), undersample majority
- Class weights: penalize misclassification of minority class more
- Threshold tuning: adjust classification threshold
- Evaluation: use PR-AUC instead of ROC-AUC
- Algorithm: use models that handle imbalance natively (CatBoost)

**Q93. What's the curse of dimensionality?**
As features increase, data becomes sparse, distance metrics break, and models overfit. Mitigation: feature selection, regularization, dimensionality reduction (PCA).

**Q94. Explain the concept of model calibration.**
A calibrated model's predicted probability matches actual frequency. If the model says 80% churn probability, ~80% of those customers should actually churn. Important for business trust.

**Q95. What's online learning vs. batch learning?**
Batch learning: train on all data at once (our approach). Online learning: update model incrementally with new data. Online is better for real-time, streaming scenarios.

## B7. Data Engineering for DS

**Q96. How would you design a data pipeline for real-time churn prediction?**
Data source (customer database) → Feature store (precomputed features) → Model serving (API) → Dashboard (real-time updates) → Action system (CRM integration).

**Q97. What is a feature store and why is it important?**
Centralized repository for storing and serving features. Ensures consistency between training and serving, avoids redundant computation, and enables feature reuse across teams.

**Q98. How would you handle data quality in production?**
Data validation on ingestion (schema, ranges, distributions), automated quality checks, anomaly detection, alerting on failures, and fallback strategies (use last known good data).

**Q99. What's the difference between ETL and ELT?**
ETL: Extract → Transform → Load (transform before loading to warehouse). ELT: Extract → Load → Transform (load raw, transform in warehouse). ELT is more flexible with modern cloud warehouses.

**Q100. How do you version datasets?**
Data versioning tools (DVC), timestamped snapshots, hash-based tracking, or simple convention: dataset_v1_20260530.csv. We use DVC-compatible naming in our project.

---

# SECTION C: MACHINE LEARNING ENGINEERING QUESTIONS (50)

## C1. MLOps & Deployment

**Q101. What is MLOps?**
Set of practices to deploy and maintain ML models in production reliably. Combines ML, DevOps, and data engineering. Includes CI/CD for ML, monitoring, versioning, and automation.

**Q102. How do you version ML models?**
Model registry (MLflow, custom), metadata (training date, hyperparameters, metrics), artifact storage (model files), and stage management (staging → production → archived).

**Q103. What's CI/CD for ML?**
Continuous Integration: automatically test code and data on every push. Continuous Delivery: automatically deploy passing models to staging. Continuous Training: automatically retrain when triggered.

**Q104. How do you monitor ML models in production?**
- Performance monitoring: track accuracy metrics over time
- Data drift: compare incoming feature distributions to training
- Prediction drift: track distribution of predictions
- Infrastructure: latency, throughput, error rates
- Business KPIs: actual churn rate vs predicted

**Q105. What is data drift?**
Change in the distribution of incoming data compared to training data. E.g., if a new tariff plan changes the average monthly charge from ₹80 to ₹120, the model's assumptions may no longer hold.

**Q106. What is concept drift?**
The relationship between features and target changes over time. E.g., customers may have tolerated high charges before, but a new competitor changes their behavior. The same features predict differently.

**Q107. How would you do blue-green deployment for ML?**
Run two identical production environments. Deploy new model to the "green" environment while "blue" serves traffic. Test green, then switch traffic. If issues, rollback to blue.

**Q108. How do you package a Python ML application?**
- requirements.txt for dependencies
- Dockerfile for containerization
- setup.py or pyproject.toml for pip installability
- __init__.py, __version__ for library structure
- README.md with usage examples

**Q109. What's the difference between a model and a serialized model?**
A model is the trained object in memory. A serialized model (saved to disk as .joblib/.pkl) can be persisted, transferred, and loaded in a different process. We use joblib.dump().

**Q110. How do you design a model serving API?**
REST API (FastAPI/Flask) with: POST /predict endpoint, input validation, error handling, logging, health check endpoint, model versioning in URL or headers.

**Q111. What is model staleness?**
When a model becomes outdated because the world changes. Mitigated by scheduled retraining, online learning, or drift-triggered retraining.

**Q112. How do you do A/B testing with ML models?**
Randomly route 50% of traffic to Model A (current) and 50% to Model B (new). Compare business metrics (churn rate, revenue saved) over statistically significant period.

**Q113. What is feature serving latency and how to optimize?**
Time to compute features for a single prediction. Optimize with: precomputed features in a feature store, caching, batch feature computation, and reducing feature complexity.

**Q114. Explain your Docker deployment.**
Our Dockerfile: Python 3.11 slim base, installs dependencies from requirements.txt, copies app files, exposes port 8501, health check endpoint, runs Streamlit. Deployed via Docker Compose with volume mounts for models/data/logs.

**Q115. How would you autoscale a model prediction API?**
Container orchestration (Kubernetes HPA), serverless (AWS Lambda), managed services (SageMaker endpoints). Scale based on request concurrency, queue depth, or CPU/memory.

## C2. Advanced ML

**Q116. What's gradient boosting?**
Sequentially trains weak learners (trees) where each new tree predicts the residual errors of the previous ensemble. The final prediction is the sum of all trees' predictions, scaled by the learning rate.

**Q117. Why does XGBoost use second-order gradients?**
Newton's method (second-order) converges faster than gradient descent (first-order). XGBoost approximates the loss function with a Taylor expansion up to the second order, giving more precise updates.

**Q118. What is bagging vs. boosting?**
Bagging (Bootstrap Aggregating): train models independently on random subsets, average results. Reduces variance. Boosting: train models sequentially, each focusing on previous errors. Reduces bias.

**Q119. What's the difference between LightGBM and XGBoost split finding?**
XGBoost: level-wise (grow tree level by level). LightGBM: leaf-wise (grow the leaf with maximum loss reduction). Leaf-wise usually performs better but can overfit on small data.

**Q120. How does CatBoost handle categorical features?**
Uses ordered target encoding: for each category, computes the mean target value of all preceding samples (in a random permutation) to avoid target leakage. Also uses combinations of categorical features.

**Q121. What is permutation importance?**
Shuffle each feature's values and measure the drop in model performance. A large drop means the important feature was important. Model-agnostic — works with any model.

**Q122. How do you implement feature importance in your project?**
Three methods: (1) Native feature_importances_ from tree models, (2) SHAP values for global and local interpretability, (3) Permutation importance as a model-agnostic check.

**Q123. What's the difference between micro and macro F1?**
Macro F1: compute F1 for each class, then average (treats all classes equally). Micro F1: compute globally by counting total TP, FP, FN (favors majority class). For imbalanced data, macro F1 is fairer.

**Q124. How do you choose the right evaluation metric?**
Depends on business objective: If cost of false positives (wasted retention effort) is high → optimize precision. If cost of false negatives (missed churners) is high → optimize recall. If optimize overall ranking → optimize AUC.

**Q125. What is calibration and how do you calibrate a model?**
Calibration ensures predicted probabilities match actual frequencies. Methods: Platt scaling (logistic regression on model outputs), isotonic regression (non-parametric). Check with calibration curves.

## C3. System Design for ML

**Q126. Design a real-time churn prediction system.**
```
Customers → Event Stream (Kafka) → Feature Store → Model Server (FastAPI)
     ↓                                                       ↓
CRM System ← Action Engine ← Prediction API ←────────────┘
                         ↓
                   Dashboard (real-time)
```

**Q127. How would you handle 1M+ predictions per day?**
Batch predictions for non-urgent, real-time API for on-demand. Use model serving framework (Triton, TF Serving). Horizontal scaling with load balancing. Cache predictions with TTL.

**Q128. How do you balance model complexity vs. latency?**
Start simple, add complexity only if it improves metrics significantly. Prune trees, quantize models (INT8), use ONNX Runtime for faster inference. A simpler model with 0.85 AUC that responds in 10ms may be preferred over a complex one with 0.87 AUC that takes 500ms.

**Q129. What is a shadow deployment?**
Run the new model in parallel with the current model, logging its predictions but not acting on them. Compare performance before switching. Zero-risk way to validate new models.

**Q130. How would you handle model rollback?**
Keep all previous model versions. If the new model degrades, switch back to the previous version instantly. Blue-green deployment or model registry with "active" flag.

## C4. Deep Learning (if applicable)

**Q131. When would you use deep learning for churn prediction?**
When data is very large (>10M rows), has complex interactions, includes unstructured data (text: call transcripts, emails), or temporal patterns (sequential behavior). For tabular data with 10K rows, gradient boosting is usually superior.

**Q132. What's a neural network approach to churn?**
Feed-forward network with embedding layers for categorical features, batch normalization, dropout for regularization. Or use TabNet (attention-based architecture for tabular data).

## C5. Practical/Behavioral

**Q133. Tell me about your ConnectTel project.**
See the STAR answers in phase14_portfolio_assets.md — Situation, Task, Action, Result format covering the full project lifecycle.

**Q134. What was the hardest part of this project?**
Balancing model performance with explainability. A black-box model might be 1% more accurate but useless to business teams who need to understand WHY a customer is at risk. SHAP analysis + business-friendly reports solved this.

**Q135. How would you improve this project?**
1. Use a real dataset instead of synthetic
2. Add temporal features (trend in charges over last 6 months)
3. Implement survival analysis for time-to-churn
4. Add A/B testing framework for retention actions
5. Deploy as REST API with FastAPI
6. Add auth, rate limiting, and production monitoring

**Q136. How do you handle stakeholders who want 100% accuracy?**
Set realistic expectations: no model is perfect. Explain the bias-variance tradeoff, show that even catching 75% of churners saves crores. Frame it as "prioritizing who to save" rather than "predicting everything perfectly."

**Q137. What would you do if your model has high bias?**
Add more features, use a more complex model, reduce regularization, engineer interaction features, or use ensemble methods.

**Q138. What would you do if your model has high variance?**
Get more data, reduce features, increase regularization, use simpler model, add dropout (for NNs), or increase training data via augmentation.

**Q139. How do you communicate uncertainty to executives?**
Use confidence intervals ("We estimate 2,000-2,500 churners next month"), probability ranges instead of point predictions, and visualizations showing the range of possible outcomes.

**Q140. How would you explain overfitting to a CEO?**
"It's like memorizing answers to a practice test instead of understanding the concepts. The model scores perfectly on training data but fails on new customers. We fix this by using cross-validation — testing on data the model has never seen."

## C6. Testing & Validation

**Q141. How do you test an ML pipeline?**
- Unit tests: data validation, feature transformation, model loading
- Integration tests: end-to-end pipeline, API endpoints
- Data tests: schema validation, distribution checks
- Model tests: performance on held-out set, fairness metrics

**Q142. What's a train-test contamination and how to prevent it?**
When test set information leaks into training (e.g., computing scaling on full data before splitting). Prevention: split first, then transform. Use sklearn Pipelines to encapsulate everything.

**Q143. How do you test for fairness?**
Check model performance across demographic groups (gender, age). Ensure similar precision/recall for all groups. Use fairness metrics: demographic parity, equalized odds.

**Q144. How do you ensure data quality in tests?**
Schema validation (correct columns, types), range checks (tenure >= 0), null checks, distribution comparison (current vs baseline), and automated alerts.

**Q145. What's the difference between unit tests and integration tests?**
Unit tests: test individual functions in isolation (e.g., feature engineering). Integration tests: test the full pipeline working together (data → features → model → prediction).

## C7. Scaling & Performance

**Q146. How would you scale the pipeline to 100M customers?**
Use Spark/Dask for distributed data processing, batch predictions with Spark MLlib or Ray, cloud ML platforms (SageMaker, Vertex AI), and store features in distributed databases.

**Q147. What's the difference between batch and stream processing?**
Batch: process data at intervals (daily, hourly). Stream: process data in real-time as it arrives. Churn prediction can use both: batch for risk scoring all customers nightly, stream for real-time event-based scoring.

**Q148. How do you optimize model training time?**
Use GPU (XGBoost GPU), reduce features, sample data for profiling, use early stopping, parallelize cross-validation, and use LightGBM for faster training.

**Q149. What is model quantization?**
Reducing the precision of model weights (FP32 → INT8). Reduces model size and inference time with minimal accuracy loss. Useful for edge deployment and high-throughput APIs.

**Q150. How do you design for failure in ML systems?**
Graceful degradation: if model fails, fall back to rule-based scoring. Circuit breakers: if API latency exceeds threshold, return cached results. Monitoring and alerting: catch issues before users notice.

---

# QUICK REFERENCE CARD

## Key Numbers to Remember
- Dataset: 10,476 customers, 22 features
- Churn Rate: ~26%
- Best Model: XGBoost (AUC ≈ 0.87)
- Revenue at Risk: ₹31.2 Cr/year
- Potential Savings (10% reduction): ₹3.54 Cr/year
- Engineered Features: 12
- Models Trained: 5
- CV Folds: 5

## Answers Framework
When explaining ANY ML concept to non-technical stakeholders:
1. Start with the business problem
2. Use an analogy
3. Show the business impact
4. Avoid jargon
5. Focus on actions, not metrics

## Project Differentiators
1. End-to-end (15 phases, not just a notebook)
2. Explainable AI (SHAP)
3. Retention Intelligence Engine (actionable recommendations)
4. Executive Dashboard (production-quality UI)
5. MLOps (Docker, CI/CD, monitoring)
6. Business focus (revenue impact, not just accuracy)
7. STAR stories for every phase
8. Ready for deployment and interviews
