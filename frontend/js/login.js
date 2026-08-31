const form = document.querySelector("#login-form");
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
            window.location.href = "/projects.html";
        } else if (response.status === 422) {
            message.textContent = "Please enter a valid email address.";
        } else {
            message.textContent = data.detail;
        }
    } catch (error) {
        message.textContent = "Unable to connect to the server. Please try again.";
    }
});
