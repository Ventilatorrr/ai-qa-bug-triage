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


if (!accessToken) {
    window.location.href = "/login.html";
} else {
    loadProject();
    loadMembers();
}
