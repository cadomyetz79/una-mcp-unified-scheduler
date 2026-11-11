"""Regression: live Ollama follow-up, 2026-11-03.

The model supplied required_preferences containing
earliest_start but omitted the actual start time.

The student's explicit soft wording must prevail.
No live model or academic records are needed here.
"""

import pytest

from agent import constraints
from agent.preference_language import reconcile


REQUEST = (
    "Plan CIS376 and CIS410 for 2027SP. "
    "I can't have classes on Fridays. "
    "If possible, I'd prefer no classes "
    "before 10:01 AM."
)


def test_exact_live_failure_replayed():
    # Actual saved model arguments:
    # earliest_start=None
    # required_preferences=["earliest_start"]
    #
    # Since the model did not provide a time,
    # the earlier classifier has nothing to
    # reconcile at this stage.
    required, corrections = reconcile(
        REQUEST,
        stated=[],
        required=["earliest_start"],
    )

    assert required == ["earliest_start"]
    assert corrections == []

    # The final deterministic resolver must
    # recover the time, require no Fridays,
    # and discard the unsupported hard flag.
    result = constraints.resolve(
        REQUEST,
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=required,
    )

    assert result.earliest_start == "10:01"
    assert result.avoid_days == ["FRI"]
    assert result.required == ["avoid_days"]
    assert result.clarify == []

    assert any(
        change.get("preference") == "earliest_start"
        and change.get("model_value") == "required"
        and change.get("applied") == "soft"
        for change in result.changes
    )


def test_missing_soft_end_time_drops_bad_required_flag():
    request = (
        "If possible, I'd prefer to finish "
        "classes by 3:00 PM."
    )

    result = constraints.resolve(
        request,
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=["latest_end"],
    )

    assert result.latest_end == "15:00"
    assert "latest_end" not in result.required


def test_missing_soft_day_value_drops_bad_required_flag():
    request = (
        "If possible, I'd prefer no classes "
        "on Fridays."
    )

    result = constraints.resolve(
        request,
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=["avoid_days"],
    )

    assert result.avoid_days == ["FRI"]
    assert "avoid_days" not in result.required


def test_supplied_soft_time_also_remains_soft():
    request = (
        "If possible, I'd prefer no classes "
        "before 10:01 AM."
    )

    result = constraints.resolve(
        request,
        earliest_start="10:01",
        latest_end=None,
        avoid_days=[],
        required=["earliest_start"],
    )

    assert result.earliest_start == "10:01"
    assert result.required == []


def test_explicit_mandatory_start_is_preserved():
    request = (
        "I must not have classes before "
        "10:01 AM."
    )

    result = constraints.resolve(
        request,
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=["earliest_start"],
    )

    assert result.earliest_start == "10:01"
    assert "earliest_start" in result.required


def test_unqualified_start_is_not_silently_softened():
    request = "No classes before 10 AM."

    result = constraints.resolve(
        request,
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=["earliest_start"],
    )

    assert result.earliest_start == "10:00"
    assert "earliest_start" in result.required


def test_unrelated_mandatory_preference_is_preserved():
    request = (
        "I can't have classes on Fridays. "
        "If possible, I'd prefer no classes "
        "before 10:01 AM."
    )

    result = constraints.resolve(
        request,
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=["earliest_start"],
    )

    assert result.avoid_days == ["FRI"]
    assert result.earliest_start == "10:01"
    assert result.required == ["avoid_days"]


def test_unsupported_model_flag_for_unmentioned_pref_unchanged():
    # This unit test verifies the resolver only
    # changes flags backed by explicit student text.
    # The full agent separately removes model
    # preferences not mentioned in the request.
    result = constraints.resolve(
        "Plan CIS376 and CIS410.",
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=["earliest_start"],
    )

    assert result.required == ["earliest_start"]


def test_preference_strength_ablation_remains_off():
    """An ablated preference checker must not fix
    the model's incorrect soft/required decision.
    This preserves evaluation baseline semantics.
    """
    result = constraints.resolve(
        REQUEST,
        earliest_start=None,
        latest_end=None,
        avoid_days=[],
        required=["earliest_start"],
        correct_model_soft_flags=False,
    )

    # Deterministic academic values and hard day
    # protection remain active, while the optional
    # model-strength correction is disabled.
    assert result.earliest_start == "10:01"
    assert result.avoid_days == ["FRI"]
    assert result.required == [
        "avoid_days", "earliest_start"
    ]
