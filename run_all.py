#!/usr/bin/env python3
"""
Master Pipeline Runner — ConnectTel Churn Platform
Executes all phases in sequence from the project root.
"""
import sys
import os
import subprocess
import time

# Ensure project root is in path and is cwd
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

print("=" * 70)
print("  CONNECTTEL CHURN PREDICTION & RETENTION INTELLIGENCE PLATFORM")
print("  Master Pipeline Runner")
print("=" * 70)
print(f"  Working directory: {PROJECT_ROOT}")
print(f"  Python: {sys.executable}")
print("=" * 70)

start_time = time.time()

phases = [
    ("Phase 1: Data Generation",      ["python3", "-m", "src.data.generate_dataset"]),
    ("Phase 2: Data Cleaning",         ["python3", "-m", "src.data.data_cleaning"]),
    ("Phase 3: Feature Engineering",   ["python3", "-m", "src.features.feature_engineering"]),
    ("Phase 4: Exploratory Data Analysis", ["python3", "-m", "src.visualization.eda"]),
    ("Phase 5: ML Pipeline",           ["python3", "-m", "src.models.ml_pipeline"]),
    ("Phase 6: Model Evaluation",      ["python3", "-m", "src.models.model_evaluation"]),
    ("Phase 7: SHAP Analysis",         ["python3", "-m", "src.models.shap_analysis"]),
    ("Phase 8: Retention Engine",      ["python3", "-m", "src.models.retention_engine"]),
]

results = {}

for phase_name, cmd in phases:
    print(f"\n{'─' * 60}")
    print(f"  {phase_name}")
    print(f"{'─' * 60}")
    phase_start = time.time()

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        elapsed = time.time() - phase_start

        if result.returncode == 0:
            results[phase_name] = ("✅ SUCCESS", f"{elapsed:.1f}s")
            print(f"  ✅ Completed in {elapsed:.1f}s")
            if result.stdout:
                # Print last few lines of output
                lines = result.stdout.strip().split("\n")
                for line in lines[-8:]:
                    print(f"    {line}")
        else:
            results[phase_name] = ("❌ FAILED", f"exit code {result.returncode}")
            print(f"  ❌ Failed (code {result.returncode})")
            if result.stderr:
                for line in result.stderr.strip().split("\n")[-5:]:
                    print(f"    ERR: {line}")
    except subprocess.TimeoutExpired:
        results[phase_name] = ("⏰ TIMEOUT", ">600s")
        print(f"  ⏰ Timeout after 600s")
    except Exception as e:
        elapsed = time.time() - phase_start
        results[phase_name] = ("❌ ERROR", str(e)[:80])
        print(f"  ❌ Error: {e}")

total_time = time.time() - start_time

print(f"\n{'=' * 70}")
print(f"  PIPELINE SUMMARY")
print(f"{'=' * 70}")
for phase, (status, detail) in results.items():
    print(f"  {status} {phase}: {detail}")
print(f"\n  Total time: {total_time:.1f}s")
print(f"{'=' * 70}")
print(f"\n  Launch dashboard:")
print(f"  cd {PROJECT_ROOT} && source .venv/bin/activate && streamlit run streamlit_app/app.py")
print(f"{'=' * 70}")
