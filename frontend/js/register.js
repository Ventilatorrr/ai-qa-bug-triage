const form = document.querySelector("#register-form");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const submitButton = document.querySelector("#register-form button[type='submit']");
const message = document.querySelector("#message");
let submissionInProgress = false;

function showRegisterMessage(text, type = "neutral") {
    message.classList.remove("message-success", "message-error");
    message.textContent = text;

    if (text && type === "success") {
        message.classList.add("message-success");
    } else if (text && type === "error") {
        message.classList.add("message-error");
    }
}

function setSubmissionInProgress(inProgress) {
    submissionInProgress = inProgress;
    submitButton.disabled = inProgress;
}

// The account already exists, so the form stays disabled rather than
// inviting a second registration that would only report a duplicate email.
function showManualLoginFallback() {
    showRegisterMessage(
        "Your account was created, but automatic login failed. Please log in to continue."
    );

    const loginLink = document.createElement("a");
    loginLink.href = "/login.html";
    loginLink.textContent = "Go to Login";
    message.append(" ", loginLink);
}

window.addEventListener("pageshow", function(event) {
    if (event.persisted) {
        showRegisterMessage("");
        setSubmissionInProgress(false);
    }
});

async function postCredentials(url, user) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(user)
    });

    return {response, data: await response.json()};
}

// Authenticates through the normal login endpoint and stores the token exactly
// as login.js does. Returns false when no token is obtained.
async function logInRegisteredUser(user) {
    try {
        const {response, data} = await postCredentials("/login", user);

        if (!response.ok || !data.access_token) {
            return false;
        }

        localStorage.setItem("access_token", data.access_token);
        window.location.replace("/projects.html");
        return true;
    } catch (error) {
        return false;
    }
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    if (submissionInProgress) {
        return;
    }

    setSubmissionInProgress(true);
    showRegisterMessage("");

    const user = {
        email: emailInput.value,
        password: passwordInput.value
    };

    try {
        const {response, data} = await postCredentials("/register", user);

        if (!response.ok) {
            showRegisterMessage(
                formatApiError(
                    data.detail,
                    "Registration failed. Please try again."
                ),
                "error"
            );
            setSubmissionInProgress(false);
            return;
        }
    } catch (error) {
        showRegisterMessage(
            "Unable to connect to the server. Please try again.",
            "error"
        );
        setSubmissionInProgress(false);
        return;
    }

    showRegisterMessage("Account created. Logging you in...", "success");

    if (!await logInRegisteredUser(user)) {
        showManualLoginFallback();
    }
});
