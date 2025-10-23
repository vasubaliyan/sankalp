// navbar.js
// Optional: future navbar JS (like mobile toggle)
// navbar.js
document.addEventListener("DOMContentLoaded", () => {
  const navUl = document.querySelector("nav ul");
  const loginLi = navUl.querySelector("li:last-child"); // last <li> is login by default

  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const sessionToken = localStorage.getItem("sessionToken");
  const isTokenValid = sessionToken && sessionToken.length > 0;

  if (isLoggedIn && isTokenValid) {
    // Replace Login link with Logout button
    loginLi.innerHTML = `<button id="logoutBtn" class="btn-logout">Logout</button>`;

    const logoutBtn = document.getElementById("logoutBtn");
    logoutBtn.addEventListener("click", () => {
      localStorage.clear();
      sessionStorage.clear();
      // window.location.href = "./login.html";
    });
  }
});