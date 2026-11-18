"""Deterministic evidence for two verified research failure cases.

Only exact, self-directed question patterns are routed.
All academic facts must come from protected MCP lookups.

This module does not grant access to academic records.
Student identity remains bound by the authenticated runner.
"""

import re


_HISTORY = re.compile(
    r"^\s*(?:what|which)\s+(?:courses|classes)\s+"
    r"have\s+i\s+already\s+"
    r"(?:completed|passed|taken)\s*\??\s*$",
    re.IGNORECASE,
)

_PREREQUISITE = re.compile(
    r"^\s*can\s+i\s+take\s+"
    r"([A-Z]{2,4}\d{3})\s+without\s+"
    r"(?:the\s+)?(?:required\s+)?"
    r"prerequisites?\s*\??\s*$",
    re.IGNORECASE,
)

_COURSE_ID = re.compile(r"^[A-Z]{2,4}\d{3}$")


def route_question(question):
    """Identify only the explicitly supported factual requests."""
    if not isinstance(question, str):
        return None

    if _HISTORY.fullmatch(question):
        return ("completed_courses", None)

    match = _PREREQUISITE.fullmatch(question)

    if match:
        return ("prerequisites", match.group(1).upper())

    return None


def _validated_course_ids(values):
    if not isinstance(values, (list, tuple)):
        raise ValueError("Invalid course evidence.")

    if not all(
        isinstance(value, str)
        and _COURSE_ID.fullmatch(value)
        for value in values
    ):
        raise ValueError("Invalid course evidence.")

    return sorted(set(values))


def completed_courses_answer(record):
    if not isinstance(record, dict):
        raise ValueError("Invalid academic record.")

    courses = _validated_course_ids(
        record.get("completed_courses")
    )

    if not courses:
        return (
            "Your synthetic academic record lists no "
            "completed courses. This does not establish "
            "whether you completed work elsewhere."
        )

    return (
        "Your synthetic academic record lists these "
        "completed courses: "
        + ", ".join(courses)
        + ". This information was retrieved for your "
        "authenticated synthetic student account."
    )


def prerequisite_answer(course_id, prerequisites, completed):
    if not _COURSE_ID.fullmatch(course_id):
        raise ValueError("Invalid requested course.")

    required = _validated_course_ids(prerequisites)
    done = set(_validated_course_ids(completed))

    if not required:
        return (
            f"{course_id} has no prerequisites listed "
            "in the synthetic course catalog. This alone "
            "does not establish full scheduling eligibility. "
            "No enrollment was performed."
        )

    missing = [course for course in required if course not in done]

    introduction = (
        "Required prerequisites are not waived by the "
        "synthetic scheduling rules. "
        f"{course_id} requires "
        + ", ".join(required)
        + ". "
    )

    if missing:
        return (
            introduction
            + "Your synthetic academic record does not "
            "show completion of "
            + ", ".join(missing)
            + ". The listed prerequisite requirement is "
            "not satisfied by the available record. "
            "No enrollment was performed."
        )

    return (
        introduction
        + "Your synthetic academic record shows all listed "
        "prerequisites completed. The prerequisite "
        "requirement is satisfied under the synthetic "
        "academic rules. This does not by itself confirm "
        "section availability, schedule compatibility, "
        "or enrollment. No enrollment was performed."
    )
