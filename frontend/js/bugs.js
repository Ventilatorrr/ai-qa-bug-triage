const params = new URLSearchParams(window.location.search);

const projectId = params.get("project_id");
const bugId = params.get("bug_id");

const backToProjectLink = document.querySelector("#back-to-project");
const bugMessage = document.querySelector("#bug-message");
const bugDetails = document.querySelector("#bug-details");
const bugDetailsGrid = document.querySelector(".bug-details-grid");
const showEditBugFormButton = document.querySelector("#show-edit-bug-form");
const deleteBugButton = document.querySelector("#delete-bug-button");
const lifecycleActions = document.querySelector("#bug-lifecycle-actions");
const lifecycleQaField = document.querySelector("#lifecycle-qa-field");
const lifecycleQaAssignee = document.querySelector("#lifecycle-qa-assignee");
const lifecycleActionButton = document.querySelector("#lifecycle-action-button");
const lifecycleGuidance = document.querySelector("#lifecycle-guidance");

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
let projectMembers = [];
let currentMember = null;
let deleteInProgress = false;
let editModeLoading = false;
let lifecycleInProgress = false;
let lifecycleTargetStatus = null;
let lifecycleActionAllowed = false;
const qaSelectionValidationMessage =
    "Select a QA Analyst before sending to Testing.";

function redirectToLogin() {
    localStorage.removeItem("access_token");
    window.location.replace("/login.html");
}

function getCurrentAccessToken() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        redirectToLogin();
        return null;
    }

    return token;
}

async function authenticatedFetch(url, options = {}) {
    const token = getCurrentAccessToken();

    if (!token) {
        return null;
    }

    const response = await fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            "Authorization": "Bearer " + token
        }
    });

    if (response.status === 401) {
        redirectToLogin();
        return null;
    }

    return response;
}

function showMessage(element, message, type = "neutral") {
    element.classList.remove("message-success", "message-error");
    element.textContent = message;

    if (message && type === "success") {
        element.classList.add("message-success");
    } else if (message && type === "error") {
        element.classList.add("message-error");
    }
}

function getCurrentUserId() {
    const token = getCurrentAccessToken();

    if (!token) {
        return null;
    }

    try {
        const payload = token.split(".")[1];
        return JSON.parse(atob(payload)).user_id;
    } catch (error) {
        return null;
    }
}

function hideRoleSpecificActions() {
    deleteBugButton.hidden = true;
    lifecycleActions.hidden = true;
    lifecycleTargetStatus = null;
}

async function loadProjectMembers(preserveVisibleState = false) {
    if (!preserveVisibleState) {
        projectMembers = [];
        currentMember = null;
        document.querySelector("#header-identity").hidden = true;
        hideRoleSpecificActions();
    }

    try {
        const response = await authenticatedFetch(`/projects/${projectId}/members`);

        if (!response) {
            return false;
        }

        let data = {};

        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (!response.ok) {
            showMessage(
                bugMessage,
                formatApiError(data?.detail, "Unable to load project members."),
                "error"
            );
            return false;
        }

        if (!Array.isArray(data)) {
            showMessage(
                bugMessage,
                "Unable to load project members. Invalid server response.",
                "error"
            );
            return false;
        }

        projectMembers = data;

        const currentUserId = getCurrentUserId();
        currentMember = projectMembers.find(function(member) {
            return member.user_id === currentUserId;
        });

        if (!currentMember) {
            showMessage(bugMessage, "Unable to determine project permissions.", "error");
            return false;
        }

        return true;
    } catch (error) {
        showMessage(
            bugMessage,
            "Unable to load project members. Please try again.",
            "error"
        );

        return false;
    }
}

function getProjectMember(userId) {
    return projectMembers.find(function(member) {
        return member.user_id === userId;
    });
}

function resetLifecycleControls() {
    lifecycleActions.hidden = true;
    lifecycleQaField.hidden = true;
    lifecycleQaAssignee.disabled = true;
    lifecycleActionButton.disabled = true;
    lifecycleActionButton.textContent = "";
    lifecycleGuidance.textContent = "";
    lifecycleTargetStatus = null;
    lifecycleActionAllowed = false;
}

function populateLifecycleQaAnalysts() {
    lifecycleQaAssignee.innerHTML = "";

    const prompt = document.createElement("option");
    prompt.value = "";
    prompt.textContent = "Select a QA Analyst";
    prompt.disabled = true;
    prompt.selected = true;
    lifecycleQaAssignee.appendChild(prompt);

    projectMembers.forEach(function(member) {
        if (member.role === "QA Analyst") {
            const option = document.createElement("option");
            option.value = member.user_id;
            option.textContent = `${member.email} (${member.role})`;
            lifecycleQaAssignee.appendChild(option);
        }
    });

    updateSelectPromptStyle(lifecycleQaAssignee);

    return lifecycleQaAssignee.options.length - 1;
}

function renderLifecycleControls() {
    resetLifecycleControls();

    if (!currentBug || !currentMember || editBugForm.hidden === false) {
        return;
    }

    const actorRole = currentMember.role;
    const assignee = getProjectMember(currentBug.assignee_id);
    const validTriageAssignee = assignee && (
        assignee.role === "QA Analyst" || assignee.role === "Developer"
    );
    const validDeveloperAssignee = assignee && assignee.role === "Developer";

    if (
        currentBug.status === "Triage" &&
        (actorRole === "Project Owner" || actorRole === "QA Analyst")
    ) {
        lifecycleActions.hidden = false;
        lifecycleTargetStatus = "Open";
        lifecycleActionButton.textContent = "Move to Open";
        lifecycleActionAllowed = Boolean(validTriageAssignee);

        if (!validTriageAssignee) {
            lifecycleGuidance.textContent =
                "Assign a QA Analyst or Developer through Edit before moving to Open.";
        }
    } else if (
        currentBug.status === "Open" &&
        (actorRole === "Project Owner" || actorRole === "Developer")
    ) {
        lifecycleActions.hidden = false;
        lifecycleTargetStatus = "Development";
        lifecycleActionButton.textContent = "Start Development";

        if (!validDeveloperAssignee) {
            lifecycleGuidance.textContent =
                "Assign a Developer through Edit before starting development.";
        } else if (
            actorRole === "Developer" &&
            currentBug.assignee_id !== currentMember.user_id
        ) {
            lifecycleGuidance.textContent =
                "Only the assigned Developer can start development.";
        } else {
            lifecycleActionAllowed = true;
        }
    } else if (
        currentBug.status === "Development" &&
        (actorRole === "Project Owner" || actorRole === "Developer")
    ) {
        lifecycleActions.hidden = false;
        lifecycleQaField.hidden = false;
        lifecycleTargetStatus = "Testing";
        lifecycleActionButton.textContent = "Send to Testing";

        const qaCount = populateLifecycleQaAnalysts();

        if (!validDeveloperAssignee) {
            lifecycleGuidance.textContent =
                "Assign a Developer through Edit before sending to testing.";
        } else if (
            actorRole === "Developer" &&
            currentBug.assignee_id !== currentMember.user_id
        ) {
            lifecycleGuidance.textContent =
                "Only the assigned Developer can send this bug to testing.";
        } else if (qaCount === 0) {
            lifecycleGuidance.textContent =
                "Add a QA Analyst to the project before sending this bug to testing.";
        } else {
            lifecycleActionAllowed = true;
            lifecycleQaAssignee.disabled = false;
        }
    }

    lifecycleActionButton.disabled = !lifecycleActionAllowed || (
        lifecycleTargetStatus === "Testing" && !lifecycleQaAssignee.value
    );
}

function renderRoleSpecificActions() {
    const identity = document.querySelector("#header-identity");
    identity.hidden = !currentMember;
    identity.textContent = currentMember
        ? `${currentMember.email} (${currentMember.role})`
        : "";

    if (currentBug) {
        renderBugAssignee(currentBug);
    }

    deleteBugButton.hidden = !(
        currentMember && (
            currentMember.role === "Project Owner" ||
            currentMember.role === "QA Analyst"
        )
    );

    renderLifecycleControls();
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

function renderBugAssignee(bug) {
    if (bug.assignee_id === null || bug.assignee_id === undefined) {
        setText("#bug-assignee", "Unassigned");
        return;
    }

    const assignee = getProjectMember(bug.assignee_id);

    setText(
        "#bug-assignee",
        assignee
            ? `${assignee.email} (${assignee.role})`
            : `User ${bug.assignee_id}`
    );
}

function renderBug(bug) {
    document.title = `BUG-${bug.id}: ${bug.title} - AI QA Bug Triage`;

    setText("#bug-reference", `BUG-${bug.id}`);
    setText("#bug-heading", bug.title);

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

    renderBugAssignee(bug);
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

async function loadBug(preserveVisibleState = false) {
    if (!preserveVisibleState) {
        bugDetails.hidden = true;
    }

    if (!localStorage.getItem("access_token")) {
        redirectToLogin();
        return false;
    }

    if (!isValidId(projectId)) {
        showMessage(bugMessage, "Invalid project ID.", "error");
        return false;
    }

    backToProjectLink.href = `/project.html?id=${projectId}`;

    if (!isValidId(bugId)) {
        showMessage(bugMessage, "Invalid bug ID.", "error");
        return false;
    }

    try {
        const response = await authenticatedFetch(
            `/projects/${projectId}/bugs/${bugId}`
        );

        if (!response) {
            return false;
        }

        let data = {};
        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (response.status === 404) {
            window.location.replace(`/project.html?id=${projectId}`);
            return false;
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
            return false;
        }

        if (!isValidBugResponse(data)) {
            showMessage(bugMessage, "Unable to load this bug report. Invalid server response.", "error");
            return false;
        }

        currentBug = data;
        renderBug(data);
        showMessage(bugMessage, "");
        bugDetails.hidden = false;

        if (await loadProjectMembers(preserveVisibleState)) {
            renderRoleSpecificActions();
        }

        return true;
    } catch (error) {
        showMessage(
            bugMessage,
            "Unable to load this bug report. Please try again.",
            "error"
        );

        return false;
    }
}

deleteBugButton.addEventListener("click", async function() {
    if (deleteInProgress || lifecycleInProgress || !currentBug) {
        return;
    }

    const confirmed = confirm(
        `Are you sure you want to delete "${currentBug.title}"?`
    );

    if (!confirmed) {
        return;
    }

    deleteInProgress = true;
    deleteBugButton.disabled = true;
    showMessage(bugMessage, "");

    try {
        const response = await authenticatedFetch(
            `/projects/${projectId}/bugs/${bugId}`,
            {
                method: "DELETE"
            }
        );

        if (!response) {
            return;
        }

        if (response.status === 204) {
            try {
                sessionStorage.setItem(
                    "bug-deletion-feedback",
                    `BUG-${currentBug.id} "${currentBug.title}" deleted successfully.`
                );
            } catch (error) {
                // Continue to the project page if session storage is unavailable.
            }

            window.location.replace(`/project.html?id=${projectId}`);
            return;
        }

        let data = {};

        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        showMessage(
            bugMessage,
            formatApiError(data?.detail, "Unable to delete this bug report."),
            "error"
        );
    } catch (error) {
        showMessage(
            bugMessage,
            "Unable to delete this bug report. Please try again.",
            "error"
        );
    } finally {
        deleteInProgress = false;
        deleteBugButton.disabled = false;
    }
});

lifecycleQaAssignee.addEventListener("change", function() {
    updateSelectPromptStyle(lifecycleQaAssignee);

    if (lifecycleTargetStatus === "Testing") {
        lifecycleActionButton.disabled = !(
            lifecycleActionAllowed && lifecycleQaAssignee.value
        );
        lifecycleGuidance.textContent = "";
    }
});

lifecycleActionButton.addEventListener("click", async function() {
    if (
        lifecycleInProgress || deleteInProgress ||
        !currentBug || !lifecycleActionAllowed || !lifecycleTargetStatus
    ) {
        return;
    }

    const requestedStatus = lifecycleTargetStatus;
    const payload = {
        status: requestedStatus
    };

    if (requestedStatus === "Testing") {
        const qaAssigneeId = Number(lifecycleQaAssignee.value);

        if (!Number.isInteger(qaAssigneeId) || qaAssigneeId <= 0) {
            lifecycleGuidance.textContent =
                qaSelectionValidationMessage;
            lifecycleActionButton.disabled = true;
            return;
        }

        payload.assignee_id = qaAssigneeId;
    }

    let lifecycleStateConfirmed = true;

    lifecycleInProgress = true;
    lifecycleActionButton.textContent = "Updating...";
    lifecycleActionButton.disabled = true;
    lifecycleQaAssignee.disabled = true;
    showEditBugFormButton.disabled = true;
    deleteBugButton.disabled = true;
    showMessage(bugMessage, "");

    try {
        const response = await authenticatedFetch(
            `/projects/${projectId}/bugs/${bugId}/status`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        if (!response) {
            lifecycleStateConfirmed = false;
            return;
        }

        let data = {};

        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (response.status === 404) {
            currentBug = null;
            bugDetails.hidden = true;
            hideRoleSpecificActions();
            showMessage(
                bugMessage,
                formatApiError(data?.detail, "This bug report is no longer available."),
                "error"
            );
            return;
        }

        if (!response.ok) {
            const errorMessage = formatApiError(
                data?.detail,
                "Unable to update this bug's status."
            );

            if (response.status === 403 || response.status === 422) {
                if (await loadBug()) {
                    showMessage(bugMessage, errorMessage, "error");
                }
            } else {
                showMessage(bugMessage, errorMessage, "error");
            }

            return;
        }

        if (!isValidBugResponse(data)) {
            const refreshed = await loadBug();

            if (refreshed) {
                showMessage(
                    bugMessage,
                    "Unable to confirm the transition response. The current bug state was refreshed.",
                    "error"
                );
            }

            return;
        }

        currentBug = data;
        renderBug(currentBug);
        renderRoleSpecificActions();

        const successMessages = {
            Open: "Bug moved to Open.",
            Development: "Bug moved to Development.",
            Testing: "Bug moved to Testing."
        };

        showMessage(bugMessage, successMessages[requestedStatus], "success");
    } catch (error) {
        lifecycleStateConfirmed = false;
        lifecycleActionButton.textContent = "Refresh required";
        showMessage(
            bugMessage,
            "Unable to confirm the status change. Refresh the page before trying again.",
            "error"
        );
    } finally {
        lifecycleInProgress = false;
        showEditBugFormButton.disabled = false;
        deleteBugButton.disabled = false;

        if (lifecycleStateConfirmed && currentBug && !bugDetails.hidden) {
            renderRoleSpecificActions();
        }
    }
});

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
    if (editModeLoading) {
        return;
    }

    editModeLoading = true;
    showMessage(editBugMessage, "");

    try {
        const response = await authenticatedFetch(
            `/projects/${projectId}/bugs/${bugId}`
        );

        if (!response) {
            return;
        }

        let data = {};
        try { data = await response.json(); } catch (error) { data = {}; }

        if (!response.ok) {
            if (response.status === 404) {
                bugDetails.hidden = true;
                hideRoleSpecificActions();
            }

            showMessage(
                bugMessage,
                formatApiError(data?.detail, "Unable to load this bug report."),
                "error"
            );
            return;
        }

        if (!isValidBugResponse(data)) {
            showMessage(bugMessage, "Unable to load this bug report. Invalid server response.", "error");
            return;
        }

        if (!await loadProjectMembers(true)) {
            return;
        }

        currentBug = data;
        renderBug(currentBug);
        renderRoleSpecificActions();
        showMessage(bugMessage, "");
        populateEditForm();
        editBugForm.insertBefore(editBugMessage, editBugForm.querySelector(".form-actions"));

        bugDetailsGrid.hidden = true;
        lifecycleActions.hidden = true;
        showEditBugFormButton.hidden = true;
        editBugForm.hidden = false;
    } catch (error) {
        showMessage(bugMessage, "Unable to load this bug report. Please try again.", "error");
    } finally {
        editModeLoading = false;
    }
});

cancelEditFormButton.addEventListener("click", function() {
    editBugForm.hidden = true;
    showMessage(editBugMessage, "");

    bugDetailsGrid.hidden = false;
    showEditBugFormButton.hidden = false;
    renderRoleSpecificActions();
});

editBugForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const trimmedTitle = editBugTitle.value.trim();
    if (!trimmedTitle) {
        showMessage(editBugMessage, "Title is required and cannot be blank.", "error");
        editBugTitle.focus({ preventScroll: true });
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
        renderRoleSpecificActions();
        return;
    }

    saveEditButton.disabled = true;
    showMessage(editBugMessage, "");

    try {
        const response = await authenticatedFetch(`/projects/${projectId}/bugs/${bugId}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response) {
            return;
        }

        let data = {};
        try { data = await response.json(); } catch (error) { data = {}; }

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
        renderRoleSpecificActions();

        bugDetails.after(editBugMessage);
        showMessage(editBugMessage, "Bug report updated successfully.", "success");
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

async function loadProjectNavigation() {
    try {
        const response = await authenticatedFetch(`/projects/${projectId}`);

        if (!response) {
            return;
        }

        const data = await response.json();
        if (!response.ok) {
            showMessage(bugMessage, formatApiError(data?.detail, "Unable to load project name."), "error");
            return;
        }
        if (typeof data.name !== "string" || !data.name.trim()) {
            showMessage(bugMessage, "Unable to load project name. Invalid server response.", "error");
            return;
        }

        backToProjectLink.textContent = data.name;
        backToProjectLink.hidden = false;
    } catch (error) {
        showMessage(bugMessage, "Unable to load project name. Please refresh the page.", "error");
    }
}

loadBug().then(function(loaded) {
    if (loaded) loadProjectNavigation();
});

window.addEventListener("pageshow", async function(event) {
    if (!localStorage.getItem("access_token")) {
        redirectToLogin();
        return;
    }

    if (event.persisted) {
        showMessage(bugMessage, "");
        showMessage(editBugMessage, "");

        if (lifecycleGuidance.textContent === qaSelectionValidationMessage) {
            lifecycleGuidance.textContent = "";
        }

        await loadBug(true);
    }
});
