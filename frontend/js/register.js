const form = document.querySelector("#register-form");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const message = document.querySelector("#message");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    message.textContent = "";

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
            message.textContent = data.message;

            setTimeout(function () {
                window.location.href = "/login.html";
            }, 1000);
        } else if (response.status === 409) {
            message.textContent = data.detail;
        } else if (response.status === 422) {
            message.textContent = data.detail[0].msg;
        } else {
            message.textContent = "Registration failed. Please try again.";
        }
    } catch (error) {
        message.textContent = "Unable to connect to the server. Please try again.";
    }
});
