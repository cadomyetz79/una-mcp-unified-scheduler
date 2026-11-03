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
    signIn.hidden = Boolean(studentId);
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

  function appendMessage(who, body) {
    const entry = document.createElement("div");
    entry.className = who === "you" ? "chat-entry mine" : "chat-entry assistant-entry";
    const label = document.createElement("span");
    label.className = "message-label";
    label.textContent = who === "you" ? "You" : "Leo";
    const text = document.createElement("p");
    text.className = "message-body";
    // Never render remote JSON as HTML: all content is textContent only.
    text.textContent = body;
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
    name.textContent = label;
    const detail = document.createElement("strong");
    detail.textContent = String(value ?? "Not available");
    row.append(name, detail);
    parent.append(row);
    return row;
  }

  // Render only allowlisted, verified section metadata supplied by the
  // authenticated gateway. Never interpolate arbitrary source text as HTML.
  function addSectionDetail(parent, section) {
    if (!section || typeof section !== "object") return;
    const item = document.createElement("article");
    item.className = "verified-section";
    const header = document.createElement("div");
    header.className = "verified-section-heading";
    const name = document.createElement("strong");
    name.textContent = String(section.course_id ?? "") + " · "
      + String(section.course_title ?? "Course title unavailable");
    const badge = document.createElement("span");
    badge.className = "section-status";
    const isExisting = section.recommendation_status === "already_enrolled";
    badge.textContent = isExisting ? "Already enrolled (synthetic)" :
      "Recommended · Not enrolled";
    header.append(name, badge);

    const facts = document.createElement("p");
    facts.className = "verified-section-facts";
    const mode = {
      online: "Online",
      in_person: "In person",
      hybrid: "Hybrid"
    }[section.modality] || "Modality unavailable";
    facts.textContent = String(section.section_id ?? "Unknown section")
      + " · " + String(section.credit_hours ?? "?") + " credits"
      + " · " + mode;

    const meetings = document.createElement("p");
    meetings.className = "verified-section-meetings";
    if (Array.isArray(section.meetings) && section.meetings.length) {
      meetings.textContent = section.meetings.map((m) => {
        const days = Array.isArray(m.days) ? m.days.join(", ") : "Days unknown";
        const location = m.location ? " · " + String(m.location) : "";
        return days + " " + String(m.start_time ?? "")
          + "–" + String(m.end_time ?? "") + location;
      }).join("; ");
    } else {
      meetings.textContent = "No scheduled meeting times listed";
    }
    item.append(header, facts, meetings);
    parent.append(item);
  }

  function showResult(payload) {
    if (!payload || payload.synthetic_data !== true || payload.enrollment_performed !== false) {
      appendMessage("assistant", "The response did not meet the synthetic research safety contract.");
      return;
    }
    const plan = payload.plan;
    if (plan && plan.student_id !== studentId) {
      resetSession("Student identity mismatch; sign in again.");
      setFeedback("The response could not be shown safely.");
      return;
    }
    const wrapper = appendMessage("assistant", plan
      ? "Here is the verified synthetic schedule proposal. No registration was performed."
      : "Here is the available synthetic policy information. No schedule was generated.");

    if (plan) {
      const details = document.createElement("div");
      details.className = "result-details";
      addField(details, "Term", plan.term_id);
      addField(details, "Student", plan.student_id);
      addField(details, "Requested credits", plan.requested_credit_hours);
      addField(details, "Verified proposed credits", plan.resulting_credit_hours);
      addField(details, "Target achieved", plan.target_met === true ? "Yes" : "No");
      const requested = plan.requested_credit_hours;
      const verified = plan.resulting_credit_hours;
      if (plan.target_met === false && Number.isInteger(requested)
        && Number.isInteger(verified) && requested > verified && verified >= 0) {
        const shortfall = addField(
          details, "Additional credits needed", String(requested - verified)
        );
        shortfall.classList.add("credit-shortfall");
      }
      addField(details, "Newly recommended sections", Array.isArray(plan.proposed_section_ids)
        ? plan.proposed_section_ids.join(", ") || "None"
        : "Not available");
      addField(details, "Full proposed schedule", Array.isArray(plan.full_section_ids)
        ? plan.full_section_ids.join(", ") || "None"
        : "Not available");
      wrapper.append(details);

      if (plan.section_details_version === "una-verified-section-details-v1"
        && Array.isArray(plan.section_details) && plan.section_details.length) {
        const heading = document.createElement("p");
        heading.className = "sources-heading";
        heading.textContent = "Verified synthetic course details";
        const sectionList = document.createElement("div");
        sectionList.className = "verified-section-list";
        for (const section of plan.section_details.slice(0, 35)) {
          addSectionDetail(sectionList, section);
        }
        wrapper.append(heading, sectionList);
      }
    }
    if (Array.isArray(payload.knowledge_sources) && payload.knowledge_sources.length) {
      const heading = document.createElement("p");
      heading.className = "sources-heading";
      heading.textContent = "Policy evidence";
      wrapper.append(heading);
      for (const hit of payload.knowledge_sources.slice(0, 5)) {
        const source = document.createElement("div");
        source.className = "source-result";
        const title = document.createElement("strong");
        title.textContent = String(hit.title ?? "Synthetic source");
        const excerpt = document.createElement("p");
        excerpt.textContent = String(hit.excerpt ?? "");
        source.append(title, excerpt);
        if (typeof hit.source_id === "string" && hit.source_id.trim()) {
          const reference = document.createElement("p");
          reference.className = "source-reference";
          reference.textContent = "Source ID: " + hit.source_id;
          source.append(reference);
        }
        wrapper.append(source);
      }
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
        setFeedback("Sign in through the configured identity provider to continue.");
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
        body: JSON.stringify({ message: text }),
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
  form.addEventListener("submit", submitMessage);
  signOut.addEventListener("click", logout);
  bootstrap();
})();
