"""Trusted planner-to-session context projection tests."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from src.gateway.plan_context import (
    PlanContext,
    from_verified_planner_result,
)


def verified_result():
    sections = [
        {"course_id": "CIS376", "section_id": "SEC1001"},
        {"course_id": "CIS410", "section_id": "SEC2002"},
    ]

    return SimpleNamespace(
        stopped_reason="answered",
        grounded=True,
        answer_source="model",
        blocked=None,
        evidence_missing=[],
        plan_cards={
            "schema_version": "leo-team-plan-v1",
            "status": "proposed_only",
            "student_id": "S10001",
            "term_id": "2027SP",
            "options": [
                {"sections": deepcopy(sections)}
            ],
        },
        trace=[
            SimpleNamespace(
                tool="plan_schedule",
                ok=True,
                arguments={
                    "course_ids": ["CIS376", "CIS410"],
                },
                result={
                    "term_id": "2027SP",
                    "requested": ["CIS376", "CIS410"],
                    "options": [
                        {"sections": deepcopy(sections)}
                    ],
                    "preferences_applied": {
                        "avoid_days": ["FRI"],
                        "earliest_start": "10:00",
                        "latest_end": None,
                        "required": ["avoid_days"],
                    },
                },
            ),
        ],
    )


def project(result):
    return from_verified_planner_result(
        result,
        expected_student_id="S10001",
        expected_term_id="2027SP",
    )


def test_verified_planner_data_creates_bounded_context():
    value = project(verified_result())

    assert value == PlanContext(
        term_id="2027SP",
        course_ids=("CIS376", "CIS410"),
        avoid_days=("FRI",),
        earliest_start="10:00",
        required_preferences=("avoid_days",),
    )

    assert not hasattr(value, "bearer_token")
    assert not hasattr(value, "messages")


@pytest.mark.parametrize("change", [
    "unverified_answer",
    "system_fallback",
    "blocked",
    "missing_evidence",
    "wrong_student",
    "wrong_term",
    "missing_cards",
    "missing_trace",
    "failed_plan",
    "duplicate_plan",
    "changed_sections",
    "changed_courses",
    "wrong_preferences",
    "missing_options",
])
def test_unverified_context_is_not_saved(change):
    result = verified_result()

    if change == "unverified_answer":
        result.grounded = False
    elif change == "system_fallback":
        result.answer_source = "system_fallback"
    elif change == "blocked":
        result.blocked = {"reason": "unverified"}
    elif change == "missing_evidence":
        result.evidence_missing = ["CIS410"]
    elif change == "wrong_student":
        result.plan_cards["student_id"] = "S10002"
    elif change == "wrong_term":
        result.plan_cards["term_id"] = "2027FA"
    elif change == "missing_cards":
        result.plan_cards = None
    elif change == "missing_trace":
        result.trace = []
    elif change == "failed_plan":
        result.trace[0].ok = False
    elif change == "duplicate_plan":
        result.trace.append(deepcopy(result.trace[0]))
    elif change == "changed_sections":
        result.plan_cards["options"][0][
            "sections"
        ][1]["section_id"] = "SEC2001"
    elif change == "changed_courses":
        result.trace[0].result[
            "requested"
        ] = ["CIS376", "CIS450"]
    elif change == "wrong_preferences":
        result.trace[0].result[
            "preferences_applied"
        ]["avoid_days"] = ["INVALID"]
    elif change == "missing_options":
        result.plan_cards["options"] = []

    assert project(result) is None


def test_foreign_identity_cannot_project_context():
    result = verified_result()

    assert from_verified_planner_result(
        result,
        expected_student_id="S10002",
        expected_term_id="2027SP",
    ) is None


def test_other_term_cannot_project_context():
    result = verified_result()

    assert from_verified_planner_result(
        result,
        expected_student_id="S10001",
        expected_term_id="2027FA",
    ) is None


def test_redacted_planner_trace_with_complete_metadata_saves_context():
    result = verified_result()
    assert "student_id" not in result.trace[0].result
    result.trace[0].result["excluded"] = []
    result.plan_cards.update({
        "requested_courses": ["CIS376", "CIS410"],
        "excluded_courses": [],
        "proposal_completeness": "complete",
    })
    assert project(result) is not None


def test_redacted_partial_proposal_metadata_and_tampering():
    result = verified_result()
    sections = [{"course_id": "CIS410", "section_id": "SEC2002"}]
    result.trace[0].result["options"][0]["sections"] = deepcopy(sections)
    result.plan_cards["options"][0]["sections"] = deepcopy(sections)
    result.trace[0].result["excluded"] = [{
        "course_id": "CIS376",
        "code": "NO_SECTION_MATCHES_PREFERENCES",
    }]
    result.plan_cards.update({
        "requested_courses": ["CIS376", "CIS410"],
        "excluded_courses": [{
            "course_id": "CIS376",
            "code": "NO_SECTION_MATCHES_PREFERENCES",
            "reason": "No open section satisfies the required day/time restrictions.",
        }],
        "proposal_completeness": "partial",
    })
    context = project(result)
    assert context is not None
    assert context.course_ids == ("CIS376", "CIS410")

    tampered = deepcopy(result)
    tampered.plan_cards["excluded_courses"][0]["reason"] = "Approved"
    assert project(tampered) is None

    tampered = deepcopy(result)
    tampered.plan_cards["proposal_completeness"] = "complete"
    assert project(tampered) is None

    tampered = deepcopy(result)
    tampered.plan_cards["requested_courses"] = ["CIS410"]
    assert project(tampered) is None
