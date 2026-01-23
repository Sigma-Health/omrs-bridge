"""
Test queries to verify diagnosis functionality with actual database.
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db


def test_concept_reference_sources():
    """Test query to see what concept reference sources exist."""
    db = next(get_db())

    # Query to see all concept reference sources
    query = """
    SELECT 
        concept_source_id,
        name,
        description,
        hl7_code,
        retired
    FROM concept_reference_source 
    ORDER BY name
    """

    result = db.execute(text(query))
    sources = result.fetchall()

    print("\n=== Concept Reference Sources ===")
    for source in sources:
        print(
            f"ID: {source.concept_source_id}, Name: {source.name}, HL7: {source.hl7_code}, Retired: {source.retired}"
        )

    # Check if any ICD10 sources exist
    icd10_sources = [
        s for s in sources if "ICD" in s.name.upper() or s.hl7_code == "ICD-10"
    ]
    print(f"\n=== ICD10 Sources Found: {len(icd10_sources)} ===")
    for source in icd10_sources:
        print(
            f"ID: {source.concept_source_id}, Name: {source.name}, HL7: {source.hl7_code}"
        )


def test_concept_reference_terms():
    """Test query to see concept reference terms."""
    db = next(get_db())

    # Query to see concept reference terms with their sources
    query = """
    SELECT 
        crt.concept_reference_term_id,
        crt.code,
        crt.name,
        crt.version,
        crs.name as source_name,
        crs.hl7_code
    FROM concept_reference_term crt
    JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
    WHERE crt.retired = 0 AND crs.retired = 0
    ORDER BY crs.name, crt.code
    LIMIT 10
    """

    result = db.execute(text(query))
    terms = result.fetchall()

    print("\n=== Sample Concept Reference Terms ===")
    for term in terms:
        print(
            f"Code: {term.code}, Name: {term.name}, Source: {term.source_name} ({term.hl7_code})"
        )


def test_diagnosis_observations():
    """Test query to see diagnosis observations."""
    db = next(get_db())

    # Query to see observations that might be diagnoses
    query = """
    SELECT 
        o.obs_id,
        o.obs_datetime,
        cn.name as concept_name,
        crt.code as reference_code,
        crs.name as source_name
    FROM obs o
    JOIN concept c ON o.value_coded = c.concept_id
    JOIN concept_name cn ON c.concept_id = cn.concept_id
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = 0
    LEFT JOIN concept_reference_map crm ON c.concept_id = crm.concept_id
        AND crm.voided = 0
    LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
        AND crt.retired = 0
    LEFT JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
        AND crs.retired = 0
    WHERE o.voided = 0
        AND o.value_coded IS NOT NULL
    ORDER BY o.obs_datetime DESC
    LIMIT 5
    """

    result = db.execute(text(query))
    observations = result.fetchall()

    print("\n=== Sample Diagnosis Observations ===")
    for obs in observations:
        print(
            f"Obs ID: {obs.obs_id}, Concept: {obs.concept_name}, Code: {obs.reference_code}, Source: {obs.source_name}"
        )


def test_icd10_mappings():
    """Test query to see ICD10 mappings specifically."""
    db = next(get_db())

    # Query to see ICD10 mappings
    query = """
    SELECT 
        c.concept_id,
        cn.name as concept_name,
        crt.code as icd10_code,
        crt.name as icd10_name,
        crs.name as source_name
    FROM concept c
    JOIN concept_name cn ON c.concept_id = cn.concept_id
        AND cn.locale = 'en'
        AND cn.concept_name_type = 'FULLY_SPECIFIED'
        AND cn.voided = 0
    JOIN concept_reference_map crm ON c.concept_id = crm.concept_id
        AND crm.voided = 0
    JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
        AND crt.retired = 0
    JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
        AND crs.retired = 0
        AND (crs.name LIKE '%ICD-10%' OR crs.name LIKE '%ICD10%' OR crs.hl7_code = 'ICD-10')
    ORDER BY crt.code
    LIMIT 10
    """

    result = db.execute(text(query))
    mappings = result.fetchall()

    print("\n=== ICD10 Mappings Found ===")
    for mapping in mappings:
        print(
            f"Concept: {mapping.concept_name}, ICD10: {mapping.icd10_code}, Source: {mapping.source_name}"
        )


if __name__ == "__main__":
    # Run the tests to see database structure
    test_concept_reference_sources()
    test_concept_reference_terms()
    test_diagnosis_observations()
    test_icd10_mappings()
