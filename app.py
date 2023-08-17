import csv, requests, os, numpy as np, pandas as pd, json, pathlib
from matplotlib import pyplot as plt
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from datetime import datetime
from functions import get_stock_history, clean_keys, buscador_previo, valiadcion_accion_existente, leer_csv, calcular_rendimientos_diarios, calcular_matriz_correlacion, verificacion_crear_archivo

app = Flask(__name__)

# RUTAS PARA ACCEDER A ARCHIVOS EXTERNOS--------------------------------------------------


@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'Static'), filename)


@app.route('/scripts/<path:filename>')
def serve_script(filename):
    return send_from_directory(os.path.join(app.root_path, 'Scripts'), filename)
# ----------------------------------------------------------------------------------------


@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    # Obtenemos el texto ingresado por el usuario en el campo "stock_symbol"
    input_text = request.args.get('input', '').strip().lower()

    # Ruta al archivo CSV
    csv_filename = 'Lista_acciones.csv'

    # Leer el contenido del archivo CSV y filtrar las acciones que coinciden con el texto ingresado
    suggestions = []
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            abreviacion = row['\ufeffAbreviacion']
            nombre_completo = row['NombreCompleto']

            if input_text in abreviacion.lower() or input_text in nombre_completo.lower():
                suggestions.append(
                    {'abreviacion': abreviacion, 'nombre_completo': nombre_completo})

    return jsonify(suggestions)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener las fechas directamente como objetos datetime
        periodo_inicial = datetime.strptime(
            request.form['start_date'], '%Y-%m-%d')
        periodo_final = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

        # Validar si la fecha inicial es posterior a la fecha final
        if periodo_inicial > periodo_final:
            return render_template('index.html', error_message="La fecha inicial debe ser anterior a la fecha final")

        stock_symbols = request.form['stock_symbol'].replace(
            " ", "").split(',')
        stock_symbols = [symbol.upper() for symbol in stock_symbols]

        # Eliminar archivos generados anteriormente con nombre que comienza con 'Historial_accion_from_'
        csv_files_to_delete = [file for file in os.listdir(pathlib.Path(
            'Historial_accion_csv_xlsx')) if file.startswith('Historial_accion_from_')]
        for file_to_delete in csv_files_to_delete:
            os.remove(pathlib.Path(
                'Historial_accion_csv_xlsx') / file_to_delete)

        # Eliminamos archivos Prices.xlsx si es que existen
        xlsx_files_to_delete = [f for f in os.listdir(
            pathlib.Path('Prices_xlsx')) if f.startswith('Precios')]
        for f in xlsx_files_to_delete:
            os.remove(pathlib.Path('Prices_xlsx') / f)

        stock_symbols.append("^MXX")

        # Validamos que existan las acciones
        for stock_symbol in stock_symbols:
            if valiadcion_accion_existente(stock_symbol):
                stock_symbol = stock_symbol.strip()
                prev_periodo_inicial = buscador_previo(
                    periodo_inicial, stock_symbol)
            else:
                msj_error = str(f'La accion {stock_symbol} no se encontró')
                return render_template('index.html', error_message=msj_error)

        csv_filenames = []  # Lista para almacenar los nombres de archivo CSV generados

        for stock_symbol in stock_symbols:
            stock_symbol = stock_symbol.strip()

            historial = get_stock_history(
                prev_periodo_inicial, periodo_final, stock_symbol)

            # Guardar los datos en un archivo CSV
            if stock_symbol == '^MXX':
                stock_symbol = 'IPC'

            csv_filename = f'Historial_accion_from_{stock_symbol}_{periodo_inicial.strftime("%Y-%m-%d")}_to_{periodo_final.strftime("%Y-%m-%d")}.csv'
            ruta_csv = f'./Historial_accion_csv_xlsx/{csv_filename}'
            historial.to_csv(ruta_csv, index=True, sep=',', encoding='utf-8')

            # Verificar si el archivo se creó correctamente
            # if os.path.exists(csv_filename):
            # Agregar el nombre del archivo a la lista
            csv_filenames.append(csv_filename)

        return render_template('result.html', csv_filenames=csv_filenames)

    return render_template('index.html')


@app.route('/display', methods=['GET'])
def display():
    csv_filename = request.args.get('csv_filename')
    ruta_csv = f'./Historial_accion_csv_xlsx/{csv_filename}'

    if csv_filename and os.path.exists(ruta_csv):
        # Leer el contenido del archivo CSV
        datos = []
        with open(ruta_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cleaned_row = clean_keys(row)
                datos.append(cleaned_row)
        fecha_inicial = datos[1]['Date']
        fecha_final = datos[-1]['Date']

        return render_template('display.html', datos=datos, nombre=csv_filename, fecha_inicial=fecha_inicial, fecha_final=fecha_final)
    else:
        return "Error: El archivo CSV no existe."


@app.route('/prices', methods=['GET'])
def prices():
    csv_filenames = request.args.getlist('csv_filename')
    all_adj_close_data = leer_csv(csv_filenames)
    return render_template('prices.html', data=all_adj_close_data)


@app.route('/matriz_correlacion', methods=['GET'])
def matriz_correlacion():
    csv_filenames = request.args.getlist('csv_filename')
    all_adj_close_data = leer_csv(csv_filenames)
    rendimientos_diarios = calcular_rendimientos_diarios(all_adj_close_data)
    matriz_correlacion = calcular_matriz_correlacion(rendimientos_diarios)
    return render_template('matriz_correlacion.html', matriz_correlacion=matriz_correlacion)


@app.route('/rendimientos', methods=['GET'])
def rendimientos():
    csv_filenames = request.args.getlist('csv_filename')

    all_adj_close_data = leer_csv(csv_filenames)
    rendimientos_diarios = calcular_rendimientos_diarios(all_adj_close_data)

    # Calcular la desviación estándar de cada acción
    desviacion_estandar = {}
    for stock_symbol, rendimientos in rendimientos_diarios.items():
        desviacion_estandar[stock_symbol] = (
            np.std(rendimientos) / 100) * (np.sqrt(252))

    # Calcular el rendimiento anual de cada acción
    rendimientos_anuales = {}
    for stock_symbol, rendimientos in rendimientos_diarios.items():
        ultimos252 = rendimientos[-252:]
        rendimientos_anuales[stock_symbol] = np.mean(ultimos252) * 252

    Cof_var = {}
    for stock_symbol, rendimientos in desviacion_estandar.items():
        Cof_var[stock_symbol] = (
            rendimientos_anuales[stock_symbol]/100)/desviacion_estandar[stock_symbol]

    # Obtener la lista de rendimientos de la última acción
    ultima_accion = list(rendimientos_diarios.keys())[-1]
    rendimientos_ultima_accion = rendimientos_diarios[ultima_accion]

    # Calcular betas, sistematico y no sistematico
    betas = {}
    sistematico = {}
    no_sistematico = {}

    for stock_symbol, rendimientos in rendimientos_diarios.items():
        if len(rendimientos) != len(rendimientos_ultima_accion):
            beta = np.polyfit(
                rendimientos, rendimientos_ultima_accion[:len(rendimientos)], 1)
            betas[stock_symbol] = beta[0]
            r2 = np.corrcoef(rendimientos, rendimientos_ultima_accion[:len(rendimientos)])[
                0, 1] ** 2
            sistematico[stock_symbol] = r2*100
            no_sistematico[stock_symbol] = (1-r2)*100
        else:
            beta = np.polyfit(rendimientos, rendimientos_ultima_accion, 1)
            betas[stock_symbol] = beta[0]
            r2 = np.corrcoef(rendimientos, rendimientos_ultima_accion)[
                0, 1] ** 2
            sistematico[stock_symbol] = r2*100
            no_sistematico[stock_symbol] = (1-r2)*100

    # Obtener TLR de cetes
    tlr = {}
    url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43945/datos/oportuno?token=095aad77fedb56adf22ea01d8e61808ae121fd87ac7d62c030ca97887d5dd2ad'

    response = requests.get(url)
    data = response.json()
    series = data['bmx']['series'][0]['datos']
    tasa = series[0]['dato']
    # SHARPES
    sharpes = {}

    for stock_symbol, rendimientos in rendimientos_diarios.items():
        tlr[stock_symbol] = float(tasa)
        sharpes[stock_symbol] = ((rendimientos_anuales[stock_symbol]/100) -
                                 (tlr[stock_symbol]/100))/desviacion_estandar[stock_symbol]

    return render_template('rendimientos.html', data=all_adj_close_data, diarios=rendimientos_diarios, desviacion_estandar=desviacion_estandar, rendimientos_anuales=rendimientos_anuales,
                           coeficiente=Cof_var, beta=betas, sistematico=sistematico, no_sistematico=no_sistematico, tlr=tlr, sharpes=sharpes)


@app.route('/download', methods=['GET'])
def download():
    csv_filename = request.args.get('csv_filename')
    ruta_csv = f'./Historial_accion_csv_xlsx/{csv_filename}'
    historial = pd.read_csv(ruta_csv)

    # Eliminar la primera fila (excepto los encabezados)
    historial = historial.iloc[1:]

    # Definir el nombre del archivo .xlsx para la conversión
    xlsx_filename = ruta_csv[:-4] + '.xlsx'

    # Guardar el DataFrame en un archivo Excel (.xlsx)
    historial.to_excel(xlsx_filename, index=False)

    if xlsx_filename:
        return send_file(xlsx_filename, as_attachment=True)
    else:
        return "Error: Nombre de archivo no proporcionado"

@app.route('/download_file', methods=['GET'])
def download_prices():
    ruta=request.args.get('ruta')

    if ruta:
        return send_file(ruta,as_attachment=True)
    else:
        return "Error archivo no encontrado"

@app.route('/download_tabla', methods=['POST'])
def download_tabla():
    try:
        tableData = request.get_json()
        opcion=int(tableData['Opcion'])

        if 'Opcion' in tableData:
            del tableData['Opcion']
        
        if opcion==1:
            tableData['headers']=tableData['headers'][:-1]
            tableData['data']= tableData['data'][2:]
            
            df = pd.DataFrame(tableData['data'], columns=tableData['headers'])
            ruta_archivo = './Prices_xlsx/Precios.xlsx'
            
            df.to_excel(ruta_archivo, header=True, index=False)
            
            return verificacion_crear_archivo(ruta_archivo)
        
        elif opcion==2:
            cleaned_data = [[value.strip() for value in sublist] for sublist in tableData['data']]
            cleaned_data=cleaned_data[1:-1]
            tableData['data'] = cleaned_data
            tableData['headers']=tableData['headers'][:-1]
            
            df = pd.DataFrame(tableData['data'], columns=tableData['headers'])
            ruta_archivo = './Rendimientos_xslx/Rendimientos.xlsx'
            
            df.to_excel(ruta_archivo, header=True, index=False)
            
            return verificacion_crear_archivo(ruta_archivo)

        elif opcion == 3:
            headers=tableData['headers'][:-1]
            data=tableData['data']

            df = pd.DataFrame(data, columns=headers)
            ruta_archivo = './MatrizCorrelacion_xlsx/MatrizCorrelacion.xlsx'

            df.to_excel(ruta_archivo, header=True, index=False)

            #MAPA DE COLOR
            data = np.array(data)
            data = data[:,1:].astype(float)

            # Crear la figura y el eje
            fig, ax = plt.subplots()
           
            # Crear el mapa de calor
            heatmap = ax.imshow(data, cmap=plt.cm.RdYlBu_r, vmin=-1, vmax=1)  # Ajusta los límites de vmin y vmax según tus necesidades

            # Agregar barra de colores
            cbar = plt.colorbar(heatmap)
            
            # Definir etiquetas de los ejes
            tick_labels = headers[1:]
            ax.set_xticks(np.arange(len(tick_labels)))
            ax.set_yticks(np.arange(len(tick_labels)))
            ax.set_xticklabels(tick_labels)
            ax.set_yticklabels(tick_labels)

            # Rotar las etiquetas y ajustar la posición
            plt.setp(ax.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor")

            # Mostrar el mapa de calor
            plt.show()

            return verificacion_crear_archivo(ruta_archivo)
        else:
            return "Opción no válida"

        
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run(debug=True)