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
const bugAffectedVersionInput = document.querySelector("#bug-affected-version");
const bugDescriptionInput = document.querySelector("#bug-description");
const bugStepsInput = document.querySelector("#bug-steps");
const bugExpectedInput = document.querySelector("#bug-expected");
const bugActualInput = document.querySelector("#bug-actual");
const bugSeverityInput = document.querySelector("#bug-severity");
const bugPriorityInput = document.querySelector("#bug-priority");
const bugAssigneeInput = document.querySelector("#bug-assignee");
const bugFixVersionInput = document.querySelector("#bug-fix-version");

const accessToken = localStorage.getItem("access_token");


function getCurrentUserId() {
    if (!accessToken) {
        return null;
    }

    const payload = accessToken.split(".")[1];

    return JSON.parse(atob(payload)).user_id;
}


async function loadProject() {
    const response = await fetch(`/projects/${projectId}`, {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const data = await response.json();

    if (response.ok) {
        projectName.textContent = data.name;
    } else {
        bugMessage.textContent = data.detail;
    }
}


async function loadMembers() {
    const response = await fetch(`/projects/${projectId}/members`, {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const data = await response.json();

    if (!response.ok) {
        memberMessage.textContent = data.detail;
        return null;
    }

    membersContainer.innerHTML = "";

    const currentUserId = getCurrentUserId();

    const currentUser = data.find(function (member) {
        return member.user_id === currentUserId;
    });

    if (currentUser && currentUser.role === "Project Owner") {
        memberManagement.hidden = false;
    }

    data.forEach(function (member) {
        const memberElement = document.createElement("div");

        memberElement.className = "project";

        const memberInfo = document.createElement("div");

        const email = document.createElement("strong");

        email.textContent = member.email;

        const role = document.createElement("span");

        role.textContent = ` (${member.role})`;

        memberInfo.appendChild(email);
        memberInfo.appendChild(role);

        memberElement.appendChild(memberInfo);

        if (
            currentUser &&
            currentUser.role === "Project Owner" &&
            member.role !== "Project Owner"
        ) {
            const removeButton = document.createElement("button");

            removeButton.textContent = "Remove";
            removeButton.type = "button";

            removeButton.addEventListener("click", function () {
                removeMember(member);
            });

            memberElement.appendChild(removeButton);
        }

        membersContainer.appendChild(memberElement);
    });

    updateMembersToggle(data.length);

    return currentUser;
}


function updateMembersToggle(memberCount) {
    toggleMembersButton.textContent = `Show Members (${memberCount})`;
}


async function addMember(event) {
    event.preventDefault();

    const member = {
        email: memberEmailInput.value,
        role: memberRoleInput.value
    };

    const response = await fetch(`/projects/${projectId}/members`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + accessToken
        },
        body: JSON.stringify(member)
    });

    const data = await response.json();

    if (response.ok) {
        memberForm.reset();
        memberForm.hidden = true;
        showMemberFormButton.hidden = false;

        memberMessage.textContent = "Member added successfully.";

        await loadMembers();
        await loadBugs();
        await loadBugAssignees();
    } else {
        memberMessage.textContent = data.detail;
    }
}


async function removeMember(member) {
    const confirmed = confirm(
        `Are you sure you want to remove "${member.email}" from this project?`
    );

    if (!confirmed) {
        return;
    }

    const response = await fetch(
        `/projects/${projectId}/members/${member.user_id}`,
        {
            method: "DELETE",
            headers: {
                "Authorization": "Bearer " + accessToken
            }
        }
    );

    const data = await response.json();

    if (response.ok) {
        memberMessage.textContent = "Member removed successfully.";

        await loadMembers();
        await loadBugs();
        await loadBugAssignees();
    } else {
        memberMessage.textContent = data.detail;
    }
}


async function loadBugAssignees() {
    const response = await fetch(`/projects/${projectId}/members`, {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const data = await response.json();

    if (!response.ok) {
        bugMessage.textContent = data.detail;
        return;
    }

    bugAssigneeInput.innerHTML = "";

    const unassignedOption = document.createElement("option");

    unassignedOption.value = "";
    unassignedOption.textContent = "Unassigned";

    bugAssigneeInput.appendChild(unassignedOption);

    data.forEach(function (member) {
        if (
            member.role === "QA Analyst" ||
            member.role === "Developer"
        ) {
            const option = document.createElement("option");

            option.value = member.user_id;
            option.textContent = `${member.email} (${member.role})`;

            bugAssigneeInput.appendChild(option);
        }
    });
}


async function updateBugAssigneeVisibility() {
    const membersResponse = await fetch(`/projects/${projectId}/members`, {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const members = await membersResponse.json();

    if (!membersResponse.ok) {
        return;
    }

    const currentUserId = getCurrentUserId();

    const currentUser = members.find(function (member) {
        return member.user_id === currentUserId;
    });

    const assigneeLabel = document.querySelector(
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


async function loadBugs() {
    const response = await fetch(`/projects/${projectId}/bugs`, {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const data = await response.json();

    if (!response.ok) {
        bugMessage.textContent = data.detail;
        return;
    }

    bugsContainer.innerHTML = "";

    if (data.length === 0) {
        const emptyMessage = document.createElement("p");

        emptyMessage.className = "page-description";
        emptyMessage.textContent = "No bugs in this project.";

        bugsContainer.appendChild(emptyMessage);

        return;
    }

    const table = document.createElement("table");

    table.className = "bug-table";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    const headers = [
        "Bug ID",
        "Title",
        "Severity",
        "Priority",
        "Status",
        "Assignee",
        "Last Updated"
    ];

    headers.forEach(function (headerText) {
        const th = document.createElement("th");

        th.textContent = headerText;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    data.forEach(function (bug) {
        const row = document.createElement("tr");

        const bugIdCell = document.createElement("td");
        const bugLink = document.createElement("a");

        bugLink.href = `/bugs.html?project_id=${projectId}&bug_id=${bug.id}`;
        bugLink.textContent = `BUG-${bug.id}`;
        bugLink.className = "bug-link";

        bugIdCell.appendChild(bugLink);

        const titleCell = document.createElement("td");
        titleCell.textContent = bug.title;

        const severityCell = document.createElement("td");
        severityCell.textContent = bug.severity || "—";

        const priorityCell = document.createElement("td");
        priorityCell.textContent = bug.priority || "—";

        const statusCell = document.createElement("td");
        statusCell.textContent = bug.status;

        const assigneeCell = document.createElement("td");
        assigneeCell.textContent = bug.assignee_id
            ? `User ${bug.assignee_id}`
            : "Unassigned";

        const updatedCell = document.createElement("td");
        updatedCell.textContent = formatDateTime(bug.updated_at);

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


toggleMembersButton.addEventListener("click", function () {
    const isExpanded = toggleMembersButton.getAttribute("aria-expanded") === "true";

    membersContent.hidden = isExpanded;

    toggleMembersButton.setAttribute(
        "aria-expanded",
        String(!isExpanded)
    );

    const memberCount = membersContainer.children.length;

    if (isExpanded) {
        toggleMembersButton.textContent = `Show Members (${memberCount})`;
    } else {
        toggleMembersButton.textContent = `Hide Members (${memberCount})`;
    }
});


showMemberFormButton.addEventListener("click", function () {
    memberForm.hidden = false;
    showMemberFormButton.hidden = true;
});


cancelMemberFormButton.addEventListener("click", function () {
    memberForm.reset();
    memberForm.hidden = true;
    showMemberFormButton.hidden = false;
    memberMessage.textContent = "";
});


memberForm.addEventListener("submit", addMember);


showBugFormButton.addEventListener("click", async function () {
    bugForm.hidden = false;
    showBugFormButton.hidden = true;

    await loadBugAssignees();
    await updateBugAssigneeVisibility();
});


cancelBugFormButton.addEventListener("click", function () {
    bugForm.reset();
    bugForm.hidden = true;
    showBugFormButton.hidden = false;
    bugMessage.textContent = "";
});


bugForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const bug = {
        title: bugTitleInput.value,
        affected_version: bugAffectedVersionInput.value || null,
        description: bugDescriptionInput.value || null,
        steps_to_reproduce: bugStepsInput.value || null,
        expected_result: bugExpectedInput.value || null,
        actual_result: bugActualInput.value || null,
        severity: bugSeverityInput.value || null,
        priority: bugPriorityInput.value || null,
        assignee_id: bugAssigneeInput.value
            ? Number(bugAssigneeInput.value)
            : null,
        fix_version: bugFixVersionInput.value || null
    };

    const response = await fetch(`/projects/${projectId}/bugs`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + accessToken
        },
        body: JSON.stringify(bug)
    });

    const data = await response.json();

    if (response.ok) {
        bugForm.reset();
        bugForm.hidden = true;
        showBugFormButton.hidden = false;

        bugMessage.textContent = `Bug #${data.id} created successfully.`;

        await loadBugs();
    } else {
        bugMessage.textContent = data.detail;
    }
});


if (!accessToken) {
    window.location.href = "/login.html";
} else {
    loadProject();
    loadMembers();
    loadBugs();
}

