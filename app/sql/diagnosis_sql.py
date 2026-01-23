"""
SQL queries for diagnoses with ICD10 codes.
"""


def get_diagnoses_with_icd10_sql() -> str:
    """
    Get SQL query for diagnoses with ICD10 codes, based on the user's query.
    This query retrieves observations that are diagnoses with their ICD10 mappings.
    """
    return """
    SELECT 
        o.obs_id,
        o.uuid AS obs_uuid,
        o.obs_datetime,
        o.comments,
        o.status,
        o.interpretation,
        
        -- Patient information
        p.patient_id,
        pt.uuid AS patient_uuid,
        pt.gender AS patient_gender,
        pt.birthdate AS patient_birthdate,
        
        -- Patient name
        pn.given_name AS patient_given_name,
        pn.family_name AS patient_family_name,
        pn.prefix AS patient_prefix,
        pn.middle_name AS patient_middle_name,
        pn.family_name2 AS patient_family_name2,
        pn.family_name_suffix AS patient_family_name_suffix,
        
        -- Encounter information
        e.encounter_id,
        e.uuid AS encounter_uuid,
        e.encounter_datetime,
        e.encounter_type,
        e.location_id,
        
        -- Visit information
        v.visit_id,
        v.uuid AS visit_uuid,
        
        -- Diagnosis concept information
        c.concept_id,
        c.uuid AS concept_uuid,
        c.short_name AS concept_short_name,
        c.description AS concept_description,
        
        -- Concept name
        cn.name AS diagnosis_name,
        cn.locale AS concept_name_locale,
        cn.concept_name_type,
        
        -- Reference code information
        crt.code AS reference_code,
        crt.name AS reference_name,
        crt.version AS reference_version,
        crt.description AS reference_description,
        crs.name AS reference_source_name,
        crs.description AS reference_source_description,
        crs.hl7_code AS reference_hl7_code

    FROM obs o
    
    -- Join with encounter and visit
    INNER JOIN encounter e ON o.encounter_id = e.encounter_id
    INNER JOIN visit v ON e.visit_id = v.visit_id
    
    -- Join with patient
    INNER JOIN patient p ON e.patient_id = p.patient_id
    INNER JOIN person pt ON p.patient_id = pt.person_id
    
    -- Join with patient name
    INNER JOIN person_name pn ON pt.person_id = pn.person_id 
        AND pn.preferred = 1 
        AND pn.voided = 0
    
    -- Join with concept (diagnosis)
    INNER JOIN concept c ON o.value_coded = c.concept_id
    
    -- Join with concept name
    INNER JOIN concept_name cn ON c.concept_id = cn.concept_id
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = 0
    
    -- Join with reference code mapping
    LEFT JOIN concept_reference_map crm ON c.concept_id = crm.concept_id
    LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
        AND crt.retired = 0
    LEFT JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
        AND crs.retired = 0

    WHERE o.voided = 0
        AND o.value_coded IS NOT NULL
        AND {where_clause}

    ORDER BY o.obs_datetime DESC, o.obs_id
    LIMIT :limit OFFSET :skip
    """


def get_diagnoses_by_visit_sql() -> str:
    """
    Get SQL query for diagnoses by specific visit.
    """
    return """
    SELECT 
        o.obs_id,
        o.uuid AS obs_uuid,
        o.obs_datetime,
        o.comments,
        o.status,
        o.interpretation,
        
        -- Patient information
        p.patient_id,
        pt.uuid AS patient_uuid,
        pt.gender AS patient_gender,
        pt.birthdate AS patient_birthdate,
        
        -- Patient name
        pn.given_name AS patient_given_name,
        pn.family_name AS patient_family_name,
        pn.prefix AS patient_prefix,
        pn.middle_name AS patient_middle_name,
        pn.family_name2 AS patient_family_name2,
        pn.family_name_suffix AS patient_family_name_suffix,
        
        -- Encounter information
        e.encounter_id,
        e.uuid AS encounter_uuid,
        e.encounter_datetime,
        e.encounter_type,
        e.location_id,
        
        -- Visit information
        v.visit_id,
        v.uuid AS visit_uuid,
        
        -- Diagnosis concept information
        c.concept_id,
        c.uuid AS concept_uuid,
        c.short_name AS concept_short_name,
        c.description AS concept_description,
        
        -- Concept name
        cn.name AS diagnosis_name,
        cn.locale AS concept_name_locale,
        cn.concept_name_type,
        
        -- Reference code information
        crt.code AS reference_code,
        crt.name AS reference_name,
        crt.version AS reference_version,
        crt.description AS reference_description,
        crs.name AS reference_source_name,
        crs.description AS reference_source_description,
        crs.hl7_code AS reference_hl7_code

    FROM obs o
    
    -- Join with encounter and visit
    INNER JOIN encounter e ON o.encounter_id = e.encounter_id
    INNER JOIN visit v ON e.visit_id = v.visit_id
    
    -- Join with patient
    INNER JOIN patient p ON e.patient_id = p.patient_id
    INNER JOIN person pt ON p.patient_id = pt.person_id
    
    -- Join with patient name
    INNER JOIN person_name pn ON pt.person_id = pn.person_id 
        AND pn.preferred = 1 
        AND pn.voided = 0
    
    -- Join with concept (diagnosis)
    INNER JOIN concept c ON o.value_coded = c.concept_id
    
    -- Join with concept name
    INNER JOIN concept_name cn ON c.concept_id = cn.concept_id
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = 0
    
    -- Join with reference code mapping
    LEFT JOIN concept_reference_map crm ON c.concept_id = crm.concept_id
    LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
        AND crt.retired = 0
    LEFT JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
        AND crs.retired = 0

    WHERE o.voided = 0
        AND o.value_coded IS NOT NULL
        AND v.visit_id = :visit_id

    ORDER BY o.obs_datetime DESC, o.obs_id
    LIMIT :limit OFFSET :skip
    """


def get_diagnoses_count_sql() -> str:
    """
    Get count query for diagnoses.
    """
    return """
    SELECT COUNT(*) as total_count
    FROM obs o
    INNER JOIN encounter e ON o.encounter_id = e.encounter_id
    INNER JOIN visit v ON e.visit_id = v.visit_id
    INNER JOIN concept c ON o.value_coded = c.concept_id
    LEFT JOIN concept_reference_map crm ON c.concept_id = crm.concept_id
    LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
        AND crt.retired = 0
    LEFT JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
        AND crs.retired = 0
        AND (crs.name LIKE '%ICD-10%' OR crs.name LIKE '%ICD10%' OR crs.hl7_code = 'ICD-10')
    WHERE o.voided = 0
        AND o.value_coded IS NOT NULL
        AND {where_clause}
    """
