from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import analytics
from .ai_service import explain_result, generate_sql
from .data import CommerceData, DatasetMissingError, load_commerce_data
from .database import (
    get_query_history,
    initialize_database,
    make_engine,
    run_read_only_query,
    save_query_history,
)
from .schemas import AIQueryRequest
from .segmentation import segment_customers
from .settings import (
    DATA_FILE,
    DATABASE_URL,
    FRONTEND_ORIGIN,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

state: dict[str, object] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        data = load_commerce_data(DATA_FILE)
        engine = make_engine(DATABASE_URL)
        initialize_database(engine, data)
        state["data"] = data
        state["engine"] = engine
        state["startup_error"] = None
    except Exception as exc:  # surfaced cleanly through /api/status
        state["startup_error"] = str(exc)
    yield


app = FastAPI(
    title="AI E-Commerce Intelligence API",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _data() -> CommerceData:
    error = state.get("startup_error")
    if error:
        raise HTTPException(status_code=503, detail=error)
    return state["data"]  # type: ignore[return-value]


def _engine():
    error = state.get("startup_error")
    if error:
        raise HTTPException(status_code=503, detail=error)
    return state["engine"]


@app.get("/api/status")
def status():
    error = state.get("startup_error")
    return {
        "ok": error is None,
        "dataset": DATA_FILE.name,
        "ai_mode": "llm" if OPENAI_API_KEY else "demo",
        "error": error,
    }


@app.get("/api/overview")
def get_overview():
    data = _data()
    return {
        "kpis": analytics.overview(data.sales, data.marketing),
        "monthly": analytics.monthly_sales(data.sales),
        "categories": analytics.category_performance(data.sales)[:10],
        "locations": analytics.location_performance(data.sales),
    }


@app.get("/api/sales")
def get_sales():
    data = _data()
    return {
        "categories": analytics.category_performance(data.sales),
        "products": analytics.top_products(data.sales, 15),
        "coupons": analytics.coupon_performance(data.sales),
        "monthly": analytics.monthly_sales(data.sales),
    }


@app.get("/api/customers")
def get_customers():
    data = _data()
    return {
        "top_customers": analytics.top_customers(data.sales, 20),
        "locations": analytics.location_performance(data.sales),
    }


@app.get("/api/segmentation")
def get_segmentation():
    return segment_customers(_data().sales)


@app.get("/api/data-preview")
def data_preview(limit: int = 50):
    data = _data()
    preview = data.sales.head(max(1, min(limit, 200))).copy()
    for col in preview.columns:
        if str(preview[col].dtype).startswith("datetime"):
            preview[col] = preview[col].astype(str)
    return {
        "columns": preview.columns.tolist(),
        "rows": preview.where(preview.notna(), None).to_dict(orient="records"),
        "total_rows": int(len(data.sales)),
    }


@app.post("/api/ai/query")
def ai_query(request: AIQueryRequest):
    engine = _engine()
    try:
        sql, mode = generate_sql(request.question, OPENAI_API_KEY, OPENAI_MODEL)
        result = run_read_only_query(engine, sql)
        records = result.where(result.notna(), None).to_dict(orient="records")
        explanation = explain_result(
            request.question,
            sql,
            records[:20],
            OPENAI_API_KEY,
            OPENAI_MODEL,
        )
        save_query_history(engine, request.question, sql, mode, len(result))
        return {
            "question": request.question,
            "mode": mode,
            "sql": sql,
            "columns": result.columns.tolist(),
            "rows": records,
            "row_count": int(len(result)),
            "explanation": explanation,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/ai/history")
def ai_history():
    return get_query_history(_engine(), 20)
