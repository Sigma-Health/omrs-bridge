#!/usr/bin/env python3
"""
Simple script to verify that drug_name and route_name are included in drug_order_info.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.sql.sql_utils import process_raw_query_results
from app.sql.orders_sql import get_drug_orders_with_enrichment_sql


def test_drug_order_info_structure():
    """Test that drug_order_info includes drug_name and route_name fields"""

    # This is a mock test to verify the structure
    # In a real scenario, you would have actual database rows

    print("Testing drug_order_info structure...")

    # Check that the SQL query includes the necessary fields
    sql = get_drug_orders_with_enrichment_sql()

    # Verify that drug_name and route_name are in the SQL query
    assert "d.name AS drug_name" in sql, "SQL query should include d.name AS drug_name"
    assert "route_cn.name AS route_name" in sql, (
        "SQL query should include route_cn.name AS route_name"
    )

    print("✓ SQL query includes drug_name and route_name fields")

    # Check that the processing function includes the fields
    # We can't easily test this without actual data, but we can check the source code
    import inspect

    source = inspect.getsource(process_raw_query_results)

    assert '"drug_name": row.drug_name' in source, (
        "process_raw_query_results should include drug_name"
    )
    assert '"route_name": row.route_name' in source, (
        "process_raw_query_results should include route_name"
    )

    print("✓ process_raw_query_results includes drug_name and route_name fields")

    print(
        "\nAll tests passed! drug_name and route_name are properly included in drug_order_info."
    )


if __name__ == "__main__":
    test_drug_order_info_structure()
