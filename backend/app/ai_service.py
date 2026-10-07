from __future__ import annotations

import re

from .database import validate_read_only_sql

SCHEMA = """
Tables:
1) sales_fact
   CustomerID, Gender, Location, Tenure_Months, Transaction_ID, Transaction_Date,
   Product_SKU, Product_Description, Product_Category, Quantity, Avg_Price,
   Delivery_Charges, Coupon_Status, GST, Offline_Spend, Online_Spend, Month,
   Coupon_Code, Discount_pct, Gross_Sales, Applied_Discount_pct, Discount_Amount,
   Net_Revenue, Tax_Value, Invoice_Value, Year, Month_Name, Year_Month, DayOfWeek
2) customers
   CustomerID, Gender, Location, Tenure_Months
3) marketing
   Date, Offline_Spend, Online_Spend
4) coupons
   Month, Product_Category, Coupon_Code, Discount_pct
5) tax
   Product_Category, GST
"""


def _demo_sql(question: str) -> str:
    q = question.lower()
    if "category" in q and ("top" in q or "highest" in q or "most" in q):
        return """
        SELECT Product_Category AS category, ROUND(SUM(Net_Revenue), 2) AS revenue
        FROM sales_fact
        GROUP BY Product_Category
        ORDER BY revenue DESC
        LIMIT 10
        """
    if "location" in q or "state" in q or "region" in q:
        return """
        SELECT Location AS location, ROUND(SUM(Net_Revenue), 2) AS revenue,
               COUNT(DISTINCT Transaction_ID) AS orders
        FROM sales_fact
        GROUP BY Location
        ORDER BY revenue DESC
        """
    if "product" in q and ("top" in q or "best" in q or "highest" in q):
        return """
        SELECT Product_Description AS product, ROUND(SUM(Net_Revenue), 2) AS revenue,
               SUM(Quantity) AS units
        FROM sales_fact
        GROUP BY Product_Description
        ORDER BY revenue DESC
        LIMIT 10
        """
    if "coupon" in q or "discount" in q:
        return """
        SELECT Coupon_Status AS coupon_status, ROUND(SUM(Net_Revenue), 2) AS revenue,
               COUNT(DISTINCT Transaction_ID) AS orders,
               ROUND(SUM(Discount_Amount), 2) AS discount_given
        FROM sales_fact
        GROUP BY Coupon_Status
        ORDER BY revenue DESC
        """
    if "customer" in q and ("top" in q or "highest" in q or "best" in q):
        return """
        SELECT CustomerID AS customer_id, ROUND(SUM(Net_Revenue), 2) AS revenue,
               COUNT(DISTINCT Transaction_ID) AS orders
        FROM sales_fact
        GROUP BY CustomerID
        ORDER BY revenue DESC
        LIMIT 10
        """
    if "month" in q or "trend" in q or "over time" in q:
        return """
        SELECT Year_Month AS month, ROUND(SUM(Net_Revenue), 2) AS revenue,
               COUNT(DISTINCT Transaction_ID) AS orders
        FROM sales_fact
        GROUP BY Year_Month
        ORDER BY Year_Month
        """
    return """
    SELECT Product_Category AS category, ROUND(SUM(Net_Revenue), 2) AS revenue,
           COUNT(DISTINCT Transaction_ID) AS orders
    FROM sales_fact
    GROUP BY Product_Category
    ORDER BY revenue DESC
    LIMIT 10
    """


def generate_sql(question: str, api_key: str, model: str) -> tuple[str, str]:
    if not api_key:
        return validate_read_only_sql(_demo_sql(question)), "demo"

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    prompt = f"""
You are a careful data analyst. Convert the user's question into one read-only SQL query.
Use only SELECT or WITH. Never write or modify data. Use only the tables and columns below.
Return SQL only, with no markdown fences and no explanation.

{SCHEMA}

User question: {question}
"""
    response = client.responses.create(model=model, input=prompt)
    sql = response.output_text.strip()
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql, flags=re.IGNORECASE | re.DOTALL)
    return validate_read_only_sql(sql), "llm"


def explain_result(
    question: str,
    sql: str,
    preview_rows: list[dict],
    api_key: str,
    model: str,
) -> str:
    if not preview_rows:
        return "The query ran successfully but returned no rows. Try a broader question or different wording."
    if not api_key:
        return (
            f"The analysis returned {len(preview_rows)} preview rows. "
            "The table below contains the calculated result. Add an OpenAI API key to enable a natural-language AI explanation."
        )
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    prompt = f"""
Explain this analysis result to a business user in 2-4 concise sentences.
Do not invent facts that are not in the result.
Question: {question}
SQL: {sql}
Result preview: {preview_rows[:12]}
"""
    response = client.responses.create(model=model, input=prompt)
    return response.output_text.strip()
