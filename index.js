/* =========================================================
   LANDING PAGE
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeLandingPage();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeLandingPage() {

    initializeSmoothScroll();

    initializeNavbar();

    initializeRevealAnimation();

}



/* =========================================================
   SMOOTH SCROLL
========================================================= */

function initializeSmoothScroll() {

    document.querySelectorAll('a[href^="#"]').forEach((link) => {

        link.addEventListener("click", function (event) {

            event.preventDefault();

            const target = document.querySelector(

                this.getAttribute("href")

            );

            if (target) {

                target.scrollIntoView({

                    behavior: "smooth"

                });

            }

        });

    });

}



/* =========================================================
   NAVBAR
========================================================= */

function initializeNavbar() {

    const navbar = document.querySelector(".landing-navbar");

    if (!navbar) return;

    window.addEventListener("scroll", () => {

        if (window.scrollY > 40) {

            navbar.style.boxShadow =
                "0 10px 25px rgba(0,0,0,.08)";

        }

        else {

            navbar.style.boxShadow = "";

        }

    });

}
/* =========================================================
   SCROLL REVEAL ANIMATION
========================================================= */

function initializeRevealAnimation() {

    const sections = document.querySelectorAll(

        ".hero, .features-section, .workflow-section, .statistics-section, .cta-section"

    );

    const observer = new IntersectionObserver(

        (entries) => {

            entries.forEach((entry) => {

                if (entry.isIntersecting) {

                    entry.target.style.opacity = "1";

                    entry.target.style.transform = "translateY(0)";

                }

            });

        },

        {

            threshold: 0.2

        }

    );

    sections.forEach((section) => {

        section.style.opacity = "0";

        section.style.transform = "translateY(40px)";

        section.style.transition = "all .6s ease";

        observer.observe(section);

    });

}



/* =========================================================
   ACTIVE NAVIGATION
========================================================= */

const navLinks = document.querySelectorAll(".landing-menu a");

navLinks.forEach((link) => {

    link.addEventListener("click", () => {

        navLinks.forEach((item) => {

            item.classList.remove("active");

        });

        link.classList.add("active");

    });

});



/* =========================================================
   HERO BUTTON EFFECT
========================================================= */

document.querySelectorAll(".hero-buttons .btn").forEach((button) => {

    button.addEventListener("click", () => {

        button.style.transform = "scale(0.97)";

        setTimeout(() => {

            button.style.transform = "";

        }, 120);

    });

});



/* =========================================================
   STATISTICS COUNTER
========================================================= */

function animateStatistics() {

    const stats = document.querySelectorAll(".stat-card h2");

    stats.forEach((stat) => {

        const text = stat.textContent.trim();

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

                stat.textContent = current + "%";

            }

            else if (text.includes("+")) {

                stat.textContent = current + "+";

            }

            else {

                stat.textContent = current;

            }

        }, 20);

    });

}

animateStatistics();
/* =========================================================
   SCROLL TO TOP BUTTON
========================================================= */

const scrollButton = document.createElement("button");

scrollButton.innerHTML = "↑";

scrollButton.className = "scroll-top-button";

document.body.appendChild(scrollButton);

scrollButton.style.position = "fixed";
scrollButton.style.right = "24px";
scrollButton.style.bottom = "24px";
scrollButton.style.width = "48px";
scrollButton.style.height = "48px";
scrollButton.style.border = "none";
scrollButton.style.borderRadius = "50%";
scrollButton.style.background = "#2563EB";
scrollButton.style.color = "#FFFFFF";
scrollButton.style.fontSize = "22px";
scrollButton.style.cursor = "pointer";
scrollButton.style.display = "none";
scrollButton.style.boxShadow = "0 8px 20px rgba(0,0,0,.2)";
scrollButton.style.zIndex = "999";

window.addEventListener("scroll", () => {

    if (window.scrollY > 300) {

        scrollButton.style.display = "block";

    }

    else {

        scrollButton.style.display = "none";

    }

});

scrollButton.addEventListener("click", () => {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

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
   PAGE READY
========================================================= */

console.log("✅ AegisFlow Landing Page Loaded Successfully");