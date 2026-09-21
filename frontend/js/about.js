async function loadApplicationVersion() {
    const versionElement = document.querySelector("#app-version");

    try {
        const response = await fetch("/version");
        if (!response.ok) {
            throw new Error("Unable to load application version.");
        }

        const data = await response.json();
        versionElement.textContent = data.version;
    } catch (error) {
        versionElement.textContent = "Unavailable";
    }
}

loadApplicationVersion();
