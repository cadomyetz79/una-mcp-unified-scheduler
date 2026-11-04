"use strict";

// Authenticated research UI only. All access tokens stay in the Python server.
// This file is NOT loaded by the default offline visual preview (/chat).
// The only browser-held auth proof is the HttpOnly session cookie (automatic)
// and a volatile CSRF token returned by the same-origin session bootstrap.
(() => {
  const status = document.getElementById("session-status");
  const signIn = document.getElementById("sign-in");
  const signOut = document.getElementById("sign-out");
  const transcript = document.getElementById("transcript");
  const form = document.getElementById("chat-form");
  const message = document.getElementById("message");
  const send = document.getElementById("send");
  const feedback = document.getElementById("feedback");
  const count = document.getElementById("char-count");
  const suggestions = [...document.querySelectorAll("[data-prompt]")];

  let csrfToken = null;
  let studentId = null;
  let working = false;

  function setFeedback(text) {
    feedback.textContent = text;
  }

  function setControls() {
    const enabled = Boolean(studentId && csrfToken && !working);
    message.disabled = !enabled;
    send.disabled = !enabled || !message.value.trim();
    send.firstChild.textContent = working ? "Working…" : (studentId ? "Send " : "Sign-in required ");
    signIn.hidden = true;
    signOut.hidden = !studentId;
    signOut.disabled = working;
    for (const suggestion of suggestions) {
      suggestion.disabled = !enabled;
    }
    count.textContent = String(message.value.length) + " / 500";
  }

  function resetSession(text) {
    studentId = null;
    csrfToken = null;
    working = false;
    status.textContent = text;
    transcript.replaceChildren();
    const notice = document.createElement("p");
    notice.className = "empty-message";
    notice.textContent = "Sign in to request a synthetic semester plan.";
    transcript.append(notice);
    setControls();
  }

  // Limited display formatting. Never interpret model HTML.
  // Only DOM text nodes and fixed elements are created.
  function appendSafeInline(parent, value) {
    const pattern = /\*\*([^*\n]{1,200})\*\*/g;
    let offset = 0;
    let match;

    while ((match = pattern.exec(value)) !== null) {
      parent.append(
        document.createTextNode(
          value.slice(offset, match.index)
        )
      );

      const strong = document.createElement("strong");
      strong.textContent = match[1];
      parent.append(strong);
      offset = pattern.lastIndex;
    }

    parent.append(
      document.createTextNode(value.slice(offset))
    );
  }

  function renderSafeReply(parent, raw) {
    const original = String(raw ?? "");

    // Bound the amount of DOM generated per response.
    const lines = original.split(/\r?\n/);
    if (original.length > 20000 || lines.length > 250) {
      parent.textContent = original;
      return;
    }

    // Normalize only the escapes observed in
    // local Ollama output; do not decode HTML tags.
    const normalized = original
      .replace(/(?:&#x20;|&#32;|&nbsp;)/gi, " ")
      .replace(/\\([*-])/g, "$1");

    let list = null;

    for (const rawLine of normalized.split(/\r?\n/)) {
      const line = rawLine.trim();

      if (!line) {
        list = null;
        continue;
      }

      const bullet = /^[-*]\s+(.+)$/.exec(line);

      if (bullet) {
        if (!list) {
          list = document.createElement("ul");
          parent.append(list);
        }

        const item = document.createElement("li");
        appendSafeInline(item, bullet[1]);
        list.append(item);
        continue;
      }

      list = null;
      const paragraph = document.createElement("p");
      appendSafeInline(paragraph, line);
      parent.append(paragraph);
    }
  }

  function appendMessage(who, body) {
    const entry = document.createElement("div");
    entry.className = who === "you" ? "chat-entry mine" : "chat-entry assistant-entry";
    const label = document.createElement("span");
    label.className = "message-label";
    label.textContent = who === "you" ? "You" : "Leo";
    const text = document.createElement(
      who === "you" ? "p" : "div"
    );
    text.className = "message-body";

    if (who === "you") {
      text.textContent = body;
    } else {
      renderSafeReply(text, body);
    }
    entry.append(label, text);
    transcript.append(entry);
    entry.scrollIntoView({ block: "nearest", behavior: "auto" });
    return entry;
  }

  function showThinking() {
    const entry = document.createElement("div");
    entry.className = "chat-entry assistant-entry thinking-entry";
    entry.setAttribute("role", "status");
    entry.setAttribute("aria-label", "Leo is thinking");
    const label = document.createElement("span");
    label.className = "message-label";
    label.textContent = "Leo";
    const bubble = document.createElement("div");
    bubble.className = "thinking-content";
    const dots = document.createElement("span");
    dots.className = "thinking-dots";
    dots.setAttribute("aria-hidden", "true");
    for (let index = 0; index < 3; index += 1) {
      const dot = document.createElement("span");
      dot.className = "thinking-dot";
      dots.append(dot);
    }
    bubble.append(dots);
    entry.append(label, bubble);
    transcript.append(entry);
    entry.scrollIntoView({ block: "nearest", behavior: "auto" });
    return entry;
  }

  function addField(parent, label, value) {
    const row = document.createElement("div");
    row.className = "result-row";
    const name = document.createElement("span");
    name.textContent = label + ": ";
    const detail = document.createElement("strong");
    detail.textContent = String(value ?? "Not available");
    row.append(name, detail);
    parent.append(row);
    return row;
  }

  // Render only allowlisted, verified section metadata supplied by the
  // authenticated gateway. Never interpolate arbitrary source text as HTML.

  // Team unified schedule cards are sourced only from
  // the trusted planner/projector, never model-generated HTML.
  function showUnifiedSection(parent, section) {
    if (!section || typeof section !== "object") return;

    const item = document.createElement("article");
    item.className = "verified-section";

    const heading = document.createElement("div");
    heading.className = "verified-section-heading";

    const name = document.createElement("strong");
    name.textContent =
      String(section.course_id ?? "") + " · " +
      String(section.section_id ?? "");

    const badge = document.createElement("span");
    badge.className = "section-status";

    const states = {
      already_registered_in_snapshot:
        "Registered in synthetic snapshot",
      proposed_not_registered_in_snapshot:
        "Proposed · Not registered in snapshot",
      not_checked:
        "Registration status not checked"
    };

    badge.textContent = " — " + (
      states[section.registration_snapshot_status] ||
      "Registration status not verified"
    );

    heading.append(name, badge);

    const facts = document.createElement("p");
    facts.className = "verified-section-facts";

    const mode = {
      online: "Online",
      in_person: "In person",
      hybrid: "Hybrid"
    }[section.modality] ||
      String(section.modality ?? "Mode unavailable");

    const seats = Number.isInteger(
      section.seats_available_snapshot
    )
      ? section.seats_available_snapshot
      : "Unknown";

    facts.textContent =
      mode + " · " + String(seats) +
      " seats in catalog snapshot";

    const meetings = document.createElement("p");
    meetings.className = "verified-section-meetings";

    if (
      Array.isArray(section.meetings) &&
      section.meetings.length
    ) {
      meetings.textContent = section.meetings
        .slice(0, 14)
        .filter(m => m && typeof m === "object")
        .map(m => {
          const days = Array.isArray(m.days)
            ? m.days.join(", ")
            : "Days unknown";

          const location = m.location
            ? " · " + String(m.location)
            : "";

          return days + " " +
            String(m.start ?? "") + "–" +
            String(m.end ?? "") + location;
        }).join("; ");
    } else {
      meetings.textContent =
        "No scheduled meetings listed";
    }

    item.append(heading, facts, meetings);
    parent.append(item);
  }

  function showResult(payload) {
    if (
      !payload ||
      typeof payload.answer !== "string"
    ) {
      appendMessage(
        "assistant",
        "The gateway response could not be verified."
      );
      return;
    }

    const cards = payload.plan_cards;

    if (cards !== null && cards !== undefined) {
      if (
        typeof cards !== "object" ||
        cards.student_id !== studentId
      ) {
        resetSession(
          "Student identity mismatch; sign in again."
        );
        setFeedback(
          "The response could not be shown safely."
        );
        return;
      }
    }

    const wrapper = appendMessage(
      "assistant",
      payload.answer
    );

    if (
      !cards ||
      cards.schema_version !== "leo-team-plan-v1" ||
      cards.status !== "proposed_only" ||
      !/^20[0-9]{2}(SP|SU|FA)$/.test(cards.term_id) ||
      !Array.isArray(cards.options)
    ) return;

    // Static statement based on the validated
    // proposed-only card contract, not LLM prose.
    const notice = document.createElement("p");
    notice.className = "proposal-notice";
    notice.textContent =
      "Proposed schedule — no enrollment performed.";

    wrapper.insertBefore(
      notice,
      wrapper.querySelector(".message-body")
    );

    const heading = document.createElement("p");
    heading.className = "sources-heading";
    heading.textContent =
      "Verified synthetic schedule proposals";
    wrapper.append(heading);

    const details = document.createElement("div");
    details.className = "result-details";

    addField(details, "Term", cards.term_id);
    addField(
      details,
      "Registration snapshot checked",
      cards.current_registrations_checked === true
        ? "Yes" : "No"
    );

    addField(
      details,
      "Enrollment performed",
      "No — proposals only"
    );

    wrapper.append(details);

    for (const option of cards.options.slice(0, 10)) {
      if (
        !option ||
        !Array.isArray(option.sections)
      ) continue;

      const optionBox = document.createElement("div");
      optionBox.className = "result-details";
      optionBox.style.marginTop = "12px";

      addField(
        optionBox,
        "Option",
        option.rank
      );
      addField(
        optionBox,
        "Total proposed credits",
        option.total_credit_hours
      );

      const fits = {
        fits_current_registration:
          "Fits current registration snapshot",
        requires_registration_change:
          "Requires registration change",
        not_confirmed:
          "Registration compatibility not confirmed",
        not_checked:
          "Registration compatibility not checked"
      };

      addField(
        optionBox,
        "Registration compatibility",
        fits[option.registration_fit] ??
          "Not verified"
      );

      for (
        const section of option.sections.slice(0, 12)
      ) {
        showUnifiedSection(optionBox, section);
      }

      wrapper.append(optionBox);
    }
  }

  async function bootstrap() {
    working = true;
    status.textContent = "Checking your secure session…";
    setControls();
    try {
      const response = await fetch("/api/student/session", {
        method: "GET",
        credentials: "same-origin",
        cache: "no-store",
        redirect: "error",
        headers: { Accept: "application/json" },
      });
      if (response.status === 401) {
        resetSession("Not signed in");
        setFeedback("Approved browser sign-in is not configured yet.");
        return;
      }
      if (!response.ok) throw new Error("Session status unavailable");
      const payload = await response.json();
      if (
        payload.authenticated !== true
        || !/^S\d{5}$/.test(payload.student_id)
        || typeof payload.csrf_token !== "string"
        || payload.csrf_token.length < 30
      ) {
        throw new Error("Invalid session response");
      }
      studentId = payload.student_id;
      csrfToken = payload.csrf_token;
      working = false;
      status.textContent = "Signed in: " + studentId;
      setFeedback("Signed in. Synthetic academic information only; no enrollment.");
      setControls();
    } catch {
      resetSession("Unable to verify sign-in");
      setFeedback("The secure session could not be verified. Sign in again or contact the research team.");
    }
  }

  async function submitMessage(event) {
    event.preventDefault();
    const text = message.value.trim();
    if (!studentId || !csrfToken || working || !text || text.length > 500) return;
    working = true;
    setControls();
    if (transcript.firstElementChild?.classList.contains("empty-message")) {
      transcript.replaceChildren();
    }
    appendMessage("you", text);
    const thinking = showThinking();
    setFeedback("Leo is checking the synthetic scheduling services…");
    try {
      const response = await fetch("/api/student/session/chat", {
        method: "POST",
        credentials: "same-origin",
        cache: "no-store",
        redirect: "error",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-CSRF-Token": csrfToken,
        },
        body: JSON.stringify({ question: text }),
      });
      if (response.status === 401) {
        resetSession("Session expired; sign in again.");
        setFeedback("Your secure session is no longer available.");
        return;
      }
      if (response.status === 403) {
        setFeedback("Request not authorized. The session or CSRF check may have changed; refresh and sign in again.");
        appendMessage("assistant", "I couldn't authorize that request.");
        return;
      }
      if (response.status === 400 || response.status === 422) {
        appendMessage("assistant", "This research prototype couldn't interpret that request. Try a suggested question.");
        return;
      }
      if (!response.ok) throw new Error("Academic response unavailable");
      const payload = await response.json();
      thinking.remove();
      showResult(payload);
      message.value = "";
      setFeedback("Verified proposal displayed. Nothing was enrolled.");
    } catch {
      appendMessage("assistant", "The request could not be verified. Please try again later.");
      setFeedback("Unable to complete the request.");
    } finally {
      // Also remove the bubble on 401, 403, validation errors and
      // network failures. No stale "thinking" indicator may remain.
      thinking.remove();
      working = false;
      setControls();
    }
  }

  async function logout() {
    if (!studentId || !csrfToken || working) return;
    working = true;
    setControls();
    try {
      const response = await fetch("/auth/logout", {
        method: "POST",
        credentials: "same-origin",
        cache: "no-store",
        redirect: "error",
        headers: { "X-CSRF-Token": csrfToken, Accept: "application/json" },
      });
      if (!response.ok) throw new Error("Logout failed");
      resetSession("Signed out");
      message.value = "";
      setFeedback("Your browser session was revoked.");
    } catch {
      setFeedback("Could not confirm logout. Reload and verify your session before leaving.");
    } finally {
      working = false;
      setControls();
    }
  }

  for (const option of suggestions) {
    option.addEventListener("click", () => {
      if (!studentId || working) return;
      message.value = option.dataset.prompt.slice(0, 500);
      setControls();
      message.focus();
    });
  }
  message.addEventListener("input", setControls);

  // Enter sends; Shift+Enter inserts a newline.
  // Respect IME composition and modifier keys.
  message.addEventListener("keydown", (event) => {
    if (
      event.key !== "Enter" ||
      event.shiftKey ||
      event.ctrlKey ||
      event.altKey ||
      event.metaKey ||
      event.isComposing ||
      event.keyCode === 229
    ) return;

    event.preventDefault();

    // Do not submit an empty message, repeat a
    // held key, or send while a request is active.
    if (
      event.repeat ||
      message.disabled ||
      send.disabled ||
      working
    ) return;

    // Reuse the existing authenticated form handler.
    form.requestSubmit(send);
  });

  form.addEventListener("submit", submitMessage);
  signOut.addEventListener("click", logout);
  bootstrap();
})();
