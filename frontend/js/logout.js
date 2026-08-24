function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login.html";
}

const logoutButton = document.querySelector("#logout-button");

logoutButton.addEventListener("click", logout);
