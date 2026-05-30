# Shared path configuration for ConnectTel Churn Platform
# Each module computes PROJECT_ROOT from its own __file__
# Used by scripts that run as: python -m src.data.data_cleaning
import os

# This file lives at src/paths.py → project root = dirname(dirname(abspath))
_src_paths_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_root(caller_file: str) -> str:
    """Get project root for any caller file."""
    # Project root is always the top-level dir with requirements.txt
    f = os.path.abspath(caller_file)
    while f and f != "/":
        if os.path.exists(os.path.join(f, "requirements.txt")):
            return f
        f = os.path.dirname(f)
    # Fallback: go up from known structure
    return _src_paths_root


def data(filename: str) -> str:
    return os.path.join(_src_paths_dir.replace("data", ""), "data", filename)


# Note: Each module should use PROJECT_ROOT directly instead of importing this.
