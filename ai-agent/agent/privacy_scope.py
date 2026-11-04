"""Narrow request-scope privacy guard.

Detect explicit requests for a different student's
academic information before any LLM or MCP call.

This does not authorize access to any record.
The authenticated identity is supplied by the agent.

Conservative coverage: additional patterns require tests.
"""

import re


_ACTION = re.compile(
    r"^\s*(?:"
    r"(?:please\s+)?"
    r"(?:show|list|display|tell|give|retrieve|fetch|"
    r"check|find|look\s+up)\b"
    r"|(?:what|which|how\s+many)\b"
    r"|(?:can|could)\s+(?:you|i)\s+"
    r"(?:show|see|access|view|retrieve|check)\b"
    r")",
    re.IGNORECASE,
)

_ACADEMIC = re.compile(
    r"\b(?:"
    r"courses?|classes?|grades?|transcripts?|"
    r"academic\s+records?|student\s+records?|"
    r"course\s+history|completed|passed|taken|"
    r"enrollments?|enrolled|registrations?|"
    r"registered|schedules?|gpa"
    r")\b",
    re.IGNORECASE,
)

_TARGETS = [
    re.compile(
        r"\bstudent\s+(S\d{5})\s+"
        r"(?:has|had|have|is|was|took|takes|"
        r"completed|passed|enrolled|registered)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(S\d{5})['’]s\s+"
        r"(?:academic\s+|student\s+|course\s+)?"
        r"(?:courses?|classes?|grades?|transcripts?|"
        r"records?|history|enrollments?|schedules?|gpa)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:for|of|from|about)\s+"
        r"(?:student\s+)?(S\d{5})\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(S\d{5})\s+"
        r"(?:has\s+)?"
        r"(?:completed|passed|taken|took|takes|enrolled)\b",
        re.IGNORECASE,
    ),
]


def other_student_record_request(
    question: str,
    authenticated_student_id: str,
) -> bool:
    """True only for a recognized foreign-record request.

    Merely mentioning a friend or classmate does
    not make a request target that person's records.
    """
    if not isinstance(question, str):
        return False

    if not _ACTION.search(question):
        return False

    if not _ACADEMIC.search(question):
        return False

    bound = authenticated_student_id.upper()

    for pattern in _TARGETS:
        for match in pattern.finditer(question):
            if match.group(1).upper() != bound:
                return True

    return False
