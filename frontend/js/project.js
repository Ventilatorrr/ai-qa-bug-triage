const params = new URLSearchParams(window.location.search);

const projectId = params.get("id");

const projectName = document.querySelector("#project-name");

const membersContainer = document.querySelector("#members");
const memberMessage = document.querySelector("#member-message");
const bugMessage = document.querySelector("#bug-message");

const membersContent = document.querySelector("#members-content");
const toggleMembersButton = document.querySelector("#toggle-members");

const memberManagement = document.querySelector("#member-management");
const showMemberFormButton = document.querySelector("#show-member-form");
const memberForm = document.querySelector("#member-form");
const cancelMemberFormButton = document.querySelector("#cancel-member-form");

const memberEmailInput = document.querySelector("#member-email");
const memberRoleInput = document.querySelector("#member-role");

const showBugFormButton = document.querySelector("#show-bug-form");
const bugForm = document.querySelector("#bug-form");
const cancelBugFormButton = document.querySelector("#cancel-bug-form");

const bugsContainer = document.querySelector("#bugs");

const bugTitleInput = document.querySelector("#bug-title");
const bugAffectedVersionInput =
    document.querySelector("#bug-affected-version");
const bugEnvironmentInput =
    document.querySelector("#bug-environment");
const bugDescriptionInput =
    document.querySelector("#bug-description");
const bugStepsInput =
    document.querySelector("#bug-steps");
const bugExpectedInput =
    document.querySelector("#bug-expected");
const bugActualInput =
    document.querySelector("#bug-actual");
const bugSeverityInput =
    document.querySelector("#bug-severity");
const bugPriorityInput =
    document.querySelector("#bug-priority");
const bugAssigneeInput =
    document.querySelector("#bug-assignee");
const bugFixVersionInput =
    document.querySelector("#bug-fix-version");

let projectMembers = [];

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

function showMemberMessage(text, type = "neutral") {
    memberMessage.classList.remove("message-success", "message-error");
    memberMessage.textContent = text;

    if (text && type === "success") {
        memberMessage.classList.add("message-success");
    } else if (text && type === "error") {
        memberMessage.classList.add("message-error");
    }
}

function getCurrentUserId() {
    const token = getCurrentAccessToken();

    if (!token) {
        return null;
    }

    const payload = token.split(".")[1];

    return JSON.parse(atob(payload)).user_id;
}


async function loadProject() {
    const response = await authenticatedFetch(`/projects/${projectId}`);

    if (!response) {
        return false;
    }

    const data = await response.json();

    if (response.ok) {
        projectName.textContent = data.name;
        return true;
    } else if (response.status === 404) {
        window.location.replace("/projects.html");
        return false;
    } else {
        bugMessage.textContent = formatApiError(data.detail);
        return false;
    }
}


async function loadMembers(preserveVisibleState = false) {
    if (!preserveVisibleState) {
        projectMembers = [];
        document.querySelector("#header-identity").hidden = true;
    }

    const response = await authenticatedFetch(`/projects/${projectId}/members`);

    if (!response) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        showMemberMessage(formatApiError(data.detail), "error");
        return null;
    }

    membersContainer.innerHTML = "";
    projectMembers = data;

    const currentUserId = getCurrentUserId();

    const currentUser = data.find(function (member) {
        return member.user_id === currentUserId;
    });

    if (currentUser) {
        const identity = document.querySelector("#header-identity");
        identity.textContent = `${currentUser.email} (${currentUser.role})`;
        identity.hidden = false;
    }

    if (
        currentUser &&
        currentUser.role === "Project Owner"
    ) {
        memberManagement.hidden = false;
    }

    data.forEach(function (member) {
        const memberElement =
            document.createElement("div");

        memberElement.className = "project";

        const memberInfo =
            document.createElement("div");

        const email =
            document.createElement("strong");

        email.textContent = member.email;

        const role =
            document.createElement("span");

        role.textContent =
            ` (${member.role})`;

        memberInfo.appendChild(email);
        memberInfo.appendChild(role);

        memberElement.appendChild(memberInfo);

        if (
            currentUser &&
            currentUser.role === "Project Owner" &&
            member.role !== "Project Owner"
        ) {
            const removeButton =
                document.createElement("button");

            removeButton.textContent = "Remove";

            removeButton.type = "button";
            removeButton.className = "context-action-button";

            removeButton.addEventListener(
                "click",
                function () {
                    removeMember(member);
                }
            );

            memberElement.appendChild(removeButton);
        }

        membersContainer.appendChild(
            memberElement
        );
    });

    updateMembersToggle();

    return currentUser;
}


function updateMembersToggle() {
    const isExpanded =
        toggleMembersButton.getAttribute(
            "aria-expanded"
        ) === "true";

    toggleMembersButton.textContent =
        isExpanded
            ? "Hide Members"
            : "Show Members";
}


async function addMember(event) {
    event.preventDefault();

    const member = {
        email: memberEmailInput.value,
        role: memberRoleInput.value
    };

    let response;
    let data = {};

    try {
        response = await authenticatedFetch(
            `/projects/${projectId}/members`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(member)
            }
        );

        if (!response) {
            return;
        }

        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }
    } catch (error) {
        showMemberMessage("Unable to add member. Please try again.", "error");
        return;
    }

    if (!response.ok) {
        showMemberMessage(formatApiError(data.detail), "error");
        return;
    }

    memberForm.reset();

    memberForm.hidden = true;

    showMemberFormButton.hidden = false;

    const addedEmail = typeof data.email === "string" ? data.email : member.email;
    const addedRole = typeof data.role === "string" ? data.role : member.role;

    showMemberMessage(
        `Member "${addedEmail}" (${addedRole}) added successfully.`,
        "success"
    );

    await loadMembers();

    await loadBugs();

    await loadBugAssignees();
}


async function removeMember(member) {
    const confirmed = confirm(
        `Are you sure you want to remove "${member.email}" from this project?`
    );

    if (!confirmed) {
        return;
    }

    let response;
    let data = {};

    try {
        response = await authenticatedFetch(
            `/projects/${projectId}/members/${member.user_id}`,
            {
                method: "DELETE"
            }
        );

        if (!response) {
            return;
        }

        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }
    } catch (error) {
        showMemberMessage("Unable to remove member. Please try again.", "error");
        return;
    }

    if (!response.ok) {
        showMemberMessage(formatApiError(data.detail), "error");
        return;
    }

    showMemberMessage(
        `Member "${member.email}" (${member.role}) removed successfully.`,
        "success"
    );

    await loadMembers();

    await loadBugs();

    await loadBugAssignees();
}


async function loadBugAssignees() {
    const response = await authenticatedFetch(`/projects/${projectId}/members`);

    if (!response) {
        return;
    }

    const data = await response.json();

    if (!response.ok) {
        bugMessage.textContent = formatApiError(data.detail);
        return;
    }

    bugAssigneeInput.innerHTML = "";

    const unassignedOption =
        document.createElement("option");

    unassignedOption.value = "";

    unassignedOption.textContent =
        "Unassigned";

    bugAssigneeInput.appendChild(
        unassignedOption
    );

    data.forEach(function (member) {
        if (
            member.role === "QA Analyst" ||
            member.role === "Developer"
        ) {
            const option =
                document.createElement("option");

            option.value = member.user_id;

            option.textContent =
                `${member.email} (${member.role})`;

            bugAssigneeInput.appendChild(
                option
            );
        }
    });

    updateSelectPromptStyle(bugAssigneeInput);
}


async function updateBugAssigneeVisibility() {
    const membersResponse = await authenticatedFetch(`/projects/${projectId}/members`);

    if (!membersResponse) {
        return;
    }

    const members =
        await membersResponse.json();

    if (!membersResponse.ok) {
        return;
    }

    const currentUserId =
        getCurrentUserId();

    const currentUser = members.find(
        function (member) {
            return member.user_id ===
                currentUserId;
        }
    );

    const assigneeLabel =
        document.querySelector(
            'label[for="bug-assignee"]'
        );

    if (
        currentUser &&
        (
            currentUser.role === "Project Owner" ||
            currentUser.role === "QA Analyst" ||
            currentUser.role === "Developer"
        )
    ) {
        bugAssigneeInput.hidden = false;
        assigneeLabel.hidden = false;
    } else {
        bugAssigneeInput.hidden = true;
        assigneeLabel.hidden = true;
    }
}


let projectBugs = [];
let bugSortColumn = "updated_at";
let bugSortDirection = "descending";

function showBugMessage(text, type = "neutral") {
    bugMessage.classList.remove("message-success", "message-error");
    bugMessage.textContent = text;

    if (text && type === "success") {
        bugMessage.classList.add("message-success");
    } else if (text && type === "error") {
        bugMessage.classList.add("message-error");
    }
}

function showBugDeletionFeedback() {
    try {
        const feedback = sessionStorage.getItem("bug-deletion-feedback");

        if (feedback) {
            sessionStorage.removeItem("bug-deletion-feedback");
            showBugMessage(feedback, "success");
        }
    } catch (error) {
        // The project page still works if session storage is unavailable.
    }
}

const severityOrder = ["Minor", "Moderate", "Major", "Blocker"];
const priorityOrder = ["Low", "Medium", "High", "Urgent"];
const statusOrder = ["Triage", "Open", "Development", "Testing", "Closed"];

function displayBugAssignee(assigneeId) {
    if (assigneeId == null || assigneeId === "") return "Unassigned";

    const member = projectMembers.find(function(member) {
        return member.user_id === assigneeId;
    });

    return member ? `${member.email} (${member.role})` : `User ${assigneeId}`;
}

function displayBugStatus(bug) {
    if (bug.status === "Closed" && bug.resolution) {
        return `Closed [${bug.resolution}]`;
    }

    return bug.status;
}

function compareBugs(first, second) {
    let firstValue = first[bugSortColumn];
    let secondValue = second[bugSortColumn];
    const firstMissing = firstValue == null || firstValue === "";
    const secondMissing = secondValue == null || secondValue === "";

    // Missing values stay last regardless of the selected direction.
    if (firstMissing && secondMissing) return 0;
    if (firstMissing) return 1;
    if (secondMissing) return -1;

    if (bugSortColumn === "severity") {
        firstValue = severityOrder.indexOf(firstValue);
        secondValue = severityOrder.indexOf(secondValue);
    } else if (bugSortColumn === "priority") {
        firstValue = priorityOrder.indexOf(firstValue);
        secondValue = priorityOrder.indexOf(secondValue);
    } else if (bugSortColumn === "status") {
        firstValue = statusOrder.indexOf(firstValue);
        secondValue = statusOrder.indexOf(secondValue);
    } else if (bugSortColumn === "updated_at") {
        firstValue = new Date(firstValue).getTime();
        secondValue = new Date(secondValue).getTime();
    } else if (bugSortColumn === "assignee_id") {
        firstValue = displayBugAssignee(firstValue);
        secondValue = displayBugAssignee(secondValue);
    }

    const comparison = typeof firstValue === "string"
        ? firstValue.toLowerCase().localeCompare(secondValue.toLowerCase())
        : firstValue - secondValue;

    return bugSortDirection === "ascending" ? comparison : -comparison;
}

async function loadBugs() {
    const response = await authenticatedFetch(`/projects/${projectId}/bugs`);

    if (!response) {
        return;
    }

    const data = await response.json();

    if (!response.ok) {
        bugMessage.textContent = formatApiError(data.detail);
        return;
    }

    projectBugs = data;
    renderBugs();
}

async function refreshProjectMemberAndBugData(preserveVisibleState = false) {
    try {
        await loadMembers(preserveVisibleState);
    } finally {
        await loadBugs();
    }
}

function renderBugs() {
    const data = [...projectBugs].sort(compareBugs);
    bugsContainer.innerHTML = "";

    if (data.length === 0) {
        const emptyMessage =
            document.createElement("p");

        emptyMessage.className =
            "page-description";

        emptyMessage.textContent =
            "No bugs in this project.";

        bugsContainer.appendChild(
            emptyMessage
        );

        return;
    }

    const table =
        document.createElement("table");

    table.className = "bug-table";

    const thead =
        document.createElement("thead");

    const headerRow =
        document.createElement("tr");

    const headers = [
        ["id", "Bug ID"],
        ["title", "Title"],
        ["severity", "Severity"],
        ["priority", "Priority"],
        ["status", "Status"],
        ["assignee_id", "Assignee"],
        ["updated_at", "Last Updated"]
    ];

    headers.forEach(function ([column, headerText]) {
        const th =
            document.createElement("th");

        th.scope = "col";
        const active = column === bugSortColumn;
        th.setAttribute("aria-sort", active ? bugSortDirection : "none");

        const button = document.createElement("button");
        button.type = "button";
        button.className = "bug-sort-button";
        button.dataset.sortColumn = column;
        button.textContent = headerText + (active
            ? (bugSortDirection === "ascending" ? " ↑" : " ↓")
            : "");
        button.addEventListener("click", function () {
            bugSortDirection = column === bugSortColumn && bugSortDirection === "ascending"
                ? "descending"
                : "ascending";
            bugSortColumn = column;
            renderBugs();
            bugsContainer.querySelector(`[data-sort-column="${column}"]`).focus();
        });
        th.appendChild(button);

        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);

    table.appendChild(thead);


    const tbody =
        document.createElement("tbody");

    data.forEach(function (bug) {
        const row =
            document.createElement("tr");


        /* Bug ID */

        const bugIdCell =
            document.createElement("td");

        const bugLink =
            document.createElement("a");

        bugLink.href =
            `/bugs.html?project_id=${projectId}&bug_id=${bug.id}`;

        bugLink.textContent =
            `BUG-${bug.id}`;

        bugLink.className =
            "bug-link";

        bugIdCell.appendChild(bugLink);


        /* Title */

        const titleCell =
            document.createElement("td");

        titleCell.textContent = bug.title;


        /* Severity */

        const severityCell =
            document.createElement("td");

        severityCell.textContent =
            bug.severity || "—";

        if (bug.severity) {
            severityCell.classList.add(
                `bug-severity-${bug.severity.toLowerCase()}`
            );
        }


        /* Priority */

        const priorityCell =
            document.createElement("td");

        priorityCell.textContent =
            bug.priority || "—";

        if (bug.priority) {
            priorityCell.classList.add(
                `bug-priority-${bug.priority.toLowerCase()}`
            );
        }


        /* Status */

        const statusCell =
            document.createElement("td");

        statusCell.textContent =
            displayBugStatus(bug);


        /* Assignee */

        const assigneeCell =
            document.createElement("td");

        assigneeCell.textContent =
            displayBugAssignee(bug.assignee_id);


        /* Last Updated */

        const updatedCell =
            document.createElement("td");

        updatedCell.textContent =
            formatDateTime(
                bug.updated_at
            );


        /* Add cells */

        row.appendChild(bugIdCell);

        row.appendChild(titleCell);

        row.appendChild(severityCell);

        row.appendChild(priorityCell);

        row.appendChild(statusCell);

        row.appendChild(assigneeCell);

        row.appendChild(updatedCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);

    bugsContainer.appendChild(table);
}


function formatDateTime(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    return date.toLocaleString();
}


/* =========================================================
   Members Toggle
   ========================================================= */

toggleMembersButton.addEventListener(
    "click",
    function () {
        const isExpanded =
            toggleMembersButton.getAttribute(
                "aria-expanded"
            ) === "true";

        membersContent.hidden =
            isExpanded;

        toggleMembersButton.setAttribute(
            "aria-expanded",
            String(!isExpanded)
        );

        updateMembersToggle();
    }
);


/* =========================================================
   Member Form
   ========================================================= */

showMemberFormButton.addEventListener(
    "click",
    function () {
        memberForm.hidden = false;

        showMemberFormButton.hidden = true;
    }
);


cancelMemberFormButton.addEventListener(
    "click",
    function () {
        memberForm.reset();

        memberForm.hidden = true;

        showMemberFormButton.hidden = false;

        showMemberMessage("");
    }
);


memberForm.addEventListener(
    "submit",
    addMember
);


/* =========================================================
   Bug Form
   ========================================================= */

function updateSelectPromptStyle(selectInput) {
    selectInput.classList.toggle(
        "select-prompt",
        selectInput.value === ""
    );
}


bugSeverityInput.addEventListener("change", function () {
    updateSelectPromptStyle(bugSeverityInput);
});


bugPriorityInput.addEventListener("change", function () {
    updateSelectPromptStyle(bugPriorityInput);
});


bugAssigneeInput.addEventListener("change", function () {
    updateSelectPromptStyle(bugAssigneeInput);
});


showBugFormButton.addEventListener(
    "click",
    async function () {
        bugForm.hidden = false;

        showBugFormButton.hidden = true;

        await loadBugAssignees();

        await updateBugAssigneeVisibility();
    }
);


cancelBugFormButton.addEventListener(
    "click",
    function () {
        bugForm.reset();
        updateSelectPromptStyle(bugSeverityInput);
        updateSelectPromptStyle(bugPriorityInput);
        updateSelectPromptStyle(bugAssigneeInput);

        bugForm.hidden = true;

        showBugFormButton.hidden = false;

        bugMessage.textContent = "";
    }
);


bugForm.addEventListener(
    "submit",
    async function (event) {
        event.preventDefault();

        const bug = {
            title:
                bugTitleInput.value,

            affected_version:
                bugAffectedVersionInput.value ||
                null,

            environment:
                bugEnvironmentInput.value ||
                null,

            description:
                bugDescriptionInput.value ||
                null,

            steps_to_reproduce:
                bugStepsInput.value ||
                null,

            expected_result:
                bugExpectedInput.value ||
                null,

            actual_result:
                bugActualInput.value ||
                null,

            severity:
                bugSeverityInput.value ||
                null,

            priority:
                bugPriorityInput.value ||
                null,

            assignee_id:
                bugAssigneeInput.value
                    ? Number(
                        bugAssigneeInput.value
                    )
                    : null,

            fix_version:
                bugFixVersionInput.value ||
                null
        };

        const response = await authenticatedFetch(
            `/projects/${projectId}/bugs`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(bug)
            }
        );

        if (!response) {
            return;
        }

        const data = await response.json();

        if (response.ok) {
            bugForm.reset();
            updateSelectPromptStyle(bugSeverityInput);
            updateSelectPromptStyle(bugPriorityInput);
            updateSelectPromptStyle(bugAssigneeInput);

            bugForm.hidden = true;

            showBugFormButton.hidden = false;

            showBugMessage(
                `BUG-${data.id} "${data.title}" created successfully.`,
                "success"
            );

            await loadBugs();
        } else {
            showBugMessage(formatApiError(data.detail), "error");
        }
    }
);


/* =========================================================
   Initial Load
   ========================================================= */

if (!localStorage.getItem("access_token")) {
    redirectToLogin();
} else {
    showBugDeletionFeedback();
    loadProject();

    refreshProjectMemberAndBugData().catch(function() {
        showMemberMessage("Unable to load project members. Please refresh the page.", "error");
    });

    window.addEventListener("pageshow", async function(event) {
        if (!localStorage.getItem("access_token")) {
            redirectToLogin();
            return;
        }

        if (!event.persisted) {
            return;
        }

        showMemberMessage("");
        showBugMessage("");

        try {
            const projectExists = await loadProject();

            if (projectExists) {
                await refreshProjectMemberAndBugData(true);
            }
        } catch (error) {
            showBugMessage("Unable to refresh this project. Please refresh the page.", "error");
        }
    });
}
