const themeToggle = document.querySelector("#theme-toggle");

const savedTheme = localStorage.getItem("theme");

if (savedTheme === "light") {
    document.body.classList.add("light-theme");
    themeToggle.textContent = "☾";
}

themeToggle.addEventListener("click", function () {
    document.body.classList.toggle("light-theme");

    const isLightTheme = document.body.classList.contains("light-theme");

    if (isLightTheme) {
        localStorage.setItem("theme", "light");
        themeToggle.textContent = "☾";
    } else {
        localStorage.setItem("theme", "dark");
        themeToggle.textContent = "☀";
    }
});
