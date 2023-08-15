$(document).ready(function () {
    $('#csvForm').submit(function (event) {
        event.preventDefault();  // Evitar la acción por defecto del formulario

        var tableData = [];
        $('#datosTabla tr:gt(0)').each(function () { // Utiliza :gt(0) para saltar la primera fila
            var rowData = [];
            $(this).find('th, td').each(function () {
                rowData.push($(this).text());
            });
            tableData.push(rowData);
        });

        $.ajax({
            type: 'post',
            url: '/download_tabla',
            data: { tableData: JSON.stringify(tableData) },
            success: function (response) {
            }
        });
    });
});
