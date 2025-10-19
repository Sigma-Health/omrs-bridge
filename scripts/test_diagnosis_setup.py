#!/usr/bin/env python3
"""
Script to test diagnosis setup and verify database structure.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db


def check_database_structure():
    """Check if the required tables exist and have data."""
    db = next(get_db())

    print("=== Checking Database Structure ===")

    # Check concept_reference_source table
    try:
        result = db.execute(
            text("SELECT COUNT(*) as count FROM concept_reference_source")
        )
        count = result.scalar()
        print(f"✓ concept_reference_source table exists with {count} records")

        # Show sample sources
        result = db.execute(
            text("SELECT name, hl7_code FROM concept_reference_source LIMIT 5")
        )
        sources = result.fetchall()
        print("  Sample sources:")
        for source in sources:
            print(f"    - {source.name} (HL7: {source.hl7_code})")

    except Exception as e:
        print(f"✗ concept_reference_source table error: {e}")

    # Check concept_reference_term table
    try:
        result = db.execute(
            text("SELECT COUNT(*) as count FROM concept_reference_term")
        )
        count = result.scalar()
        print(f"✓ concept_reference_term table exists with {count} records")
    except Exception as e:
        print(f"✗ concept_reference_term table error: {e}")

    # Check concept_reference_map table
    try:
        result = db.execute(text("SELECT COUNT(*) as count FROM concept_reference_map"))
        count = result.scalar()
        print(f"✓ concept_reference_map table exists with {count} records")
    except Exception as e:
        print(f"✗ concept_reference_map table error: {e}")

    # Check obs table
    try:
        result = db.execute(text("SELECT COUNT(*) as count FROM obs WHERE voided = 0"))
        count = result.scalar()
        print(f"✓ obs table exists with {count} non-voided records")
    except Exception as e:
        print(f"✗ obs table error: {e}")


def check_icd10_sources():
    """Check for ICD10 sources in the database."""
    db = next(get_db())

    print("\n=== Checking for ICD10 Sources ===")

    # Look for ICD10 sources
    query = """
    SELECT 
        concept_source_id,
        name,
        description,
        hl7_code
    FROM concept_reference_source 
    WHERE retired = 0
        AND (name LIKE '%ICD%' OR hl7_code LIKE '%ICD%')
    ORDER BY name
    """

    result = db.execute(text(query))
    sources = result.fetchall()

    if sources:
        print(f"Found {len(sources)} potential ICD10 sources:")
        for source in sources:
            print(
                f"  - ID: {source.concept_source_id}, Name: {source.name}, HL7: {source.hl7_code}"
            )
    else:
        print("No ICD10 sources found. You may need to:")
        print("  1. Import ICD10 mappings into concept_reference_source")
        print("  2. Import ICD10 codes into concept_reference_term")
        print("  3. Create mappings in concept_reference_map")


def check_diagnosis_observations():
    """Check for diagnosis observations."""
    db = next(get_db())

    print("\n=== Checking for Diagnosis Observations ===")

    # Look for observations with coded values
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

    if observations:
        print(f"Found {len(observations)} recent observations:")
        for obs in observations:
            print(f"  - Obs {obs.obs_id}: {obs.concept_name}")
            if obs.reference_code:
                print(f"    Code: {obs.reference_code} (Source: {obs.source_name})")
            else:
                print("    No reference code found")
    else:
        print("No observations found")


def test_diagnosis_api_query():
    """Test the actual diagnosis API query."""
    db = next(get_db())

    print("\n=== Testing Diagnosis API Query ===")

    # Test the main diagnosis query
    query = """
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
        
        -- ICD10 code information
        crt.code AS icd10_code,
        crt.name AS icd10_name,
        crt.version AS icd10_version,
        crt.description AS icd10_description,
        crs.name AS icd10_source_name,
        crs.description AS icd10_source_description,
        crs.hl7_code AS icd10_hl7_code

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
    
    -- Join with ICD10 mapping
    LEFT JOIN concept_reference_map crm ON c.concept_id = crm.concept_id
        AND crm.voided = 0
    LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
        AND crt.retired = 0
    LEFT JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
        AND crs.retired = 0
        AND (crs.name LIKE '%ICD-10%' OR crs.name LIKE '%ICD10%' OR crs.hl7_code = 'ICD-10')

    WHERE o.voided = 0
        AND o.value_coded IS NOT NULL
        AND 1=1

    ORDER BY o.obs_datetime DESC, o.obs_id
    LIMIT 3
    """

    try:
        result = db.execute(text(query))
        rows = result.fetchall()

        if rows:
            print(f"✓ Diagnosis query successful, found {len(rows)} records:")
            for row in rows:
                print(f"  - Obs {row.obs_id}: {row.diagnosis_name}")
                if row.icd10_code:
                    print(
                        f"    ICD10: {row.icd10_code} (Source: {row.icd10_source_name})"
                    )
                else:
                    print("    No ICD10 code found")
        else:
            print("No diagnosis observations found")

    except Exception as e:
        print(f"✗ Diagnosis query failed: {e}")


if __name__ == "__main__":
    print("Diagnosis Setup Verification")
    print("=" * 40)

    check_database_structure()
    check_icd10_sources()
    check_diagnosis_observations()
    test_diagnosis_api_query()

    print("\n=== Summary ===")
    print("If you see any errors above, you may need to:")
    print("1. Ensure your database has the required tables")
    print("2. Import ICD10 mappings if none exist")
    print("3. Check that observations have coded values")
    print("4. Verify the API endpoints work with your data")
