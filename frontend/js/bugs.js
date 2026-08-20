const form = document.querySelector("form");
const titleInput = document.querySelector("#title");
const emailInput = document.querySelector("#email");
const descriptionInput = document.querySelector("#description");
const message = document.querySelector("#message");

function getBugData() {
    return {
        title: titleInput.value,
        email: emailInput.value,
        description: descriptionInput.value
    };
}

function submitBug(bug) {
    console.log(bug);
    message.textContent = "Bug submitted successfully!";
}

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const bug = getBugData();

    submitBug(bug);
});

