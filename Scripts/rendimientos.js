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

color_data( "datosTabla", "tr" )