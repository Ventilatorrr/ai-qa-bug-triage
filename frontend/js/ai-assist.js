// Keep the supported fields in the same relative order as both bug forms.
const aiAssistFields = [
    ["title", "title", "Title"],
    ["affected_version", "affected-version", "Affected Version"],
    ["environment", "environment", "Environment"],
    ["description", "description", "Description"],
    ["steps_to_reproduce", "steps", "Steps to Reproduce"],
    ["expected_result", "expected", "Expected Result"],
    ["actual_result", "actual", "Actual Result"],
    ["severity", "severity", "Severity"],
    ["priority", "priority", "Priority"],
    ["assignee_id", "assignee", "Assignee"]
];

function collectAiAssistContext(form, prefix) {
    const context = {};
    for (const [field, suffix] of aiAssistFields) {
        const value = form.querySelector(`#${prefix}${suffix}`).value;
        context[field] = field === "assignee_id" ? (value === "" ? null : Number(value)) : value;
    }
    return context;
}

// Nothing is stored outside this page's form session or sent by review actions.
const aiAssistSessions = new WeakMap();

function endAiAssistSession(form) {
    const session = aiAssistSessions.get(form);
    if (!session) return;
    aiAssistSessions.delete(form);
    form.removeEventListener("input", session.updateCurrentValues);
    form.removeEventListener("change", session.updateCurrentValues);
    session.pending.clear();
    session.area.replaceChildren();
    session.area.hidden = true;
    session.message.textContent = "";
    session.button.disabled = false;
}

function beginAiAssistSession(form, prefix, button, message, area) {
    endAiAssistSession(form);
    const session = {form, prefix, button, message, area, pending: new Map(), loading: false, requestId: 0};
    session.updateCurrentValues = () => {
        for (const [field, suffix] of aiAssistFields) {
            const pending = session.pending.get(field);
            if (pending) {
                pending.current.textContent = aiDisplayValue(form.querySelector(`#${prefix}${suffix}`));
            }
        }
    };
    aiAssistSessions.set(form, session);
    form.addEventListener("input", session.updateCurrentValues);
    form.addEventListener("change", session.updateCurrentValues);
    area.replaceChildren();
    area.hidden = true;
    button.disabled = false;
    message.textContent = "";
}

function isCurrentAiSession(session) {
    return aiAssistSessions.get(session.form) === session &&
        session.form.isConnected && !session.form.hidden && !session.button.hidden;
}

function aiDisplayValue(input, value = input.value) {
    if (value === "") return "Not provided";
    if (input.options) {
        const option = Array.from(input.options).find(option => option.value === String(value));
        return option ? option.textContent.trim() : (typeof value === "number" ? `User ${value}` : String(value));
    }
    return String(value);
}

function aiReviewButton(label, action, fieldLabel) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "context-action-button secondary-action-button";
    button.textContent = label;
    if (fieldLabel) button.setAttribute("aria-label", `${label} ${fieldLabel} suggestion`);
    button.addEventListener("click", action);
    return button;
}

function resolveAiSuggestion(session, field, use) {
    if (!isCurrentAiSession(session) || !session.pending.has(field)) return;
    const pending = session.pending.get(field);
    if (use) {
        // Membership can change after the form's dropdown was populated. The
        // backend validated this ID; Create/Save will recheck eligibility.
        if (field === "assignee_id" && !Array.from(pending.input.options).some(option => option.value === String(pending.value))) {
            const option = document.createElement("option");
            option.value = String(pending.value);
            option.textContent = `User ${pending.value}`;
            pending.input.appendChild(option);
        }
        pending.input.value = String(pending.value);
        // Preserve the form's existing select prompt styling and change handlers.
        pending.input.dispatchEvent(new Event("input", {bubbles: true}));
        pending.input.dispatchEvent(new Event("change", {bubbles: true}));
    }
    pending.card.remove();
    session.pending.delete(field);
    if (!session.pending.size) {
        session.area.replaceChildren();
        session.area.hidden = true;
        session.button.disabled = false;
        session.message.textContent = "AI suggestions reviewed. You can request AI Assist again. Choose Create or Save to save form values.";
    }
}

function renderAiSuggestions(session, suggestions) {
    const heading = document.createElement("h3");
    heading.id = `${session.prefix}ai-suggestions-heading`;
    heading.textContent = "AI Suggestions";
    session.area.setAttribute("aria-labelledby", heading.id);
    const note = document.createElement("p");
    note.textContent = "Review suggestions before using them. Use replaces the current form value. Only Create or Save saves your changes.";
    const bulk = document.createElement("div");
    bulk.className = "ai-suggestion-actions";
    for (const [label, use] of [["Use All", true], ["Dismiss All", false]]) {
        bulk.appendChild(aiReviewButton(label, () => {
            for (const field of Array.from(session.pending.keys())) resolveAiSuggestion(session, field, use);
            session.button.focus({preventScroll: true});
        }));
    }
    session.area.replaceChildren(heading, note, bulk);

    for (const [field, suffix, label] of aiAssistFields) {
        if (!Object.hasOwn(suggestions, field)) continue;
        const input = session.form.querySelector(`#${session.prefix}${suffix}`);
        const card = document.createElement("article");
        card.className = "ai-suggestion";
        const title = document.createElement("h4");
        title.textContent = label;
        const comparison = document.createElement("dl");
        const current = document.createElement("dd");
        const suggested = document.createElement("dd");
        current.textContent = aiDisplayValue(input);
        suggested.textContent = aiDisplayValue(input, suggestions[field]);
        for (const [text, value] of [["Current form value", current], ["Suggested value", suggested]]) {
            const term = document.createElement("dt");
            term.textContent = text;
            comparison.appendChild(term);
            comparison.appendChild(value);
        }
        const actions = document.createElement("div");
        actions.className = "ai-suggestion-actions";
        for (const [text, use] of [["Use", true], ["Dismiss", false]]) {
            actions.appendChild(aiReviewButton(text, () => {
                resolveAiSuggestion(session, field, use);
                const next = session.area.querySelector("button") || session.button;
                next.focus({preventScroll: true});
            }, label));
        }
        card.appendChild(title);
        card.appendChild(comparison);
        card.appendChild(actions);
        session.area.appendChild(card);
        session.pending.set(field, {input, card, current, value: suggestions[field]});
    }
    session.area.hidden = false;
}

function isAiSuggestionResponse(data, form, prefix) {
    if (!data || !data.suggestions || typeof data.suggestions !== "object" || Array.isArray(data.suggestions)) return false;
    const entries = Object.entries(data.suggestions);
    if (data.outcome === "no_usable_suggestions") return entries.length === 0;
    if (data.outcome !== "suggestions" || !entries.length) return false;
    return entries.every(([field, value]) => {
        const definition = aiAssistFields.find(([key]) => key === field);
        if (!definition) return false;
        const input = form.querySelector(`#${prefix}${definition[1]}`);
        if (field === "assignee_id") {
            return Number.isSafeInteger(value) && value > 0;
        } else if (typeof value !== "string" || !value.trim()) return false;
        // The backend remains authoritative. Reject unmappable classification
        // values here as well so using a suggestion cannot clear a select.
        return !input.options || Array.from(input.options).some(option => !option.disabled && option.value === String(value));
    });
}

function usableAiFormSuggestions(form, prefix, suggestions) {
    const usable = {};
    for (const [field, suffix] of aiAssistFields) {
        if (!Object.hasOwn(suggestions, field)) continue;
        const input = form.querySelector(`#${prefix}${suffix}`);
        if (!input.options) {
            // Native controls can sanitize text (notably CR/LF in text inputs).
            // Exclude a mismatch before review; never silently rewrite the value
            // preserved by REQ-019 or apply a different value through Use.
            const probe = input.cloneNode(false);
            probe.value = suggestions[field];
            if (probe.value !== suggestions[field]) continue;
        }
        usable[field] = suggestions[field];
    }
    return usable;
}

async function submitAiAssist(form, prefix, url, button, message, sendRequest) {
    const session = aiAssistSessions.get(form);
    if (!session || !isCurrentAiSession(session) || session.loading || session.pending.size) return;
    session.loading = true;
    const requestId = ++session.requestId;
    const isCurrentRequest = () => isCurrentAiSession(session) && session.requestId === requestId;
    button.disabled = true;
    message.textContent = "Requesting AI assistance...";
    try {
        const response = await sendRequest(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(collectAiAssistContext(form, prefix))
        });
        if (!isCurrentRequest()) return;
        if (!response) {
            message.textContent = "";
            return;
        }
        const data = await response.json();
        if (!isCurrentRequest()) return;
        if (!response.ok) {
            message.textContent = formatApiError(data.detail, "Unable to request AI assistance.");
        } else if (!isAiSuggestionResponse(data, form, prefix)) {
            message.textContent = "Unable to process the AI assistance response. Please try again.";
        } else if (data.outcome === "no_usable_suggestions") {
            message.textContent = "No usable AI suggestions are available. You can continue manually or request AI Assist again.";
        } else {
            const usable = usableAiFormSuggestions(form, prefix, data.suggestions);
            if (!Object.keys(usable).length) {
                message.textContent = "No usable AI suggestions are available. You can continue manually or request AI Assist again.";
            } else {
                renderAiSuggestions(session, usable);
                message.textContent = Object.keys(usable).length < Object.keys(data.suggestions).length
                    ? "Some suggestions could not be represented unchanged in the form and were excluded. Review the remaining suggestions."
                    : "AI suggestions are ready for review. Use or dismiss all pending suggestions before requesting AI Assist again.";
            }
        }
    } catch (error) {
        if (isCurrentRequest()) message.textContent = "Unable to request AI assistance. Please try again.";
    } finally {
        // A late completion must not unlock or change a newer session's request.
        if (isCurrentRequest()) {
            session.loading = false;
            button.disabled = session.pending.size > 0;
        }
    }
}
