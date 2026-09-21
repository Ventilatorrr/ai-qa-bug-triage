const form = document.querySelector("#register-form");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const message = document.querySelector("#message");

function showRegisterMessage(text, type = "neutral") {
    message.classList.remove("message-success", "message-error");
    message.textContent = text;

    if (text && type === "success") {
        message.classList.add("message-success");
    } else if (text && type === "error") {
        message.classList.add("message-error");
    }
}

window.addEventListener("pageshow", function(event) {
    if (event.persisted) {
        showRegisterMessage("");
    }
});

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    showRegisterMessage("");

    const user = {
        email: emailInput.value,
        password: passwordInput.value
    };

    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(user)
        });

        const data = await response.json();

        if (response.ok) {
            showRegisterMessage(data.message, "success");

            setTimeout(function () {
                window.location.href = "/login.html";
            }, 1000);
        } else {
            showRegisterMessage(
                formatApiError(
                    data.detail,
                    "Registration failed. Please try again."
                ),
                "error"
            );
        }
    } catch (error) {
        showRegisterMessage(
            "Unable to connect to the server. Please try again.",
            "error"
        );
    }
});
