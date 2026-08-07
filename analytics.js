/* =========================================================
   ANALYTICS PAGE
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeAnalytics();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeAnalytics() {

    initializeFilters();

    animateKPIs();

    initializeCharts();

}



/* =========================================================
   FILTERS
========================================================= */

function initializeFilters() {

    const filters = document.querySelectorAll("select");

    filters.forEach((filter) => {

        filter.addEventListener("change", () => {

            console.log("Analytics Filter :", filter.value);

        });

    });

}



/* =========================================================
   KPI ANIMATION
========================================================= */

function animateKPIs() {

    const values = document.querySelectorAll(".kpi-value");

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
   CHART PLACEHOLDERS
========================================================= */

function initializeCharts() {

    const charts = document.querySelectorAll(".chart-placeholder");

    charts.forEach((chart, index) => {

        chart.innerHTML = `
            <div style="text-align:center;">
                <h2 style="font-size:42px;margin-bottom:12px;">📊</h2>
                <p>Chart ${index + 1} will load here</p>
            </div>
        `;

    });

}



/* =========================================================
   EXPORT ANALYTICS
========================================================= */

function initializeExportButton() {

    const exportButton = document.querySelector(".export-btn");

    if (!exportButton) return;

    exportButton.addEventListener("click", () => {

        alert("Analytics report exported successfully.");

    });

}



/* =========================================================
   REFRESH BUTTON
========================================================= */

function initializeRefreshButton() {

    const refreshButton = document.querySelector(".refresh-btn");

    if (!refreshButton) return;

    refreshButton.addEventListener("click", () => {

        location.reload();

    });

}



/* =========================================================
   AI INSIGHTS
========================================================= */

function initializeInsights() {

    const insights = document.querySelector(".recommendation-box");

    if (!insights) return;

    insights.style.transition = "0.3s ease";

}
/* =========================================================
   CARD HOVER EFFECTS
========================================================= */

document.querySelectorAll(".chart-card").forEach((card) => {

    card.addEventListener("mouseenter", () => {

        card.style.transition = "0.3s ease";

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
   CHART REFRESH PLACEHOLDER
========================================================= */

function refreshCharts() {

    console.log("Refreshing analytics charts...");

    document.querySelectorAll(".chart-placeholder").forEach((chart) => {

        chart.style.opacity = "0.5";

        setTimeout(() => {

            chart.style.opacity = "1";

        }, 500);

    });

}



/* =========================================================
   INITIALIZE OPTIONAL FEATURES
========================================================= */

initializeExportButton();

initializeRefreshButton();

initializeInsights();



/* =========================================================
   PAGE READY
========================================================= */

console.log("✅ Analytics Page Loaded Successfully");