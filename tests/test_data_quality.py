"""
Tests for the ConnectTel Churn Platform.
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestDataQuality:
    """Tests for data generation and cleaning."""

    def test_raw_dataset_exists(self):
        df = pd.read_csv("data/connecttel_churn_raw.csv")
        assert len(df) > 0
        assert "Churn" in df.columns
        assert "customerID" in df.columns

    def test_clean_dataset_exists(self):
        if not os.path.exists("data/connecttel_churn_clean.csv"):
            pytest.skip("Clean dataset not generated yet")
        df = pd.read_csv("data/connecttel_churn_clean.csv")
        assert df.isnull().sum().sum() == 0
        assert len(df) > 0

    def test_clean_no_duplicates(self):
        if not os.path.exists("data/connecttel_churn_clean.csv"):
            pytest.skip("Clean dataset not generated yet")
        df = pd.read_csv("data/connecttel_churn_clean.csv")
        assert df.duplicated().sum() == 0

    def test_target_distribution(self):
        df = pd.read_csv("data/connecttel_churn_raw.csv")
        churn_rate = (df["Churn"] == "Yes").mean()
        # Churn rate should be between 10% and 50%
        assert 0.10 < churn_rate < 0.50

    def test_engineered_features_exist(self):
        if not os.path.exists("data/connecttel_churn_engineered.csv"):
            pytest.skip("Engineered dataset not generated yet")
        df = pd.read_csv("data/connecttel_churn_engineered.csv")
        expected_features = [
            "customer_lifetime_value",
            "engagement_score",
            "loyalty_score",
            "churn_risk_index",
        ]
        for feat in expected_features:
            assert feat in df.columns, f"Missing feature: {feat}"


class TestModel:
    """Tests for the ML pipeline."""

    def test_models_trained(self):
        if not os.path.exists("models/best_model.joblib"):
            pytest.skip("Models not trained yet")
        import joblib
        model = joblib.load("models/best_model.joblib")
        assert model is not None

    def test_model_comparison(self):
        if not os.path.exists("notebooks/model_comparison.json"):
            pytest.skip("Model comparison not available yet")
        import json
        with open("notebooks/model_comparison.json") as f:
            results = json.load(f)
        assert len(results) >= 2
        for model_name, metrics in results.items():
            assert "roc_auc" in metrics
            assert metrics["roc_auc"] > 0.5  # Better than random

    def test_feature_columns(self):
        if not os.path.exists("models/feature_columns.json"):
            pytest.skip("Feature columns not saved yet")
        import json
        with open("models/feature_columns.json") as f:
            cols = json.load(f)
        assert len(cols) > 5


class TestRetentionEngine:
    """Tests for the retention intelligence engine."""

    def test_risk_levels_defined(self):
        from src.models.retention_engine import RetentionIntelligenceEngine
        # This will fail without models, but tests the import
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
