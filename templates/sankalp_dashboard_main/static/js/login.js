import { sanitizeInput } from "./sanitize.js";
import { generateSessionToken } from "./utils/token.js";


document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  // Placeholder backend authentication
  // TODO: Replace this with a real API call (POST /api/auth/login)
  
  const isAuthenticated = email && password; // temporary condition

  if (isAuthenticated) {
    const token = generateSessionToken();

    // Save login info locally
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("userEmail", email);
    localStorage.setItem("sessionToken", token);

    console.log("Session started with token:", token);

    // Redirect
    // window.location.href = "./dashboard.html";
  } else {
    alert("Invalid credentials. Please try again.");
  }
});
