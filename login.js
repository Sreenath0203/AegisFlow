/* =========================================================
   LOGIN PAGE
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeLogin();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeLogin() {

    initializeLoginForm();

    initializeRememberMe();

}



/* =========================================================
   LOGIN FORM
========================================================= */

function initializeLoginForm() {

    const form = document.querySelector(".login-form");

    if (!form) return;

    form.addEventListener("submit", (event) => {

        event.preventDefault();

        if (!validateLogin()) {

            return;

        }

        alert("Login Successful!");

        window.location.href = "dashboard.html";

    });

}



/* =========================================================
   LOGIN VALIDATION
========================================================= */

function validateLogin() {

    const email = document.querySelector('input[type="email"]');

    const password = document.querySelector('input[type="password"]');

    if (!email || !password) return false;

    if (email.value.trim() === "") {

        alert("Please enter your email address.");

        email.focus();

        return false;

    }

    if (password.value.trim() === "") {

        alert("Please enter your password.");

        password.focus();

        return false;

    }

    return true;

}



/* =========================================================
   REMEMBER ME
========================================================= */

function initializeRememberMe() {

    const checkbox = document.querySelector('input[type="checkbox"]');

    if (!checkbox) return;

    checkbox.addEventListener("change", () => {

        console.log("Remember Me :", checkbox.checked);

    });

}
/* =========================================================
   SHOW / HIDE PASSWORD
========================================================= */

function initializePasswordToggle() {

    const passwordField = document.querySelector('input[type="password"]');

    if (!passwordField) return;

    passwordField.addEventListener("dblclick", () => {

        passwordField.type =
            passwordField.type === "password"
                ? "text"
                : "password";

    });

}

initializePasswordToggle();



/* =========================================================
   EMAIL FORMAT VALIDATION
========================================================= */

function validateEmailFormat(email) {

    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return pattern.test(email);

}



/* =========================================================
   PASSWORD STRENGTH
========================================================= */

function validatePasswordStrength(password) {

    return password.length >= 8;

}



/* =========================================================
   REAL-TIME VALIDATION
========================================================= */

const emailInput = document.querySelector('input[type="email"]');

const passwordInput = document.querySelector('input[type="password"]');

if (emailInput) {

    emailInput.addEventListener("blur", () => {

        if (
            emailInput.value !== "" &&
            !validateEmailFormat(emailInput.value)
        ) {

            alert("Please enter a valid email address.");

        }

    });

}

if (passwordInput) {

    passwordInput.addEventListener("blur", () => {

        if (
            passwordInput.value !== "" &&
            !validatePasswordStrength(passwordInput.value)
        ) {

            alert("Password must contain at least 8 characters.");

        }

    });

}



/* =========================================================
   INPUT FOCUS EFFECT
========================================================= */

document.querySelectorAll(".input-field").forEach((input) => {

    input.addEventListener("focus", () => {

        input.style.transition = "0.2s ease";

    });

});
/* =========================================================
   LOGIN BUTTON ANIMATION
========================================================= */

const loginButton = document.querySelector(".login-button");

if (loginButton) {

    loginButton.addEventListener("click", () => {

        loginButton.style.transform = "scale(0.98)";

        loginButton.disabled = true;

        const originalText = loginButton.innerHTML;

        loginButton.innerHTML = `
            <i data-lucide="loader-circle"></i>
            Logging in...
        `;

        if (typeof lucide !== "undefined") {

            lucide.createIcons();

        }

        setTimeout(() => {

            loginButton.style.transform = "";

            loginButton.disabled = false;

            loginButton.innerHTML = originalText;

            if (typeof lucide !== "undefined") {

                lucide.createIcons();

            }

        }, 1500);

    });

}



/* =========================================================
   KEYBOARD SHORTCUT
========================================================= */

document.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {

        const form = document.querySelector(".login-form");

        if (form) {

            form.requestSubmit();

        }

    }

});



/* =========================================================
   PAGE READY
========================================================= */

console.log("✅ Login Page Loaded Successfully");