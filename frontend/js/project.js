const params = new URLSearchParams(window.location.search);
const projectId = params.get("id");

const projectName = document.querySelector("#project-name");
const membersContainer = document.querySelector("#members");
const message = document.querySelector("#message");

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
        message.textContent = data.detail;
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
        message.textContent = data.detail;
        return;
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

    return currentUser;
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
        message.textContent = "";
        loadMembers();
    } else {
        message.textContent = data.detail;
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
        message.textContent = "";
        loadMembers();
    } else {
        message.textContent = data.detail;
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
        message.textContent = data.detail;
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
            currentUser.role === "QA Analyst"
        )
    ) {
        bugAssigneeInput.hidden = false;
        assigneeLabel.hidden = false;
    } else {
        bugAssigneeInput.hidden = true;
        assigneeLabel.hidden = true;
    }
}

showMemberFormButton.addEventListener("click", function () {
    memberForm.hidden = false;
    showMemberFormButton.hidden = true;
});

cancelMemberFormButton.addEventListener("click", function () {
    memberForm.reset();
    memberForm.hidden = true;
    showMemberFormButton.hidden = false;
    message.textContent = "";
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
    message.textContent = "";
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
        message.textContent = `Bug #${data.id} created successfully.`;
    } else {
        message.textContent = data.detail;
    }
});

if (!accessToken) {
    window.location.href = "/login.html";
} else {
    loadProject();
    loadMembers();
}
