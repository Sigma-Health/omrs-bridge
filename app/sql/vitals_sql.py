"""
SQL queries for vitals/observations with visit information.
"""


def get_vitals_by_visit_sql() -> str:
    """
    Get SQL query for vitals/observations by visit.
    This query retrieves observations that are vital signs with their concept information.
    """
    return """
    SELECT 
        o.obs_id,
        o.uuid AS obs_uuid,
        o.obs_datetime,
        o.comments,
        o.status,
        o.interpretation,
        o.value_numeric,
        o.value_text,
        o.value_coded,
        o.value_datetime,
        
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
        
        -- Concept information (vital sign)
        c.concept_id,
        c.uuid AS concept_uuid,
        c.short_name AS concept_short_name,
        c.description AS concept_description,
        
        -- Concept name
        cn.name AS concept_name,
        cn.locale AS concept_name_locale,
        cn.concept_name_type,
        
        -- Coded value name (if value is coded)
        cvn.name AS value_coded_name,
        
        -- Concept class for filtering vital signs
        cc.name AS concept_class_name

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
    
    -- Join with concept (vital sign)
    INNER JOIN concept c ON o.concept_id = c.concept_id
    
    -- Join with concept name
    INNER JOIN concept_name cn ON c.concept_id = cn.concept_id
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = 0
    
    -- Join with concept class to filter vital signs
    INNER JOIN concept_class cc ON c.class_id = cc.concept_class_id
    
    -- Left join with coded value name
    LEFT JOIN concept_name cvn ON o.value_coded = cvn.concept_id
        AND cvn.locale = 'en'
        AND cvn.concept_name_type = 'FULLY_SPECIFIED'
        AND cvn.voided = 0

    WHERE o.voided = 0
        AND v.visit_id = :visit_id
        AND cc.name IN ('Vitals', 'Vital Signs', 'Vital', 'Vital Sign')
        AND (o.value_numeric IS NOT NULL 
             OR o.value_text IS NOT NULL 
             OR o.value_coded IS NOT NULL 
             OR o.value_datetime IS NOT NULL)

    ORDER BY o.obs_datetime DESC, o.obs_id
    LIMIT :limit OFFSET :skip
    """


def get_vitals_by_visit_uuid_sql() -> str:
    """
    Get SQL query for vitals/observations by visit UUID.
    """
    return """
    SELECT 
        o.obs_id,
        o.uuid AS obs_uuid,
        o.obs_datetime,
        o.comments,
        o.status,
        o.interpretation,
        o.value_numeric,
        o.value_text,
        o.value_coded,
        o.value_datetime,
        
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
        
        -- Concept information (vital sign)
        c.concept_id,
        c.uuid AS concept_uuid,
        c.short_name AS concept_short_name,
        c.description AS concept_description,
        
        -- Concept name
        cn.name AS concept_name,
        cn.locale AS concept_name_locale,
        cn.concept_name_type,
        
        -- Coded value name (if value is coded)
        cvn.name AS value_coded_name,
        
        -- Concept class for filtering vital signs
        cc.name AS concept_class_name

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
    
    -- Join with concept (vital sign)
    INNER JOIN concept c ON o.concept_id = c.concept_id
    
    -- Join with concept name
    INNER JOIN concept_name cn ON c.concept_id = cn.concept_id
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = 0
    
    -- Join with concept class to filter vital signs
    INNER JOIN concept_class cc ON c.class_id = cc.concept_class_id
    
    -- Left join with coded value name
    LEFT JOIN concept_name cvn ON o.value_coded = cvn.concept_id
        AND cvn.locale = 'en'
        AND cvn.concept_name_type = 'FULLY_SPECIFIED'
        AND cvn.voided = 0

    WHERE o.voided = 0
        AND v.uuid = :visit_uuid
        AND cc.name IN ('Vitals', 'Vital Signs', 'Vital', 'Vital Sign')
        AND (o.value_numeric IS NOT NULL 
             OR o.value_text IS NOT NULL 
             OR o.value_coded IS NOT NULL 
             OR o.value_datetime IS NOT NULL)

    ORDER BY o.obs_datetime DESC, o.obs_id
    LIMIT :limit OFFSET :skip
    """


def get_vitals_count_by_visit_sql() -> str:
    """
    Get count query for vitals by visit.
    """
    return """
    SELECT COUNT(*) as total_count
    FROM obs o
    INNER JOIN encounter e ON o.encounter_id = e.encounter_id
    INNER JOIN visit v ON e.visit_id = v.visit_id
    INNER JOIN concept c ON o.concept_id = c.concept_id
    INNER JOIN concept_class cc ON c.class_id = cc.concept_class_id
    WHERE o.voided = 0
        AND v.visit_id = :visit_id
        AND cc.name IN ('Vitals', 'Vital Signs', 'Vital', 'Vital Sign')
        AND (o.value_numeric IS NOT NULL 
             OR o.value_text IS NOT NULL 
             OR o.value_coded IS NOT NULL 
             OR o.value_datetime IS NOT NULL)
    """


def get_vitals_grouped_by_type_sql() -> str:
    """
    Get SQL query for vitals grouped by concept type.
    """
    return """
    SELECT 
        o.obs_id,
        o.uuid AS obs_uuid,
        o.obs_datetime,
        o.comments,
        o.status,
        o.interpretation,
        o.value_numeric,
        o.value_text,
        o.value_coded,
        o.value_datetime,
        
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
        
        -- Concept information (vital sign)
        c.concept_id,
        c.uuid AS concept_uuid,
        c.short_name AS concept_short_name,
        c.description AS concept_description,
        
        -- Concept name
        cn.name AS concept_name,
        cn.locale AS concept_name_locale,
        cn.concept_name_type,
        
        -- Coded value name (if value is coded)
        cvn.name AS value_coded_name,
        
        -- Concept class for filtering vital signs
        cc.name AS concept_class_name

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
    
    -- Join with concept (vital sign)
    INNER JOIN concept c ON o.concept_id = c.concept_id
    
    -- Join with concept name
    INNER JOIN concept_name cn ON c.concept_id = cn.concept_id
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = 0
    
    -- Join with concept class to filter vital signs
    INNER JOIN concept_class cc ON c.class_id = cc.concept_class_id
    
    -- Left join with coded value name
    LEFT JOIN concept_name cvn ON o.value_coded = cvn.concept_id
        AND cvn.locale = 'en'
        AND cvn.concept_name_type = 'FULLY_SPECIFIED'
        AND cvn.voided = 0

    WHERE o.voided = 0
        AND v.visit_id = :visit_id
        AND cc.name IN ('Vitals', 'Vital Signs', 'Vital', 'Vital Sign')
        AND (o.value_numeric IS NOT NULL 
             OR o.value_text IS NOT NULL 
             OR o.value_coded IS NOT NULL 
             OR o.value_datetime IS NOT NULL)

    ORDER BY cn.name, o.obs_datetime DESC, o.obs_id
    LIMIT :limit OFFSET :skip
    """
