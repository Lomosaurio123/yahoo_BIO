
@app.route('/download_csv', methods=['POST'])
def download_csv():
    data = request.form.getlist('data[]')
    filename = request.form.get('nombre_csv')  # Obtener el nombre del archivo
    print(filename)

    contenido_csv = generar_csv(data)

    # Preparar la respuesta para descargar el archivo CSV
    response = make_response(contenido_csv)
    response.headers["Content-Disposition"] = f