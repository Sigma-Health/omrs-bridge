from app.sql.orders_sql import get_single_order_with_expansion_sql


def test_single_order_expansion_sql_uses_short_name_fallbacks():
    sql = get_single_order_with_expansion_sql()

    assert (
        "COALESCE(sm_short_cn.name, sm_concept.short_name) AS set_member_concept_short_name"
        in sql
    )
    assert (
        "COALESCE(answer_short_cn.name, answer_concept.short_name) AS answer_concept_short_name"
        in sql
    )
    assert (
        "COALESCE(sm_answer_short_cn.name, sm_answer_concept.short_name) AS set_member_answer_concept_short_name"
        in sql
    )
    assert (
        "COALESCE(parent_short_cn.name, parent_concept.short_name) AS parent_concept_short_name"
        in sql
    )

    assert "LEFT OUTER JOIN concept_name sm_short_cn ON (" in sql
    assert "LEFT OUTER JOIN concept_name answer_short_cn ON (" in sql
    assert "LEFT OUTER JOIN concept_name sm_answer_short_cn ON (" in sql
    assert "LEFT OUTER JOIN concept_name parent_short_cn ON (" in sql
