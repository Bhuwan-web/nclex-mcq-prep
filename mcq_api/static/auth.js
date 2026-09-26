(() => {
  const tokenKey = "nclex_access_token";
  const isSignup = window.location.pathname === "/signup";
  const $ = (id) => document.getElementById(id);
  const email = $("email");
  const password = $("password");
  const button = $("submit-button");
  const error = $("error-message");

  function setMode() {
    document.title = `${isSignup ? "Create account" : "Sign in"} | NCLEX Practice Hub`;
    $("form-eyebrow").textContent = isSignup ? "START YOUR JOURNEY" : "WELCOME BACK";
    $("form-title").textContent = isSignup ? "Let’s get started." : "Good to see you.";
    $("form-description").textContent = isSignup ? "Create an account and keep your progress moving." : "Sign in to keep your progress moving.";
    $("submit-label").textContent = isSignup ? "Create account" : "Sign in";
    $("switch-question").textContent = isSignup ? "Already have an account?" : "New to the hub?";
    $("switch-link").textContent = isSignup ? "Sign in" : "Create an account";
    $("switch-link").href = isSignup ? "/login" : "/signup";
    password.autocomplete = isSignup ? "new-password" : "current-password";
    $("password-hint").hidden = !isSignup;
  }

  $("password-toggle").addEventListener("click", () => {
    const visible = password.type === "password";
    password.type = visible ? "text" : "password";
    $("password-toggle").textContent = visible ? "Hide" : "Show";
    $("password-toggle").setAttribute("aria-label", `${visible ? "Hide" : "Show"} password`);
    $("password-toggle").setAttribute("aria-pressed", String(visible));
  });

  function showError(message) {
    error.textContent = message;
    error.hidden = false;
  }

  $("auth-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    error.hidden = true;
    email.removeAttribute("aria-invalid");
    password.removeAttribute("aria-invalid");
    if (!email.value.trim() || !email.checkValidity()) {
      email.setAttribute("aria-invalid", "true");
      showError("Enter a valid email address to continue.");
      email.focus();
      return;
    }
    if (password.value.length < 8) {
      password.setAttribute("aria-invalid", "true");
      showError("Your password must be at least 8 characters.");
      password.focus();
      return;
    }
    button.disabled = true;
    $("submit-label").textContent = isSignup ? "Creating account…" : "Signing in…";
    try {
      const cleanEmail = email.value.trim();
      if (isSignup) {
        const register = await fetch("/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: cleanEmail, password: password.value }),
        });
        if (!register.ok) {
          const body = await register.json().catch(() => ({}));
          throw new Error(body.detail || "Could not create your account. Please try again.");
        }
      }
      const response = await fetch("/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: cleanEmail, password: password.value }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Sign in failed. Check your email and password.");
      localStorage.setItem(tokenKey, body.access_token);
      window.location.assign("/");
    } catch (exception) {
      const messages = {
        "Incorrect email or password": "That email and password combination was not recognized. Try again or create an account.",
        "An account with this email already exists": "An account already exists for this email. Sign in instead.",
      };
      showError(messages[exception.message] || exception.message);
    } finally {
      button.disabled = false;
      $("submit-label").textContent = isSignup ? "Create account" : "Sign in";
    }
  });
  setMode();
})();
