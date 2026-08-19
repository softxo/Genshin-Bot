const savedTheme = localStorage.getItem("theme") || "blue";

document.documentElement.dataset.theme = savedTheme;

function setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
}