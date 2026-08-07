/* =========================================================
   SUPPLIERS PAGE
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeSuppliers();

});

/* =========================================================
   INITIALIZATION
========================================================= */

function initializeSuppliers() {

    initializeSearch();

    initializeFilters();

    initializeTableActions();

}

/* =========================================================
   SEARCH
========================================================= */

function initializeSearch() {

    const searchInput = document.querySelector(".toolbar .search-box input");

    if (!searchInput) return;

    searchInput.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        const rows = document.querySelectorAll("tbody tr");

        rows.forEach((row) => {

            const text = row.textContent.toLowerCase();

            row.style.display = text.includes(value)
                ? ""
                : "none";

        });

    });

}

/* =========================================================
   FILTERS
========================================================= */

function initializeFilters() {

    const filters = document.querySelectorAll("select");

    filters.forEach((filter) => {

        filter.addEventListener("change", () => {

            console.log("Filter Changed :", filter.value);

        });

    });

}
/* =========================================================
   TABLE ACTIONS
========================================================= */

function initializeTableActions() {

    initializeViewButtons();

    initializeEditButtons();

    initializeDeleteButtons();

}



/* =========================================================
   VIEW BUTTON
========================================================= */

function initializeViewButtons() {

    const viewButtons = document.querySelectorAll(
        ".table-actions .icon-button:first-child"
    );

    viewButtons.forEach((button) => {

        button.addEventListener("click", () => {

            window.location.href = "supplier-details.html";

        });

    });

}



/* =========================================================
   EDIT BUTTON
========================================================= */

function initializeEditButtons() {

    const editButtons = document.querySelectorAll(
        ".table-actions .icon-button:nth-child(2)"
    );

    editButtons.forEach((button) => {

        button.addEventListener("click", () => {

            alert("Edit Supplier feature will be available soon.");

        });

    });

}



/* =========================================================
   DELETE BUTTON
========================================================= */

function initializeDeleteButtons() {

    const deleteButtons = document.querySelectorAll(
        ".table-actions .icon-button:nth-child(3)"
    );

    deleteButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const row = button.closest("tr");

            const supplierName = row.children[1].textContent.trim();

            const confirmDelete = confirm(

                `Delete ${supplierName}?`

            );

            if (confirmDelete) {

                row.remove();

            }

        });

    });

}
/* =========================================================
   PAGINATION
========================================================= */

const paginationButtons = document.querySelectorAll(".pagination button");

paginationButtons.forEach((button) => {

    button.addEventListener("click", () => {

        console.log("Pagination :", button.textContent.trim());

    });

});



/* =========================================================
   TABLE ROW HOVER EFFECT
========================================================= */

document.querySelectorAll("tbody tr").forEach((row) => {

    row.addEventListener("mouseenter", () => {

        row.style.transition = "0.25s";

    });

});



/* =========================================================
   SUPPLIER COUNT
========================================================= */

function updateSupplierCount() {

    const totalRows = document.querySelectorAll("tbody tr").length;

    const countElement = document.querySelector(".pagination-info strong:last-child");

    if (countElement) {

        countElement.textContent = totalRows;

    }

}

updateSupplierCount();



/* =========================================================
   PAGE READY
========================================================= */

console.log("✅ Suppliers Page Loaded Successfully");