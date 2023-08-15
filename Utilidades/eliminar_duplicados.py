import csv
from collections import defaultdict

def eliminar_duplicados(archivo_csv):
    # Leer el archivo CSV
    with open(archivo_csv, 'r') as file:
        reader = csv.reader(file)
        # Leer las cabeceras
        headers = next(reader)
        # Crear un diccionario para rastrear las filas con la misma abreviación
        abreviaciones_duplicadas = defaultdict(list)
        # Recorrer las filas y agrupar las filas con la misma abreviación
        for row in reader:
            abreviacion = row[1]  # Columna de abreviaciones (cambiar el índice según corresponda)
            abreviaciones_duplicadas[abreviacion].append(row)

    acciones_eliminadas = 0
    filas_eliminadas = []

    # Eliminar las filas duplicadas, dejando solo una de ellas
    for abreviacion, filas in abreviaciones_duplicadas.items():
        if len(filas) > 1:
            # Mantener la primera fila y eliminar las demás
            filas_eliminadas.extend(filas[1:])
            acciones_eliminadas += len(filas) - 1

    # Imprimir las acciones eliminadas y las filas correspondientes
    print(f"Acciones eliminadas: {acciones_eliminadas}")
    print("Filas eliminadas:")
    for fila in filas_eliminadas:
        print(fila)

# Especificar el archivo CSV que contiene las abreviaciones y nombres completos
archivo_csv = 'Lista_acciones.csv'  # Cambiar a la ruta correcta
eliminar_duplicados(archivo_csv)
