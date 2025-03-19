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

    //pagination
    var currentPage = document.getElementById("ActivePage");;
    currentPage = currentPage.dataset.currentPage || 1;
    var totalRow= document.getElementById("TotalRow");
        let totalPages = 1;

        function fetchPagination(page) {
            fetch(`/paginate_view?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    currentPage = data.page;
                    totalPages = data.total_pages;

                    document.getElementById("pageInfo").innerText = `Page ${currentPage} of ${totalPages}`;

                    document.getElementById("prevBtn").disabled = !data.prev_page;
                    document.getElementById("nextBtn").disabled = !data.next_page;
                })
                .catch(error => console.error("Error fetching pagination:", error));
        }

        function changePage(step) {
            let newPage = currentPage + step;
            if (newPage >= 1 && newPage <= totalPages) {
                fetchPagination(newPage);
            }
        }

        // Load pagination on page load
        fetchPagination(currentPage);
});
