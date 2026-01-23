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
        COALESCE(short_cn.name, c.short_name) AS concept_short_name,
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

    -- Join for SHORT concept name (to populate short_name field)
    LEFT OUTER JOIN concept_name short_cn ON (
        short_cn.concept_id = c.concept_id 
        AND short_cn.locale = 'en'
        AND short_cn.concept_name_type = 'SHORT'
        AND short_cn.voided = false
    )

    WHERE {where_clause}

    ORDER BY o.order_id
    LIMIT :limit OFFSET :skip
    """


def get_drug_orders_with_enrichment_sql() -> str:
    """
    Get the SQL query for drug orders (order_type_id=2) with enrichment data.
    Includes drug_order and drug table joins with concept name resolution.
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
        COALESCE(short_cn.name, c.short_name) AS concept_short_name,
        c.description AS concept_description,
        c.is_set AS concept_is_set,
        
        -- Concept name information
        cn.concept_name_id AS concept_name_id,
        cn.name AS concept_name,
        cn.locale AS concept_name_locale,
        cn.locale_preferred AS concept_name_locale_preferred,
        cn.concept_name_type AS concept_name_type,
        
        -- Drug order information
        do.order_id AS drug_order_id,
        do.drug_inventory_id,
        do.dose,
        do.as_needed,
        do.dosing_type,
        do.quantity,
        do.as_needed_condition,
        do.num_refills,
        do.dosing_instructions,
        do.duration,
        do.duration_units,
        do.quantity_units,
        do.route AS drug_order_route,
        do.dose_units,
        do.frequency,
        do.brand_name,
        do.dispense_as_written,
        do.drug_non_coded,
        
        -- Drug information
        d.drug_id,
        d.concept_id AS drug_concept_id,
        d.name AS drug_name,
        d.uuid AS drug_uuid,
        d.combination AS drug_combination,
        d.strength AS drug_strength,
        d.dosage_form AS drug_dosage_form,
        d.route AS drug_route,
        
        -- Concept names for drug_order units/frequency
        duration_cn.name AS duration_units_name,
        quantity_cn.name AS quantity_units_name,
        route_cn.name AS route_name,
        dose_cn.name AS dose_units_name,
        frequency_cn.name AS frequency_name

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

    -- Join for SHORT concept name (to populate short_name field)
    LEFT OUTER JOIN concept_name short_cn ON (
        short_cn.concept_id = c.concept_id 
        AND short_cn.locale = 'en'
        AND short_cn.concept_name_type = 'SHORT'
        AND short_cn.voided = false
    )
    
    -- Join for drug_order table
    LEFT OUTER JOIN drug_order do ON (
        do.order_id = o.order_id
    )
    
    -- Join for drug table
    LEFT OUTER JOIN drug d ON (
        d.drug_id = do.drug_inventory_id
        AND d.retired = false
    )
    
    -- Join for concept names of drug_order units/frequency
    LEFT OUTER JOIN concept_name duration_cn ON (
        duration_cn.concept_id = do.duration_units
        AND duration_cn.locale = 'en'
        AND duration_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND duration_cn.voided = false
    )
    
    LEFT OUTER JOIN concept_name quantity_cn ON (
        quantity_cn.concept_id = do.quantity_units
        AND quantity_cn.locale = 'en'
        AND quantity_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND quantity_cn.voided = false
    )
    
    LEFT OUTER JOIN concept_name route_cn ON (
        route_cn.concept_id = do.route
        AND route_cn.locale = 'en'
        AND route_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND route_cn.voided = false
    )
    
    LEFT OUTER JOIN concept_name dose_cn ON (
        dose_cn.concept_id = do.dose_units
        AND dose_cn.locale = 'en'
        AND dose_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND dose_cn.voided = false
    )
    
    LEFT OUTER JOIN concept_name frequency_cn ON (
        frequency_cn.concept_id = do.frequency
        AND frequency_cn.locale = 'en'
        AND frequency_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND frequency_cn.voided = false
    )

    WHERE {where_clause}

    ORDER BY o.order_id
    LIMIT :limit OFFSET :skip
    """


def get_single_order_with_expansion_sql() -> str:
    """
    Get a single order with enrichment details and conditional expansion.

    If the order's concept is_set=true (panel), it will include set members (actual orders).
    If the order's concept is_set=false (regular), it will include parent concept metadata.

    This query returns:
    - Main order with all enrichment details (same as get_orders_with_enrichment_sql)
    - Set members (if is_set=true) - actual orders that are members of this panel
    - Parent concept metadata (if is_set=false) - metadata about the parent concept
    """
    return """
    -- Main order query with enrichment
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
        
        -- Main concept information
        c.concept_id AS concept_id,
        c.uuid AS concept_uuid,
        COALESCE(short_cn.name, c.short_name) AS concept_short_name,
        c.description AS concept_description,
        c.is_set AS concept_is_set,
        
        -- Main concept name information
        cn.concept_name_id AS concept_name_id,
        cn.name AS concept_name,
        cn.locale AS concept_name_locale,
        cn.locale_preferred AS concept_name_locale_preferred,
        cn.concept_name_type AS concept_name_type,
        
        -- Concept datatype information
        cdt.concept_datatype_id AS concept_datatype_id,
        cdt.uuid AS concept_datatype_uuid,
        cdt.name AS concept_datatype_name,
        cdt.description AS concept_datatype_description,
        
        -- Concept class information
        cc.concept_class_id AS concept_class_id,
        cc.uuid AS concept_class_uuid,
        cc.name AS concept_class_name,
        cc.description AS concept_class_description,
        
        -- Main concept answer information
        ca.concept_answer_id AS concept_answer_id,
        ca.sort_weight AS concept_answer_sort_weight,
        answer_concept.concept_id AS answer_concept_id,
        answer_concept.uuid AS answer_concept_uuid,
        answer_concept.short_name AS answer_concept_short_name,
        answer_concept.description AS answer_concept_description,
        answer_concept.is_set AS answer_concept_is_set,
        
        -- Main concept answer name information
        answer_cn.concept_name_id AS answer_concept_name_id,
        answer_cn.name AS answer_concept_name,
        answer_cn.locale AS answer_concept_name_locale,
        answer_cn.concept_name_type AS answer_concept_name_type,
        
        -- Set members (if is_set=true) - concept definitions that are members of this panel
        sm_concept.concept_id AS set_member_concept_id,
        sm_concept.uuid AS set_member_concept_uuid,
        sm_concept.short_name AS set_member_concept_short_name,
        sm_concept.description AS set_member_concept_description,
        sm_concept.is_set AS set_member_concept_is_set,
        
        -- Set member concept name information
        sm_cn.concept_name_id AS set_member_concept_name_id,
        sm_cn.name AS set_member_concept_name,
        sm_cn.locale AS set_member_concept_name_locale,
        sm_cn.concept_name_type AS set_member_concept_name_type,
        
        -- Set member concept datatype information
        sm_cdt.concept_datatype_id AS set_member_concept_datatype_id,
        sm_cdt.uuid AS set_member_concept_datatype_uuid,
        sm_cdt.name AS set_member_concept_datatype_name,
        sm_cdt.description AS set_member_concept_datatype_description,
        
        -- Set member concept class information
        sm_cc.concept_class_id AS set_member_concept_class_id,
        sm_cc.uuid AS set_member_concept_class_uuid,
        sm_cc.name AS set_member_concept_class_name,
        sm_cc.description AS set_member_concept_class_description,
        
        -- Set member concept answer information
        sm_ca.concept_answer_id AS set_member_concept_answer_id,
        sm_ca.sort_weight AS set_member_concept_answer_sort_weight,
        sm_answer_concept.concept_id AS set_member_answer_concept_id,
        sm_answer_concept.uuid AS set_member_answer_concept_uuid,
        sm_answer_concept.short_name AS set_member_answer_concept_short_name,
        sm_answer_concept.description AS set_member_answer_concept_description,
        sm_answer_concept.is_set AS set_member_answer_concept_is_set,
        
        -- Set member answer concept name information
        sm_answer_cn.concept_name_id AS set_member_answer_concept_name_id,
        sm_answer_cn.name AS set_member_answer_concept_name,
        sm_answer_cn.locale AS set_member_answer_concept_name_locale,
        sm_answer_cn.concept_name_type AS set_member_answer_concept_name_type,
        
        -- Parent concept metadata (if is_set=false) - metadata about the parent concept
        parent_concept.concept_id AS parent_concept_id,
        parent_concept.uuid AS parent_concept_uuid,
        parent_concept.short_name AS parent_concept_short_name,
        parent_concept.description AS parent_concept_description,
        parent_concept.is_set AS parent_concept_is_set,
        
        -- Parent concept name information
        parent_cn.concept_name_id AS parent_concept_name_id,
        parent_cn.name AS parent_concept_name,
        parent_cn.locale AS parent_concept_name_locale,
        parent_cn.concept_name_type AS parent_concept_name_type,
        
        -- Parent concept datatype information
        parent_cdt.concept_datatype_id AS parent_concept_datatype_id,
        parent_cdt.uuid AS parent_concept_datatype_uuid,
        parent_cdt.name AS parent_concept_datatype_name,
        parent_cdt.description AS parent_concept_datatype_description,
        
        -- Parent concept class information
        parent_cc.concept_class_id AS parent_concept_class_id,
        parent_cc.uuid AS parent_concept_class_uuid,
        parent_cc.name AS parent_concept_class_name,
        parent_cc.description AS parent_concept_class_description

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

    -- Join for main concept information
    LEFT OUTER JOIN concept c ON (
        c.concept_id = o.concept_id 
        AND c.retired = false
    )

    -- Join for main concept name information (English locale, FULLY_SPECIFIED type)
    LEFT OUTER JOIN concept_name cn ON (
        cn.concept_id = c.concept_id 
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = false
    )

    -- Join for SHORT concept name (to populate short_name field)
    LEFT OUTER JOIN concept_name short_cn ON (
        short_cn.concept_id = c.concept_id 
        AND short_cn.locale = 'en'
        AND short_cn.concept_name_type = 'SHORT'
        AND short_cn.voided = false
    )

    -- Join for concept datatype information
    LEFT OUTER JOIN concept_datatype cdt ON (
        cdt.concept_datatype_id = c.datatype_id
        AND cdt.retired = false
    )

    -- Join for concept class information
    LEFT OUTER JOIN concept_class cc ON (
        cc.concept_class_id = c.class_id
        AND cc.retired = false
    )

    -- Join for main concept answer information
    LEFT OUTER JOIN concept_answer ca ON (
        ca.concept_id = c.concept_id
    )
    
    LEFT OUTER JOIN concept answer_concept ON (
        answer_concept.concept_id = ca.answer_concept
        AND answer_concept.retired = false
    )
    
    LEFT OUTER JOIN concept_name answer_cn ON (
        answer_cn.concept_id = answer_concept.concept_id
        AND answer_cn.locale = 'en'
        AND answer_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND answer_cn.voided = false
    )

    -- Join for set members (if is_set=true) - concept definitions that are members of this panel
    LEFT OUTER JOIN concept_set cs ON (
        cs.concept_set = c.concept_id
        AND c.is_set = 1
    )
    
    LEFT OUTER JOIN concept sm_concept ON (
        sm_concept.concept_id = cs.concept_id
        AND sm_concept.retired = false
    )
    
    LEFT OUTER JOIN concept_name sm_cn ON (
        sm_cn.concept_id = sm_concept.concept_id
        AND sm_cn.locale = 'en'
        AND sm_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND sm_cn.voided = false
    )
    
    LEFT OUTER JOIN concept_datatype sm_cdt ON (
        sm_cdt.concept_datatype_id = sm_concept.datatype_id
        AND sm_cdt.retired = false
    )
    
    LEFT OUTER JOIN concept_class sm_cc ON (
        sm_cc.concept_class_id = sm_concept.class_id
        AND sm_cc.retired = false
    )
    
    LEFT OUTER JOIN concept_answer sm_ca ON (
        sm_ca.concept_id = sm_concept.concept_id
    )
    
    LEFT OUTER JOIN concept sm_answer_concept ON (
        sm_answer_concept.concept_id = sm_ca.answer_concept
        AND sm_answer_concept.retired = false
    )
    
    LEFT OUTER JOIN concept_name sm_answer_cn ON (
        sm_answer_cn.concept_id = sm_answer_concept.concept_id
        AND sm_answer_cn.locale = 'en'
        AND sm_answer_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND sm_answer_cn.voided = false
    )

    -- Join for parent concept metadata (if is_set=false) - metadata about the parent concept
    LEFT OUTER JOIN concept_set parent_cs ON (
        parent_cs.concept_id = c.concept_id
        AND c.is_set = 0
    )
    
    LEFT OUTER JOIN concept parent_concept ON (
        parent_concept.concept_id = parent_cs.concept_set
        AND parent_concept.retired = false
    )
    
    LEFT OUTER JOIN concept_name parent_cn ON (
        parent_cn.concept_id = parent_concept.concept_id
        AND parent_cn.locale = 'en'
        AND parent_cn.concept_name_type = 'FULLY_SPECIFIED'
        AND parent_cn.voided = false
    )
    
    LEFT OUTER JOIN concept_datatype parent_cdt ON (
        parent_cdt.concept_datatype_id = parent_concept.datatype_id
        AND parent_cdt.retired = false
    )
    
    LEFT OUTER JOIN concept_class parent_cc ON (
        parent_cc.concept_class_id = parent_concept.class_id
        AND parent_cc.retired = false
    )

    WHERE {where_clause}

    ORDER BY o.order_id, sm_concept.concept_id
    """
