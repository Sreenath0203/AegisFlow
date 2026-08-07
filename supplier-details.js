/* =========================================================
   SUPPLIER DETAILS
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeSupplierDetails();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeSupplierDetails() {

    animateProgressBars();

    animateStatistics();

    initializeButtons();

}

/* =========================================================
   PROGRESS BARS
========================================================= */

function animateProgressBars() {

    const progressBars = document.querySelectorAll(".progress-fill");

    progressBars.forEach((bar) => {

        const targetWidth = bar.dataset.width;

        bar.style.width = "0%";

        setTimeout(() => {

            bar.style.transition = "width 1.2s ease";

            bar.style.width = targetWidth;

        }, 300);

    });

}
/* =========================================================
   ANIMATED STATISTICS
========================================================= */

function animateStatistics() {

    const values = document.querySelectorAll(".metric-value");

    values.forEach((value) => {

        const text = value.textContent.trim();

        const target = parseInt(text.replace(/\D/g, ""));

        if (isNaN(target)) return;

        let current = 0;

        const increment = Math.ceil(target / 50);

        const timer = setInterval(() => {

            current += increment;

            if (current >= target) {

                current = target;

                clearInterval(timer);

            }

            if (text.includes("%")) {

                value.textContent = current + "%";

            }

            else {

                value.textContent = current;

            }

        }, 20);

    });

}



/* =========================================================
   BUTTONS
========================================================= */

function initializeButtons() {

    initializeExportButton();

    initializePrintButton();

    initializeEditButton();

}



/* =========================================================
   EXPORT
========================================================= */

function initializeExportButton() {

    const exportButton = document.querySelector(".export-btn");

    if (!exportButton) return;

    exportButton.addEventListener("click", () => {

        alert("Supplier report exported successfully.");

    });

}



/* =========================================================
   PRINT
========================================================= */

function initializePrintButton() {

    const printButton = document.querySelector(".print-btn");

    if (!printButton) return;

    printButton.addEventListener("click", () => {

        window.print();

    });

}



/* =========================================================
   EDIT
========================================================= */

function initializeEditButton() {

    const editButton = document.querySelector(".edit-btn");

    if (!editButton) return;

    editButton.addEventListener("click", () => {

        alert("Edit Supplier feature coming soon.");

    });

}
/* =========================================================
   STATUS BADGE
========================================================= */

function initializeStatusBadge() {

    const badges = document.querySelectorAll(".badge");

    badges.forEach((badge) => {

        badge.addEventListener("click", () => {

            alert("Supplier Status : " + badge.textContent.trim());

        });

    });

}

initializeStatusBadge();



/* =========================================================
   CARD HOVER EFFECT
========================================================= */

document.querySelectorAll(".details-card").forEach((card) => {

    card.addEventListener("mouseenter", () => {

        card.style.transition = "0.3s ease";

    });

});



/* =========================================================
   QUICK ACTIONS
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
   PAGE READY
========================================================= */

console.log("✅ Supplier Details Loaded Successfully");