/* =========================================================
   AI RECOMMENDATIONS
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeRecommendations();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeRecommendations() {

    initializeFilters();

    initializeActionButtons();

    animateConfidenceScores();

}



/* =========================================================
   FILTERS
========================================================= */

function initializeFilters() {

    const filters = document.querySelectorAll("select");

    filters.forEach((filter) => {

        filter.addEventListener("change", () => {

            console.log("Recommendation Filter :", filter.value);

        });

    });

}



/* =========================================================
   CONFIDENCE SCORE ANIMATION
========================================================= */

function animateConfidenceScores() {

    const scores = document.querySelectorAll(".confidence-score");

    scores.forEach((score) => {

        score.style.transition = "0.3s ease";

    });

}
/* =========================================================
   ACTION BUTTONS
========================================================= */

function initializeActionButtons() {

    initializeAcceptButtons();

    initializeRejectButtons();

}



/* =========================================================
   ACCEPT RECOMMENDATION
========================================================= */

function initializeAcceptButtons() {

    const acceptButtons = document.querySelectorAll(".btn-primary");

    acceptButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const card = button.closest(".recommendation-card");

            if (!card) return;

            const badge = card.querySelector(".badge");

            if (badge) {

                badge.textContent = "Accepted";

                badge.className = "badge badge-success";

            }

            alert("Recommendation Accepted.");

        });

    });

}



/* =========================================================
   REJECT RECOMMENDATION
========================================================= */

function initializeRejectButtons() {

    const rejectButtons = document.querySelectorAll(".btn-secondary");

    rejectButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const card = button.closest(".recommendation-card");

            if (!card) return;

            const badge = card.querySelector(".badge");

            if (badge) {

                badge.textContent = "Rejected";

                badge.className = "badge badge-danger";

            }

            alert("Recommendation Rejected.");

        });

    });

}
/* =========================================================
   CARD HOVER EFFECTS
========================================================= */

document.querySelectorAll(".recommendation-card").forEach((card) => {

    card.addEventListener("mouseenter", () => {

        card.style.transition = "0.3s ease";

    });

});



/* =========================================================
   BUTTON CLICK EFFECT
========================================================= */

document.querySelectorAll(".recommendation-actions .btn").forEach((button) => {

    button.addEventListener("click", () => {

        button.style.transform = "scale(0.97)";

        setTimeout(() => {

            button.style.transform = "";

        }, 120);

    });

});



/* =========================================================
   CONFIDENCE BADGE INTERACTION
========================================================= */

document.querySelectorAll(".confidence-score").forEach((score) => {

    score.addEventListener("mouseenter", () => {

        score.style.transform = "scale(1.05)";

    });

    score.addEventListener("mouseleave", () => {

        score.style.transform = "scale(1)";

    });

});



/* =========================================================
   REFRESH RECOMMENDATIONS (PLACEHOLDER)
========================================================= */

function refreshRecommendations() {

    console.log("Refreshing AI recommendations...");

}



/* =========================================================
   PAGE READY
========================================================= */

console.log("✅ AI Recommendations Loaded Successfully");