const params = new URLSearchParams(window.location.search);

const projectId = params.get("project_id");
const bugId = params.get("bug_id");

const accessToken = localStorage.getItem("access_token");

const backToProjectLink = document.querySelector("#back-to-project");
const bugMessage = document.querySelector("#bug-message");
const bugDetails = document.querySelector("#bug-details");


function isValidId(value) {
    return typeof value === "string" && /^[1-9]\d*$/.test(value);
}


function displayValue(value, emptyValue = "Not provided") {
    if (isMissingValue(value)) {
        return emptyValue;
    }

    return String(value);
}


function isMissingValue(value) {
    return (
        value === null ||
        value === undefined ||
        (typeof value === "string" && value.trim() === "")
    );
}


function formatDateTime(value) {
    if (!value) {
        return "Not provided";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return displayValue(value);
    }

    return date.toLocaleString();
}


function setText(selector, value, emptyValue) {
    const element = document.querySelector(selector);

    element.textContent = displayValue(value, emptyValue);
    element.classList.toggle("missing-value", isMissingValue(value));
}


function renderBug(bug) {
    document.title = `BUG-${bug.id}: ${bug.title} - AI QA Bug Triage`;

    setText("#bug-reference", `BUG-${bug.id}`);
    setText("#bug-heading", bug.title);
    setText("#bug-status", bug.status);

    setText("#bug-title", bug.title);
    setText("#bug-environment", bug.environment);
    setText("#bug-description", bug.description);
    setText("#bug-steps", bug.steps_to_reproduce);
    setText("#bug-actual-result", bug.actual_result);
    setText("#bug-expected-result", bug.expected_result);
    setText("#bug-severity", bug.severity);
    setText("#bug-priority", bug.priority);

    const severityElement = document.querySelector("#bug-severity");
    const priorityElement = document.querySelector("#bug-priority");

    severityElement.classList.remove(
        "bug-severity-blocker", "bug-severity-major",
        "bug-severity-moderate", "bug-severity-minor"
    );
    priorityElement.classList.remove(
        "bug-priority-urgent", "bug-priority-high",
        "bug-priority-medium", "bug-priority-low"
    );

    if (!isMissingValue(bug.severity)) {
        severityElement.classList.add(
            `bug-severity-${bug.severity.toLowerCase()}`
        );
    }

    if (!isMissingValue(bug.priority)) {
        priorityElement.classList.add(
            `bug-priority-${bug.priority.toLowerCase()}`
        );
    }

    setText("#bug-status-detail", bug.status);

    const hasResolution = !isMissingValue(bug.resolution);

    setText("#bug-resolution", bug.resolution);
    document.querySelector("#bug-resolution-label").hidden = !hasResolution;
    document.querySelector("#bug-resolution").hidden = !hasResolution;

    setText(
        "#bug-assignee",
        bug.assignee_id === null || bug.assignee_id === undefined
            ? "Unassigned"
            : `User ${bug.assignee_id}`
    );
    setText("#bug-affected-version", bug.affected_version);
    setText("#bug-fix-version", bug.fix_version);
    setText(
        "#bug-created-at",
        bug.created_at ? formatDateTime(bug.created_at) : null
    );
    setText(
        "#bug-updated-at",
        bug.updated_at ? formatDateTime(bug.updated_at) : null
    );

    bugMessage.textContent = "";
    bugDetails.hidden = false;
}


async function loadBug() {
    bugDetails.hidden = true;

    if (!accessToken) {
        window.location.href = "/login.html";
        return;
    }

    if (!isValidId(projectId)) {
        bugMessage.textContent = "Invalid project ID.";
        return;
    }

    backToProjectLink.href = `/project.html?id=${projectId}`;

    if (!isValidId(bugId)) {
        bugMessage.textContent = "Invalid bug ID.";
        return;
    }

    try {
        const response = await fetch(
            `/projects/${projectId}/bugs/${bugId}`,
            {
                headers: {
                    "Authorization": "Bearer " + accessToken
                }
            }
        );

        let data = {};

        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "/login.html";
            return;
        }

        if (!response.ok) {
            bugMessage.textContent = formatApiError(
                data?.detail,
                "Unable to load this bug report."
            );
            return;
        }

        if (
            !data || typeof data !== "object" || Array.isArray(data) ||
            !Number.isInteger(data.id) || String(data.id) !== bugId ||
            !Number.isInteger(data.project_id) || String(data.project_id) !== projectId ||
            typeof data.title !== "string" || !data.title.trim() ||
            typeof data.status !== "string" || !data.status.trim()
        ) {
            bugMessage.textContent = "Unable to load this bug report. Invalid server response.";
            return;
        }

        renderBug(data);
    } catch (error) {
        bugMessage.textContent =
            "Unable to load this bug report. Please try again.";
    }
}


loadBug();
