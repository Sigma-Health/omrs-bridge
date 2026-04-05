from fastapi.testclient import TestClient

from app.auth import get_current_api_key
from app.main import app
from app.api.patient_history import patient_history


client = TestClient(app)


def override_api_key():
    return "test-key"


app.dependency_overrides[get_current_api_key] = override_api_key


def test_get_patient_history_by_type(monkeypatch):
    def fake_history(db, patient_uuid, requested_type):
        return {
            "patient_id": 7,
            "patient_uuid": patient_uuid,
            "requested_type": requested_type,
            "counts": {
                "visits": 1,
                "complaints": 1,
                "examination_notes": 0,
                "orders": 0,
                "treatments": 0,
            },
            "visits": [
                {
                    "visit_id": 12,
                    "visit_uuid": "11111111-1111-1111-1111-111111111111",
                    "visit_date_started": "2026-04-01T10:00:00",
                    "visit_date_stopped": "2026-04-01T11:00:00",
                    "complaints": [
                        {
                            "group_obs_id": 4,
                            "group_uuid": "22222222-2222-2222-2222-222222222222",
                            "encounter_id": 30,
                            "encounter_uuid": "33333333-3333-3333-3333-333333333333",
                            "visit_id": 12,
                            "obs_datetime": "2026-04-01T10:05:00",
                            "complaint": {
                                "obs_id": 5,
                                "uuid": "44444444-4444-4444-4444-444444444444",
                                "concept_id": 1,
                                "concept_name": "Chief complaint",
                                "value_coded": None,
                                "value_coded_name": None,
                                "value_text": "Headache",
                                "value_numeric": None,
                                "obs_datetime": "2026-04-01T10:05:00",
                                "comments": None,
                                "creator_id": 1,
                                "creator_name": "Clinician",
                            },
                            "duration": None,
                            "duration_unit": None,
                            "hpi": None,
                        }
                    ],
                    "examination_notes": [],
                    "orders": [],
                    "treatments": [],
                }
            ],
        }

    monkeypatch.setattr(patient_history, "get_history", fake_history)

    response = client.get(
        "/api/v1/patient-history/patient/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        params={"type": "complaint"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requested_type"] == "complaint"
    assert payload["visits"][0]["visit_id"] == 12
    assert payload["visits"][0]["complaints"][0]["complaint"]["value_text"] == "Headache"


def test_get_patient_history_summary(monkeypatch):
    def fake_summary(db, patient_uuid, max_items_per_category):
        return {
            "patient_id": 7,
            "patient_uuid": patient_uuid,
            "summary": "1 visits on record. recent complaints/HPI include Headache.",
            "max_items_per_category": max_items_per_category,
            "counts": {
                "visits": 1,
                "complaints": 1,
                "examination_notes": 1,
                "orders": 1,
                "treatments": 1,
            },
            "visits": [
                {
                    "visit_id": 12,
                    "visit_uuid": "11111111-1111-1111-1111-111111111111",
                    "visit_date_started": "2026-04-01T10:00:00",
                    "visit_date_stopped": None,
                    "complaints": [],
                    "examination_notes": [],
                    "orders": [],
                    "treatments": [],
                }
            ],
        }

    monkeypatch.setattr(patient_history, "get_history_summary", fake_summary)

    response = client.get(
        "/api/v1/patient-history/patient/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/summary",
        params={"max_items_per_category": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["max_items_per_category"] == 3
    assert "Headache" in payload["summary"]
