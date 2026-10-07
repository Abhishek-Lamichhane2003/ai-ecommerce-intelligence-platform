from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .analytics import customer_summary


def segment_customers(sales: pd.DataFrame, n_clusters: int = 4) -> dict:
    customers = customer_summary(sales).copy()
    if len(customers) < 4:
        return {"customers": [], "profiles": [], "silhouette_score": None}

    k = min(n_clusters, len(customers))
    features = pd.DataFrame(
        {
            "recency": customers["recency_days"].clip(lower=0),
            "frequency": np.log1p(customers["frequency"].clip(lower=0)),
            "monetary": np.log1p(customers["monetary"].clip(lower=0)),
        }
    )
    scaled = StandardScaler().fit_transform(features)
    model = KMeans(n_clusters=k, random_state=42, n_init=20)
    customers["cluster"] = model.fit_predict(scaled)

    score = None
    if k > 1 and len(customers) > k:
        score = float(silhouette_score(scaled, customers["cluster"]))

    profiles = (
        customers.groupby("cluster", as_index=False)
        .agg(
            customers=("CustomerID", "count"),
            avg_recency=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_revenue=("monetary", "sum"),
        )
    )
    ranked = profiles.copy()
    ranked["value_score"] = (
        ranked["avg_monetary"].rank(pct=True)
        + ranked["avg_frequency"].rank(pct=True)
        + (-ranked["avg_recency"]).rank(pct=True)
    )
    order = ranked.sort_values("value_score", ascending=False)["cluster"].tolist()
    names = ["Champions", "Loyal", "Developing", "At Risk"]
    mapping = {
        cluster: names[i] if i < len(names) else f"Segment {i + 1}"
        for i, cluster in enumerate(order)
    }
    customers["segment"] = customers["cluster"].map(mapping)
    profiles["segment"] = profiles["cluster"].map(mapping)
    profiles = profiles.sort_values("total_revenue", ascending=False)

    customer_cols = [
        "CustomerID",
        "recency_days",
        "frequency",
        "monetary",
        "avg_order_value",
        "segment",
    ]
    if "location" in customers.columns:
        customer_cols.append("location")
    customer_records = customers[customer_cols].to_dict(orient="records")
    return {
        "customers": customer_records,
        "profiles": profiles.to_dict(orient="records"),
        "silhouette_score": score,
    }
