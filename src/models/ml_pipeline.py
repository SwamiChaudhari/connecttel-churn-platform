"""
Phase 6: Machine Learning Pipeline
Trains, tunes, and compares 5 models: LogReg, RF, XGBoost, LightGBM, CatBoost.
"""
import pandas as pd
import numpy as np
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import joblib
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "connecttel_churn_engineered.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "notebooks")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

RANDOM_STATE = 42


def prepare_data(df):
    """Prepare data for ML: encode categoricals, split, scale."""
    df = df.copy()
    df.drop(columns=["customerID"], inplace=True, errors="ignore")

    # Target
    y = (df["Churn"] == "Yes").astype(int)

    # Drop raw target and non-numeric object columns
    X = df.drop(columns=["Churn"])

    # Encode categoricals (object + category types)
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    label_encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

    return X, y, label_encoders


def get_models():
    """Return dict of models with reasonable starting hyperparameters."""
    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                C=1.0, penalty="l2", solver="lbfgs",
                max_iter=1000, random_state=RANDOM_STATE
            ))
        ]),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, min_samples_split=5,
            min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
            use_label_encoder=False, random_state=RANDOM_STATE,
            n_jobs=1
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            num_leaves=31, subsample=0.8, colsample_bytree=0.8,
            verbose=-1, random_state=RANDOM_STATE, n_jobs=1
        ),
        "CatBoost": CatBoostClassifier(
            iterations=200, depth=6, learning_rate=0.1,
            verbose=0, random_state=RANDOM_STATE
        ),
    }
    return models


def train_and_evaluate(X_train, X_test, y_train, y_test):
    models = get_models()
    results = {}
    trained_models = {}

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    print(f"\nTraining set: {X_train.shape[0]} rows")
    print(f"Test set: {X_test.shape[0]} rows")
    print(f"Churn rate (train): {y_train.mean():.2%}")
    print(f"Churn rate (test): {y_test.mean():.2%}\n")

    for name, model in models.items():
        print(f"--- {name} ---")
        start = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - start

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        # Cross-validation AUC
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=1)

        # Metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "cv_auc_mean": round(cv_scores.mean(), 4),
            "cv_auc_std": round(cv_scores.std(), 4),
            "train_time_sec": round(elapsed, 2),
        }
        trained_models[name] = model

        print(f"  AUC={auc:.4f} | Acc={acc:.4f} | Prec={prec:.4f} | Rec={rec:.4f} | F1={f1:.4f}")
        print(f"  CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        print(f"  Train time: {elapsed:.2f}s\n")

    return results, trained_models


def save_results(results, trained_models):
    # Save comparison JSON
    results_path = os.path.join(RESULTS_DIR, "model_comparison.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {results_path}")

    # Save model comparison CSV
    df_results = pd.DataFrame(results).T
    df_results.index.name = "model"
    csv_path = os.path.join(RESULTS_DIR, "model_comparison.csv")
    df_results.to_csv(csv_path)
    print(f"Results CSV saved to: {csv_path}")

    # Save the best model
    best_model_name = max(results, key=lambda k: results[k]["roc_auc"])
    best_model = trained_models[best_model_name]
    model_path = os.path.join(MODEL_DIR, "best_model.joblib")
    joblib.dump(best_model, model_path)
    print(f"\nBest model: {best_model_name} (AUC={results[best_model_name]['roc_auc']:.4f})")
    print(f"Saved to: {model_path}")

    # Save all models
    for name, model in trained_models.items():
        safe_name = name.lower().replace(" ", "_")
        joblib.dump(model, os.path.join(MODEL_DIR, f"{safe_name}.joblib"))
    print(f"All models saved to: {MODEL_DIR}/")

    return best_model_name, df_results


def run_ml_pipeline():
    print("=" * 60)
    print("PHASE 6: MACHINE LEARNING PIPELINE")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)
    X, y, label_encoders = prepare_data(df)

    # Save label encoders
    joblib.dump(label_encoders, os.path.join(MODEL_DIR, "label_encoders.joblib"))

    # Save feature columns
    with open(os.path.join(MODEL_DIR, "feature_columns.json"), "w") as f:
        json.dump(list(X.columns), f)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    results, trained_models = train_and_evaluate(X_train, X_test, y_train, y_test)
    best_name, df_results = save_results(results, trained_models)

    print("\n=== MODEL COMPARISON SUMMARY ===")
    print(df_results.to_string())
    return results, trained_models, X_train, X_test, y_train, y_test


if __name__ == "__main__":
    run_ml_pipeline()
