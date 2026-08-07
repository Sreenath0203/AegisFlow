/* =========================================================
   DASHBOARD
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeDashboard();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeDashboard() {

    updateCurrentDate();

    updateGreeting();

    animateKPICards();

    initializeSearch();

}

/* =========================================================
   CURRENT DATE
========================================================= */

function updateCurrentDate() {

    const dateElement = document.getElementById("currentDate");

    if (!dateElement) return;

    const today = new Date();

    const options = {

        weekday: "long",

        year: "numeric",

        month: "long",

        day: "numeric"

    };

    dateElement.textContent = today.toLocaleDateString(
        "en-IN",
        options
    );

}

/* =========================================================
   GREETING
========================================================= */

function updateGreeting() {

    const greeting = document.getElementById("dashboardGreeting");

    if (!greeting) return;

    const hour = new Date().getHours();

    let message = "Good Evening";

    if (hour < 12) {

        message = "Good Morning";

    }

    else if (hour < 17) {

        message = "Good Afternoon";

    }

    greeting.textContent = message + ", Ravi";

}
/* =========================================================
   KPI CARD ANIMATION
========================================================= */

function animateKPICards() {

    const values = document.querySelectorAll(".kpi-value");

    values.forEach((value) => {

        const text = value.textContent.trim();

        const target = parseInt(text.replace(/\D/g, ""));

        if (isNaN(target)) return;

        let current = 0;

        const duration = 1200;

        const increment = Math.ceil(target / (duration / 16));

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

        }, 16);

    });

}

/* =========================================================
   SEARCH
========================================================= */

function initializeSearch() {

    const searchInput = document.querySelector(".search-box input");

    if (!searchInput) return;

    searchInput.addEventListener("keyup", function () {

        const searchText = this.value.toLowerCase();

        const tableRows = document.querySelectorAll("tbody tr");

        tableRows.forEach((row) => {

            const content = row.textContent.toLowerCase();

            row.style.display = content.includes(searchText)
                ? ""
                : "none";

        });

    });

}
/* =========================================================
   NOTIFICATION BUTTON
========================================================= */

const notificationButton = document.querySelector(".icon-button");

if (notificationButton) {

    notificationButton.addEventListener("click", () => {

        alert("No new notifications.");

    });

}



/* =========================================================
   BUTTON INTERACTIONS
========================================================= */

document.querySelectorAll(".btn").forEach((button) => {

    button.addEventListener("click", function () {

        this.style.transform = "scale(0.98)";

        setTimeout(() => {

            this.style.transform = "";

        }, 120);

    });

});



/* =========================================================
   CARD HOVER EFFECT
========================================================= */

document.querySelectorAll(".kpi-card").forEach((card) => {

    card.addEventListener("mouseenter", () => {

        card.style.transition = "0.3s";

    });

});



/* =========================================================
   CHART PLACEHOLDERS
========================================================= */

document.querySelectorAll(".chart-placeholder").forEach((chart) => {

    chart.innerHTML = `
        <div style="text-align:center;">
            <h3 style="margin-bottom:10px;">📈</h3>
            <p>Chart will load here</p>
        </div>
    `;

});



/* =========================================================
   DASHBOARD READY
========================================================= */

console.log("✅ Dashboard Initialized Successfully");