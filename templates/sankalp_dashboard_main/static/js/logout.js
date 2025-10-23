
// Logout button functionality
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    // Clear session storage/localStorage
    localStorage.clear();
    sessionStorage.clear();

    // Redirect to login page
    // window.location.href = "./login.html";
  });
}