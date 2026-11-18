# Step 108 — Leo Schedule Card Verification

Date: 2026-11-03
Student: S10001 (synthetic)
Term: 2027SP
Starting checkpoint: 5d1d605

## CONFIRMED — Operator-provided browser output

The operator submitted:

"Plan CIS376 and CIS410, but I can't
have classes on Fridays."

The response displayed a prominent
proposed-only notice.

The verified cards displayed:

- Term 2027SP
- Registration snapshot checked: Yes
- Enrollment performed: No
- Option 1, six proposed credits
- Compatibility with current registration
- CIS376 / SEC1001 registered in snapshot
- CIS410 / SEC2002 proposed, not registered

The returned schedule had no Friday
meetings.

The copied output showed clearer
labels separating metadata values.

## CONFIRMED — Automated evidence

The Chromium browser regression verified:

- Proposed-only notice
- Card label readability
- Verified schedule cards
- Safe formatting and inert HTML
- Enter and Shift+Enter
- Protected MCP access
- Session revocation

Automated regression suites were also
rerun before this milestone commit.

## Limitations

The screenshot was collected by the
scripted Chromium test.

The live-model observation was supplied
by the operator as copied browser text.

The demonstration uses synthetic data,
mocked Banner services and isolated
local authentication.

No real student registration occurred.
