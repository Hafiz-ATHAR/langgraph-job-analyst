import os

# Belt-and-suspenders defaults for app.config.Settings. CI sets these via the
# workflow env block; local dev usually has them in .env. This fallback keeps
# `pytest` runnable on a fresh checkout where neither is present.
os.environ.setdefault("TAVILY_API_KEY", "dummy")
os.environ.setdefault("MLFLOW_TRACKING_URI", "file:///tmp/mlflow-test")
os.environ.setdefault("MLFLOW_EXPERIMENT", "test")
