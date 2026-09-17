const form = document.querySelector("#login-form");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const message = document.querySelector("#message");
let authenticatedRedirectInProgress = false;

function showLoginMessage(text, type = "neutral") {
    message.classList.remove("message-success", "message-error");
    message.textContent = text;

    if (text && type === "success") {
        message.classList.add("message-success");
    } else if (text && type === "error") {
        message.classList.add("message-error");
    }
}

function redirectAuthenticatedUser() {
    if (!localStorage.getItem("access_token")) {
        return false;
    }

    if (!authenticatedRedirectInProgress) {
        authenticatedRedirectInProgress = true;
        window.location.replace("/projects.html");
    }

    return true;
}

redirectAuthenticatedUser();

window.addEventListener("pageshow", function(event) {
    if (redirectAuthenticatedUser()) {
        return;
    }

    if (event.persisted) {
        showLoginMessage("");
    }
});

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    showLoginMessage("");

    const user = {
        email: emailInput.value,
        password: passwordInput.value
    };

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(user)
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", data.access_token);
            authenticatedRedirectInProgress = true;
            window.location.replace("/projects.html");
        } else {
            showLoginMessage(formatApiError(data.detail), "error");
        }
    } catch (error) {
        showLoginMessage(
            "Unable to connect to the server. Please try again.",
            "error"
        );
    }
});
