import {authenticatedFetch, getCurrentUserId, redirectToLogin} from "./auth.js";

const projectsContainer = document.querySelector("#projects");
const message = document.querySelector("#message");
const projectForm = document.querySelector("#project-form");

const showProjectFormButton = document.querySelector("#show-project-form");
const cancelProjectFormButton = document.querySelector("#cancel-project-form");
const createProjectButton = document.querySelector("#create-project-button");
let editingProjectId = null;
// Edit row of that session; list refreshes keep it so unsaved typing survives.
let editingProjectElement = null;
// Project id -> locked edit row whose rename Save is still pending.
const pendingProjectSaves = new Map();
let projectFormFeedback = null;
// Opening or cancelling New Project starts a new form interaction.
let projectFormSession = 0;
let projectListLoad = 0;


if (!localStorage.getItem("access_token")) {
    redirectToLogin();
}

function showProjectMessage(text, type = "neutral", formFeedback = null) {
    projectFormFeedback = text ? formFeedback : null;
    message.classList.remove("message-success", "message-error");
    message.textContent = text;

    if (text && type === "success") {
        message.classList.add("message-success");
    } else if (text && type === "error") {
        message.classList.add("message-error");
    }
}

function clearProjectFormFeedback(context = null, nameValidationOnly = false) {
    if (projectFormFeedback &&
        (context === null || projectFormFeedback.context === context) &&
        (!nameValidationOnly || projectFormFeedback.nameValidation)) {
        showProjectMessage("");
    }
}

function clearCorrectedProjectNameFeedback(input, context) {
    if (input.value.trim()) {
        clearProjectFormFeedback(context, true);
    }
}


async function getProjectRole(projectId) {
    const response = await authenticatedFetch(`/projects/${projectId}/members`);

    if (!response) {
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
    // Overlapping refreshes must not interleave rows; only the latest renders.
    const load = ++projectListLoad;
    const response = await authenticatedFetch("/projects");

    if (!response) {
        return;
    }

    const data = await response.json();

    if (load !== projectListLoad) {
        return;
    }

    if (response.ok) {
        const projectElements = [];

        for (const project of data) {
            // Keep a pending Save's locked row; its response settles that row.
            if (pendingProjectSaves.has(project.id)) {
                projectElements.push(pendingProjectSaves.get(project.id));
                continue;
            }

            const role = await getProjectRole(project.id);

            if (editingProjectId === project.id && role === "Project Owner") {
                projectElements.push(editingProjectElement);
                continue;
            }

            const projectElement = document.createElement("div");
            renderProjectView(projectElement, project, role);
            projectElements.push(projectElement);
        }

        if (load === projectListLoad) {
            projectsContainer.replaceChildren(...projectElements);
        }
    } else {
        showProjectMessage(formatApiError(data.detail), "error");
    }
}


loadProjects();

window.addEventListener("pageshow", function(event) {
    if (!localStorage.getItem("access_token")) {
        redirectToLogin();
        return;
    }

    if (event.persisted) {
        showProjectMessage("");
    }
});


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
        editButton.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="1.8" stroke-linecap="round"
                stroke-linejoin="round" aria-hidden="true" focusable="false">
                <path d="M15 5l4 4M4 16l11-11a2.828 2.828 0 0 1 4 4L8 20l-5 1 1-5Z" />
                <path d="M4 16l4 4" />
            </svg>`;
        editButton.setAttribute("aria-label", `Edit project ${project.name}`);
        editButton.title = `Edit project ${project.name}`;
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
    projectNameInput.addEventListener("input", function () {
        clearCorrectedProjectNameFeedback(projectNameInput, project.id);
    });

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
    clearProjectFormFeedback();
    editingProjectId = project.id;
    editingProjectElement = projectElement;
    renderProjectEdit(projectElement, project);
}


function cancelProjectEdit(project, projectElement) {
    clearProjectFormFeedback(project.id);
    editingProjectId = null;
    renderProjectView(projectElement, project, "Project Owner");
}


function setProjectEditPending(projectElement, projectNameInput, pending) {
    projectNameInput.readOnly = pending;

    for (const button of projectElement.querySelectorAll("button")) {
        button.disabled = pending;
    }
}


async function saveProjectEdit(project, projectNameInput, projectElement) {
    // One Save per edit: while the PUT is pending the row is locked, so newer
    // typing, Cancel, Delete or another Save cannot race the earlier response.
    if (projectNameInput.readOnly) {
        return;
    }

    const newName = projectNameInput.value;

    if (!newName.trim()) {
        showProjectMessage("Project name is required.", "error", {
            context: project.id, nameValidation: true
        });
        return;
    }

    setProjectEditPending(projectElement, projectNameInput, true);
    pendingProjectSaves.set(project.id, projectElement);

    try {
        const response = await authenticatedFetch(`/projects/${project.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: newName
            })
        });

        if (!response) {
            return;
        }

        const data = await response.json();

        if (response.ok) {
            clearProjectFormFeedback(project.id);
            // A late Save must not end another project's newer edit session.
            if (editingProjectId === project.id) {
                editingProjectId = null;
            }
            renderProjectView(projectElement, data, "Project Owner");
        } else {
            showProjectMessage(formatApiError(data.detail), "error", response.status === 422 ? {
                context: project.id, nameValidation: data.detail === "Project name is required."
            } : null);
        }
    } catch (error) {
        showProjectMessage("Unable to save project. Please try again.", "error");
    } finally {
        // After success the row has been re-rendered, so this only affects a retry.
        setProjectEditPending(projectElement, projectNameInput, false);
        pendingProjectSaves.delete(project.id);
    }
}


async function deleteProject(project, projectElement) {
    const confirmed = confirm(
        `Are you sure you want to delete "${project.name}"?`
    );

    if (!confirmed) {
        return;
    }

    const response = await authenticatedFetch(`/projects/${project.id}`, {
        method: "DELETE"
    });

    if (!response) {
        return;
    }

    const data = await response.json();

    if (response.ok) {
        editingProjectId = null;
        projectElement.remove();
        try {
            sessionStorage.removeItem(`bug-list-sort:${getCurrentUserId()}:${project.id}`);
        } catch (error) {
            // Successful deletion must not depend on session storage availability.
        }
        showProjectMessage(
            `Project "${project.name}" deleted successfully.`,
            "success"
        );
    } else {
        showProjectMessage(formatApiError(data.detail), "error");
    }
}


showProjectFormButton.addEventListener("click", function () {
    clearProjectFormFeedback();
    ++projectFormSession;
    createProjectButton.disabled = false;
    projectForm.hidden = false;
    showProjectFormButton.hidden = true;
});


cancelProjectFormButton.addEventListener("click", function () {
    clearProjectFormFeedback("create");
    ++projectFormSession;
    createProjectButton.disabled = false;
    projectForm.reset();
    projectForm.hidden = true;
    showProjectFormButton.hidden = false;
});

document.querySelector("#project-name").addEventListener("input", function (event) {
    clearCorrectedProjectNameFeedback(event.target, "create");
});


projectForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    // One Create per form interaction: repeated clicks or Enter must not send
    // another POST while the first is pending.
    if (createProjectButton.disabled) {
        return;
    }

    const projectName = document.querySelector("#project-name").value;

    if (!projectName.trim()) {
        showProjectMessage("Project name is required.", "error", {
            context: "create", nameValidation: true
        });
        return;
    }

    const session = projectFormSession;
    createProjectButton.disabled = true;

    try {
        const response = await authenticatedFetch("/projects", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: projectName
            })
        });

        if (!response) {
            return;
        }

        const data = await response.json();

        if (session !== projectFormSession) {
            // A cancelled Create may still have saved a project: refresh the
            // list without touching the newer form or its feedback.
            if (response.ok) loadProjects();
            return;
        }

        if (response.ok) {
            projectForm.reset();
            projectForm.hidden = true;
            showProjectFormButton.hidden = false;
            showProjectMessage(
                `Project "${data.name}" created successfully.`,
                "success",
                {context: "create"}
            );
            loadProjects();
        } else {
            showProjectMessage(formatApiError(data.detail), "error", response.status === 422 ? {
                context: "create", nameValidation: data.detail === "Project name is required."
            } : null);
        }
    } catch (error) {
        if (session === projectFormSession) {
            showProjectMessage("Unable to create project. Please try again.", "error");
        }
    } finally {
        // A late completion must not unlock a newer interaction's pending Create.
        if (session === projectFormSession) {
            createProjectButton.disabled = false;
        }
    }
});
