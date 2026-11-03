"""Proposed OCR -> advising handoff for SYNTHETIC transcript observations.

This is a boundary/contract, NOT an OCR engine, a transcript parser or a
Banner record updater. All OCR observations remain unverified evidence.
It rejects raw text, personally identifying fields and unknown fields;
the trusted gateway must resolve the student identity independently.

The interface intentionally stays separate from PublicKnowledgeRetriever:
student transcripts must never enter public-policy RAG by default.
"""

from dataclasses import dataclass
import math
import re
from collections.abc import Mapping


SCHEMA_VERSION = "una-synthetic-ocr-handoff-v1"
STUDENT_ID = re.compile(r"S[0-9]{5}\Z")
DOCUMENT_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}\Z")
COURSE_ID = re.compile(r"[A-Z]{2,8}[ -]?[0-9]{3,4}[A-Z]?\Z")
TERM_ID = re.compile(r"(?:19|20)[0-9]{2}(?:SP|SU|FA)\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GRADES = frozenset({
    "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-",
    "D+", "D", "D-", "F", "P", "NP", "S", "U", "W",
    "I", "IP", "TR",
})
TOP_LEVEL = frozenset({
    "schema_version", "synthetic_data", "student_id", "document_id",
    "source_sha256", "page_count", "courses",
})
COURSE_FIELDS = frozenset({
    "course_id", "term_id", "grade", "source_page", "confidence",
})


@dataclass(frozen=True)
class OCRCourseFinding:
    """A single OCR observation, never an authoritative grade record."""

    course_id: str
    term_id: str
    grade: str
    source_page: int
    confidence: float


@dataclass(frozen=True)
class SyntheticTranscriptHandoff:
    """Validated evidence from a synthetic source only."""

    student_id: str
    document_id: str
    source_sha256: str
    page_count: int
    courses: tuple[OCRCourseFinding, ...]

    @property
    def authoritative(self) -> bool:
        """A handoff cannot establish completed credits or prerequisites."""
        return False

    @property
    def needs_manual_review(self) -> bool:
        """Conservative provisional threshold, not a validated OCR metric."""
        return any(finding.confidence < 0.90 for finding in self.courses)


def _required_text(data: Mapping, key: str, pattern: re.Pattern) -> str:
    value = data.get(key)
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"Invalid OCR handoff field: {key}.")
    return value


def validate_synthetic_ocr_handoff(
    payload: Mapping,
    *,
    expected_student_id: str,
) -> SyntheticTranscriptHandoff:
    """Fail closed on malformed, misbound or unprovenanced OCR evidence.

    `expected_student_id` must come from a verified application session;
    never pass an AI-chosen or transcript-claimed identity as authority.
    """
    if (
        type(expected_student_id) is not str
        or STUDENT_ID.fullmatch(expected_student_id) is None
    ):
        raise ValueError("Trusted student identity required.")

    if not isinstance(payload, dict) or set(payload) != TOP_LEVEL:
        raise ValueError("Invalid OCR handoff fields.")

    if (
        payload["schema_version"] != SCHEMA_VERSION
        or payload["synthetic_data"] is not True
    ):
        raise ValueError("Only versioned synthetic OCR evidence is supported.")

    student_id = _required_text(payload, "student_id", STUDENT_ID)
    if student_id != expected_student_id:
        raise PermissionError("OCR evidence is not bound to this student.")

    document_id = _required_text(payload, "document_id", DOCUMENT_ID)
    source_hash = _required_text(payload, "source_sha256", SHA256)
    page_count = payload["page_count"]
    if type(page_count) is not int or not 1 <= page_count <= 200:
        raise ValueError("Invalid OCR source page count.")

    entries = payload["courses"]
    if type(entries) is not list or not 1 <= len(entries) <= 100:
        raise ValueError("Invalid OCR course observations.")

    findings = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != COURSE_FIELDS:
            raise ValueError("Invalid OCR course fields.")
        course_id = _required_text(entry, "course_id", COURSE_ID)
        term_id = _required_text(entry, "term_id", TERM_ID)
        grade = entry["grade"]
        if type(grade) is not str or grade not in GRADES:
            raise ValueError("Invalid OCR grade.")
        page = entry["source_page"]
        confidence = entry["confidence"]
        if type(page) is not int or not 1 <= page <= page_count:
            raise ValueError("Invalid OCR source page.")
        if (
            type(confidence) not in (int, float)
            or not math.isfinite(confidence)
            or not 0 <= confidence <= 1
        ):
            raise ValueError("Invalid OCR confidence.")

        observation = (course_id, term_id, grade, page)
        if observation in seen:
            raise ValueError("Duplicate OCR observation.")
        seen.add(observation)
        findings.append(OCRCourseFinding(
            course_id=course_id,
            term_id=term_id,
            grade=grade,
            source_page=page,
            confidence=float(confidence),
        ))

    return SyntheticTranscriptHandoff(
        student_id=student_id,
        document_id=document_id,
        source_sha256=source_hash,
        page_count=page_count,
        courses=tuple(findings),
    )
