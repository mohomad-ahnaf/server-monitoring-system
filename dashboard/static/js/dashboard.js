/* ====================================
   Dashboard JavaScript
   ==================================== */

/**
 * Auto-refresh metrics every 30 seconds
 */
function autoRefreshMetrics() {
    setInterval(() => {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                updateDashboardMetrics(data);
            })
            .catch(error => console.error('Error refreshing metrics:', error));
    }, 30000); // 30 seconds
}

/**
 * Update dashboard metrics
 */
function updateDashboardMetrics(data) {
    // Update CPU Usage
    const cpuElement = document.querySelector('[data-metric="cpu"]');
    if (cpuElement) {
        cpuElement.textContent = data.cpu_usage + '%';
        cpuElement.className = getStatusClass(data.cpu_usage, 70, 85);
    }

    // Update Memory Usage
    const memElement = document.querySelector('[data-metric="memory"]');
    if (memElement) {
        memElement.textContent = data.memory_usage + '%';
        memElement.className = getStatusClass(data.memory_usage, 80, 90);
    }

    // Update Disk Usage
    const diskElement = document.querySelector('[data-metric="disk"]');
    if (diskElement) {
        diskElement.textContent = data.disk_usage + '%';
        diskElement.className = getStatusClass(data.disk_usage, 80, 95);
    }

    // Update Alert Count
    const alertBadge = document.getElementById('alert-count');
    if (alertBadge) {
        alertBadge.textContent = data.unresolved_alerts;
    }

    // Update Last Updated Time
    const timestampElement = document.querySelector('[data-metric="timestamp"]');
    if (timestampElement) {
        const date = new Date(data.timestamp);
        timestampElement.textContent = date.toLocaleTimeString();
    }
}

/**
 * Determine status class based on thresholds
 */
function getStatusClass(value, warning, critical) {
    if (value >= critical) {
        return 'status-critical';
    } else if (value >= warning) {
        return 'status-warning';
    } else {
        return 'status-ok';
    }
}

/**
 * Format bytes to human readable
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

/**
 * Show loading indicator
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="text-center"><div class="loading"></div></div>';
    }
}

/**
 * Show error message
 */
function showError(message, elementId = null) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    if (elementId) {
        document.getElementById(elementId).innerHTML = alertHtml;
    } else {
        document.body.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

/**
 * Show success message
 */
function showSuccess(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.body.insertAdjacentHTML('afterbegin', alertHtml);
}

/**
 * Fetch data from API with error handling
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        showError('Error fetching data: ' + error.message);
        return null;
    }
}

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // Start auto-refresh
    autoRefreshMetrics();
    
    // Add event listeners
    initializeEventListeners();
});

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Refresh button
    const refreshButton = document.getElementById('refresh-btn');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            location.reload();
        });
    }

    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });
    }

    // Check saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
}

/**
 * Export table to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    let rows = table.querySelectorAll('tr');

    for (let row of rows) {
        let rowData = [];
        let cells = row.querySelectorAll('td, th');
        
        for (let cell of cells) {
            rowData.push('"' + cell.textContent.replace(/"/g, '""') + '"');
        }
        
        csv.push(rowData.join(','));
    }

    downloadCSV(csv.join('\n'), filename);
}

/**
 * Download CSV file
 */
function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(csvFile);
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

/**
 * Confirm action dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Toast notification (if Bootstrap Toast is available)
 */
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const toastContainer = document.createElement('div');
    toastContainer.innerHTML = toastHtml;
    toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; width: 400px; max-width: 90%;';
    
    document.body.appendChild(toastContainer);
    
    setTimeout(() => {
        toastContainer.remove();
    }, 5000);
}

/**
 * Utility: Debounce function
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Utility: Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
