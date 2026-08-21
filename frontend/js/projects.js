const projectsContainer = document.querySelector("#projects");
const message = document.querySelector("#message");

const projectForm = document.querySelector("#project-form");


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
            const projectElement = document.createElement("a");

            projectElement.textContent = project.name;
            projectElement.href = `/project.html?id=${project.id}`;

            projectsContainer.appendChild(projectElement);
        });
    } else {
        message.textContent = data.detail;
    }
}

loadProjects();


projectForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const projectName = document.querySelector("#project-name").value;

    const accessToken = localStorage.getItem("access_token");

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
        loadProjects();
    } else {
        message.textContent = data.detail;
    }
});
