import pandas as pd

from app.analytics import overview


def test_overview_metrics():
    sales = pd.DataFrame(
        {
            "Net_Revenue": [100.0, 50.0, 25.0],
            "Transaction_ID": [1, 1, 2],
            "CustomerID": [10, 10, 20],
            "Quantity": [1, 2, 1],
            "Discount_Amount": [5.0, 0.0, 2.0],
            "Transaction_Date": pd.to_datetime(["2019-01-01", "2019-01-01", "2019-01-02"]),
        }
    )
    marketing = pd.DataFrame({"Online_Spend": [10.0], "Offline_Spend": [5.0]})
    result = overview(sales, marketing)
    assert result["revenue"] == 175.0
    assert result["orders"] == 2
    assert result["customers"] == 2
    assert result["units"] == 4.0
