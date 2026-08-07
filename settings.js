/* =========================================================
   SETTINGS PAGE
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeSettings();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeSettings() {

    initializeSaveButton();

    initializeThemeSelection();

    initializeCheckboxes();

}



/* =========================================================
   SAVE BUTTON
========================================================= */

function initializeSaveButton() {

    const saveButton = document.querySelector(".settings-actions .btn");

    if (!saveButton) return;

    saveButton.addEventListener("click", (event) => {

        event.preventDefault();

        alert("Settings saved successfully.");

    });

}



/* =========================================================
   THEME SELECTION
========================================================= */

function initializeThemeSelection() {

    const themeOptions = document.querySelectorAll(

        'input[name="theme"]'

    );

    themeOptions.forEach((option) => {

        option.addEventListener("change", () => {

            console.log("Theme :", option.value);

        });

    });

}



/* =========================================================
   CHECKBOXES
========================================================= */

function initializeCheckboxes() {

    const checkboxes = document.querySelectorAll(

        'input[type="checkbox"]'

    );

    checkboxes.forEach((checkbox) => {

        checkbox.addEventListener("change", () => {

            console.log(

                checkbox.parentElement.textContent.trim(),

                checkbox.checked

            );

        });

    });

}
/* =========================================================
   PROFILE VALIDATION
========================================================= */

function validateProfile() {

    const inputs = document.querySelectorAll(

        '.settings-card input[type="text"], .settings-card input[type="email"]'

    );

    let valid = true;

    inputs.forEach((input) => {

        if (input.value.trim() === "") {

            input.style.borderColor = "#EF4444";

            valid = false;

        }

        else {

            input.style.borderColor = "";

        }

    });

    return valid;

}



/* =========================================================
   PASSWORD VALIDATION
========================================================= */

function validatePassword() {

    const passwordFields = document.querySelectorAll(

        'input[type="password"]'

    );

    if (passwordFields.length < 2) return true;

    const currentPassword = passwordFields[0].value.trim();

    const newPassword = passwordFields[1].value.trim();

    if (newPassword !== "" && newPassword.length < 8) {

        alert("New password must contain at least 8 characters.");

        return false;

    }

    if (currentPassword === newPassword && newPassword !== "") {

        alert("New password cannot be the same as the current password.");

        return false;

    }

    return true;

}



/* =========================================================
   INPUT HIGHLIGHT
========================================================= */

document.querySelectorAll(".input-field").forEach((input) => {

    input.addEventListener("focus", () => {

        input.style.transition = "0.2s ease";

    });

});



/* =========================================================
   SAVE VALIDATION
========================================================= */

const saveButton = document.querySelector(".settings-actions .btn");

if (saveButton) {

    saveButton.addEventListener("click", (event) => {

        event.preventDefault();

        if (!validateProfile()) {

            alert("Please complete all required profile fields.");

            return;

        }

        if (!validatePassword()) {

            return;

        }

        alert("Settings validated successfully.");

    });

}
/* =========================================================
   THEME PREVIEW
========================================================= */

document.querySelectorAll('input[name="theme"]').forEach((theme) => {

    theme.addEventListener("change", () => {

        if (theme.checked) {

            console.log("Selected Theme :", theme.parentElement.textContent.trim());

        }

    });

});



/* =========================================================
   BUTTON CLICK EFFECT
========================================================= */

document.querySelectorAll(".btn").forEach((button) => {

    button.addEventListener("click", () => {

        button.style.transform = "scale(0.98)";

        setTimeout(() => {

            button.style.transform = "";

        }, 120);

    });

});



/* =========================================================
   RESET FORM (PLACEHOLDER)
========================================================= */

function resetSettingsForm() {

    console.log("Reset Settings Form");

}



/* =========================================================
   PAGE READY
========================================================= */

console.log("✅ Settings Page Loaded Successfully");