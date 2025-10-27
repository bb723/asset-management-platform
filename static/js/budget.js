/**
 * Budget Management JavaScript
 * Handles budget table interactivity, calculations, and saving
 */

let budgetData = [];
let isDirty = false;

/**
 * Initialize budget functionality
 */
function initBudget(buildingId, saveUrl) {
    console.log('Initializing budget for building:', buildingId);

    // Calculate initial totals
    calculateTotals();

    // Add event listeners to budget inputs
    $('.budget-input').on('input', function() {
        isDirty = true;
        calculateTotals();
        $(this).addClass('border-warning');
    });

    // Save budget button handlers
    $('#saveBudget, #saveBudgetBottom').on('click', function() {
        saveBudget(buildingId, saveUrl);
    });

    // Warn on navigation if unsaved changes
    window.addEventListener('beforeunload', function(e) {
        if (isDirty) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });

    // Allow tab navigation in table
    $('.budget-input').on('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const inputs = $('.budget-input');
            const currentIndex = inputs.index(this);
            const nextIndex = e.shiftKey ? currentIndex - 1 : currentIndex + 1;

            if (nextIndex >= 0 && nextIndex < inputs.length) {
                inputs.eq(nextIndex).focus();
            }
        }
    });
}

/**
 * Calculate all totals in the budget table
 */
function calculateTotals() {
    let grandTotal = 0;

    // Calculate category totals (row totals)
    $('tr[data-category]').each(function() {
        const row = $(this);
        const inputs = row.find('.budget-input');
        let categoryTotal = 0;

        inputs.each(function() {
            const value = parseFloat($(this).val()) || 0;
            categoryTotal += value;
        });

        row.find('.category-total').text(formatCurrency(categoryTotal));
        grandTotal += categoryTotal;
    });

    // Calculate monthly totals (column totals)
    const months = [];
    $('.budget-input').each(function() {
        const month = $(this).data('month');
        if (!months.includes(month)) {
            months.push(month);
        }
    });

    months.forEach(month => {
        let monthTotal = 0;
        $(`.budget-input[data-month="${month}"]`).each(function() {
            const value = parseFloat($(this).val()) || 0;
            monthTotal += value;
        });

        $(`.month-total[data-month="${month}"]`).text(formatCurrency(monthTotal));
    });

    // Update grand total
    $('#grandTotal').text(formatCurrency(grandTotal));
}

/**
 * Save budget to server
 */
function saveBudget(buildingId, saveUrl) {
    console.log('Saving budget...');

    // Show loading state
    showLoadingSpinner();

    // Collect budget data
    budgetData = [];
    $('.budget-input').each(function() {
        const input = $(this);
        const category = input.data('category');
        const month = input.data('month');
        const amount = parseFloat(input.val()) || 0;

        budgetData.push({
            building_id: buildingId,
            category: category,
            month: month,
            amount: amount,
            notes: ''
        });
    });

    // Send to server
    $.ajax({
        url: saveUrl,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(budgetData),
        success: function(response) {
            hideLoadingSpinner();

            if (response.success) {
                console.log('Budget saved successfully:', response);
                isDirty = false;

                // Remove warning borders
                $('.budget-input').removeClass('border-warning');

                // Show success message
                showSuccessMessage('Budget saved successfully!');

                // Add success animation
                $('#saveBudget, #saveBudgetBottom').addClass('save-success');
                setTimeout(() => {
                    $('#saveBudget, #saveBudgetBottom').removeClass('save-success');
                }, 500);
            } else {
                console.error('Failed to save budget:', response.message);
                showErrorMessage('Failed to save budget: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            hideLoadingSpinner();
            console.error('Error saving budget:', error);
            showErrorMessage('Error saving budget. Please try again.');
        }
    });
}

/**
 * Format number as currency
 */
function formatCurrency(value) {
    return '$' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

/**
 * Show loading spinner
 */
function showLoadingSpinner() {
    if ($('.spinner-overlay').length === 0) {
        $('body').append(`
            <div class="spinner-overlay">
                <div class="spinner-border text-light" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `);
    }
}

/**
 * Hide loading spinner
 */
function hideLoadingSpinner() {
    $('.spinner-overlay').remove();
}

/**
 * Show success message
 */
function showSuccessMessage(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show fade-in" role="alert">
            <i class="bi bi-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Remove existing alerts
    $('.container .alert').remove();

    // Add new alert
    $('.container').prepend(alertHtml);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        $('.alert').fadeOut(() => {
            $(this).remove();
        });
    }, 5000);

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Show error message
 */
function showErrorMessage(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show fade-in" role="alert">
            <i class="bi bi-exclamation-triangle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Remove existing alerts
    $('.container .alert').remove();

    // Add new alert
    $('.container').prepend(alertHtml);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        $('.alert').fadeOut(() => {
            $(this).remove();
        });
    }, 5000);

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Export budget to CSV
 */
function exportBudgetToCSV() {
    console.log('Exporting budget to CSV...');

    let csv = 'Category,';

    // Get month headers
    const months = [];
    $('.budget-input').each(function() {
        const month = $(this).data('month');
        if (!months.includes(month)) {
            months.push(month);
        }
    });

    csv += months.join(',') + ',Total\n';

    // Add data rows
    $('tr[data-category]').each(function() {
        const row = $(this);
        const category = row.data('category');
        csv += `"${category}",`;

        const values = [];
        months.forEach(month => {
            const input = row.find(`.budget-input[data-month="${month}"]`);
            const value = parseFloat(input.val()) || 0;
            values.push(value.toFixed(2));
        });

        csv += values.join(',');

        const total = row.find('.category-total').text().replace(/[$,]/g, '');
        csv += ',' + total + '\n';
    });

    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'budget_export.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    console.log('Budget exported successfully');
}

// Make functions available globally
window.initBudget = initBudget;
window.exportBudgetToCSV = exportBudgetToCSV;
