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

    if any(key in cards for key in (
        "requested_courses", "excluded_courses", "proposal_completeness",
    )):
        # The model-visible planner trace intentionally omits student_id
        # and registered section IDs. Do not reproject it as a full
        # identity-bearing plan. Identity was checked against the trusted
        # server session above; compare only the additive metadata here.
        requested_courses = data.get("requested")
        raw_excluded = data.get("excluded")
        if (
            type(requested_courses) is not list
            or not requested_courses
            or any(type(x) is not str for x in requested_courses)
            or len(set(requested_courses)) != len(requested_courses)
            or type(raw_excluded) is not list
            or type(cards.get("requested_courses")) is not list
            or cards["requested_courses"] != requested_courses
            or type(cards.get("excluded_courses")) is not list
        ):
            return None

        reasons = {
            "UNKNOWN_COURSE": "Course not found in the catalog snapshot.",
            "NO_SECTIONS_IN_TERM": "No sections offered in the selected term.",
            "ALL_SECTIONS_FULL": "All sections are full in the seat snapshot.",
            "NO_SECTION_MATCHES_PREFERENCES": "No open section satisfies the required day/time restrictions.",
            "ALREADY_COMPLETED": "Course already completed in the academic snapshot.",
            "MISSING_PREREQUISITE": "Required prerequisite is missing in the academic snapshot.",
        }

        expected_exclusions = []
        seen = set()
        for item in raw_excluded:
            if type(item) is not dict:
                return None
            cid = item.get("course_id")
            code = item.get("code")
            if (
                type(cid) is not str
                or cid not in requested_courses
                or type(code) is not str
                or code not in reasons
                or (cid, code) in seen
            ):
                return None
            seen.add((cid, code))
            expected_exclusions.append({
                "course_id": cid,
                "code": code,
                "reason": reasons[code],
            })

        if cards["excluded_courses"] != expected_exclusions:
            return None

        expected_completeness = (
            "partial" if expected_exclusions else "complete"
        )
        if cards.get("proposal_completeness") != expected_completeness:
            return None

        requested_ids = set(requested_courses)
        excluded_ids = {x["course_id"] for x in expected_exclusions}
        for option in cards["options"]:
            if (
                type(option) is not dict
                or type(option.get("sections")) is not list
            ):
                return None
            proposed_ids = set()
            for section in option["sections"]:
                if (
                    type(section) is not dict
                    or type(section.get("course_id")) is not str
                ):
                    return None
                proposed_ids.add(section["course_id"])
            if (
                proposed_ids & excluded_ids
                or proposed_ids | excluded_ids != requested_ids
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


# This is intentionally narrow. A full-string match
# prevents unrelated instructions from being silently
# combined with prior academic context.
_START_FOLLOWUP = re.compile(
    r"^\s*(?:actually[,\s]+)?"
    r"(?:i(?:'d| would)?\s+prefer)\s+"
    r"(?:classes|a\s+schedule)(?:\s+that)?\s+"
    r"(?:start|starts|starting)\s+"
    r"(?P<mode>after|at)\s+"
    r"(?P<hour>0?[1-9]|1[0-2])"
    r"(?::(?P<minute>[0-5]\d))?\s*"
    r"(?P<ampm>a\.?m\.?|p\.?m\.?)"
    r"(?:[,.]?\s*keep\s+everything\s+else\s+"
    r"the\s+same)?[.!?]?\s*$",
    re.IGNORECASE,
)

_WEEKDAY_NAMES = {
    "MON": "Mondays",
    "TUE": "Tuesdays",
    "WED": "Wednesdays",
    "THU": "Thursdays",
    "FRI": "Fridays",
    "SAT": "Saturdays",
    "SUN": "Sundays",
}


def _display_time(value: str) -> str:
    hour, minute = map(int, value.split(":"))
    suffix = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:{minute:02d} {suffix}"


def resolve_start_time_followup(
    question: str,
    context: PlanContext | None,
    *,
    expected_term_id: str,
) -> str | None:
    """Construct a new request from a narrow follow-up.

    Returns None if the wording or context cannot
    be interpreted reliably.

    The returned request still needs all normal
    authenticated MCP and planner checks.

    This helper does not access academic records.
    """
    if (
        type(context) is not PlanContext
        or type(question) is not str
        or len(question) > 500
        or context.term_id != expected_term_id
    ):
        return None

    normalized_question = question.replace("’", "'")
    match = _START_FOLLOWUP.fullmatch(
        normalized_question
    )

    if match is None:
        return None

    # The planner represents only one earliest-start
    # preference. Do not replace an earlier hard
    # constraint with a new soft preference.
    if "earliest_start" in context.required_preferences:
        return None

    hour = int(match.group("hour"))
    minute = int(match.group("minute") or "0")

    if match.group("ampm").lower().startswith("p"):
        if hour != 12:
            hour += 12
    elif hour == 12:
        hour = 0

    new_minutes = hour * 60 + minute

    # "After 10" excludes exactly 10:00.
    # "At 10" permits 10:00.
    if match.group("mode").lower() == "after":
        new_minutes += 1

    if not 7 * 60 <= new_minutes <= 18 * 60:
        return None

    start = (
        f"{new_minutes // 60:02d}:"
        f"{new_minutes % 60:02d}"
    )

    # Build a normalized scheduling request using
    # only fields from trusted PlanContext and the
    # explicitly recognized follow-up time.
    parts = [
        "Plan " + " and ".join(context.course_ids)
        + f" for {context.term_id}."
    ]

    if context.avoid_days:
        mandatory = (
            "avoid_days" in context.required_preferences
        )

        for day in context.avoid_days:
            name = _WEEKDAY_NAMES[day]

            if mandatory:
                parts.append(
                    f"I can't have classes on {name}."
                )
            else:
                parts.append(
                    "If possible, I'd prefer no classes "
                    f"on {name}."
                )

    if context.latest_end is not None:
        end = _display_time(context.latest_end)

        if (
            "latest_end"
            in context.required_preferences
        ):
            parts.append(
                f"I must be done with classes by {end}."
            )
        else:
            parts.append(
                "If possible, I'd prefer to finish "
                f"classes by {end}."
            )

    parts.append(
        "If possible, I'd prefer no classes "
        f"before {_display_time(start)}."
    )

    rewritten = " ".join(parts)

    if len(rewritten) > 4000:
        return None

    return rewritten


# Narrow continuation: add one mandatory weekday.
# This does not interpret unrestricted conversation.
_ADD_DAY_FOLLOWUP = re.compile(
    r"^\s*(?:actually[,\s]+)?"
    r"i\s+(?:can't|cannot|can\s+not)\s+"
    r"have\s+classes\s+on\s+"
    r"(?P<day>mondays?|tuesdays?|wednesdays?|"
    r"thursdays?|fridays?|saturdays?|sundays?)"
    r"(?:\s+either)?"
    r"(?:[,.]?\s*keep\s+everything\s+else\s+the\s+same)?"
    r"[.!?]?\s*$",
    re.IGNORECASE,
)

_DAY_CODES = {
    "monday": "MON",
    "tuesday": "TUE",
    "wednesday": "WED",
    "thursday": "THU",
    "friday": "FRI",
    "saturday": "SAT",
    "sunday": "SUN",
}

_NEW_SCHEDULE = re.compile(
    r"^\s*start\s+a\s+new\s+schedule\s*:\s*"
    r"plan\s+(?P<courses>[A-Z]{2,4}\d{3}"
    r"(?:\s+and\s+[A-Z]{2,4}\d{3}){0,7})"
    r"(?:\s+for\s+(?P<term>20\d{2}(?:SP|SU|FA)))?"
    r"[.!]?\s*$",
    re.IGNORECASE,
)


def _added_day_code(question: str) -> str | None:
    if type(question) is not str or len(question) > 500:
        return None

    match = _ADD_DAY_FOLLOWUP.fullmatch(
        question.replace("’", "'")
    )
    if match is None:
        return None

    return _DAY_CODES.get(
        match.group("day").lower().removesuffix("s")
    )


def resolve_add_day_followup(
    question: str,
    context: PlanContext | None,
    *,
    expected_term_id: str,
) -> str | None:
    """Reconstruct a day addition from trusted context.

    A previous soft day preference cannot be merged
    with a mandatory day using the present schema.
    That unsupported case is rejected.
    """
    if (
        type(context) is not PlanContext
        or context.term_id != expected_term_id
    ):
        return None

    added = _added_day_code(question)
    if added is None or added in context.avoid_days:
        return None

    if (
        context.avoid_days
        and "avoid_days" not in context.required_preferences
    ):
        return None

    days = set(context.avoid_days) | {added}

    parts = [
        "Plan " + " and ".join(context.course_ids)
        + f" for {context.term_id}."
    ]

    for code, name in _WEEKDAY_NAMES.items():
        if code in days:
            parts.append(
                f"I can't have classes on {name}."
            )

    if context.earliest_start is not None:
        start = _display_time(context.earliest_start)
        if "earliest_start" in context.required_preferences:
            parts.append(
                f"I can't have classes before {start}."
            )
        else:
            parts.append(
                "If possible, I'd prefer no classes "
                f"before {start}."
            )

    if context.latest_end is not None:
        end = _display_time(context.latest_end)
        if "latest_end" in context.required_preferences:
            parts.append(
                f"I must be done with classes by {end}."
            )
        else:
            parts.append(
                "If possible, I'd prefer to finish "
                f"classes by {end}."
            )

    rewritten = " ".join(parts)
    return rewritten if len(rewritten) <= 4000 else None


def continuation_cards_safe(
    *,
    original_question: str,
    prior_context: PlanContext | None,
    resolved_question: str | None,
    candidate_context: PlanContext | None,
) -> bool:
    """Check continuity before cards are shown or saved."""

    # A fresh first-turn plan has no prior context.
    if prior_context is None:
        return True

    if (
        type(candidate_context) is not PlanContext
        or type(original_question) is not str
    ):
        return False

    # Explicit reset is distinct from a follow-up.
    reset = _NEW_SCHEDULE.fullmatch(original_question)
    if reset:
        courses = tuple(
            re.split(r"\s+and\s+", reset.group("courses").upper(),
                     flags=re.IGNORECASE)
        )
        term = (reset.group("term") or prior_context.term_id).upper()
        return (
            candidate_context.course_ids == courses
            and candidate_context.term_id == term
            and not candidate_context.avoid_days
            and candidate_context.earliest_start is None
            and candidate_context.latest_end is None
            and not candidate_context.required_preferences
        )

    if resolved_question is None:
        return False

    if (
        candidate_context.term_id != prior_context.term_id
        or candidate_context.course_ids
        != prior_context.course_ids
        or candidate_context.latest_end
        != prior_context.latest_end
    ):
        return False

    old_required = set(
        prior_context.required_preferences
    )
    new_required = set(
        candidate_context.required_preferences
    )

    start_request = resolve_start_time_followup(
        original_question,
        prior_context,
        expected_term_id=prior_context.term_id,
    )

    if (
        start_request is not None
        and start_request == resolved_question
    ):
        # Start time is the only field this form
        # of continuation is allowed to change.
        if (
            set(candidate_context.avoid_days)
            != set(prior_context.avoid_days)
            or new_required != old_required
            or candidate_context.earliest_start is None
        ):
            return False

        match = re.search(
            r"before (\d{1,2}:\d{2} [AP]M)\.$",
            start_request,
        )

        return bool(
            match
            and _display_time(
                candidate_context.earliest_start
            ) == match.group(1)
        )

    day_request = resolve_add_day_followup(
        original_question,
        prior_context,
        expected_term_id=prior_context.term_id,
    )

    if (
        day_request is None
        or day_request != resolved_question
    ):
        return False

    added = _added_day_code(original_question)
    if added is None:
        return False

    expected_days = set(prior_context.avoid_days)
    expected_days.add(added)

    return (
        set(candidate_context.avoid_days)
        == expected_days
        and new_required
        == old_required | {"avoid_days"}
        and candidate_context.earliest_start
        == prior_context.earliest_start
    )
