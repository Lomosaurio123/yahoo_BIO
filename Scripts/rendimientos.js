// Funcion para descargar el csv

function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;

    // Crear el archivo CSV
    csvFile = new Blob([csv], { type: "text/csv" });

    // Crear un enlace de descarga
    downloadLink = document.createElement("a");

    // Establecer el enlace para el archivo CSV
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);

    // Simular el clic para descargar el archivo
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
    downloadLink.click();
  }

// Funcion para generar el csv
function generateCSV() {
    // Obtener los datos de la tabla
    var table = document.getElementById("datosTabla");
    var rows = table.getElementsByTagName("tr");

    var csv = "";
    for (var i = 0; i < rows.length; i++) {
      var row = [],
        cols = rows[i].querySelectorAll("td, th");

      for (var j = 0; j < cols.length; j++) {
        row.push(cols[j].innerText);
      }

      csv += row.join(",") + "\n";
    }

    // Descargar el archivo CSV
    downloadCSV(csv, "Rendimientos.csv"); 

}

function color_data( id_tabla, id_filas ) {

    // Obtener los datos de la tabla
    var table = document.getElementById( id_tabla );
    var rows = table.getElementsByTagName( id_filas );
        
    // Obtener la cantidad de acciones
    
    cantidad_acciones = rows[1].querySelectorAll("td, th").length - 1;
    
    for( let accion = 1; accion <= cantidad_acciones; accion ++ ) {
    
        // Evaluar la diferencia de valores por cada acción
        for (let i = rows.length - 1; i >= 3; i--) {
            
            let columna_actual = rows[i].querySelectorAll("td, th");
    
            let columna_posterior = rows[i - 1].querySelectorAll("td, th");
    
            if( parseFloat(columna_actual[ accion ].innerText) > parseFloat(columna_posterior[ accion ].innerText) ) columna_actual[accion].classList.add("color-verde");
    
            else columna_actual[accion].classList.add("color-rojo");
            
        }
    
    }
        
}

function rendimiento_anual( id_tabla, id_filas ) {

    
    // Obtener los datos de la tabla
    var table = document.getElementById( id_tabla );
    var rows = table.getElementsByTagName( id_filas );
        
    // Obtener la cantidad de acciones
    
    cantidad_acciones = rows[1].querySelectorAll("td, th").length - 1;

    rendimientos = []
    
    for( let accion = 1; accion <= cantidad_acciones; accion ++ ) {

        let suma = 0
    
        // Evaluar la diferencia de valores por cada acción
        for ( let i = 2; i < rows.length; i++ ) {
            
            let columna = rows[i].querySelectorAll("td, th");

            suma += parseFloat( columna[accion].innerText )
            
        }

        rendimientos.push( ( suma / rows.length ) * 252 )
    
    }

    return rendimientos

}


  // Asociar la función de generación de CSV al botón "Generar CSV"
document.getElementById("GenerarCSV").addEventListener("click", generateCSV);

color_data( "datosTabla", "tr" )

// Llamar a la función para calcular los rendimientos
const rendimientosCalculados = rendimiento_anual("datosTabla", "tr");

// Obtener la fila "RendimientoAnual" de la tabla "accionesTabla"
const filaRendimientoAnual = document.getElementById("RendimientoAnual");

// Agregar las celdas con los rendimientos anuales en la fila "RendimientoAnual"
rendimientosCalculados.forEach((rendimiento) => {
    const celdaRendimientoAnual = filaRendimientoAnual.insertCell();
    celdaRendimientoAnual.innerHTML = rendimiento.toFixed(2) + "%"; // Formatear el rendimiento con dos decimales y agregar el símbolo de porcentaje
});