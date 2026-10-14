function logout() {
    localStorage.removeItem("access_token");
    window.location.replace("/login.html");
}

const logoutButton = document.querySelector("#logout-button");

logoutButton.addEventListener("click", logout);

// Public informational pages support both guest and authenticated navigation.
const guestAccountActions = document.querySelector("#guest-account-actions");
if (guestAccountActions) {
    const isLoggedIn = Boolean(localStorage.getItem("access_token"));
    guestAccountActions.hidden = isLoggedIn;
    logoutButton.hidden = !isLoggedIn;
    document.querySelector("#about-projects-link").hidden = !isLoggedIn;
    const aboutProjectNavigation = document.querySelector("#about-project-navigation");
    if (aboutProjectNavigation) aboutProjectNavigation.hidden = !isLoggedIn;
}
