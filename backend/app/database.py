from __future__ import annotations

import re
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .data import CommerceData

BLOCKED_SQL = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|replace|attach|detach|pragma|grant|revoke)\b",
    re.IGNORECASE,
)


def make_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)


def initialize_database(engine: Engine, data: CommerceData) -> None:
    data.sales.to_sql("sales_fact", engine, if_exists="replace", index=False)
    data.customers.to_sql("customers", engine, if_exists="replace", index=False)
    data.marketing.to_sql("marketing", engine, if_exists="replace", index=False)
    data.coupons.to_sql("coupons", engine, if_exists="replace", index=False)
    data.tax.to_sql("tax", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS query_history (
                    created_at TEXT NOT NULL,
                    question TEXT NOT NULL,
                    generated_sql TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    row_count INTEGER NOT NULL
                )
                """
            )
        )


def validate_read_only_sql(sql: str) -> str:
    cleaned = sql.strip().strip("`").strip()
    if cleaned.lower().startswith("sql"):
        cleaned = cleaned[3:].strip()
    if not re.match(r"^(select|with)\b", cleaned, re.IGNORECASE):
        raise ValueError("Only SELECT or WITH queries are allowed.")
    if BLOCKED_SQL.search(cleaned):
        raise ValueError("The generated SQL contains a blocked operation.")
    if ";" in cleaned.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")
    return cleaned.rstrip(";")


def run_read_only_query(engine: Engine, sql: str, limit: int = 500) -> pd.DataFrame:
    safe_sql = validate_read_only_sql(sql)
    wrapped = f"SELECT * FROM ({safe_sql}) AS safe_query LIMIT {int(limit)}"
    with engine.connect() as conn:
        return pd.read_sql_query(text(wrapped), conn)


def save_query_history(
    engine: Engine,
    question: str,
    sql: str,
    mode: str,
    row_count: int,
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO query_history(created_at, question, generated_sql, mode, row_count)
                VALUES (:created_at, :question, :generated_sql, :mode, :row_count)
                """
            ),
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "question": question,
                "generated_sql": sql,
                "mode": mode,
                "row_count": int(row_count),
            },
        )


def get_query_history(engine: Engine, limit: int = 20) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT created_at, question, generated_sql, mode, row_count
                FROM query_history
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": int(limit)},
        ).mappings().all()
    return [dict(row) for row in rows]
