document.addEventListener('DOMContentLoaded', function() {
    const formExcel = document.getElementById('formCargarExcel');
    
    if (formExcel) {
        formExcel.addEventListener('submit', function(e) {
            e.preventDefault(); // Detiene el envío automático

            Swal.fire({
                title: '¿Deseas realizar estos registros?',
                text: "Se procesará el archivo Excel. Los registros nuevos se crearán y los existentes actualizarán su información.",
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#0d6efd',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, cargar alumnos',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit(); // Si confirma, se envía el formulario
                }
            });
        });
    }
});