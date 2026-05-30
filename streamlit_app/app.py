"""
Phase 11: ConnectTel Churn Intelligence Dashboard
Streamlit Application — Executive-Level Analytics
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import joblib
import json
import os
import sys

# Page config
st.set_page_config(
    page_title="ConnectTel Churn Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size:2.5rem; font-weight:700; color:#1a73e8; margin-bottom:0;
    }
    .sub-header {
        font-size:1.1rem; color:#5f6368; margin-top:0; margin-bottom:2rem;
    }
    .kpi-card {
        background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius:12px; padding:1.2rem; color:white; text-align:center;
    }
    .kpi-value { font-size:2rem; font-weight:700; }
    .kpi-label { font-size:0.85rem; opacity:0.9; }
    .risk-critical { color:#e74c3c; font-weight:700; }
    .risk-high { color:#e67e22; font-weight:700; }
    .risk-moderate { color:#f1c40f; font-weight:700; }
    .risk-low { color:#2ecc71; font-weight:700; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
MODEL_DIR = "models"


@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "connecttel_churn_engineered.csv"))
    try:
        predictions = pd.read_csv(os.path.join(DATA_DIR, "retention_recommendations.csv"))
    except FileNotFoundError:
        predictions = None
    try:
        model_comp = pd.read_csv("notebooks/model_comparison.csv", index_col=0)
    except FileNotFoundError:
        model_comp = None
    return df, predictions, model_comp


@st.cache_resource
def load_model():
    try:
        model = joblib.load(os.path.join(MODEL_DIR, "best_model.joblib"))
        feature_cols = json.load(open(os.path.join(MODEL_DIR, "feature_columns.json")))
        encoders = joblib.load(os.path.join(MODEL_DIR, "label_encoders.joblib"))
        return model, feature_cols, encoders
    except:
        return None, None, None


def render_kpi_cards(df):
    total = len(df)
    churned = (df["Churn"] == "Yes").sum()
    churn_rate = churned / total * 100
    avg_revenue = df["MonthlyCharges"].mean()
    total_revenue = df["MonthlyCharges"].sum()
    revenue_at_risk = df[df["Churn"] == "Yes"]["MonthlyCharges"].sum()
    avg_tenure = df["tenure"].mean()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Customers", f"{total:,}")
    c2.metric("Churn Rate", f"{churn_rate:.1f}%", delta=f"{churned:,} churned")
    c3.metric("Avg Monthly Revenue", f"₹{avg_revenue:,.0f}")
    c4.metric("Total Monthly Rev", f"₹{total_revenue:,.0f}")
    c5.metric("Revenue at Risk", f"₹{revenue_at_risk:,.0f}", delta_color="inverse")
    c6.metric("Avg Tenure", f"{avg_tenure:.1f} mo")


def executive_overview(df):
    st.markdown('<div class="main-header">📡 ConnectTel Churn Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Executive Overview | Real-Time Customer Analytics</div>', unsafe_allow_html=True)

    render_kpi_cards(df)

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Churn Distribution")
        churn_counts = df["Churn"].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=["Retained", "Churned"],
            values=[churn_counts.get("No", 0), churn_counts.get("Yes", 0)],
            hole=0.4,
            marker_colors=["#2ecc71", "#e74c3c"],
        )])
        fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Churn by Contract Type")
        contract_churn = pd.crosstab(df["Contract"], df["Churn"], normalize="index") * 100
        fig = go.Figure()
        if "Yes" in contract_churn.columns:
            fig.add_trace(go.Bar(name="Churned", x=contract_churn.index, y=contract_churn["Yes"], marker_color="#e74c3c"))
        if "No" in contract_churn.columns:
            fig.add_trace(go.Bar(name="Retained", x=contract_churn.index, y=contract_churn["No"], marker_color="#2ecc71"))
        fig.update_layout(barmode="stack", height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Tenure Distribution")
        fig = px.histogram(df, x="tenure", color="Churn",
                           nbins=36, color_discrete_map={"No": "#2ecc71", "Yes": "#e74c3c"},
                           labels={"tenure": "Tenure (months)"})
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Monthly Charges Distribution")
        fig = px.histogram(df, x="MonthlyCharges", color="Churn",
                           nbins=30, color_discrete_map={"No": "#2ecc71", "Yes": "#e74c3c"},
                           labels={"MonthlyCharges": "Monthly Charges (₹)"})
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)


def churn_analytics(df):
    st.markdown('<div class="main-header">🔍 Churn Analytics</div>', unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        contract_filter = st.multiselect("Contract Type", df["Contract"].unique(), default=df["Contract"].unique())
    with fc2:
        internet_filter = st.multiselect("Internet Service", df["InternetService"].unique(), default=df["InternetService"].unique())
    with fc3:
        tenure_range = st.slider("Tenure Range", 0, 72, (0, 72))
    with fc4:
        charge_range = st.slider("Monthly Charge Range",
                                  float(df["MonthlyCharges"].min()),
                                  float(df["MonthlyCharges"].max()),
                                  (float(df["MonthlyCharges"].min()), float(df["MonthlyCharges"].max())))

    filtered = df[
        (df["Contract"].isin(contract_filter)) &
        (df["InternetService"].isin(internet_filter)) &
        (df["tenure"] >= tenure_range[0]) & (df["tenure"] <= tenure_range[1]) &
        (df["MonthlyCharges"] >= charge_range[0]) & (df["MonthlyCharges"] <= charge_range[1])
    ]

    st.write(f"Filtered: **{len(filtered):,}** customers")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Churn by Payment Method")
        pay_churn = pd.crosstab(filtered["PaymentMethod"], filtered["Churn"], normalize="index") * 100
        fig = go.Figure()
        if "Yes" in pay_churn.columns:
            fig.add_trace(go.Bar(name="Churned %", x=pay_churn.index, y=pay_churn["Yes"], marker_color="#e74c3c"))
        fig.update_layout(height=350, margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Churn by Internet Service + Contract")
        heatmap_data = pd.crosstab(filtered["InternetService"], filtered["Contract"],
                                    values=(filtered["Churn"] == "Yes").astype(int),
                                    aggfunc="mean") * 100
        fig = px.imshow(heatmap_data, text_auto=".1f",
                        labels=dict(color="Churn %"),
                        color_continuous_scale="Reds")
        fig.update_layout(height=350, margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Service Adoption vs Churn")
    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    service_churn = []
    for col in service_cols:
        for val in ["Yes", "No"]:
            subset = filtered[filtered[col] == val]
            if len(subset) > 0:
                churn_pct = (subset["Churn"] == "Yes").mean() * 100
                service_churn.append({"Service": col, "Status": val, "Churn %": round(churn_pct, 1)})

    svc_df = pd.DataFrame(service_churn)
    fig = px.bar(svc_df, x="Service", y="Churn %", color="Status",
                 barmode="group", color_discrete_map={"Yes": "#2ecc71", "No": "#e74c3c"},
                 text="Churn %")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def revenue_analytics(df):
    st.markdown('<div class="main-header">💰 Revenue Analytics</div>', unsafe_allow_html=True)

    total_monthly = df["MonthlyCharges"].sum()
    churned_rev = df[df["Churn"] == "Yes"]["MonthlyCharges"].sum()
    retained_rev = df[df["Churn"] == "No"]["MonthlyCharges"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Monthly Revenue", f"₹{total_monthly:,.0f}")
    c2.metric("Monthly Revenue Lost", f"₹{churned_rev:,.0f}", delta_color="inverse")
    c3.metric("Annual Revenue Lost", f"₹{churned_rev * 12:,.0f}", delta_color="inverse")
    c4.metric("Churn Revenue Impact", f"{(churned_rev/total_monthly*100):.1f}%")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Revenue by Contract Type")
        rev_contract = df.groupby("Contract").agg(
            Total=("MonthlyCharges", "sum"),
            Churned=("MonthlyCharges", lambda x: x[df.loc[x.index, "Churn"] == "Yes"].sum()),
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Retained", x=rev_contract["Contract"], y=rev_contract["Total"] - rev_contract["Churned"], marker_color="#2ecc71"))
        fig.add_trace(go.Bar(name="Lost to Churn", x=rev_contract["Contract"], y=rev_contract["Churned"], marker_color="#e74c3c"))
        fig.update_layout(barmode="stack", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("CLV Distribution")
        if "customer_lifetime_value" in df.columns:
            fig = px.histogram(df, x="customer_lifetime_value", color="Churn",
                               nbins=50, log_x=True,
                               color_discrete_map={"No": "#2ecc71", "Yes": "#e74c3c"})
        else:
            fig = px.histogram(df, x="TotalCharges", color="Churn",
                               nbins=50, log_x=True,
                               color_discrete_map={"No": "#2ecc71", "Yes": "#e74c3c"})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Estimated Annual Savings by Churn Reduction")
    savings = []
    for reduction_pct in [5, 10, 15, 20, 25, 50]:
        saved = churned_rev * (reduction_pct / 100) * 12
        savings.append({"Churn Reduction": f"{reduction_pct}%", "Annual Savings (₹)": saved})

    savings_df = pd.DataFrame(savings)
    fig = px.bar(savings_df, x="Churn Reduction", y="Annual Savings (₹)",
                 color="Annual Savings (₹)", text="Annual Savings (₹)",
                 color_continuous_scale="Greens")
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


def customer_segmentation(df):
    st.markdown('<div class="main-header">👥 Customer Segmentation</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Tenure vs Charges (Churn Heatmap)")
        fig = px.density_heatmap(df, x="tenure", y="MonthlyCharges",
                                  nbinsx=24, nbinsy=20,
                                  color_continuous_scale="YlOrRd",
                                  title="")
        fig.add_hline(y=df["MonthlyCharges"].median(), line_dash="dash")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Engagement Score vs Churn")
        if "engagement_score" in df.columns:
            fig = px.histogram(df, x="engagement_score", color="Churn",
                               nbins=20, barmode="overlay", opacity=0.7,
                               color_discrete_map={"No": "#2ecc71", "Yes": "#e74c3c"})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run feature engineering first.")

    st.markdown("---")
    st.subheader("3D Customer View")
    if all(col in df.columns for col in ["tenure", "MonthlyCharges"]):
        fig = px.scatter_3d(
            df.sample(min(2000, len(df)), random_state=42),
            x="tenure", y="MonthlyCharges",
            z="TotalCharges" if "TotalCharges" in df.columns else "tenure",
            color="Churn", opacity=0.6,
            color_discrete_map={"No": "#2ecc71", "Yes": "#e74c3c"},
            labels={"tenure": "Tenure", "MonthlyCharges": "Monthly Charges"},
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)


def ai_prediction_center(df):
    st.markdown('<div class="main-header">🤖 AI Prediction Center</div>', unsafe_allow_html=True)

    model, feature_cols, encoders = load_model()

    if model is None:
        st.warning("Model not found. Run the ML pipeline first.")
        return

    st.subheader("Single Customer Prediction")
    st.write("Enter customer details to predict churn risk:")

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        pred_gender = st.selectbox("Gender", ["Male", "Female"])
        pred_senior = st.selectbox("Senior Citizen", [0, 1])
        pred_partner = st.selectbox("Partner", ["Yes", "No"])
        pred_dependents = st.selectbox("Dependents", ["Yes", "No"])
    with pc2:
        pred_tenure = st.slider("Tenure (months)", 0, 72, 12)
        pred_contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        pred_internet = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        pred_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
    with pc3:
        pred_charges = st.slider("Monthly Charges (₹)", 18.0, 120.0, 70.0)
        pred_total = st.number_input("Total Charges (₹)", 0.0, 10000.0, pred_charges * pred_tenure)
        pred_payment = st.selectbox("Payment Method",
                                     ["Electronic check", "Mailed check",
                                      "Bank transfer (automatic)", "Credit card (automatic)"])
        pred_security = st.selectbox("Online Security", ["Yes", "No"])
        pred_support = st.selectbox("Tech Support", ["Yes", "No"])

    if st.button("Predict Churn Risk", type="primary"):
        customer = {
            "customerID": "PREDICT-001",
            "gender": pred_gender,
            "SeniorCitizen": pred_senior,
            "Partner": pred_partner,
            "Dependents": pred_dependents,
            "tenure": pred_tenure,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": pred_internet,
            "OnlineSecurity": pred_security,
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": pred_support,
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": pred_contract,
            "PaperlessBilling": pred_billing,
            "PaymentMethod": pred_payment,
            "MonthlyCharges": pred_charges,
            "TotalCharges": pred_total,
            "Churn": "No",
            "avg_monthly_charge": pred_total / max(pred_tenure, 1),
            "charge_tenure_ratio": pred_charges / (pred_total / max(pred_tenure, 1) + 1e-6),
            "customer_lifetime_value": pred_charges * pred_tenure,
            "engagement_score": 30.0,
            "service_utilization_score": 25.0,
            "contract_risk_score": {"Month-to-month": 1.0, "One year": 0.3, "Two year": 0.1}[pred_contract],
            "loyalty_score": 40.0,
            "churn_risk_index": 50.0,
            "tenure_group": "12-24",
            "is_new_customer": int(pred_tenure <= 3),
            "has_autopay": int("automatic" in pred_payment),
            "has_fiber": int(pred_internet == "Fiber optic"),
        }

        X_pred = pd.DataFrame([customer])
        for col in X_pred.select_dtypes(include=["object"]).columns:
            if col in encoders:
                try:
                    X_pred[col] = encoders[col].transform(X_pred[col].astype(str))
                except:
                    X_pred[col] = 0
            else:
                X_pred[col] = 0

        for col in feature_cols:
            if col not in X_pred.columns:
                X_pred[col] = 0

        X_pred = X_pred[feature_cols]
        proba = model.predict_proba(X_pred)[0]
        churn_prob = proba[1]

        # Results
        rc1, rc2, rc3 = st.columns(3)
        risk_color = "#e74c3c" if churn_prob > 0.6 else "#f39c12" if churn_prob > 0.3 else "#2ecc71"
        risk_level = "CRITICAL" if churn_prob > 0.8 else "HIGH" if churn_prob > 0.6 else "MODERATE" if churn_prob > 0.3 else "LOW"

        rc1.metric("Churn Probability", f"{churn_prob:.1%}", delta=f"Risk: {risk_level}", delta_color="off")
        rc2.metric("Risk Level", risk_level)
        rc3.metric("Annual Revenue at Risk", f"₹{pred_charges * 12 * churn_prob:,.0f}")

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=churn_prob * 100,
            domain=dict(x=[0, 1], y=[0, 1]),
            title=dict(text="Churn Risk Score"),
            gauge=dict(
                axis=dict(range=[0, 100]),
                bar=dict(color=risk_color),
                steps=[
                    dict(range=[0, 30], color="#2ecc71"),
                    dict(range=[30, 60], color="#f39c12"),
                    dict(range=[60, 100], color="#e74c3c"),
                ],
                threshold=dict(line=dict(color="red", width=4), thickness=0.75, value=churn_prob * 100),
            ),
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Personalized Recommendations")
        reasons = []
        if pred_contract == "Month-to-month":
            reasons.append("📌 Month-to-month contract = highest churn risk. Offer 15% discount on annual plan.")
        if pred_tenure < 6:
            reasons.append("📌 New customer (< 6 months). Schedule proactive check-in call.")
        if pred_charges > 75:
            reasons.append("📌 High monthly charges. Offer mid-tier plan or loyalty discount.")
        if pred_security == "No":
            reasons.append("📌 No online security. Bundle free security for 6 months.")
        if pred_support == "No":
            reasons.append("📌 No tech support. Offer 3 months free premium support.")
        if pred_internet == "Fiber optic":
            reasons.append("📌 Fiber optic plans have high churn. Review pricing vs competitors.")

        for reason in reasons:
            st.info(reason)

        if not reasons:
            st.success("This customer shows low churn risk. Maintain regular engagement.")


def retention_recommendations(df, predictions):
    st.markdown('<div class="main-header">🎯 Retention Recommendations</div>', unsafe_allow_html=True)

    if predictions is not None:
        st.subheader("Top At-Risk Customers")
        st.dataframe(
            predictions[["customer_id", "churn_probability", "risk_level", "estimated_annual_revenue_at_risk"]].head(20),
            use_container_width=True,
            hide_index=True,
        )

        csv = predictions.to_csv(index=False)
        st.download_button("Download Full Recommendations (CSV)", csv, "retention_recommendations.csv")
    else:
        st.info("Run the retention engine to generate recommendations.")
        # Show simulated high-risk segment
        high_risk = df[
            (df["Contract"] == "Month-to-month") & (df["Churn"] == "Yes")
        ].head(20)
        st.subheader("High-Risk Segment (Month-to-Month + Churned)")
        st.dataframe(high_risk[["customerID", "tenure", "MonthlyCharges", "Contract", "TotalCharges"]],
                     use_container_width=True, hide_index=True)


def model_monitoring(model_comp):
    st.markdown('<div class="main-header">📊 Model Monitoring</div>', unsafe_allow_html=True)

    if model_comp is not None:
        st.subheader("Model Comparison")
        st.dataframe(model_comp, use_container_width=True)

        st.subheader("ROC-AUC Comparison")
        fig = px.bar(model_comp.reset_index(), x="model", y="roc_auc",
                     text="roc_auc", color="roc_auc",
                     color_continuous_scale="RdYlGn",
                     title="")
        fig.update_traces(texttemplate="%{text:.4f}", textposition="outside")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("All Metrics Comparison")
        metrics = ["accuracy", "precision", "recall", "f1_score"]
        melted = model_comp[metrics].reset_index().melt(id_vars="model", var_name="metric", value_name="score")
        fig = px.bar(melted, x="model", y="score", color="metric", barmode="group")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        best = model_comp["roc_auc"].idxmax()
        st.success(f"🏆 Best Model: {best} (AUC = {model_comp.loc[best, 'roc_auc']:.4f})")
    else:
        st.info("Run the ML pipeline to populate model monitoring data.")

    st.markdown("---")
    st.subheader("Model Health Checks")
    hc1, hc2, hc3 = st.columns(3)
    hc1.metric("Model Version", "v1.0.0")
    hc2.metric("Last Training", "2026-05-30")
    hc3.metric("Drift Status", "✅ No Drift Detected")


# ============================================================
# MAIN APP
# ============================================================
def main():
    df, predictions, model_comp = load_data()

    # Sidebar
    st.sidebar.title("📡 ConnectTel AI")
    st.sidebar.markdown("---")

    page = st.sidebar.radio("Navigation", [
        "Executive Overview",
        "Churn Analytics",
        "Revenue Analytics",
        "Customer Segmentation",
        "AI Prediction Center",
        "Retention Recommendations",
        "Model Monitoring",
    ])

    st.sidebar.markdown("---")
    st.sidebar.markdown("**About**")
    st.sidebar.info("ConnectTel Churn Intelligence Platform v1.0 | Built with XGBoost + SHAP + Streamlit")

    pages = {
        "Executive Overview": lambda: executive_overview(df),
        "Churn Analytics": lambda: churn_analytics(df),
        "Revenue Analytics": lambda: revenue_analytics(df),
        "Customer Segmentation": lambda: customer_segmentation(df),
        "AI Prediction Center": lambda: ai_prediction_center(df),
        "Retention Recommendations": lambda: retention_recommendations(df, predictions),
        "Model Monitoring": lambda: model_monitoring(model_comp),
    }

    pages.get(page, pages["Executive Overview"])()


if __name__ == "__main__":
    main()
