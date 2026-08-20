const form = document.querySelector("#login-form");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const message = document.querySelector("#message");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const user = {
        email: emailInput.value,
        password: passwordInput.value
    };

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
        message.textContent = "Login successful.";
    } else {
        message.textContent = data.detail;
    }
});
