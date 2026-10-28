// Loaded first in <body> so a saved light theme applies before the page is painted
// (BUG-52). theme.js, at the end of the page, keeps the toggle button in sync.
try {
    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light-theme");
    }
} catch (error) {
    // Without storage access the default dark theme is used.
}
