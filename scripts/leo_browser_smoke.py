"""Real Chromium UI test with intercepted synthetic HTTP responses.

Does not start an authentication server, issue sessions, or call MCP.
Only exercises the original Leo browser JavaScript and DOM.
"""

import asyncio
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright, expect


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src/gateway/leo_ui"
EVIDENCE = ROOT / "docs/evidence"

CSRF = "local_browser_test_csrf_" + "x" * 32

PUBLIC = {
    "styles.css": "text/css",
    "interactive.css": "text/css",
    "leo-theme.css": "text/css",
    "unified.js": "application/javascript",
    "una-lion-mark.png": "image/png",
}


def make_cards(student_id):
    return {
        "schema_version": "leo-team-plan-v1",
        "status": "proposed_only",
        "student_id": student_id,
        "term_id": "2027SP",
        "current_registrations_checked": True,
        "options": [
            {
                "rank": 1,
                "total_credit_hours": 6,
                "registration_fit":
                    "fits_current_registration",
                "sections": [
                    {
                        "course_id": "CIS376",
                        "section_id": "SEC1001",
                        "modality": "in_person",
                        "seats_available_snapshot": 5,
                        "registration_snapshot_status":
                            "already_registered_in_snapshot",
                        "meetings": [{
                            "days": ["MON", "WED"],
                            "start": "09:30",
                            "end": "10:45",
                            "location": "Building A 101",
                        }],
                    },
                    {
                        "course_id": "CIS410",
                        "section_id": "SEC2002",
                        "modality": "online",
                        "seats_available_snapshot": 22,
                        "registration_snapshot_status":
                            "proposed_not_registered_in_snapshot",
                        "meetings": [],
                    },
                ],
            },
        ],
    }


async def run():
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    state = {
        "wrong_student": False,
        "partial": False,
        "conflict": False,
        "chat_calls": [],
        "logout_calls": 0,
        "signed_in": True,
    }

    async def intercept(route):
        request = route.request
        path = urlsplit(request.url).path

        if path == "/leo/session":
            html = (
                ASSETS / "session.html"
            ).read_text(encoding="utf-8")

            html = html.replace(
                "Authenticated Leo research interface "
                "— synthetic data only.",
                "Browser UI test — simulated session; "
                "no real authentication.",
            )

            return await route.fulfill(
                status=200,
                content_type="text/html",
                body=html,
            )

        if path.startswith("/leo-assets/"):
            name = path[len("/leo-assets/"):]

            if name not in PUBLIC:
                return await route.fulfill(status=404)

            return await route.fulfill(
                status=200,
                content_type=PUBLIC[name],
                body=(ASSETS / name).read_bytes(),
            )

        if path == "/api/student/session":
            if not state["signed_in"]:
                return await route.fulfill(
                    status=401,
                    json={
                        "detail": "Session authentication required."
                    },
                )
            return await route.fulfill(
                status=200,
                json={
                    "authenticated": True,
                    "student_id": "S10001",
                    "csrf_token": CSRF,
                    "synthetic_data": True,
                },
            )

        if path == "/api/student/session/chat":
            if not state["signed_in"]:
                return await route.fulfill(
                    status=401,
                    json={
                        "detail": "Session authentication required."
                    },
                )
            body = json.loads(request.post_data or "{}")
            csrf = request.headers.get("x-csrf-token")

            if csrf != CSRF:
                return await route.fulfill(
                    status=403,
                    json={"detail": "CSRF denied"},
                )

            assert set(body) == {"question"}
            state["chat_calls"].append(body["question"])

            if state["conflict"]:
                return await route.fulfill(
                    status=409,
                    json={"detail": "UNTRUSTED_CONFLICT_BODY"},
                )

            student = (
                "S10002"
                if state["wrong_student"]
                else "S10001"
            )

            cards = make_cards(student)
            if state["partial"]:
                cards.update(requested_courses=["CIS376", "CIS410"], proposal_completeness="partial",
                    excluded_courses=[{"course_id": "CIS376", "code": "NO_SECTION_MATCHES_PREFERENCES",
                        "reason": "No open section satisfies the required day/time restrictions."}])
                cards["options"][0]["sections"] = cards["options"][0]["sections"][1:]
                cards["options"][0]["total_credit_hours"] = 3
            return await route.fulfill(
                status=200,
                json={
                    "answer":
                        "Synthetic proposal: SEC1001 "
                        "and SEC2002, 6 credit hours.",
                    "plan_cards": cards,
                },
            )

        if path == "/auth/logout":
            assert (
                request.headers.get("x-csrf-token")
                == CSRF
            )

            state["logout_calls"] += 1
            state["signed_in"] = False

            return await route.fulfill(
                status=200,
                json={"signed_out": True},
            )

        return await route.fulfill(status=404)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )

        page = await context.new_page()
        errors = []

        page.on(
            "pageerror",
            lambda error: errors.append(str(error)),
        )

        # Every request is intercepted. No live server
        # or external identity provider is contacted.
        await page.route("**/*", intercept)

        await page.goto(
            "http://leo.browser.test/leo/session",
            wait_until="networkidle",
        )

        print("=== VERIFY SESSION BOOTSTRAP ===")

        await expect(
            page.locator("#session-status")
        ).to_contain_text("Signed in: S10001")

        assert await page.locator(
            "img[data-brand-lion]"
        ).evaluate(
            "(img) => img.complete && img.naturalWidth > 0"
        )

        print("LEO_LOGO_AND_SESSION_RENDERED")

        print("=== VERIFY CHAT AND SCHEDULE CARDS ===")

        await page.locator("#message").fill(
            "Plan CIS376 and CIS410"
        )

        await expect(
            page.locator("#send")
        ).to_be_enabled()

        await page.locator("#send").click()

        await expect(
            page.get_by_text(
                "Verified synthetic schedule proposals"
            )
        ).to_be_visible()

        await expect(
            page.locator(".verified-section")
        ).to_have_count(2)

        await expect(
            page.locator("#feedback")
        ).to_contain_text("Nothing was enrolled")

        assert state["chat_calls"] == [
            "Plan CIS376 and CIS410"
        ]

        await page.screenshot(
            path=str(
                EVIDENCE /
                "2026-11-02-step80-leo-desktop.png"
            ),
            full_page=True,
        )

        print("LEO_CHAT_AND_CARDS_RENDERED")

        print("=== VERIFY STALE SCHEDULE CONFLICT ===")
        state["conflict"] = True
        retry_question = "I can't have classes on Wednesdays either."
        await page.locator("#message").fill(retry_question)
        await page.locator("#send").click()
        await expect(page.locator("#feedback")).to_contain_text("Schedule changed.")
        await expect(page.locator(".thinking-entry")).to_have_count(0)
        await expect(page.locator("#message")).to_have_value(retry_question)
        await expect(page.locator("#send")).to_be_enabled()
        await expect(page.locator(".verified-section")).to_have_count(2)
        assert await page.get_by_text("UNTRUSTED_CONFLICT_BODY").count() == 0
        await page.screenshot(
            path=str(EVIDENCE / "2026-11-04-step134-conflict.png"),
            full_page=True,
        )
        state["conflict"] = False
        await page.locator("#send").click()
        await expect(page.locator(".verified-section")).to_have_count(4)
        await expect(page.locator("#message")).to_have_value("")
        print("LEO_CONFLICT_PRESERVES_MESSAGE_AND_RETRY_VERIFIED")

        state["partial"] = True
        await page.locator("#message").fill("No Wednesdays or Fridays")
        await page.locator("#send").click()
        latest = page.locator(".assistant-entry").last
        await expect(latest.locator(".proposal-notice")).to_contain_text("Partial proposal")
        await expect(latest.locator(".verified-exclusions")).to_contain_text("Excluded course")
        await expect(latest.locator(".verified-exclusions")).to_contain_text("CIS376")
        await expect(latest.locator(".verified-exclusions")).to_contain_text("required day/time restrictions")
        await expect(latest.locator(".verified-section")).to_have_count(1)
        assert await latest.evaluate("(el) => [...el.children].indexOf(el.querySelector('.verified-exclusions')) < [...el.children].indexOf(el.querySelector('.message-body'))")
        await page.screenshot(path=str(EVIDENCE / "partial-proposal.png"), full_page=True)
        print("DETERMINISTIC_PARTIAL_EXCLUSION_VERIFIED")
        state["partial"] = False

        print("=== VERIFY LOGOUT ===")

        await page.locator("#sign-out").click()

        await expect(
            page.locator("#session-status")
        ).to_contain_text("Signed out")

        await expect(
            page.locator("#message")
        ).to_be_disabled()

        assert state["logout_calls"] == 1

        # The intercepted session endpoint must also
        # reject subsequent requests after logout.
        await page.reload(wait_until="networkidle")

        await expect(
            page.locator("#session-status")
        ).to_contain_text("Not signed in")

        await expect(
            page.locator("#message")
        ).to_be_disabled()

        print("LEO_LOGOUT_CLEARED_SESSION_UI")

        print("=== VERIFY WRONG-STUDENT CARDS ===")

        # Reset the isolated simulated test fixture.
        # This is not a real sign-in endpoint.
        state["signed_in"] = True
        state["wrong_student"] = True

        await page.reload(wait_until="networkidle")

        await page.locator("#message").fill(
            "Plan CIS376 and CIS410"
        )

        await page.locator("#send").click()

        await expect(
            page.locator("#session-status")
        ).to_contain_text("Student identity mismatch")

        await expect(
            page.locator("#message")
        ).to_be_disabled()

        print("LEO_CROSS_STUDENT_CARDS_REJECTED")

        print("=== VERIFY MOBILE LAYOUT ===")

        state["wrong_student"] = False

        await page.set_viewport_size(
            {"width": 390, "height": 844}
        )

        await page.reload(wait_until="networkidle")

        await expect(
            page.locator("#session-status")
        ).to_contain_text("Signed in: S10001")

        await page.screenshot(
            path=str(
                EVIDENCE /
                "2026-11-02-step80-leo-mobile.png"
            ),
            full_page=True,
        )

        no_horizontal_overflow = await page.evaluate(
            "() => document.documentElement.scrollWidth "
            "<= window.innerWidth + 2"
        )

        assert no_horizontal_overflow, (
            "Mobile layout has horizontal overflow."
        )

        assert not errors, (
            "Browser JavaScript errors: " + repr(errors)
        )

        await context.close()
        await browser.close()

        print("LEO_MOBILE_LAYOUT_VERIFIED")
        print("STEP_80_REAL_BROWSER_UI_TEST_PASSED")


if __name__ == "__main__":
    asyncio.run(run())
