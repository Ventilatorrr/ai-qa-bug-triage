const projectsContainer = document.querySelector("#projects");
const message = document.querySelector("#message");

async function loadProjects() {
    const accessToken = localStorage.getItem("access_token");

    const response = await fetch("/projects", {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const data = await response.json();

    if (response.ok) {
        projectsContainer.innerHTML = "";

        data.forEach(function (project) {
            const projectElement = document.createElement("p");

            projectElement.textContent = project.name;

            projectsContainer.appendChild(projectElement);
        });
    } else {
        message.textContent = data.detail;
    }
}

loadProjects();
