"""Validated scheduling context for a browser session.

Only trusted server code should construct this from
verified planner evidence. Never accept this structure
directly from a browser or language-model response.

No tokens, student records, tool traces, or raw chat text.
"""

from dataclasses import dataclass
import re


_TERM = re.compile(r"20[0-9]{2}(SP|SU|FA)")
_COURSE = re.compile(r"[A-Z]{2,4}[0-9]{3}")
_TIME = re.compile(r"([01][0-9]|2[0-3]):[0-5][0-9]")

_DAYS = frozenset({
    "MON", "TUE", "WED", "THU",
    "FRI", "SAT", "SUN",
})

_PREFERENCES = frozenset({
    "avoid_days",
    "earliest_start",
    "latest_end",
})


@dataclass(frozen=True)
class PlanContext:
    """Small, immutable snapshot of validated plan inputs."""

    term_id: str
    course_ids: tuple[str, ...]
    avoid_days: tuple[str, ...] = ()
    earliest_start: str | None = None
    latest_end: str | None = None
    required_preferences: tuple[str, ...] = ()

    def __post_init__(self):
        if (
            type(self.term_id) is not str
            or not _TERM.fullmatch(self.term_id)
        ):
            raise ValueError("Invalid term.")

        if (
            type(self.course_ids) is not tuple
            or not 1 <= len(self.course_ids) <= 8
            or any(
                type(course) is not str
                or not _COURSE.fullmatch(course)
                for course in self.course_ids
            )
            or len(set(self.course_ids))
            != len(self.course_ids)
        ):
            raise ValueError("Invalid course identifiers.")

        if (
            type(self.avoid_days) is not tuple
            or len(self.avoid_days) > 7
            or any(
                type(day) is not str
                or day not in _DAYS
                for day in self.avoid_days
            )
            or len(set(self.avoid_days))
            != len(self.avoid_days)
        ):
            raise ValueError("Invalid avoided days.")

        for value in (
            self.earliest_start,
            self.latest_end,
        ):
            if value is not None and (
                type(value) is not str
                or not _TIME.fullmatch(value)
            ):
                raise ValueError("Invalid time preference.")

        if (
            type(self.required_preferences) is not tuple
            or len(self.required_preferences) > 3
            or any(
                type(preference) is not str
                or preference not in _PREFERENCES
                for preference in self.required_preferences
            )
            or len(set(self.required_preferences))
            != len(self.required_preferences)
        ):
            raise ValueError("Invalid mandatory preferences.")

        specified = {
            "avoid_days": bool(self.avoid_days),
            "earliest_start": self.earliest_start is not None,
            "latest_end": self.latest_end is not None,
        }

        if any(
            not specified[preference]
            for preference in self.required_preferences
        ):
            raise ValueError(
                "Mandatory preference has no specified value."
            )


def from_verified_planner_result(
    result,
    *,
    expected_student_id: str,
    expected_term_id: str,
) -> PlanContext | None:
    """Project authenticated planner evidence into context.

    Input must come from the trusted scheduling runner.
    Never call with browser JSON or standalone LLM prose.

    Reject incomplete, inconsistent or multiple plans.
    """
    if (
        getattr(result, "stopped_reason", None) != "answered"
        or getattr(result, "grounded", None) is not True
        or getattr(result, "answer_source", None)
        not in ("model", "model+system_note")
        or getattr(result, "blocked", None)
        or getattr(result, "evidence_missing", None)
    ):
        return None

    cards = getattr(result, "plan_cards", None)

    if (
        type(cards) is not dict
        or cards.get("schema_version") != "leo-team-plan-v1"
        or cards.get("status") != "proposed_only"
        or cards.get("student_id") != expected_student_id
        or cards.get("term_id") != expected_term_id
        or type(cards.get("options")) is not list
        or not cards["options"]
    ):
        return None

    trace = getattr(result, "trace", None)

    if type(trace) is not list:
        return None

    plans = [
        entry for entry in trace
        if getattr(entry, "tool", None) == "plan_schedule"
    ]

    # A retry or a failed plan must not overwrite
    # previously verified session context.
    if (
        len(plans) != 1
        or getattr(plans[0], "ok", None) is not True
    ):
        return None

    entry = plans[0]
    data = getattr(entry, "result", None)
    args = getattr(entry, "arguments", None)

    if (
        type(data) is not dict
        or type(args) is not dict
        or data.get("term_id") != expected_term_id
        or type(data.get("requested")) is not list
        or type(args.get("course_ids")) is not list
        or type(data.get("options")) is not list
        or type(data.get("preferences_applied")) is not dict
    ):
        return None

    requested = data["requested"]
    supplied = args["course_ids"]

    if (
        not requested
        or any(type(x) is not str for x in requested)
        or any(type(x) is not str for x in supplied)
    ):
        return None

    normalized = [
        x.strip().upper().replace(" ", "")
        for x in supplied
    ]

    if normalized != requested:
        return None

    if len(data["options"]) != len(cards["options"]):
        return None

    # Cross-check the displayed verified sections
    # against the successful planner's output.
    for raw, displayed in zip(
        data["options"], cards["options"]
    ):
        if (
            type(raw) is not dict
            or type(displayed) is not dict
            or type(raw.get("sections")) is not list
            or type(displayed.get("sections")) is not list
            or not raw["sections"]
        ):
            return None

        def pairs(sections):
            output = []
            for section in sections:
                if type(section) is not dict:
                    return None
                cid = section.get("course_id")
                sid = section.get("section_id")
                if type(cid) is not str or type(sid) is not str:
                    return None
                output.append((cid, sid))
            return output

        original = pairs(raw["sections"])
        shown = pairs(displayed["sections"])

        if (
            original is None
            or shown is None
            or original != shown
            or any(cid not in requested for cid, _ in shown)
        ):
            return None

    preferences = data["preferences_applied"]

    days = preferences.get("avoid_days")
    required = preferences.get("required")

    if type(days) is not list or type(required) is not list:
        return None

    try:
        return PlanContext(
            term_id=expected_term_id,
            course_ids=tuple(requested),
            avoid_days=tuple(days),
            earliest_start=preferences.get("earliest_start"),
            latest_end=preferences.get("latest_end"),
            required_preferences=tuple(required),
        )
    except (TypeError, ValueError):
        return None
