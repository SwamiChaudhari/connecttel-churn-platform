"""
Phase 12: MLOps & Production Readiness
Logging, monitoring, error handling, versioning.
"""
import os
import logging
import logging.handlers
import json
import time
import yaml
from datetime import datetime
from pathlib import Path

# ============================================================
# LOGGING SETUP
# ============================================================
def setup_logging(config_path: str = "config/logging_config.yaml") -> logging.Logger:
    """Setup production-grade logging with rotation."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("connecttel_churn")
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_fmt)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "connecttel_churn.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_fmt)

    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


# ============================================================
# MODEL VERSIONING
# ============================================================
class ModelVersionManager:
    """Manages model versions and metadata."""

    def __init__(self, registry_dir: str = "models"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(exist_ok=True)
        self.registry_file = self.registry_dir / "model_registry.json"

    def register_model(self, model_name: str, metrics: dict, model_path: str) -> str:
        """Register a new model version."""
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        entry = {
            "version": version,
            "model_name": model_name,
            "metrics": metrics,
            "model_path": model_path,
            "registered_at": datetime.now().isoformat(),
            "status": "active",
        }

        registry = self._load_registry()
        registry.setdefault(model_name, []).append(entry)
        self._save_registry(registry)

        return version

    def get_latest_version(self, model_name: str) -> dict:
        """Get latest version of a model."""
        registry = self._load_registry()
        versions = registry.get(model_name, [])
        if not versions:
            return None
        return versions[-1]

    def get_best_model(self, model_name: str, metric: str = "roc_auc") -> dict:
        """Get the best model version by a metric."""
        registry = self._load_registry()
        versions = registry.get(model_name, [])
        if not versions:
            return None
        return max(versions, key=lambda x: x["metrics"].get(metric, 0))

    def _load_registry(self) -> dict:
        if self.registry_file.exists():
            return json.loads(self.registry_file.read_text())
        return {}

    def _save_registry(self, data: dict):
        self.registry_file.write_text(json.dumps(data, indent=2, default=str))


# ============================================================
# MODEL MONITORING
# ============================================================
class ModelMonitor:
    """Monitors model performance and data drift."""

    def __init__(self, log_dir: str = "logs/monitoring"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_prediction(self, customer_id: str, prediction: float, risk_level: str):
        """Log individual prediction for audit."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "customer_id": customer_id,
            "prediction": prediction,
            "risk_level": risk_level,
        }
        log_file = self.log_dir / f"predictions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def check_drift(self, baseline_stats: dict, current_stats: dict, threshold: float = 0.05) -> dict:
        """Simple drift detection using mean shift."""
        drift_report = {
            "timestamp": datetime.now().isoformat(),
            "drifted": False,
            "features": {},
        }

        for feature in baseline_stats:
            if feature in current_stats:
                baseline_mean = baseline_stats[feature]["mean"]
                current_mean = current_stats[feature]["mean"]
                shift = abs(current_mean - baseline_mean) / (baseline_mean + 1e-6)

                is_drifted = shift > threshold
                drift_report["features"][feature] = {
                    "baseline_mean": baseline_mean,
                    "current_mean": current_mean,
                    "shift": round(shift, 4),
                    "drifted": is_drifted,
                }
                if is_drifted:
                    drift_report["drifted"] = True

        log_file = self.log_dir / "drift_log.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(drift_report, default=str) + "\n")

        return drift_report


# ============================================================
# CONFIGURATION MANAGER
# ============================================================
class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            value = value.get(k, default) if isinstance(value, dict) else default
        return value

    def get_data_path(self) -> str:
        return self.get("dataset.raw")

    def get_model_dir(self) -> str:
        return self.get("mlops.model_registry_dir", "models/")


# ============================================================
# ERROR HANDLING UTILITIES
# ============================================================
class ChurnPlatformError(Exception):
    """Base exception for the platform."""
    pass


class DataQualityError(ChurnPlatformError):
    """Raised when data quality checks fail."""
    pass


class ModelNotFoundError(ChurnPlatformError):
    """Raised when model files are missing."""
    pass


class PredictionError(ChurnPlatformError):
    """Raised when prediction fails."""
    pass


def validate_input(data: dict, required_fields: list) -> bool:
    """Validate customer input data."""
    missing = [f for f in required_fields if f not in data or data[f] is None]
    if missing:
        raise DataQualityError(f"Missing required fields: {missing}")
    if not (0 <= data.get("MonthlyCharges", 0) <= 500):
        raise DataQualityError(f"MonthlyCharges out of range: {data.get('MonthlyCharges')}")
    if not (0 <= data.get("tenure", 0) <= 200):
        raise DataQualityError(f"tenure out of range: {data.get('tenure')}")
    return True


# ============================================================
# RETRAINING PIPELINE (Placeholder)
# ============================================================
class RetrainingPipeline:
    """Automated retraining pipeline skeleton."""

    def __init__(self, config: ConfigManager, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def check_retrain_needed(self) -> bool:
        """Check if retraining is needed based on monitoring."""
        monitor = ModelMonitor()
        drift_log = Path("logs/monitoring/drift_log.jsonl")
        if drift_log.exists():
            lines = drift_log.readlines()
            if lines:
                latest = json.loads(lines[-1])
                if latest.get("drifted"):
                    self.logger.warning("Data drift detected! Retraining recommended.")
                    return True
        return False

    def retrain(self):
        """Execute retraining pipeline."""
        self.logger.info("Starting automated retraining...")
        # In production: fetch new data, retrain, evaluate, deploy
        self.logger.info("Retraining pipeline completed.")
