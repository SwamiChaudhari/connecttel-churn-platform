"""
Phase 9: Retention Intelligence Engine
Generates personalized retention recommendations for each customer.
"""
import pandas as pd
import numpy as np
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import joblib

from sklearn.preprocessing import LabelEncoder

MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data")
REPORT_DIR = os.path.join(PROJECT_ROOT, "docs")
os.makedirs(REPORT_DIR, exist_ok=True)


class RetentionIntelligenceEngine:
    """
    AI-powered retention recommendation system.
    Takes customer features, predicts churn, and generates
    personalized retention strategies.
    """

    def __init__(self):
        self.model = joblib.load(os.path.join(MODEL_DIR, "best_model.joblib"))
        self.feature_columns = json.load(open(os.path.join(MODEL_DIR, "feature_columns.json")))
        self.label_encoders = joblib.load(os.path.join(MODEL_DIR, "label_encoders.joblib"))

        # Define recommendation rules
        self.recommendation_rules = {
            "MonthlyCharges": {
                "threshold": 75,
                "high": [
                    "Offer 10-15% loyalty discount",
                    "Recommend mid-tier plan with better value",
                    "Provide cost-saving bundle options",
                ],
                "low": ["Current pricing is competitive — no action needed"],
            },
            "Contract": {
                "value": "Month-to-month",
                "actions": [
                    "Incentivize contract upgrade: 15% discount on annual plan",
                    "Offer 2-year contract with free installation",
                    "Provide loyalty bonus (free month) for contract commitment",
                ],
            },
            "tenure": {
                "low_threshold": 6,
                "actions": [
                    "Assign dedicated retention manager for first 90 days",
                    "Schedule proactive check-in call within 30 days",
                    "Send personalized onboarding content",
                    "Offer welcome bonus (free service for 1 month)",
                ],
            },
            "OnlineSecurity": {
                "value": "No",
                "actions": [
                    "Include free online security for 6 months",
                    "Bundle security with existing plan at 50% off",
                ],
            },
            "TechSupport": {
                "value": "No",
                "actions": [
                    "Provide 3 months free premium tech support",
                    "Offer 24/7 priority support access",
                ],
            },
            "InternetService": {
                "value": "Fiber optic",
                "actions": [
                    "Review fiber pricing against competitors",
                    "Offer upgrade to premium fiber at same price",
                    "Provide free speed boost trial",
                ],
            },
            "PaymentMethod": {
                "value": "Electronic check",
                "actions": [
                    "Switch to auto-pay: ₹50/month discount for 6 months",
                    "Offer credit card payment with cashback",
                ],
            },
            "PaperlessBilling": {
                "value": "Yes",
                "actions": [
                    "Send personalized monthly usage report",
                    "Offer paper bill option if preferred",
                ],
            },
            "engagement_score": {
                "low_threshold": 30,
                "actions": [
                    "Recommend complementary services",
                    "Offer service bundle discount (3+ services, 20% off)",
                    "Send targeted service discovery content",
                ],
            },
        }

    def predict_churn(self, customer_data: dict) -> dict:
        """Predict churn probability for a single customer."""
        df_input = pd.DataFrame([customer_data])

        # Encode
        for col in df_input.select_dtypes(include=["object"]).columns:
            if col in self.label_encoders:
                try:
                    df_input[col] = self.label_encoders[col].transform(df_input[col].astype(str))
                except ValueError:
                    df_input[col] = 0

        # Ensure all feature columns are present
        for col in self.feature_columns:
            if col not in df_input.columns:
                df_input[col] = 0

        X = df_input[self.feature_columns]

        proba = self.model.predict_proba(X)[0]
        prediction = self.model.predict(X)[0]

        return {
            "churn_probability": float(proba[1]),
            "risk_level": self._get_risk_level(float(proba[1])),
            "prediction": "Yes" if prediction == 1 else "No",
        }

    def _get_risk_level(self, prob):
        if prob >= 0.8:
            return "CRITICAL"
        elif prob >= 0.6:
            return "HIGH"
        elif prob >= 0.4:
            return "MODERATE"
        else:
            return "LOW"

    def identify_churn_reasons(self, customer_data: dict) -> list:
        """Identify why a customer is at risk."""
        reasons = []
        rules = self.recommendation_rules

        if customer_data.get("MonthlyCharges", 0) > rules["MonthlyCharges"]["threshold"]:
            reasons.append({
                "factor": "High Monthly Charges",
                "detail": f"₹{customer_data['MonthlyCharges']}/month (above ₹{rules['MonthlyCharges']['threshold']} threshold)",
                "impact": "HIGH",
            })

        if customer_data.get("Contract") == "Month-to-month":
            reasons.append({
                "factor": "No Long-term Contract",
                "detail": "Month-to-month commitment = easy to leave",
                "impact": "HIGH",
            })

        if customer_data.get("tenure", 0) < rules["tenure"]["low_threshold"]:
            reasons.append({
                "factor": "Low Tenure (New Customer)",
                "detail": f"Only {customer_data['tenure']} months with ConnectTel",
                "impact": "HIGH",
            })

        if customer_data.get("OnlineSecurity") == "No":
            reasons.append({
                "factor": "No Online Security",
                "detail": "Missing value-added security service",
                "impact": "MEDIUM",
            })

        if customer_data.get("TechSupport") == "No":
            reasons.append({
                "factor": "No Tech Support",
                "detail": "No dedicated technical assistance",
                "impact": "MEDIUM",
            })

        if customer_data.get("InternetService") == "Fiber optic":
            reasons.append({
                "factor": "Fiber Optic (Price-Sensitive)",
                "detail": "Fiber plans have highest churn rate",
                "impact": "MEDIUM",
            })

        if customer_data.get("PaymentMethod") == "Electronic check":
            reasons.append({
                "factor": "Electronic Check Payment",
                "detail": "Payment friction increases churn risk",
                "impact": "MEDIUM",
            })

        if customer_data.get("engagement_score", 0) < rules["engagement_score"]["low_threshold"]:
            reasons.append({
                "factor": "Low Engagement Score",
                "detail": f"Score: {customer_data.get('engagement_score', 0)}/100 (below {rules['engagement_score']['low_threshold']})",
                "impact": "LOW",
            })

        return reasons

    def generate_recommendations(self, customer_data: dict) -> list:
        """Generate personalized retention recommendations."""
        recommendations = []
        rules = self.recommendation_rules

        # High charges
        if customer_data.get("MonthlyCharges", 0) > rules["MonthlyCharges"]["threshold"]:
            for action in rules["MonthlyCharges"]["high"]:
                recommendations.append({
                    "action": action,
                    "category": "Pricing",
                    "priority": "HIGH" if customer_data["MonthlyCharges"] > 90 else "MEDIUM",
                })

        # Month-to-month contract
        if customer_data.get("Contract") == "Month-to-month":
            for action in rules["Contract"]["actions"]:
                recommendations.append({
                    "action": action,
                    "category": "Contract",
                    "priority": "HIGH",
                })

        # Low tenure
        if customer_data.get("tenure", 0) < rules["tenure"]["low_threshold"]:
            for action in rules["tenure"]["actions"]:
                recommendations.append({
                    "action": action,
                    "category": "Onboarding",
                    "priority": "HIGH",
                })

        # No security
        if customer_data.get("OnlineSecurity") == "No":
            for action in rules["OnlineSecurity"]["actions"]:
                recommendations.append({
                    "action": action,
                    "category": "Security",
                    "priority": "MEDIUM",
                })

        # No tech support
        if customer_data.get("TechSupport") == "No":
            for action in rules["TechSupport"]["actions"]:
                recommendations.append({
                    "action": action,
                    "category": "Support",
                    "priority": "MEDIUM",
                })

        # Fiber optic
        if customer_data.get("InternetService") == "Fiber optic":
            for action in rules["InternetService"]["actions"]:
                recommendations.append({
                    "action": action,
                    "category": "Internet",
                    "priority": "MEDIUM",
                })

        # Electronic check
        if customer_data.get("PaymentMethod") == "Electronic check":
            for action in rules["PaymentMethod"]["actions"]:
                recommendations.append({
                    "action": action,
                    "category": "Payment",
                    "priority": "MEDIUM",
                })

        # Low engagement
        if customer_data.get("engagement_score", 0) < rules["engagement_score"]["low_threshold"]:
            for action in rules["engagement_score"]["actions"]:
                recommendations.append({
                    "action": action,
                    "category": "Engagement",
                    "priority": "MEDIUM",
                })

        # Deduplicate and sort by priority
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec["action"] not in seen:
                seen.add(rec["action"])
                unique_recs.append(rec)

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        unique_recs.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return unique_recs

    def full_analysis(self, customer_data: dict) -> dict:
        """Complete analysis: risk + reasons + recommendations."""
        prediction = self.predict_churn(customer_data)
        reasons = self.identify_churn_reasons(customer_data)
        recommendations = self.generate_recommendations(customer_data)

        # Calculate estimated customer value
        monthly_revenue = customer_data.get("MonthlyCharges", 0)
        tenure = customer_data.get("tenure", 0)
        estimated_ltv = monthly_revenue * max(tenure, 1)
        revenue_at_risk = monthly_revenue * prediction["churn_probability"]

        return {
            "customer_id": customer_data.get("customerID", "Unknown"),
            "churn_probability": round(prediction["churn_probability"], 4),
            "risk_level": prediction["risk_level"],
            "reasons": reasons,
            "recommendations": recommendations[:5],  # Top 5
            "estimated_monthly_revenue": monthly_revenue,
            "estimated_annual_revenue_at_risk": round(revenue_at_risk * 12, 2),
        }

    def batch_analysis(self, df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
        """Analyze all customers and return top N at risk."""
        all_results = []

        for idx, row in df.iterrows():
            customer = row.to_dict()
            result = self.full_analysis(customer)
            all_results.append(result)

        results_df = pd.DataFrame(all_results)
        results_df = results_df.sort_values("churn_probability", ascending=False)
        return results_df.head(top_n)


def run_retention_engine():
    print("=== Phase 9: Retention Intelligence Engine ===")

    engine = RetentionIntelligenceEngine()

    # Load sample customers
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "connecttel_churn_engineered.csv"))

    # Demo: Analyze 5 sample customers
    print("\n--- Sample Customer Analyses ---\n")
    sample_customers = df.sample(5, random_state=42)

    for idx, (_, row) in enumerate(sample_customers.iterrows(), 1):
        analysis = engine.full_analysis(row.to_dict())
        print(f"[{idx}] Customer: {analysis['customer_id']}")
        print(f"    Churn Probability: {analysis['churn_probability']:.2%} ({analysis['risk_level']})")
        print(f"    Revenue at Risk: ₹{analysis['estimated_annual_revenue_at_risk']:,.2f}/year")
        print(f"    Key Reasons:")
        for reason in analysis["reasons"][:3]:
            print(f"      - {reason['factor']}: {reason['detail']} (Impact: {reason['impact']})")
        print(f"    Top Recommendations:")
        for rec in analysis["recommendations"][:3]:
            print(f"      [{rec['priority']}] {rec['action']}")
        print()

    # Batch analysis for top at-risk customers
    print("--- Batch Analysis: Top 20 At-Risk Customers ---")
    top_risk = engine.batch_analysis(df, top_n=20)
    print(top_risk[["customer_id", "churn_probability", "risk_level", "estimated_annual_revenue_at_risk"]].to_string(index=False))

    # Save results
    output_path = os.path.join(OUTPUT_DIR, "retention_recommendations.csv")
    top_risk.to_csv(output_path, index=False)
    print(f"\nTop 20 at-risk customer report saved to: {output_path}")

    return top_risk


if __name__ == "__main__":
    run_retention_engine()
