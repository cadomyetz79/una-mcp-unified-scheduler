"use strict";

const form = document.getElementById("chat-form");
const input = document.getElementById("question");
const sendButton = document.getElementById("send-button");
const conversation = document.getElementById("conversation");
const status = document.getElementById("request-status");

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = String(text);
  return node;
}

function showMessage(kind, text, cards) {
  const welcome = conversation.querySelector(".welcome");
  if (welcome) welcome.remove();

  const wrapper = element("article", "message " + kind);
  wrapper.appendChild(
    element("div", "message-label",
      kind === "user" ? "You" : "Scheduling Assistant")
  );
  wrapper.appendChild(element("p", "message-text", text));

  if (kind === "assistant" && cards) {
    renderCards(wrapper, cards);
  }

  conversation.appendChild(wrapper);
  conversation.scrollTop = conversation.scrollHeight;
}

function renderCards(container, cards) {
  if (
    !cards ||
    cards.schema_version !== "leo-team-plan-v1" ||
    cards.status !== "proposed_only" ||
    !Array.isArray(cards.options)
  ) return;

  const group = element("section", "plan-group");
  group.appendChild(
    element("div", "plan-heading",
      "Verified schedule proposals · " + String(cards.term_id || ""))
  );

  for (const option of cards.options.slice(0, 10)) {
    if (!option || !Array.isArray(option.sections)) continue;

    const card = element("div", "plan-card");
    card.appendChild(
      element("div", "plan-title",
        "Option " + String(option.rank))
    );
    card.appendChild(
      element("div", "plan-meta",
        String(option.total_credit_hours) +
        " credit hours · " +
        String(option.registration_fit || "Registration not verified"))
    );

    for (const section of option.sections.slice(0, 12)) {
      if (!section) continue;

      const row = element("div", "section");
      row.appendChild(
        element("div", "section-title",
          String(section.course_id || "") + " · " +
          String(section.section_id || ""))
      );

      const details = [
        String(section.modality || "Mode not specified"),
        String(section.seats_available_snapshot ?? "?") +
          " seats in snapshot",
        String(section.registration_snapshot_status || "not_checked"),
      ];

      row.appendChild(
        element("div", "section-detail", details.join(" · "))
      );

      if (Array.isArray(section.meetings)) {
        for (const meeting of section.meetings.slice(0, 14)) {
          if (!meeting) continue;

          const days = Array.isArray(meeting.days)
            ? meeting.days.join("/")
            : "";

          row.appendChild(
            element("div", "section-detail",
              days + " " +
              String(meeting.start || "") + "–" +
              String(meeting.end || "") + " " +
              String(meeting.location || ""))
          );
        }
      }

      card.appendChild(row);
    }

    group.appendChild(card);
  }

  if (group.children.length > 1) container.appendChild(group);
}

function errorMessage(code) {
  if (code === 401) {
    return "Student sign-in is required. Approved authentication is not connected to this preview.";
  }
  if (code === 403) {
    return "Your account is not authorized to access these academic records.";
  }
  if (code === 503) {
    return "The scheduling service is not currently available.";
  }
  if (code === 422) {
    return "Please provide a valid scheduling question.";
  }
  return "The request could not be completed.";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = input.value.trim();
  if (!question || sendButton.disabled) return;

  showMessage("user", question);
  input.value = "";
  sendButton.disabled = true;
  status.textContent = "Contacting the scheduling gateway…";

  try {
    // Same-origin only. No token storage or demo credential bypass.
    // The existing gateway currently requires an authorized bearer token.
    // Approved browser authentication must be integrated separately.
    const response = await fetch("/api/chat", {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      showMessage("assistant", errorMessage(response.status));
      status.textContent = "Request not completed.";
      return;
    }

    const data = await response.json();
    if (!data || typeof data.answer !== "string") {
      throw new Error("Invalid gateway response");
    }

    showMessage("assistant", data.answer, data.plan_cards);
    status.textContent = "Response received. No enrollment performed.";
  } catch {
    showMessage(
      "assistant",
      "The gateway could not complete the request."
    );
    status.textContent = "Connection unavailable.";
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
