import pytest

from app.database import validate_read_only_sql


def test_allows_select():
    assert validate_read_only_sql("SELECT * FROM sales_fact") == "SELECT * FROM sales_fact"


def test_blocks_delete():
    with pytest.raises(ValueError):
        validate_read_only_sql("DELETE FROM sales_fact")


def test_blocks_multiple_statements():
    with pytest.raises(ValueError):
        validate_read_only_sql("SELECT 1; DROP TABLE sales_fact")
