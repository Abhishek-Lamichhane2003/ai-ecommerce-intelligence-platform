from __future__ import annotations

import numpy as np
import pandas as pd


def overview(sales: pd.DataFrame, marketing: pd.DataFrame) -> dict:
    revenue = float(sales["Net_Revenue"].sum()) if not sales.empty else 0.0
    orders = int(sales["Transaction_ID"].nunique()) if not sales.empty else 0
    customers = int(sales["CustomerID"].nunique()) if not sales.empty else 0
    units = float(sales["Quantity"].sum()) if not sales.empty else 0.0
    aov = revenue / orders if orders else 0.0
    discounts = float(sales["Discount_Amount"].sum()) if not sales.empty else 0.0
    marketing_spend = 0.0
    if not marketing.empty:
        marketing_spend = float(
            marketing["Online_Spend"].fillna(0).sum()
            + marketing["Offline_Spend"].fillna(0).sum()
        )
    roas = revenue / marketing_spend if marketing_spend else None
    return {
        "revenue": revenue,
        "orders": orders,
        "customers": customers,
        "units": units,
        "aov": aov,
        "discounts": discounts,
        "marketing_spend": marketing_spend,
        "roas": roas,
        "transaction_lines": int(len(sales)),
        "start_date": sales["Transaction_Date"].min().date().isoformat() if not sales.empty else None,
        "end_date": sales["Transaction_Date"].max().date().isoformat() if not sales.empty else None,
    }


def monthly_sales(sales: pd.DataFrame) -> list[dict]:
    if sales.empty:
        return []
    out = (
        sales.groupby("Year_Month", as_index=False)
        .agg(
            revenue=("Net_Revenue", "sum"),
            orders=("Transaction_ID", "nunique"),
            units=("Quantity", "sum"),
        )
        .sort_values("Year_Month")
    )
    return out.to_dict(orient="records")


def category_performance(sales: pd.DataFrame) -> list[dict]:
    if sales.empty:
        return []
    out = (
        sales.groupby("Product_Category", as_index=False)
        .agg(
            revenue=("Net_Revenue", "sum"),
            orders=("Transaction_ID", "nunique"),
            units=("Quantity", "sum"),
            customers=("CustomerID", "nunique"),
            avg_price=("Avg_Price", "mean"),
        )
        .sort_values("revenue", ascending=False)
        .rename(columns={"Product_Category": "category"})
    )
    return out.to_dict(orient="records")


def location_performance(sales: pd.DataFrame) -> list[dict]:
    if sales.empty or "Location" not in sales.columns:
        return []
    out = (
        sales.groupby("Location", as_index=False)
        .agg(
            revenue=("Net_Revenue", "sum"),
            orders=("Transaction_ID", "nunique"),
            customers=("CustomerID", "nunique"),
            units=("Quantity", "sum"),
        )
        .sort_values("revenue", ascending=False)
        .rename(columns={"Location": "location"})
    )
    return out.to_dict(orient="records")


def top_products(sales: pd.DataFrame, n: int = 15) -> list[dict]:
    key = "Product_Description" if "Product_Description" in sales.columns else "Product_SKU"
    if sales.empty or key not in sales.columns:
        return []
    out = (
        sales.groupby(key, as_index=False)
        .agg(
            revenue=("Net_Revenue", "sum"),
            units=("Quantity", "sum"),
            orders=("Transaction_ID", "nunique"),
        )
        .sort_values("revenue", ascending=False)
        .head(n)
        .rename(columns={key: "product"})
    )
    return out.to_dict(orient="records")


def customer_summary(sales: pd.DataFrame) -> pd.DataFrame:
    if sales.empty:
        return pd.DataFrame()
    snapshot = sales["Transaction_Date"].max() + pd.Timedelta(days=1)
    agg = {
        "last_purchase": ("Transaction_Date", "max"),
        "first_purchase": ("Transaction_Date", "min"),
        "frequency": ("Transaction_ID", "nunique"),
        "monetary": ("Net_Revenue", "sum"),
        "units": ("Quantity", "sum"),
    }
    if "Location" in sales.columns:
        agg["location"] = ("Location", "first")
    if "Gender" in sales.columns:
        agg["gender"] = ("Gender", "first")
    if "Tenure_Months" in sales.columns:
        agg["tenure_months"] = ("Tenure_Months", "first")
    out = sales.groupby("CustomerID", as_index=False).agg(**agg)
    out["recency_days"] = (snapshot - out["last_purchase"]).dt.days
    out["avg_order_value"] = np.where(
        out["frequency"] > 0, out["monetary"] / out["frequency"], 0.0
    )
    return out.sort_values("monetary", ascending=False)


def top_customers(sales: pd.DataFrame, n: int = 20) -> list[dict]:
    out = customer_summary(sales).head(n).copy()
    if out.empty:
        return []
    for col in ["last_purchase", "first_purchase"]:
        out[col] = out[col].astype(str)
    return out.to_dict(orient="records")


def coupon_performance(sales: pd.DataFrame) -> list[dict]:
    if sales.empty or "Coupon_Status" not in sales.columns:
        return []
    out = (
        sales.groupby("Coupon_Status", as_index=False)
        .agg(
            revenue=("Net_Revenue", "sum"),
            orders=("Transaction_ID", "nunique"),
            customers=("CustomerID", "nunique"),
            discount_given=("Discount_Amount", "sum"),
        )
        .sort_values("revenue", ascending=False)
        .rename(columns={"Coupon_Status": "coupon_status"})
    )
    return out.to_dict(orient="records")
