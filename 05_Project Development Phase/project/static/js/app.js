document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      document.body.classList.toggle("dark");
      const icon = toggle.querySelector("i");
      icon.className = document.body.classList.contains("dark") ? "fas fa-sun" : "fas fa-moon";
    });
  }
});
