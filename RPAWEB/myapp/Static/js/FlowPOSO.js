document.addEventListener("DOMContentLoaded", function () {
    // Set Default Date
    var dateInput = document.getElementById("dateInput");
    var selectedDate = dateInput.dataset.selectedDate;
    if (!dateInput.value) {
        dateInput.value = selectedDate || new Date().toISOString().split("T")[0];
    }

    // Set Rows Per Page
    var rowsPerPageElement = document.getElementById("cmb_rowsPerPage");
    var rowsPerPage = rowsPerPageElement.dataset.rowsPerPage || 10;
    rowsPerPageElement.value = rowsPerPage;

    // Set Search Term
    var searchTermInput = document.getElementById("search_term");
    searchTermInput.value = searchTermInput.dataset.searchTerm || "";

    // Set Selected Customer
    var customerDropdown = document.getElementById("cmb_Customer");
    customerDropdown.value = customerDropdown.dataset.selectedCustomer || "ALL";

    // Set Selected Distribution Channel
    var distChannelDropdown = document.getElementById("cmb_DistChannel");
    distChannelDropdown.value = distChannelDropdown.dataset.selectedDistChannel || "ALL";

    // Handle Checkboxes
    var checkboxes = ["kolom_ocr", "kolom_download"];
    checkboxes.forEach(function (id) {
        var checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.checked = checkbox.dataset.checked === "true";
        }
    });

    // === OCR Column Toggle ===
    var kolomOCRCheckbox = document.getElementById("kolom_ocr");
    var ocrColumns = document.querySelectorAll(".ocr-column");

    function toggleOCRColumns() {
        var displayStyle = kolomOCRCheckbox.checked ? "table-cell" : "none";
        ocrColumns.forEach(col => col.style.display = displayStyle);
    }

    toggleOCRColumns();
    kolomOCRCheckbox.addEventListener("change", toggleOCRColumns);

    // === Download Column Toggle ===
    var kolomDownloadCheckbox = document.getElementById("kolom_download");
    var downloadColumns = document.querySelectorAll(".download-column");

    function toggleDownloadColumns() {
        var displayStyle = kolomDownloadCheckbox.checked ? "table-cell" : "none";
        downloadColumns.forEach(col => col.style.display = displayStyle);
    }

    toggleDownloadColumns();
    kolomDownloadCheckbox.addEventListener("change", toggleDownloadColumns);
});
