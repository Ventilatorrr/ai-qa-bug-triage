const params = new URLSearchParams(window.location.search);

const projectId = params.get("project_id");
const bugId = params.get("bug_id");

const accessToken = localStorage.getItem("access_token");

const backToProjectLink = document.querySelector("#back-to-project");
const bugMessage = document.querySelector("#bug-message");
const bugDetails = document.querySelector("#bug-details");
const bugDetailsGrid = document.querySelector(".bug-details-grid");
const showEditBugFormButton = document.querySelector("#show-edit-bug-form");

const editBugForm = document.querySelector("#edit-bug-form");
const editBugMessage = document.querySelector("#edit-bug-message");
const editBugTitle = document.querySelector("#edit-bug-title");
const editBugEnvironment = document.querySelector("#edit-bug-environment");
const editBugDescription = document.querySelector("#edit-bug-description");
const editBugSteps = document.querySelector("#edit-bug-steps");
const editBugActual = document.querySelector("#edit-bug-actual");
const editBugExpected = document.querySelector("#edit-bug-expected");
const editBugSeverity = document.querySelector("#edit-bug-severity");
const editBugPriority = document.querySelector("#edit-bug-priority");
const editBugAssignee = document.querySelector("#edit-bug-assignee");
const editBugAffectedVersion = document.querySelector("#edit-bug-affected-version");
const editBugFixVersion = document.querySelector("#edit-bug-fix-version");
const saveEditButton = document.querySelector("#save-edit-button");
const cancelEditFormButton = document.querySelector("#cancel-edit-form");
const editBugAssigneeLabel = document.querySelector("#edit-bug-assignee-label");

let currentBug = null;
let projectMembers = null;

function showMessage(element, message, type = "neutral") {
    element.classList.remove("message-success", "message-error");
    element.textContent = message;

    if (message && type === "success") {
        element.classList.add("message-success");
    } else if (message && type === "error") {
        element.classList.add("message-error");
    }
}

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
}

function isValidBugResponse(data) {
    return (
        data && typeof data === "object" && !Array.isArray(data) &&
        Number.isInteger(data.id) && String(data.id) === bugId &&
        Number.isInteger(data.project_id) && String(data.project_id) === projectId &&
        typeof data.title === "string" && data.title.trim() !== "" &&
        typeof data.status === "string" && data.status.trim() !== ""
    );
}

async function loadBug() {
    bugDetails.hidden = true;

    if (!accessToken) {
        window.location.href = "/login.html";
        return;
    }

    if (!isValidId(projectId)) {
        showMessage(bugMessage, "Invalid project ID.", "error");
        return;
    }

    backToProjectLink.href = `/project.html?id=${projectId}`;

    if (!isValidId(bugId)) {
        showMessage(bugMessage, "Invalid bug ID.", "error");
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
            showMessage(
                bugMessage,
                formatApiError(
                    data?.detail,
                    "Unable to load this bug report."
                ),
                "error"
            );
            return;
        }

        if (!isValidBugResponse(data)) {
            showMessage(bugMessage, "Unable to load this bug report. Invalid server response.", "error");
            return;
        }

        currentBug = data;
        renderBug(data);
        showMessage(bugMessage, "");
        bugDetails.hidden = false;
    } catch (error) {
        showMessage(
            bugMessage,
            "Unable to load this bug report. Please try again.",
            "error"
        );
    }
}

function updateSelectPromptStyle(selectInput) {
    selectInput.classList.toggle(
        "select-prompt",
        selectInput.value === ""
    );
}

editBugSeverity.addEventListener("change", function() {
    updateSelectPromptStyle(editBugSeverity);
});
editBugPriority.addEventListener("change", function() {
    updateSelectPromptStyle(editBugPriority);
});
editBugAssignee.addEventListener("change", function() {
    updateSelectPromptStyle(editBugAssignee);
});

function populateEditForm() {
    editBugTitle.value = currentBug.title;
    editBugEnvironment.value = currentBug.environment || "";
    editBugDescription.value = currentBug.description || "";
    editBugSteps.value = currentBug.steps_to_reproduce || "";
    editBugActual.value = currentBug.actual_result || "";
    editBugExpected.value = currentBug.expected_result || "";
    editBugSeverity.value = currentBug.severity || "";
    editBugPriority.value = currentBug.priority || "";
    editBugAffectedVersion.value = currentBug.affected_version || "";
    editBugFixVersion.value = currentBug.fix_version || "";

    editBugAssignee.innerHTML = "";

    if (currentBug.status === "Closed") {
        editBugAssignee.disabled = true;
        editBugAssigneeLabel.hidden = true;
        editBugAssignee.hidden = true;
    } else {
        editBugAssignee.disabled = false;
        editBugAssigneeLabel.hidden = false;
        editBugAssignee.hidden = false;

        const isAlreadyUnassigned = currentBug.assignee_id === null || currentBug.assignee_id === undefined;
        const triageStatus = currentBug.status === "Triage";

        if (triageStatus) {
            // Triage: active unassignment allowed
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "Unassigned";
            editBugAssignee.appendChild(option);
        } else if (isAlreadyUnassigned) {
            // Non-Triage bug already unassigned (e.g. member removed):
            // show disabled placeholder so the state is visible, but do not
            // let the user actively choose "Unassigned" as a new action.
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "Unassigned (current)";
            option.disabled = true;
            editBugAssignee.appendChild(option);
        }

        if (projectMembers) {
            projectMembers.forEach(function(member) {
                const role = member.role;
                let canAssign = false;
                if (currentBug.status === "Triage" || currentBug.status === "Open") {
                    if (role === "QA Analyst" || role === "Developer") canAssign = true;
                } else if (currentBug.status === "Development") {
                    if (role === "Developer") canAssign = true;
                } else if (currentBug.status === "Testing") {
                    if (role === "QA Analyst") canAssign = true;
                }

                if (canAssign) {
                    const option = document.createElement("option");
                    option.value = member.user_id;
                    option.textContent = `${member.email} (${member.role})`;
                    editBugAssignee.appendChild(option);
                }
            });
        }

        const currentAssigneeOption = Array.from(editBugAssignee.options).find(
            function(opt) { return opt.value === String(currentBug.assignee_id); }
        );

        if (!isAlreadyUnassigned && !currentAssigneeOption) {
            // Assigned to a user who is no longer a selectable member:
            // add a read-only placeholder for the current assignee.
            const option = document.createElement("option");
            option.value = currentBug.assignee_id;
            option.textContent = `User ${currentBug.assignee_id}`;
            editBugAssignee.appendChild(option);
        }

        // Pre-select the current value. For the already-unassigned case
        // this selects the disabled placeholder (value "").
        editBugAssignee.value = isAlreadyUnassigned ? "" : String(currentBug.assignee_id);
    }

    updateSelectPromptStyle(editBugSeverity);
    updateSelectPromptStyle(editBugPriority);
    updateSelectPromptStyle(editBugAssignee);
}

showEditBugFormButton.addEventListener("click", async function() {
    showEditBugFormButton.disabled = true;
    showMessage(editBugMessage, "");
    showMessage(bugMessage, "Loading...");

    let latestBug = null;
    try {
        const response = await fetch(`/projects/${projectId}/bugs/${bugId}`, {
            headers: { "Authorization": "Bearer " + accessToken }
        });

        let data = {};
        try { data = await response.json(); } catch (error) { data = {}; }

        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "/login.html";
            return;
        }

        if (!response.ok) {
            bugDetails.hidden = true;
            showMessage(
                bugMessage,
                formatApiError(data?.detail, "Unable to load this bug report."),
                "error"
            );
            showEditBugFormButton.disabled = false;
            return;
        }

        if (!isValidBugResponse(data)) {
            bugDetails.hidden = true;
            showMessage(bugMessage, "Unable to load this bug report. Invalid server response.", "error");
            showEditBugFormButton.disabled = false;
            return;
        }

        latestBug = data;
    } catch (error) {
        showMessage(bugMessage, "Unable to load this bug report. Please try again.", "error");
        showEditBugFormButton.disabled = false;
        return;
    }

    currentBug = latestBug;
    renderBug(currentBug);

    let membersData = [];
    if (currentBug.status !== "Closed") {
        try {
            const membersResponse = await fetch(`/projects/${projectId}/members`, {
                headers: { "Authorization": "Bearer " + accessToken }
            });

            let data = {};
            try { data = await membersResponse.json(); } catch (error) { data = {}; }

            if (membersResponse.status === 401) {
                localStorage.removeItem("access_token");
                window.location.href = "/login.html";
                return;
            }

            if (!membersResponse.ok) {
                showMessage(
                    bugMessage,
                    formatApiError(data?.detail, "Unable to load project members."),
                    "error"
                );
                showEditBugFormButton.disabled = false;
                return;
            }

            if (!Array.isArray(data)) {
                showMessage(bugMessage, "Unable to load project members. Invalid server response.", "error");
                showEditBugFormButton.disabled = false;
                return;
            }

            membersData = data;
        } catch (error) {
            showMessage(bugMessage, "Unable to load project members. Please try again.", "error");
            showEditBugFormButton.disabled = false;
            return;
        }
    }

    projectMembers = membersData;
    showMessage(bugMessage, "");
    populateEditForm();

    bugDetailsGrid.hidden = true;
    showEditBugFormButton.hidden = true;
    editBugForm.hidden = false;
    showEditBugFormButton.disabled = false;
});

cancelEditFormButton.addEventListener("click", function() {
    editBugForm.hidden = true;
    showMessage(editBugMessage, "");

    bugDetailsGrid.hidden = false;
    showEditBugFormButton.hidden = false;
});

editBugForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const trimmedTitle = editBugTitle.value.trim();
    if (!trimmedTitle) {
        showMessage(editBugMessage, "Title is required and cannot be blank.", "error");
        editBugTitle.focus();
        return;
    }

    const payload = {};

    if (trimmedTitle !== currentBug.title) {
        payload.title = trimmedTitle;
    }

    const envVal = editBugEnvironment.value || null;
    if (envVal !== currentBug.environment) payload.environment = envVal;

    const descVal = editBugDescription.value || null;
    if (descVal !== currentBug.description) payload.description = descVal;

    const stepsVal = editBugSteps.value || null;
    if (stepsVal !== currentBug.steps_to_reproduce) payload.steps_to_reproduce = stepsVal;

    const actualVal = editBugActual.value || null;
    if (actualVal !== currentBug.actual_result) payload.actual_result = actualVal;

    const expectedVal = editBugExpected.value || null;
    if (expectedVal !== currentBug.expected_result) payload.expected_result = expectedVal;

    const severityVal = editBugSeverity.value || null;
    if (severityVal !== currentBug.severity) payload.severity = severityVal;

    const priorityVal = editBugPriority.value || null;
    if (priorityVal !== currentBug.priority) payload.priority = priorityVal;

    const affectedVal = editBugAffectedVersion.value || null;
    if (affectedVal !== currentBug.affected_version) payload.affected_version = affectedVal;

    const fixVal = editBugFixVersion.value || null;
    if (fixVal !== currentBug.fix_version) payload.fix_version = fixVal;

    if (currentBug.status !== "Closed") {
        const isAlreadyUnassigned = currentBug.assignee_id === null || currentBug.assignee_id === undefined;
        if (isAlreadyUnassigned) {
            // Only include assignee_id if the user picked a real replacement member.
            // An empty select value means "still unassigned" — do not patch.
            if (editBugAssignee.value) {
                payload.assignee_id = parseInt(editBugAssignee.value, 10);
            }
        } else {
            const assigneeVal = editBugAssignee.value ? parseInt(editBugAssignee.value, 10) : null;
            if (assigneeVal !== currentBug.assignee_id) {
                payload.assignee_id = assigneeVal;
            }
        }
    }

    if (Object.keys(payload).length === 0) {
        editBugForm.hidden = true;
        bugDetailsGrid.hidden = false;
        showEditBugFormButton.hidden = false;
        return;
    }

    saveEditButton.disabled = true;
    showMessage(editBugMessage, "");

    try {
        const response = await fetch(`/projects/${projectId}/bugs/${bugId}`, {
            method: "PATCH",
            headers: {
                "Authorization": "Bearer " + accessToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        let data = {};
        try { data = await response.json(); } catch (error) { data = {}; }

        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "/login.html";
            return;
        }

        if (!response.ok) {
            showMessage(
                editBugMessage,
                formatApiError(data?.detail, "Unable to save bug changes."),
                "error"
            );
            saveEditButton.disabled = false;
            return;
        }

        if (!isValidBugResponse(data)) {
            showMessage(
                editBugMessage,
                "Unable to confirm the update result. Please refresh the page.",
                "error"
            );
            saveEditButton.disabled = false;
            return;
        }

        currentBug = data;
        renderBug(currentBug);

        editBugForm.hidden = true;
        bugDetailsGrid.hidden = false;
        showEditBugFormButton.hidden = false;

        showMessage(bugMessage, "Bug report updated successfully.", "success");
    } catch (error) {
        showMessage(
            editBugMessage,
            "An error occurred while saving. Please try again.",
            "error"
        );
    } finally {
        saveEditButton.disabled = false;
    }
});

loadBug();
