const projectsContainer = document.querySelector("#projects");
const message = document.querySelector("#message");
const projectForm = document.querySelector("#project-form");

const accessToken = localStorage.getItem("access_token");

const showProjectFormButton = document.querySelector("#show-project-form");
const cancelProjectFormButton = document.querySelector("#cancel-project-form");
let editingProjectId = null;


if (!accessToken) {
    window.location.href = "/login.html";
}

function showProjectMessage(text, type = "neutral") {
    message.classList.remove("message-success", "message-error");
    message.textContent = text;

    if (text && type === "success") {
        message.classList.add("message-success");
    } else if (text && type === "error") {
        message.classList.add("message-error");
    }
}

function getCurrentUserId() {
    const payload = accessToken.split(".")[1];

    return JSON.parse(atob(payload)).user_id;
}


async function getProjectRole(projectId) {
    const response = await fetch(`/projects/${projectId}/members`, {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login.html";
        return null;
    }

    if (!response.ok) {
        return null;
    }

    const members = await response.json();
    const currentUserId = getCurrentUserId();

    const currentUser = members.find(function (member) {
        return member.user_id === currentUserId;
    });

    if (!currentUser) {
        return null;
    }

    const identity = document.querySelector("#header-identity");
    identity.textContent = currentUser.email;
    identity.hidden = false;

    return currentUser.role;
}


async function loadProjects() {
    const response = await fetch("/projects", {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login.html";
        return;
    }

    const data = await response.json();

    if (response.ok) {
        projectsContainer.innerHTML = "";

        for (const project of data) {
            const role = await getProjectRole(project.id);

            const projectElement = document.createElement("div");

            if (editingProjectId === project.id && role === "Project Owner") {
                renderProjectEdit(projectElement, project);
            } else {
                renderProjectView(projectElement, project, role);
            }

            projectsContainer.appendChild(projectElement);
        }
    } else {
        showProjectMessage(formatApiError(data.detail), "error");
    }
}


loadProjects();


function renderProjectView(projectElement, project, role) {
    projectElement.className = "project";
    projectElement.innerHTML = "";

    const projectLink = document.createElement("a");
    projectLink.textContent = project.name;
    projectLink.className = "project-name";
    projectLink.href = `/project.html?id=${project.id}`;

    projectElement.appendChild(projectLink);

    if (role === "Project Owner") {
        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.type = "button";
        editButton.className = "project-edit-button context-action-button";
        editButton.addEventListener("click", function () {
            startProjectEdit(project, projectElement);
        });

        const projectButtons = document.createElement("div");
        projectButtons.className = "project-buttons equal-action-buttons";
        projectButtons.appendChild(editButton);

        projectElement.appendChild(projectButtons);
    }
}


function renderProjectEdit(projectElement, project) {
    projectElement.className = "project project-editing";
    projectElement.innerHTML = "";

    const projectNameInput = document.createElement("input");
    projectNameInput.type = "text";
    projectNameInput.className = "form-input project-edit-input";
    projectNameInput.value = project.name;
    projectNameInput.setAttribute("aria-label", "Project name");

    const saveButton = document.createElement("button");
    saveButton.textContent = "Save";
    saveButton.type = "button";
    saveButton.className = "project-save-button context-action-button";
    saveButton.addEventListener("click", function () {
        saveProjectEdit(project, projectNameInput, projectElement);
    });

    const cancelButton = document.createElement("button");
    cancelButton.textContent = "Cancel";
    cancelButton.type = "button";
    cancelButton.className = "project-cancel-button context-action-button";
    cancelButton.addEventListener("click", function () {
        cancelProjectEdit(project, projectElement);
    });

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.type = "button";
    deleteButton.className = "project-delete-button context-action-button";
    deleteButton.addEventListener("click", function () {
        deleteProject(project, projectElement);
    });

    const projectButtons = document.createElement("div");
    projectButtons.className = "project-buttons equal-action-buttons";
    projectButtons.append(deleteButton, cancelButton, saveButton);

    projectElement.append(projectNameInput, projectButtons);
}


function startProjectEdit(project, projectElement) {
    editingProjectId = project.id;
    renderProjectEdit(projectElement, project);
}


function cancelProjectEdit(project, projectElement) {
    editingProjectId = null;
    renderProjectView(projectElement, project, "Project Owner");
}


async function saveProjectEdit(project, projectNameInput, projectElement) {
    const newName = projectNameInput.value;

    const response = await fetch(`/projects/${project.id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + accessToken
        },
        body: JSON.stringify({
            name: newName
        })
    });

    const data = await response.json();

    if (response.ok) {
        editingProjectId = null;
        renderProjectView(projectElement, data, "Project Owner");
    } else {
        showProjectMessage(formatApiError(data.detail), "error");
    }
}


async function deleteProject(project, projectElement) {
    const confirmed = confirm(
        `Are you sure you want to delete "${project.name}"?`
    );

    if (!confirmed) {
        return;
    }

    const response = await fetch(`/projects/${project.id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const data = await response.json();

    if (response.ok) {
        editingProjectId = null;
        projectElement.remove();
        showProjectMessage(
            `Project "${project.name}" deleted successfully.`,
            "success"
        );
    } else {
        showProjectMessage(formatApiError(data.detail), "error");
    }
}


showProjectFormButton.addEventListener("click", function () {
    projectForm.hidden = false;
    showProjectFormButton.hidden = true;
});


cancelProjectFormButton.addEventListener("click", function () {
    projectForm.reset();
    projectForm.hidden = true;
    showProjectFormButton.hidden = false;
});


projectForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const projectName = document.querySelector("#project-name").value;

    const response = await fetch("/projects", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + accessToken
        },
        body: JSON.stringify({
            name: projectName
        })
    });

    const data = await response.json();

    if (response.ok) {
        projectForm.reset();
        projectForm.hidden = true;
        showProjectFormButton.hidden = false;
        showProjectMessage(
            `Project "${data.name}" created successfully.`,
            "success"
        );
        loadProjects();
    } else {
        showProjectMessage(formatApiError(data.detail), "error");
    }
});
