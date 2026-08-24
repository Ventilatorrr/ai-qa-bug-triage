const projectsContainer = document.querySelector("#projects");
const message = document.querySelector("#message");
const projectForm = document.querySelector("#project-form");
const accessToken = localStorage.getItem("access_token");
const showProjectFormButton = document.querySelector("#show-project-form");
const cancelProjectFormButton = document.querySelector("#cancel-project-form");

if (!accessToken) {
    window.location.href = "/login.html";
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

        data.forEach(function (project) {
            const projectElement = document.createElement("div");
            projectElement.className = "project";

            const projectLink = document.createElement("a");
            projectLink.textContent = project.name;
            projectLink.className = "project-name";
            projectLink.href = `/project.html?id=${project.id}`;

            const editButton = document.createElement("button");
            editButton.textContent = "Edit";
            editButton.type = "button";

            editButton.addEventListener("click", function () {
                editProject(project);
            });

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.type = "button";

            deleteButton.addEventListener("click", function () {
                deleteProject(project);
            });

            const projectButtons = document.createElement("div");
            projectButtons.className = "project-buttons";

            projectButtons.appendChild(editButton);
            projectButtons.appendChild(deleteButton);

            projectElement.appendChild(projectLink);
            projectElement.appendChild(projectButtons);

            projectsContainer.appendChild(projectElement);
        });
    } else {
        message.textContent = data.detail;
    }
}

loadProjects();

async function editProject(project) {
    const newName = prompt(
        "Enter the new project name:",
        project.name
    );

    if (newName === null) {
        return;
    }

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
        loadProjects();
    } else {
        if (response.status === 422) {
            message.textContent = "Project name can't be empty.";
        } else {
            message.textContent = data.detail;
        }
    }
}

async function deleteProject(project) {
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
        loadProjects();
    } else {
        message.textContent = data.detail;
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
        loadProjects();
    } else {
        message.textContent = data.detail;
    }
});
