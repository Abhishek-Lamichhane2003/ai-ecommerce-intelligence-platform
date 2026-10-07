# AI E-Commerce Intelligence Platform

A full-stack Data Science + Software Engineering portfolio project built on the Kaggle Online Shopping dataset.

## What it demonstrates

- Data cleaning and feature engineering with Pandas
- Revenue, product, location, coupon, and customer analytics
- RFM-style customer features
- K-Means customer segmentation
- Silhouette-score evaluation
- Natural-language analytics and text-to-SQL
- React frontend
- FastAPI REST backend
- SQLAlchemy database layer
- SQLite for easy local development
- PostgreSQL through Docker Compose
- REST API design
- CORS configuration
- SQL validation and read-only query execution
- Query history persistence
- Unit tests with pytest
- Dockerized frontend/backend/database
- GitHub Actions continuous integration

## Pages

- Executive Overview
- Sales Intelligence
- Customer Intelligence
- Customer Segmentation
- AI Data Analyst
- Data Explorer

## Local setup

See `START_HERE.md`.

## AI Analyst

The backend supports two modes:

1. **Demo SQL mode** — works without an API key and maps common business questions to safe SQL.
2. **LLM mode** — when `OPENAI_API_KEY` is supplied, the backend generates read-only SQL from natural-language questions and produces a short business explanation.

Generated SQL is validated before execution. Write operations such as INSERT, UPDATE, DELETE, DROP, ALTER, and CREATE are blocked.

## Dataset

Place the Kaggle CSV at:

```text
data/ecommerce_sales.csv
```

The dataset is not committed to the repository.
