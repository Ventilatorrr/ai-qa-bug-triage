const params = new URLSearchParams(window.location.search);
const projectId = params.get("id");

const projectName = document.querySelector("#project-name");

async function loadProject() {
    const accessToken = localStorage.getItem("access_token");

    const response = await fetch(`/projects/${projectId}`, {
        headers: {
            "Authorization": "Bearer " + accessToken
        }
    });

    const data = await response.json();

    if (response.ok) {
        projectName.textContent = data.name;
    } else {
        projectName.textContent = data.detail;
    }
}

loadProject();
