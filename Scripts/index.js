// Variable para mantener las sugerencias anteriores
let previousSuggestions = [];

// Función para obtener las sugerencias de acciones
function getActionSuggestions() {
    // Obtenemos el valor ingresado por el usuario en el campo "stock_symbol"
    const inputValue = document.getElementById('stock_symbol').value;

    if (inputValue === '') {
        // Si está vacío, limpiamos las sugerencias
        document.getElementById('suggestions').innerHTML = ''; 
        return; 
      }

    // Verificamos si el valor ingresado contiene una coma
    if (inputValue.includes(',')) {
        const inputParts = inputValue.split(',').map(part => part.trim());

        // Obtén sugerencias para la última parte después de la coma
        const lastInputPart = inputParts[inputParts.length - 1];
        fetch(`/get_suggestions?input=${lastInputPart}`)
            .then(response => response.json())
            .then(data => {
                // Borramos las sugerencias anteriores
                const suggestionsDiv = document.getElementById('suggestions');
                suggestionsDiv.innerHTML = '';

                // Mostramos las nuevas sugerencias (abreviación y nombre completo)
                data.forEach(item => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.textContent = `${item.abreviacion} - ${item.nombre_completo}`;
                    suggestionsDiv.appendChild(suggestionItem);
                });
            });
    } else {
        // Si no hay coma, borramos las sugerencias anteriores
        fetch(`/get_suggestions?input=${inputValue}`)
            .then(response => response.json())
            .then(data => {
                // Borramos las sugerencias anteriores
                const suggestionsDiv = document.getElementById('suggestions');
                suggestionsDiv.innerHTML = '';

                // Mostramos las nuevas sugerencias (abreviación y nombre completo)
                data.forEach(item => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.textContent = `${item.abreviacion} - ${item.nombre_completo}`;
                    suggestionsDiv.appendChild(suggestionItem);
                });
            });
    }
}

// Función para mostrar el mensaje de error si es necesario
function showError(errorMessage) {
    if (errorMessage) {
        alert(errorMessage);  // Muestra una alerta simple
        }
}