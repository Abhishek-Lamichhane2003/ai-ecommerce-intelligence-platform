from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class CommerceData:
    sales: pd.DataFrame
    customers: pd.DataFrame
    marketing: pd.DataFrame
    coupons: pd.DataFrame
    tax: pd.DataFrame


class DatasetMissingError(FileNotFoundError):
    pass


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    aliases = {
        "Product_Cateogry": "Product_Category",
        "Customer_ID": "CustomerID",
        "TransactionID": "Transaction_ID",
        "TransactionDate": "Transaction_Date",
        "Average_Price": "Avg_Price",
        "Delivery_Charge": "Delivery_Charges",
        "Discount_Percent": "Discount_pct",
    }
    df = df.rename(columns={k: v for k, v in aliases.items() if k in df.columns})
    unnamed = [c for c in df.columns if c.lower().startswith("unnamed")]
    if unnamed:
        df = df.drop(columns=unnamed)
    return df


def _normalize_gst(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0)
    return pd.Series(np.where(values > 1, values / 100.0, values), index=series.index)


def load_commerce_data(path: str | Path) -> CommerceData:
    path = Path(path)
    if not path.exists():
        raise DatasetMissingError(
            f"Dataset not found at {path}. Put the Kaggle CSV there and name it ecommerce_sales.csv."
        )

    raw = _clean_columns(pd.read_csv(path, low_memory=False))
    required = [
        "CustomerID",
        "Transaction_ID",
        "Transaction_Date",
        "Product_Category",
        "Quantity",
        "Avg_Price",
    ]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(
            "The CSV does not match the expected Kaggle Online Shopping dataset. "
            f"Missing columns: {', '.join(missing)}"
        )

    numeric_cols = [
        "CustomerID",
        "Tenure_Months",
        "Transaction_ID",
        "Quantity",
        "Avg_Price",
        "Delivery_Charges",
        "GST",
        "Offline_Spend",
        "Online_Spend",
        "Month",
        "Discount_pct",
    ]
    for col in numeric_cols:
        if col in raw.columns:
            raw[col] = pd.to_numeric(raw[col], errors="coerce")

    raw["Transaction_Date"] = pd.to_datetime(
        raw["Transaction_Date"], errors="coerce", format="mixed"
    )
    if "Date" in raw.columns:
        raw["Date"] = pd.to_datetime(raw["Date"], errors="coerce", format="mixed")

    sales = raw.dropna(
        subset=["CustomerID", "Transaction_ID", "Transaction_Date", "Product_Category"]
    ).copy()

    sales["Month"] = sales["Transaction_Date"].dt.month.astype("Int64")
    sales["Year"] = sales["Transaction_Date"].dt.year.astype("Int64")
    sales["Month_Name"] = sales["Transaction_Date"].dt.strftime("%b")
    sales["Year_Month"] = sales["Transaction_Date"].dt.to_period("M").astype(str)
    sales["DayOfWeek"] = sales["Transaction_Date"].dt.day_name()

    for col in ["Quantity", "Avg_Price", "Delivery_Charges", "Discount_pct"]:
        if col not in sales.columns:
            sales[col] = 0.0
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0.0)

    if "GST" not in sales.columns:
        sales["GST"] = 0.0
    sales["GST"] = _normalize_gst(sales["GST"])

    sales["Gross_Sales"] = sales["Quantity"] * sales["Avg_Price"]
    coupon_used = (
        sales.get("Coupon_Status", pd.Series("", index=sales.index))
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("used")
    )
    sales["Applied_Discount_pct"] = np.where(coupon_used, sales["Discount_pct"], 0.0)
    sales["Discount_Amount"] = sales["Gross_Sales"] * sales["Applied_Discount_pct"] / 100.0
    sales["Net_Revenue"] = sales["Gross_Sales"] - sales["Discount_Amount"]
    sales["Tax_Value"] = sales["Net_Revenue"] * sales["GST"]
    sales["Invoice_Value"] = (
        sales["Net_Revenue"] + sales["Tax_Value"] + sales["Delivery_Charges"]
    )

    for col in ["CustomerID", "Transaction_ID"]:
        sales[col] = sales[col].round().astype("Int64")

    customer_cols = [
        c for c in ["CustomerID", "Gender", "Location", "Tenure_Months"] if c in sales.columns
    ]
    customers = (
        sales[customer_cols]
        .drop_duplicates(subset=["CustomerID"], keep="last")
        .reset_index(drop=True)
    )

    marketing_date = "Date" if "Date" in raw.columns else "Transaction_Date"
    if marketing_date in raw.columns and {"Offline_Spend", "Online_Spend"}.issubset(raw.columns):
        marketing = raw[[marketing_date, "Offline_Spend", "Online_Spend"]].copy()
        marketing = marketing.rename(columns={marketing_date: "Date"})
        marketing["Date"] = pd.to_datetime(marketing["Date"], errors="coerce", format="mixed")
        marketing["Offline_Spend"] = pd.to_numeric(marketing["Offline_Spend"], errors="coerce")
        marketing["Online_Spend"] = pd.to_numeric(marketing["Online_Spend"], errors="coerce")
        marketing = (
            marketing.dropna(subset=["Date"])
            .drop_duplicates(subset=["Date"], keep="first")
            .sort_values("Date")
            .reset_index(drop=True)
        )
    else:
        marketing = pd.DataFrame(columns=["Date", "Offline_Spend", "Online_Spend"])

    coupon_cols = [
        c for c in ["Month", "Product_Category", "Coupon_Code", "Discount_pct"] if c in raw.columns
    ]
    if {"Month", "Product_Category"}.issubset(coupon_cols):
        coupons = raw[coupon_cols].copy()
        coupons["Month"] = pd.to_numeric(coupons["Month"], errors="coerce").astype("Int64")
        coupons["Discount_pct"] = pd.to_numeric(coupons.get("Discount_pct"), errors="coerce")
        coupons = coupons.dropna(subset=["Month", "Product_Category"])
        coupons = coupons.drop_duplicates(
            subset=["Month", "Product_Category"], keep="last"
        ).reset_index(drop=True)
    else:
        coupons = pd.DataFrame(columns=["Month", "Product_Category", "Coupon_Code", "Discount_pct"])

    if {"Product_Category", "GST"}.issubset(raw.columns):
        tax = raw[["Product_Category", "GST"]].copy()
        tax["GST"] = _normalize_gst(tax["GST"])
        tax = (
            tax.dropna(subset=["Product_Category"])
            .drop_duplicates(subset=["Product_Category"], keep="last")
            .reset_index(drop=True)
        )
    else:
        tax = pd.DataFrame(columns=["Product_Category", "GST"])

    return CommerceData(
        sales=sales.reset_index(drop=True),
        customers=customers,
        marketing=marketing,
        coupons=coupons,
        tax=tax,
    )
