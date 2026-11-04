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
