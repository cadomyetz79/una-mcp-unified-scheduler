"""Offline WS3-plan to Leo display-contract tests; no external services."""
from copy import deepcopy

import pytest

from src.unified.plan_cards import project_verified_plan_cards


def plan():
    return {
        "student_id": "S10001", "term_id": "2027SP",
        "current_registrations_checked": True,
        "current_registrations": [{"section_id": "SEC1001", "course_id": "CIS376"}],
        "options": [{"rank": 1, "registration_fit": "fits_current_registration",
                     "total_credit_hours": 6,
                     "section_ids": ["SEC1001", "SEC2002"],
                     "sections": [
                         {"section_id": "SEC1001", "course_id": "CIS376", "modality": "in_person",
                          "seats_available": 5, "meetings": [{"days": ["MON", "WED"], "start": "09:30", "end": "10:45", "location": "Building A 101"}]},
                         {"section_id": "SEC2002", "course_id": "CIS410", "modality": "online",
                          "seats_available": 22, "meetings": []},
                     ]}],
    }


def project(payload):
    return project_verified_plan_cards(payload, expected_student_id="S10001", expected_term_id="2027SP")


def test_success_snapshot_and_no_invented_details():
    result = project(plan())
    assert result["status"] == "proposed_only"
    assert result["options"][0]["sections"][0]["registration_snapshot_status"] == "already_registered_in_snapshot"
    assert result["options"][0]["sections"][1]["registration_snapshot_status"] == "proposed_not_registered_in_snapshot"
    assert result["options"][0]["sections"][1]["meetings"] == []
    assert "title" not in result["options"][0]["sections"][1]
    assert "credit_hours" not in result["options"][0]["sections"][1]
    assert "enrolled" not in result["status"]


def test_no_options_is_a_valid_nontransactional_result():
    p = plan()
    p["options"] = []
    assert project(p)["options"] == []


def test_registrations_not_checked_is_displayed_honestly():
    p = plan()
    p["current_registrations_checked"] = False
    p["current_registrations"] = []
    p["options"][0]["registration_fit"] = "not_checked"
    assert project(p)["options"][0]["sections"][0]["registration_snapshot_status"] == "not_checked"


def test_another_student_forbidden():
    p = plan()
    p["student_id"] = "S10002"
    with pytest.raises(PermissionError):
        project(p)


@pytest.mark.parametrize("field,value", [("term_id", "2027FA"), ("term_id", "nope"),
                                         ("student_id", None), ("options", None), ("options", {})])
def test_bad_plan_identity_or_type_is_rejected(field, value):
    p = plan()
    p[field] = value
    with pytest.raises((ValueError, PermissionError)):
        project(p)


@pytest.mark.parametrize("mutate", [
    lambda p: p["options"][0].update(section_ids=["SEC1001", "SEC9999"]),
    lambda p: p["options"][0].update(section_ids=["SEC1001", "SEC1001"]),
    lambda p: p["options"][0].update(total_credit_hours="6"),
    lambda p: p["options"][0].update(total_credit_hours=True),
    lambda p: p["options"][0].update(registration_fit="registered"),
    lambda p: p["options"][0].update(rank=2),
    lambda p: p["options"][0]["sections"][1].update(course_id="CIS376"),
    lambda p: p["options"][0]["sections"][1].update(seats_available=-1),
    lambda p: p["options"][0]["sections"][0]["meetings"][0].update(start="10:50"),
    lambda p: p["options"][0]["sections"][0]["meetings"][0].update(days=["MON", "MOON"]),
    lambda p: p["options"][0]["sections"][0]["meetings"][0].update(location="bad\nhtml"),
    lambda p: p.update(current_registrations_checked=False),
    lambda p: p["options"][0].update(sections=[]),
])
def test_rejects_unverified_sections_and_proposal_state(mutate):
    p = plan()
    mutate(p)
    with pytest.raises(ValueError):
        project(p)


def test_does_not_modify_original_planner_response():
    p = plan()
    copy = deepcopy(p)
    project(p)
    assert p == copy
