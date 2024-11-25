// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(amount);
}

function formatDate(dateString) {
    if (!dateString) return 'No especificado';
    return new Date(dateString).toLocaleDateString('es-CL');
}

// Notifications
function showNotification(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.appendChild(toast);
    document.body.appendChild(container);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        container.remove();
    });
}

// DataTables Configuration
$.extend(true, $.fn.dataTable.defaults, {
    language: {
        url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json'
    },
    dom: '<"d-flex justify-content-between align-items-center mb-4"Bf>rtip',
    buttons: [
        {
            extend: 'collection',
            text: '<i class="bx bx-export me-1"></i>Exportar',
            buttons: ['copy', 'csv', 'excel', 'pdf']
        }
    ],
    pageLength: 10,
    responsive: true,
    processing: true,
    stateSave: true
});

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
