"""
SQL queries for orders with enrichment data.
"""


def get_orders_with_enrichment_sql() -> str:
    """
    Get the reusable SQL query for orders with enrichment (provider, orderer, patient, concept info).
    This query can be reused with different WHERE conditions.
    """
    return """
    SELECT 
        o.order_id,
        o.order_type_id,
        o.concept_id,
        o.orderer,
        o.encounter_id,
        o.instructions,
        o.date_activated,
        o.auto_expire_date,
        o.date_stopped,
        o.order_reason,
        o.order_reason_non_coded,
        o.creator,
        o.date_created,
        o.voided,
        o.voided_by,
        o.date_voided,
        o.void_reason,
        o.patient_id,
        o.accession_number,
        o.uuid,
        o.urgency,
        o.order_number,
        o.previous_order_id,
        o.order_action,
        o.comment_to_fulfiller,
        o.care_setting,
        o.scheduled_date,
        o.order_group_id,
        o.sort_weight,
        o.fulfiller_comment,
        o.fulfiller_status,
        o.form_namespace_and_path,
        
        -- Provider information
        p.provider_id,
        p.name AS provider_name,
        p.identifier AS provider_identifier,
        p.uuid AS provider_uuid,
        
        -- Orderer person information
        op.person_id AS orderer_person_id,
        op.uuid AS orderer_uuid,
        op.gender AS orderer_gender,
        op.birthdate AS orderer_birthdate,
        
        -- Orderer name information
        opn.given_name AS orderer_given_name,
        opn.family_name AS orderer_family_name,
        opn.prefix AS orderer_prefix,
        opn.middle_name AS orderer_middle_name,
        opn.family_name2 AS orderer_family_name2,
        opn.family_name_suffix AS orderer_family_name_suffix,
        
        -- Patient person information
        pt.person_id AS patient_person_id,
        pt.uuid AS patient_uuid,
        pt.gender AS patient_gender,
        pt.birthdate AS patient_birthdate,
        
        -- Patient name information
        ptn.given_name AS patient_given_name,
        ptn.family_name AS patient_family_name,
        ptn.prefix AS patient_prefix,
        ptn.middle_name AS patient_middle_name,
        ptn.family_name2 AS patient_family_name2,
        ptn.family_name_suffix AS patient_family_name_suffix,
        
        -- Concept information
        c.concept_id AS concept_id,
        c.uuid AS concept_uuid,
        c.short_name AS concept_short_name,
        c.description AS concept_description,
        c.is_set AS concept_is_set,
        
        -- Concept name information
        cn.concept_name_id AS concept_name_id,
        cn.name AS concept_name,
        cn.locale AS concept_name_locale,
        cn.locale_preferred AS concept_name_locale_preferred,
        cn.concept_name_type AS concept_name_type

    FROM orders o

    -- Join with encounter and visit
    INNER JOIN encounter e ON o.encounter_id = e.encounter_id
    INNER JOIN visit v ON e.visit_id = v.visit_id

    -- Join for orderer information through provider table
    LEFT OUTER JOIN provider p ON (
        p.provider_id = o.orderer 
        AND p.retired = false
    )

    LEFT OUTER JOIN person op ON (
        op.person_id = p.person_id 
        AND op.voided = false
    )

    LEFT OUTER JOIN person_name opn ON (
        opn.person_id = o.orderer 
        AND opn.preferred = true 
        AND opn.voided = false
    )

    -- Join for patient information
    LEFT OUTER JOIN person pt ON (
        pt.person_id = o.patient_id 
        AND pt.voided = false
    )

    LEFT OUTER JOIN person_name ptn ON (
        ptn.person_id = o.patient_id 
        AND ptn.preferred = true 
        AND ptn.voided = false
    )

    -- Join for concept information
    LEFT OUTER JOIN concept c ON (
        c.concept_id = o.concept_id 
        AND c.retired = false
    )

    -- Join for concept name information (English locale, FULLY_SPECIFIED type)
    LEFT OUTER JOIN concept_name cn ON (
        cn.concept_id = c.concept_id 
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = false
    )

    WHERE {where_clause}

    ORDER BY o.order_id
    LIMIT :limit OFFSET :skip
    """
