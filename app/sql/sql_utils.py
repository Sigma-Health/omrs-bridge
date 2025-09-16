"""
SQL utilities for building and executing dynamic queries.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text


def build_where_clause(conditions: Dict[str, Any]) -> str:
    """
    Build WHERE clause from conditions dictionary.

    Args:
        conditions: Dictionary of field -> value conditions

    Returns:
        WHERE clause string
    """
    where_parts = []

    for field, value in conditions.items():
        if field == "order_type_id":
            where_parts.append("o.order_type_id = :order_type_id")
        elif field == "visit_uuid":
            where_parts.append("v.uuid = :visit_uuid")
        elif field == "voided":
            where_parts.append("o.voided = :voided")
        elif field == "encounter_id":
            where_parts.append("o.encounter_id = :encounter_id")
        elif field == "patient_id":
            where_parts.append("o.patient_id = :patient_id")
        elif field == "concept_id":
            where_parts.append("o.concept_id = :concept_id")
        elif field == "orderer":
            where_parts.append("o.orderer = :orderer")
        elif field == "date_activated_from":
            where_parts.append("o.date_activated >= :date_activated_from")
        elif field == "date_activated_to":
            where_parts.append("o.date_activated <= :date_activated_to")
        elif field == "urgency":
            where_parts.append("o.urgency = :urgency")
        elif field == "order_action":
            where_parts.append("o.order_action = :order_action")
        elif field == "concept_uuid":
            where_parts.append("c.uuid = :concept_uuid")
        elif field == "order_id":
            where_parts.append("o.order_id = :order_id")
        elif field == "order_uuid":
            where_parts.append("o.uuid = :order_uuid")
        # Add more conditions as needed

    return " AND ".join(where_parts) if where_parts else "1=1"


def execute_enriched_orders_query(
    db: Session,
    sql_template: str,
    conditions: Dict[str, Any],
    skip: int = 0,
    limit: int = 100,
):
    """
    Execute enriched orders query with dynamic WHERE conditions.

    Args:
        db: Database session
        sql_template: SQL template with {where_clause} placeholder
        conditions: Dictionary of WHERE conditions
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        SQLAlchemy result object
    """
    import logging

    logger = logging.getLogger(__name__)

    # Build WHERE clause
    where_clause = build_where_clause(conditions)
    logger.info(f"Generated WHERE clause: {where_clause}")

    # Replace placeholder in SQL template
    sql = sql_template.format(where_clause=where_clause)

    # Prepare parameters (include pagination)
    params = conditions.copy()
    params.update({"limit": limit, "skip": skip})
    logger.info(f"SQL parameters: {params}")

    # Log first 500 characters of SQL for debugging
    logger.info(f"Generated SQL (first 500 chars): {sql[:500]}...")

    # Execute query
    return db.execute(text(sql), params)


def process_raw_query_results(result) -> List[Dict[str, Any]]:
    """
    Process raw SQL query results into enriched order dictionaries.
    """
    orders = []
    for row in result:
        order_dict = {
            # Order fields
            "order_id": row.order_id,
            "order_type_id": row.order_type_id,
            "concept_id": row.concept_id,
            "orderer": row.orderer,
            "encounter_id": row.encounter_id,
            "instructions": row.instructions,
            "date_activated": row.date_activated,
            "auto_expire_date": row.auto_expire_date,
            "date_stopped": row.date_stopped,
            "order_reason": row.order_reason,
            "order_reason_non_coded": row.order_reason_non_coded,
            "creator": row.creator,
            "date_created": row.date_created,
            "voided": row.voided,
            "voided_by": row.voided_by,
            "date_voided": row.date_voided,
            "void_reason": row.void_reason,
            "patient_id": row.patient_id,
            "accession_number": row.accession_number,
            "uuid": row.uuid,
            "urgency": row.urgency,
            "order_number": row.order_number,
            "previous_order_id": row.previous_order_id,
            "order_action": row.order_action,
            "comment_to_fulfiller": row.comment_to_fulfiller,
            "care_setting": row.care_setting,
            "scheduled_date": row.scheduled_date,
            "order_group_id": row.order_group_id,
            "sort_weight": row.sort_weight,
            "fulfiller_comment": row.fulfiller_comment,
            "fulfiller_status": row.fulfiller_status,
            "form_namespace_and_path": row.form_namespace_and_path,
        }

        # Build enriched orderer info
        orderer_info = None
        if row.orderer_person_id:
            orderer_name_parts = []
            if row.orderer_prefix:
                orderer_name_parts.append(row.orderer_prefix)
            if row.orderer_given_name:
                orderer_name_parts.append(row.orderer_given_name)
            if row.orderer_middle_name:
                orderer_name_parts.append(row.orderer_middle_name)
            if row.orderer_family_name:
                orderer_name_parts.append(row.orderer_family_name)
            if row.orderer_family_name2:
                orderer_name_parts.append(row.orderer_family_name2)
            if row.orderer_family_name_suffix:
                orderer_name_parts.append(row.orderer_family_name_suffix)

            orderer_name = (
                " ".join(orderer_name_parts)
                if orderer_name_parts
                else row.provider_name
            )

            orderer_info = {
                "person_id": row.orderer_person_id,
                "uuid": row.orderer_uuid,
                "name": orderer_name,
                "gender": row.orderer_gender,
                "birthdate": row.orderer_birthdate,
                "provider_id": row.provider_id,
                "provider_name": row.provider_name,
                "provider_identifier": row.provider_identifier,
                "provider_uuid": row.provider_uuid,
            }

        # Build enriched patient info
        patient_info = None
        if row.patient_person_id:
            patient_name_parts = []
            if row.patient_prefix:
                patient_name_parts.append(row.patient_prefix)
            if row.patient_given_name:
                patient_name_parts.append(row.patient_given_name)
            if row.patient_middle_name:
                patient_name_parts.append(row.patient_middle_name)
            if row.patient_family_name:
                patient_name_parts.append(row.patient_family_name)
            if row.patient_family_name2:
                patient_name_parts.append(row.patient_family_name2)
            if row.patient_family_name_suffix:
                patient_name_parts.append(row.patient_family_name_suffix)

            patient_name = " ".join(patient_name_parts) if patient_name_parts else None

            patient_info = {
                "person_id": row.patient_person_id,
                "uuid": row.patient_uuid,
                "name": patient_name,
                "gender": row.patient_gender,
                "birthdate": row.patient_birthdate,
            }

        # Build enriched concept info
        concept_info = None
        if row.concept_id:
            concept_info = {
                "concept_id": row.concept_id,
                "uuid": row.concept_uuid,
                "name": row.concept_name,
                "short_name": row.concept_short_name,
                "description": row.concept_description,
                "is_set": row.concept_is_set,
            }

        # Add enriched information to order
        order_dict["orderer_info"] = orderer_info
        order_dict["patient_info"] = patient_info
        order_dict["concept_info"] = concept_info

        orders.append(order_dict)

    return orders


def process_expanded_order_results(result) -> Dict[str, Any]:
    """
    Process raw SQL query results for a single order with expansion into structured format.

    Returns:
        Dictionary with main order, set_members (if panel), and parent_concept (if regular)
    """
    import logging

    logger = logging.getLogger(__name__)

    rows = list(result)
    logger.info(f"Processing {len(rows)} rows for expanded order results")

    if not rows:
        logger.warning("No rows returned from SQL query")
        return None

    # Get the first row for main order data
    main_row = rows[0]
    logger.info(
        f"Main row - order_id: {main_row.order_id}, concept_id: {main_row.concept_id}, is_set: {main_row.concept_is_set}"
    )

    # Build main order dictionary (same as process_raw_query_results)
    order_dict = {
        # Order fields
        "order_id": main_row.order_id,
        "order_type_id": main_row.order_type_id,
        "concept_id": main_row.concept_id,
        "orderer": main_row.orderer,
        "encounter_id": main_row.encounter_id,
        "instructions": main_row.instructions,
        "date_activated": main_row.date_activated,
        "auto_expire_date": main_row.auto_expire_date,
        "date_stopped": main_row.date_stopped,
        "order_reason": main_row.order_reason,
        "order_reason_non_coded": main_row.order_reason_non_coded,
        "creator": main_row.creator,
        "date_created": main_row.date_created,
        "voided": main_row.voided,
        "voided_by": main_row.voided_by,
        "date_voided": main_row.date_voided,
        "void_reason": main_row.void_reason,
        "patient_id": main_row.patient_id,
        "accession_number": main_row.accession_number,
        "uuid": main_row.uuid,
        "urgency": main_row.urgency,
        "order_number": main_row.order_number,
        "previous_order_id": main_row.previous_order_id,
        "order_action": main_row.order_action,
        "comment_to_fulfiller": main_row.comment_to_fulfiller,
        "care_setting": main_row.care_setting,
        "scheduled_date": main_row.scheduled_date,
        "order_group_id": main_row.order_group_id,
        "sort_weight": main_row.sort_weight,
        "fulfiller_comment": main_row.fulfiller_comment,
        "fulfiller_status": main_row.fulfiller_status,
        "form_namespace_and_path": main_row.form_namespace_and_path,
    }

    # Build enriched orderer info
    orderer_info = None
    if main_row.orderer_person_id:
        orderer_name_parts = []
        if main_row.orderer_prefix:
            orderer_name_parts.append(main_row.orderer_prefix)
        if main_row.orderer_given_name:
            orderer_name_parts.append(main_row.orderer_given_name)
        if main_row.orderer_middle_name:
            orderer_name_parts.append(main_row.orderer_middle_name)
        if main_row.orderer_family_name:
            orderer_name_parts.append(main_row.orderer_family_name)
        if main_row.orderer_family_name2:
            orderer_name_parts.append(main_row.orderer_family_name2)
        if main_row.orderer_family_name_suffix:
            orderer_name_parts.append(main_row.orderer_family_name_suffix)

        orderer_name = (
            " ".join(orderer_name_parts)
            if orderer_name_parts
            else main_row.provider_name
        )

        orderer_info = {
            "person_id": main_row.orderer_person_id,
            "uuid": main_row.orderer_uuid,
            "name": orderer_name,
            "gender": main_row.orderer_gender,
            "birthdate": main_row.orderer_birthdate,
            "provider_id": main_row.provider_id,
            "provider_name": main_row.provider_name,
            "provider_identifier": main_row.provider_identifier,
            "provider_uuid": main_row.provider_uuid,
        }

    # Build enriched patient info
    patient_info = None
    if main_row.patient_person_id:
        patient_name_parts = []
        if main_row.patient_prefix:
            patient_name_parts.append(main_row.patient_prefix)
        if main_row.patient_given_name:
            patient_name_parts.append(main_row.patient_given_name)
        if main_row.patient_middle_name:
            patient_name_parts.append(main_row.patient_middle_name)
        if main_row.patient_family_name:
            patient_name_parts.append(main_row.patient_family_name)
        if main_row.patient_family_name2:
            patient_name_parts.append(main_row.patient_family_name2)
        if main_row.patient_family_name_suffix:
            patient_name_parts.append(main_row.patient_family_name_suffix)

        patient_name = " ".join(patient_name_parts) if patient_name_parts else None

        patient_info = {
            "person_id": main_row.patient_person_id,
            "uuid": main_row.patient_uuid,
            "name": patient_name,
            "gender": main_row.patient_gender,
            "birthdate": main_row.patient_birthdate,
        }

    # Build enriched concept info with additional metadata
    concept_info = None
    if main_row.concept_id:
        concept_info = {
            "concept_id": main_row.concept_id,
            "uuid": main_row.concept_uuid,
            "name": main_row.concept_name,
            "short_name": main_row.concept_short_name,
            "description": main_row.concept_description,
            "is_set": main_row.concept_is_set,
            "datatype": {
                "concept_datatype_id": main_row.concept_datatype_id,
                "uuid": main_row.concept_datatype_uuid,
                "name": main_row.concept_datatype_name,
                "description": main_row.concept_datatype_description,
            }
            if main_row.concept_datatype_id
            else None,
            "concept_class": {
                "concept_class_id": main_row.concept_class_id,
                "uuid": main_row.concept_class_uuid,
                "name": main_row.concept_class_name,
                "description": main_row.concept_class_description,
            }
            if main_row.concept_class_id
            else None,
        }

    # Add enriched information to order
    order_dict["orderer_info"] = orderer_info
    order_dict["patient_info"] = patient_info
    order_dict["concept_info"] = concept_info

    # Process set members (if panel - is_set=true)
    set_members = []
    logger.info(f"Checking if concept is_set == 1: {main_row.concept_is_set == 1}")
    if main_row.concept_is_set == 1:
        logger.info("Processing set members for panel concept")
        seen_orders = set()
        for i, row in enumerate(rows):
            logger.info(
                f"Row {i}: set_member_order_id={row.set_member_order_id}, set_member_concept_id={row.set_member_concept_id}"
            )
            if row.set_member_order_id and row.set_member_order_id not in seen_orders:
                seen_orders.add(row.set_member_order_id)
                logger.info(f"Adding set member order: {row.set_member_order_id}")

                set_member_order = {
                    "order_id": row.set_member_order_id,
                    "uuid": row.set_member_order_uuid,
                    "order_number": row.set_member_order_number,
                    "instructions": row.set_member_instructions,
                    "date_activated": row.set_member_date_activated,
                    "auto_expire_date": row.set_member_auto_expire_date,
                    "date_stopped": row.set_member_date_stopped,
                    "voided": row.set_member_voided,
                    "urgency": row.set_member_urgency,
                    "order_action": row.set_member_order_action,
                    "accession_number": row.set_member_accession_number,
                    "concept_info": {
                        "concept_id": row.set_member_concept_id,
                        "uuid": row.set_member_concept_uuid,
                        "name": row.set_member_concept_name,
                        "short_name": row.set_member_concept_short_name,
                        "description": row.set_member_concept_description,
                        "is_set": row.set_member_concept_is_set,
                    }
                    if row.set_member_concept_id
                    else None,
                }
                set_members.append(set_member_order)

    # Process parent concept metadata (if regular concept - is_set=false)
    parent_concept_info = None
    if main_row.concept_is_set == 0 and main_row.parent_concept_id:
        parent_concept_info = {
            "concept_id": main_row.parent_concept_id,
            "uuid": main_row.parent_concept_uuid,
            "name": main_row.parent_concept_name,
            "short_name": main_row.parent_concept_short_name,
            "description": main_row.parent_concept_description,
            "is_set": main_row.parent_concept_is_set,
            "datatype": {
                "concept_datatype_id": main_row.parent_concept_datatype_id,
                "uuid": main_row.parent_concept_datatype_uuid,
                "name": main_row.parent_concept_datatype_name,
                "description": main_row.parent_concept_datatype_description,
            }
            if main_row.parent_concept_datatype_id
            else None,
            "concept_class": {
                "concept_class_id": main_row.parent_concept_class_id,
                "uuid": main_row.parent_concept_class_uuid,
                "name": main_row.parent_concept_class_name,
                "description": main_row.parent_concept_class_description,
            }
            if main_row.parent_concept_class_id
            else None,
        }

    # Build final result
    result_dict = {
        "order": order_dict,
        "set_members": set_members if set_members else None,
        "parent_concept": parent_concept_info,
    }

    logger.info(
        f"Final result - set_members count: {len(set_members)}, parent_concept: {parent_concept_info is not None}"
    )

    return result_dict
