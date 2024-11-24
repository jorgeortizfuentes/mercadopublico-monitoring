// Función para formatear números como moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(amount);
}

// Función para formatear fechas
function formatDate(dateString) {
    if (!dateString) return 'No especificado';
    return new Date(dateString).toLocaleDateString('es-CL');
}

// Función para mostrar notificaciones
function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.querySelector('main').insertAdjacentElement('afterbegin', alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Configurar tema oscuro para DataTables
$.extend(true, $.fn.dataTable.defaults, {
    "theme": 'dark',
    "processing": true,
    "serverSide": false,
    "searching": true,
    "ordering": true,
    "language": {
        "url": "//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json"
    }
});
