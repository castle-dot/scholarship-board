// Flips data-theme on <html> between "light" and "dark" and remembers the
// choice in localStorage. The INITIAL theme (before this file even loads)
// is set by a tiny inline <script> in base.html's <head> — that one runs
// synchronously so there's no flash of the wrong theme on page load.
document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("theme-toggle-btn");
  if (!btn) return;

  btn.addEventListener("click", function () {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  });
});