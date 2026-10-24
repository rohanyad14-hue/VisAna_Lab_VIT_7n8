"""
Flask API exposing ECharts-ready sales data from an SQL database (MySQL or SQLite).
Designed for Containerized (Docker) and Kubernetes (Services & Deployments) Workloads.

Author: Rohan Yadav (26MML0020)
Course: Visual Analytics Lab (VL2026270106069)
"""

import os
import time
from functools import lru_cache
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text

# ----------------------------------------------------------------- Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database URL from environment:
# Kubernetes default: mysql+pymysql://root:password@mysql-service:3306/salesdb
# Local fallback: sqlite:///sales.db
DEFAULT_SQLITE = f"sqlite:///{os.path.join(BASE_DIR, 'sales.db')}"
DB_URL = os.environ.get("DB_URL", DEFAULT_SQLITE)
SQL_QUERY = os.environ.get("SQL_QUERY", "SELECT date, region, category, sales, units FROM sales")
CACHE_SECONDS = int(os.environ.get("CACHE_SECONDS", 30))

REQUIRED_COLS = {"date", "region", "category", "sales"}

app = Flask(__name__)
CORS(app)


def get_engine():
    """Create engine with connection pooling and retry support."""
    return create_engine(
        DB_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )


engine = get_engine()


# ---------------------------------------------------------- Data Loading
def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Data source is missing columns: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"])
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0)
    return df


def _load_sql() -> pd.DataFrame:
    global engine
    # Try reading from current engine; if connection fails, retry with fallback
    try:
        with engine.connect() as conn:
            return _clean(pd.read_sql(text(SQL_QUERY), conn))
    except Exception as err:
        # If connecting to MySQL service fails during cold start, try fallback SQLite if available
        if os.path.exists(os.path.join(BASE_DIR, "sales.db")) and not DB_URL.startswith("sqlite"):
            print(f"[WARN] Primary DB failed ({err}). Retrying fallback SQLite.")
            fallback_engine = create_engine(DEFAULT_SQLITE)
            with fallback_engine.connect() as conn:
                return _clean(pd.read_sql(text(SQL_QUERY), conn))
        raise err


@lru_cache(maxsize=4)
def _cached(bucket: int) -> pd.DataFrame:
    """Load once per CACHE_SECONDS window. `bucket` busts the cache."""
    return _load_sql()


def get_df() -> pd.DataFrame:
    bucket = int(pd.Timestamp.now().timestamp() // CACHE_SECONDS)
    df = _cached(bucket).copy()

    for col in ("region", "category"):
        vals = request.args.get(col)
        if vals:
            df = df[df[col].isin([v.strip() for v in vals.split(",")])]
    if request.args.get("start"):
        df = df[df["date"] >= pd.to_datetime(request.args["start"])]
    if request.args.get("end"):
        df = df[df["date"] <= pd.to_datetime(request.args["end"])]
    return df


@app.errorhandler(ValueError)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(FileNotFoundError)
def missing_file(e):
    return jsonify(error=f"File not found: {e.filename}"), 500


# ------------------------------------------------------------- Endpoints
@app.get("/")
def index():
    return jsonify({
        "service": "VeloceAnalytics REST API",
        "author": "Rohan Yadav (26MML0020)",
        "course": "Visual Analytics Lab (VL2026270106069)",
        "status": "healthy",
        "database": DB_URL.split("@")[-1] if "@" in DB_URL else "local_sqlite",
        "documentation": "/api/health"
    })


@app.get("/api/health")
def health():
    try:
        df = _load_sql()
        return jsonify({
            "status": "UP",
            "sql": {
                "ok": True,
                "rows": len(df),
                "source": DB_URL.split("@")[-1] if "@" in DB_URL else "sqlite",
                "timestamp": pd.Timestamp.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "status": "DOWN",
            "sql": {
                "ok": False,
                "error": str(e)
            }
        }), 503


@app.get("/api/filters")
def filters():
    """Distinct values for dropdown filters."""
    df = get_df()
    return jsonify(
        regions=sorted(df["region"].unique().tolist()),
        categories=sorted(df["category"].unique().tolist()),
        min_date=df["date"].min().date().isoformat() if len(df) else "2025-01-01",
        max_date=df["date"].max().date().isoformat() if len(df) else "2025-12-31",
    )


@app.get("/api/sales/summary")
def summary():
    """KPI cards metrics."""
    df = get_df()
    monthly = df.groupby(df["date"].dt.to_period("M"))["sales"].sum()
    best = monthly.idxmax() if len(monthly) else None
    return jsonify(
        total_sales=round(float(df["sales"].sum()), 2),
        avg_daily_sales=round(float(df.groupby("date")["sales"].sum().mean() or 0), 2),
        orders=int(len(df)),
        top_region=df.groupby("region")["sales"].sum().idxmax() if len(df) else None,
        top_category=df.groupby("category")["sales"].sum().idxmax() if len(df) else None,
        best_month=str(best) if best is not None else None,
    )


@app.get("/api/sales/monthly")
def monthly_trend():
    """Monthly sales line chart, one series per region."""
    df = get_df()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    pv = df.pivot_table(index="month", columns="region", values="sales",
                        aggfunc="sum", fill_value=0).round(2)
    return jsonify(
        months=pv.index.tolist(),
        series=[{"name": r, "type": "line", "smooth": True, "data": pv[r].tolist()}
                for r in pv.columns],
    )


@app.get("/api/sales/by-category")
def by_category():
    """Stacked bar chart: category on x-axis, stacked by region."""
    df = get_df()
    pv = df.pivot_table(index="category", columns="region", values="sales",
                        aggfunc="sum", fill_value=0).round(2)
    return jsonify(
        categories=pv.index.tolist(),
        series=[{"name": r, "type": "bar", "stack": "total", "data": pv[r].tolist()}
                for r in pv.columns],
    )


@app.get("/api/sales/share")
def share():
    """Pie chart: share of sales by category or region."""
    by = request.args.get("by", "category")
    if by not in ("category", "region"):
        raise ValueError("by must be 'category' or 'region'")
    s = get_df().groupby(by)["sales"].sum().round(2)
    return jsonify(by=by, data=[{"name": k, "value": float(v)} for k, v in s.items()])


@app.get("/api/sales/combo")
def combo():
    """Bar + line combo: monthly total and cumulative total."""
    df = get_df()
    total = df.groupby(df["date"].dt.to_period("M").astype(str))["sales"].sum().round(2)
    return jsonify(
        months=total.index.tolist(),
        monthly=total.tolist(),
        cumulative=total.cumsum().round(2).tolist(),
    )


@app.get("/api/sales/daily")
def daily():
    """Time-series data with daily granularity."""
    s = get_df().groupby("date")["sales"].sum().round(2)
    return jsonify(data=[[d.date().isoformat(), float(v)] for d, v in s.items()])


@app.get("/api/sales/heatmap")
def heatmap():
    """Heatmap: region x month."""
    df = get_df()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    pv = df.pivot_table(index="region", columns="month", values="sales",
                        aggfunc="sum", fill_value=0).round(2)
    data = [[j, i, float(pv.iloc[i, j])]
            for i in range(len(pv.index)) for j in range(len(pv.columns))]
    return jsonify(months=pv.columns.tolist(), regions=pv.index.tolist(), data=data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
