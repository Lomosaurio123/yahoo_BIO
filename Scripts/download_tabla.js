document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor de Opcion del formulario
    const opcionInput = document.querySelector('input[name="Opcion"]');
    const opcionValue = opcionInput ? opcionInput.value : '';

    // Obtener los encabezados de la tabla
    const headers = [];
    const headerCells = document.querySelectorAll('#datosTabla th');
    headerCells.forEach(cell => {
        headers.push(cell.textContent);
    });

    // Obtener los datos de la tabla
    const data = [];
    const stockSymbols = new Set();

    const tableRows = document.querySelectorAll('#datosTabla tr:not(:first-child)');
    tableRows.forEach(row => {
        const rowData = [];

        // Obtener las celdas de datos para esta fila
        const dataCells = row.querySelectorAll('td');
        dataCells.forEach(cell => {
            rowData.push(cell.textContent);
        });

        // Obtener el símbolo de stock asociado a las celdas de datos
        const stockSymbol = row.getAttribute('data-stock-symbol');
        stockSymbols.add(stockSymbol);

        data.push(rowData);
    });

    // Agregar los símbolos de stock a los encabezados
    stockSymbols.forEach(symbol => {
        headers.push(symbol);
    });

    // Enviar los datos al backend
    const tableData = {
        headers: headers,
        data: data,
        Opcion: opcionValue  // Usar el valor de Opcion obtenido del formulario
    };

    fetch('/download_tabla', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tableData)
    })
        .then(response => {
            console.log('Se envió la tabla:');
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
