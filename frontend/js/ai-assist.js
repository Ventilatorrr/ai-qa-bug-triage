function collectAiAssistContext(form, prefix) {
    const fields = {
        title: "title",
        affected_version: "affected-version",
        environment: "environment",
        description: "description",
        steps_to_reproduce: "steps",
        expected_result: "expected",
        actual_result: "actual",
        severity: "severity",
        priority: "priority"
    };
    const context = {};
    for (const [field, suffix] of Object.entries(fields)) {
        context[field] = form.querySelector(`#${prefix}${suffix}`).value;
    }
    const assignee = form.querySelector(`#${prefix}assignee`).value;
    context.assignee_id = assignee === "" ? null : Number(assignee);
    return context;
}

const pendingAiAssistButtons = new WeakSet();

async function submitAiAssist(form, prefix, url, button, message, sendRequest) {
    if (pendingAiAssistButtons.has(button)) {
        return;
    }
    pendingAiAssistButtons.add(button);
    button.disabled = true;
    message.textContent = "Requesting AI assistance...";
    try {
        const response = await sendRequest(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(collectAiAssistContext(form, prefix))
        });
        if (!response) {
            message.textContent = "";
            return;
        }
        const data = await response.json();
        // This slice has no successful generation response contract yet.
        message.textContent = response.ok
            ? "Unable to process the AI assistance response."
            : formatApiError(data.detail, "Unable to request AI assistance.");
    } catch (error) {
        message.textContent = "Unable to request AI assistance. Please try again.";
    } finally {
        pendingAiAssistButtons.delete(button);
        button.disabled = false;
    }
}
