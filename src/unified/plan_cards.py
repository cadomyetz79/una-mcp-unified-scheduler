"""Fail-closed projection of WS3 *verified* schedule proposals for Leo UI.

Only call this with a result from the authenticated, deterministic team planner.
Never use model-generated prose as input; never treat a proposal as registration.
No title or per-course credit field is emitted: those are not in WS3's plan.
"""

from __future__ import annotations

import re
from typing import Any

_STUDENT = re.compile(r"S[0-9]{5}\Z")  # Synthetic research identity only.
_TERM = re.compile(r"(?:19|20)[0-9]{2}(?:SP|SU|FA)\Z")
_COURSE = re.compile(r"[A-Z]{2,8}[0-9]{3,4}[A-Z]?\Z")
_SECTION = re.compile(r"[A-Z][A-Z0-9_-]{1,31}\Z")
_TIME = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]\Z")
_DAYS = frozenset({"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"})
_FITS = frozenset({"fits_current_registration", "requires_registration_change", "not_confirmed", "not_checked"})


def _text(value: Any, pattern: re.Pattern, label: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"Invalid {label} in verified plan.")
    return value


def _meeting(raw: Any) -> dict:
    if type(raw) is not dict:
        raise ValueError("Invalid section meeting.")
    days = raw.get("days")
    if type(days) is not list or not days or any(type(d) is not str or d not in _DAYS for d in days):
        raise ValueError("Invalid meeting days.")
    if len(set(days)) != len(days):
        raise ValueError("Duplicate meeting days.")
    start = _text(raw.get("start"), _TIME, "start time")
    end = _text(raw.get("end"), _TIME, "end time")
    if end <= start:
        raise ValueError("Meeting ends before it starts.")
    location = raw.get("location", "")
    if type(location) is not str or len(location) > 120 or any(ord(ch) < 32 for ch in location):
        raise ValueError("Invalid meeting location.")
    return {"days": list(days), "start": start, "end": end, "location": location}


def _section(raw: Any, existing_ids: set[str] | None) -> dict:
    if type(raw) is not dict:
        raise ValueError("Invalid section record.")
    sid = _text(raw.get("section_id"), _SECTION, "section ID")
    cid = _text(raw.get("course_id"), _COURSE, "course ID")
    modality = raw.get("modality")
    if type(modality) is not str or not modality or len(modality) > 48 or any(not (c.isalnum() or c in "_- ") for c in modality):
        raise ValueError("Invalid section modality.")
    seats = raw.get("seats_available")
    if type(seats) is not int or not 0 <= seats <= 100000:
        raise ValueError("Invalid seat snapshot.")
    meetings = raw.get("meetings")
    if type(meetings) is not list or len(meetings) > 14:
        raise ValueError("Invalid meeting list.")
    return {
        "section_id": sid, "course_id": cid, "modality": modality,
        "seats_available_snapshot": seats,
        "meetings": [_meeting(m) for m in meetings],
        "registration_snapshot_status": (
            "not_checked" if existing_ids is None
            else "already_registered_in_snapshot" if sid in existing_ids
            else "proposed_not_registered_in_snapshot"
        ),
    }


def project_verified_plan_cards(plan: dict, *, expected_student_id: str, expected_term_id: str) -> dict:
    """Project a trusted WS3 planner dict into a minimal, non-transactional UI view.

    The *caller* must obtain expected IDs from an authenticated server session,
    not from the browser payload. Reject mismatches rather than returning cards.
    """
    _text(expected_student_id, _STUDENT, "authenticated synthetic student ID")
    _text(expected_term_id, _TERM, "expected term")
    if type(plan) is not dict:
        raise ValueError("Verified plan must be a dictionary.")
    if plan.get("student_id") != expected_student_id:
        raise PermissionError("Plan does not belong to the authenticated student.")
    if plan.get("term_id") != expected_term_id:
        raise ValueError("Plan term does not match the authorized request.")
    checked = plan.get("current_registrations_checked")
    if checked not in (True, False, None) or type(checked) not in (bool, type(None)):
        raise ValueError("Invalid registration-check flag.")
    existing = plan.get("current_registrations", [])
    if type(existing) is not list or len(existing) > 60:
        raise ValueError("Invalid current-registration snapshot.")
    if checked is not True and existing:
        raise ValueError("Unverified current-registration snapshot.")
    existing_ids: set[str] | None = set() if checked is True else None
    if existing_ids is not None:
        for item in existing:
            if type(item) is not dict:
                raise ValueError("Invalid current-registration record.")
            sid = _text(item.get("section_id"), _SECTION, "registered section ID")
            if sid in existing_ids:
                raise ValueError("Duplicate current registration.")
            existing_ids.add(sid)
    options = plan.get("options")
    if type(options) is not list or len(options) > 10:
        raise ValueError("Invalid verified options.")
    cards = []
    for index, option in enumerate(options, start=1):
        if type(option) is not dict:
            raise ValueError("Invalid verified option.")
        raw_sections = option.get("sections")
        ids = option.get("section_ids")
        if type(raw_sections) is not list or not 1 <= len(raw_sections) <= 12:
            raise ValueError("Invalid option sections.")
        if type(ids) is not list or len(ids) != len(raw_sections):
            raise ValueError("Section ID list does not match option.")
        sections = [_section(raw, existing_ids) for raw in raw_sections]
        if [s["section_id"] for s in sections] != ids or len(set(ids)) != len(ids):
            raise ValueError("Unverified or duplicate option section IDs.")
        if len({s["course_id"] for s in sections}) != len(sections):
            raise ValueError("Multiple sections of the same course in one option.")
        credits = option.get("total_credit_hours")
        if type(credits) is not int or not 0 <= credits <= 50:
            raise ValueError("Invalid verified total credits.")
        fit = option.get("registration_fit")
        if type(fit) is not str or fit not in _FITS:
            raise ValueError("Unknown registration fit result.")
        if existing_ids is None and fit != "not_checked":
            raise ValueError("Registration fit claimed without registration check.")
        if existing_ids is not None and fit == "not_checked":
            raise ValueError("Registration fit missing after registration check.")
        rank = option.get("rank")
        if type(rank) is not int or rank != index:
            raise ValueError("Unverified option ranking.")
        cards.append({"rank": rank, "total_credit_hours": credits,
                      "registration_fit": fit, "sections": sections})
    return {"schema_version": "leo-team-plan-v1", "status": "proposed_only",
            "student_id": expected_student_id, "term_id": expected_term_id,
            "current_registrations_checked": checked is True, "options": cards}
