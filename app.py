import csv
import io
import requests
from flask import Flask, make_response, render_template, request, send_file, jsonify, send_from_directory
import datetime
import os
import numpy as np
from functions import get_stock_history, clean_keys, get_adj_close

app = Flask(__name__)

@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

@app.route('/Scripts/<path:filename>')
def serve_script(filename):
    return send_from_directory('Scripts', filename)

@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    # Obtenemos el texto ingresado por el usuario en el campo "stock_symbol"
    input_text = request.args.get('input', '').strip().lower()

    # Ruta al archivo CSV
    csv_filename = 'Lista_acciones.csv'

    # Leer el contenido del archivo CSV y filtrar las acciones que coinciden con el texto ingresado
    suggestions = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            abreviacion = row['ï»¿Abreviacion']
            nombre_completo = row['NombreCompleto']

            if input_text in abreviacion.lower() or input_text in nombre_completo.lower():
                suggestions.append({'abreviacion': abreviacion, 'nombre_completo': nombre_completo})

    return jsonify(suggestions)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        periodo_inicial = [
            int(request.form['start_year']),
            int(request.form['start_month']),
            int(request.form['start_day'])
        ]
        periodo_final = [
            int(request.form['end_year']),
            int(request.form['end_month']),
            int(request.form['end_day'])
        ]
        stock_symbols = request.form['stock_symbol'].split(',') 
        stock_symbols.append("^MXX")

        start_date = datetime.datetime(periodo_inicial[0], periodo_inicial[1], periodo_inicial[2])
        end_date = datetime.datetime(periodo_final[0], periodo_final[1], periodo_final[2])

        # Eliminar archivos CSV con nombre que comienza con 'Historial_'
        csv_files_to_delete = [file for file in os.listdir() if file.startswith('Historial_accion_from_')]
        for file_to_delete in csv_files_to_delete:
            os.remove(file_to_delete)

        csv_filenames = []  # Lista para almacenar los nombres de archivo CSV generados

        for stock_symbol in stock_symbols:
            stock_symbol = stock_symbol.strip()

            historial = get_stock_history(start_date, end_date, stock_symbol)

            # Guardar los datos en un archivo CSV
            csv_filename = f'Historial_accion_from_{stock_symbol}_{start_date.strftime("%Y-%m-%d")}_to_{end_date.strftime("%Y-%m-%d")}.csv'
            historial.to_csv(csv_filename, index=True)

            # Verificar si el archivo se creó correctamente
            if os.path.exists(csv_filename):
                csv_filenames.append(csv_filename)  # Agregar el nombre del archivo a la lista

        return render_template('result.html', csv_filenames=csv_filenames)

    return render_template('index.html')

@app.route('/acciones', methods=['GET'])
def acciones():
    # Lista para almacenar las abreviaciones de las acciones y sus nombres completos
    lista_acciones = []

    # Ruta al archivo CSV
    csv_filename = 'Lista_acciones.csv'

    # Leer y mostrar el contenido del archivo CSV
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            abreviacion = row['ï»¿Abreviacion']
            nombre_completo = row['NombreCompleto']
            lista_acciones.append({'abreviacion': abreviacion, 'nombre_completo': nombre_completo})

    return render_template('acciones.html', lista_acciones=lista_acciones)

@app.route('/download', methods=['GET'])
def download():
    csv_filename = request.args.get('csv_filename')
    if csv_filename:
        return send_file(csv_filename, as_attachment=True)
    else:
        return "Error: Nombre de archivo no proporcionado."


@app.route('/display', methods=['GET'])
def display():
    csv_filename = request.args.get('csv_filename')


    if csv_filename and os.path.exists(csv_filename):
        # Leer el contenido del archivo CSV
        datos = []
        with open(csv_filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cleaned_row = clean_keys(row)
                datos.append(cleaned_row)

        return render_template('display.html', datos=datos,nombre=csv_filename)
    else:
        return "Error: El archivo CSV no existe."

@app.route('/prices', methods=['GET'])
def prices():
    csv_filenames = request.args.getlist('csv_filename')
    all_adj_close_data = [] 

    for csv_filename in csv_filenames:
        if os.path.exists(csv_filename):
            stock_symbol, adj_close_data = get_adj_close(csv_filename)
            all_adj_close_data.append({'stock_symbol': stock_symbol, 'adj_close_data': adj_close_data})

    return render_template('prices.html', data=all_adj_close_data)

@app.route('/rendimientos', methods=['GET'])
def rendimientos():
    csv_filenames = request.args.getlist('csv_filename')
    all_adj_close_data = [] 

    for csv_filename in csv_filenames:
        if os.path.exists(csv_filename):
            stock_symbol, adj_close_data = get_adj_close(csv_filename)
            all_adj_close_data.append({'stock_symbol': stock_symbol, 'adj_close_data': adj_close_data})

    # Calcular los rendimientos diarios y guardarlos en un diccionario
    rendimientos_diarios = {}
    for data in all_adj_close_data:
        stock_symbol = data['stock_symbol']
        adj_close_data = data['adj_close_data']

        rendimientos_diarios[stock_symbol] = []
        for i in range(1, len(adj_close_data)):
            previous_close = adj_close_data[i-1]['adj_close']
            current_close = adj_close_data[i]['adj_close']
            result = ((previous_close / current_close) - 1) * 100
            rendimientos_diarios[stock_symbol].append(result)


    # Calcular la desviación estándar de cada acción
    desviacion_estandar = {}
    for stock_symbol, rendimientos in rendimientos_diarios.items():
        desviacion_estandar[stock_symbol] = (np.std(rendimientos) / 100) * (np.sqrt(252))

    # Calcular el rendimiento anual de cada acción
    rendimientos_anuales = {}
    for stock_symbol, rendimientos in rendimientos_diarios.items():
        rendimientos_anuales[stock_symbol] = np.mean(rendimientos) * 252

    Cof_var = {}
    for stock_symbol, rendimientos in desviacion_estandar.items():
        Cof_var[stock_symbol] = (rendimientos_anuales[stock_symbol]/100)/desviacion_estandar[stock_symbol]

    
    # Obtener la lista de rendimientos de la última acción
    ultima_accion = list(rendimientos_diarios.keys())[-1]
    rendimientos_ultima_accion = rendimientos_diarios[ultima_accion]
    
    #Calcular betas, sistematico y no sistematico
    betas = {}
    sistematico={}
    no_sistematico={}
    

    for stock_symbol, rendimientos in rendimientos_diarios.items():
        if len(rendimientos) != len(rendimientos_ultima_accion):
            beta = np.polyfit(rendimientos, rendimientos_ultima_accion[:len(rendimientos)], 1)
            betas[stock_symbol] = beta[0]
            r2 = np.corrcoef(rendimientos, rendimientos_ultima_accion[:len(rendimientos)])[0, 1] ** 2
            sistematico[stock_symbol] = r2*100
            no_sistematico[stock_symbol]=(1-r2)*100
        else:
            beta = np.polyfit(rendimientos, rendimientos_ultima_accion, 1)
            betas[stock_symbol] = beta[0]
            r2 = np.corrcoef(rendimientos, rendimientos_ultima_accion)[0, 1] ** 2
            sistematico[stock_symbol] = r2*100
            no_sistematico[stock_symbol]=(1-r2)*100
            
    #Obtener TLR de cetes
    tlr={}
    url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43945/datos/oportuno?token=095aad77fedb56adf22ea01d8e61808ae121fd87ac7d62c030ca97887d5dd2ad'

    response = requests.get(url)
    data = response.json()
    series = data['bmx']['series'][0]['datos']
    tasa = series[0]['dato'] 
    #SHARPES
    sharpes={}

    for stock_symbol, rendimientos in rendimientos_diarios.items():
        tlr[stock_symbol] = float(tasa)
        sharpes[stock_symbol]=((rendimientos_anuales[stock_symbol]/100)-(tlr[stock_symbol]/100))/desviacion_estandar[stock_symbol]

    return render_template('rendimientos.html', data=all_adj_close_data, desviacion_estandar=desviacion_estandar, rendimientos_anuales=rendimientos_anuales, coeficiente=Cof_var, beta=betas, sistematico=sistematico, no_sistematico=no_sistematico, tlr=tlr, sharpes=sharpes)


def generar_csv(data):
    if not data:
        return "Error: No se seleccionaron datos para la generación del CSV."

    csv_data = {}
    for item in data:
        date, stock_symbol, adj_close = item.split(',')
        if date not in csv_data:
            csv_data[date] = {}
        csv_data[date][stock_symbol] = adj_close

    # Generar el archivo CSV en memoria
    csv_buffer = io.StringIO()
    fieldnames = ['Fecha'] + list(csv_data[data[0].split(',')[0]].keys())
    writer = csv.writer(csv_buffer)
    writer.writerow(fieldnames)

    for date, adj_close_data in csv_data.items():
        row_data = [date]
        for stock_symbol in fieldnames[1:]:
            row_data.append(adj_close_data.get(stock_symbol, ''))
        writer.writerow(row_data)

    return csv_buffer.getvalue()

@app.route('/download_csv', methods=['POST'])
def download_csv():
    data = request.form.getlist('data[]')
    filename = request.form.get('nombre_csv')  # Obtener el nombre del archivo

    contenido_csv = generar_csv(data)

    # Preparar la respuesta para descargar el archivo CSV
    response = make_response(contenido_csv)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"

    return response

if __name__ == '__main__':
    app.run(debug=True)