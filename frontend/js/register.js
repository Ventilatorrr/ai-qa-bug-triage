const form = document.querySelector("#register-form");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const message = document.querySelector("#message");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const user = {
        email: emailInput.value,
        password: passwordInput.value
    };

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
    } else if (response.status === 409) {
        message.textContent = data.detail;
    } else if (response.status === 422) {
        message.textContent = data.detail[0].msg;
    }
});
