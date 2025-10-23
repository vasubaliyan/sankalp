
// main.js
document.getElementById('startBtn').addEventListener('click', () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const sessionToken = localStorage.getItem("sessionToken");

  // Placeholder validation: session token exists
  const isTokenValid = sessionToken && sessionToken.length > 0;

  if (isLoggedIn && isTokenValid) {
    // User logged in → go to dashboard
    // window.location.href = "./dashboard.html";
  } else {
    // Not logged in → go to login page
    // window.location.href = "./login.html";
  }
});