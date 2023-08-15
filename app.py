import csv, requests, os, numpy as np, pandas as pd,json
import xlsxwriter
from io import BytesIO
from flask import Flask, Response, render_template, request, send_file, jsonify, send_from_directory
from datetime import datetime
from functions import get_stock_history, clean_keys, get_adj_close, buscador_previo, valiadcion_accion_existente, leer_csv, calcular_rendimientos_diarios, calcular_matriz_correlacion

app = Flask(__name__)

#RUTAS PARA ACCEDER A ARCHIVOS EXTERNOS--------------------------------------------------
@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'Static'), filename)

@app.route('/scripts/<path:filename>')
def serve_script(filename):
    return send_from_directory(os.path.join(app.root_path, 'Scripts'), filename)
#----------------------------------------------------------------------------------------

@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    # Obtenemos el texto ingresado por el usuario en el campo "stock_symbol"
    input_text = request.args.get('input', '').strip().lower()

    # Ruta al archivo CSV
    csv_filename = 'Lista_acciones.csv'

    # Leer el contenido del archivo CSV y filtrar las acciones que coinciden con el texto ingresado
    suggestions = []
    with open(csv_filename, newline='',encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            abreviacion = row['\ufeffAbreviacion']
            nombre_completo = row['NombreCompleto']

            if input_text in abreviacion.lower() or input_text in nombre_completo.lower():
                suggestions.append({'abreviacion': abreviacion, 'nombre_completo': nombre_completo})

    return jsonify(suggestions)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener las fechas directamente como objetos datetime
        periodo_inicial = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        periodo_final = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

        # Validar si la fecha inicial es posterior a la fecha final
        if periodo_inicial > periodo_final:
            return render_template('index.html', error_message="La fecha inicial debe ser anterior a la fecha final")

        stock_symbols = request.form['stock_symbol'].replace(" ", "").split(',') 
        stock_symbols = [symbol.upper() for symbol in stock_symbols]

        # Eliminar archivos generados anteriormente con nombre que comienza con 'Historial_accion_from_'
        csv_files_to_delete = [file for file in os.listdir() if file.startswith('Historial_accion_from_')]
        for file_to_delete in csv_files_to_delete:
            os.remove(file_to_delete)

        #Validamos que existan las acciones
        for stock_symbol in stock_symbols:
            if valiadcion_accion_existente(stock_symbol):
                    stock_symbol = stock_symbol.strip()
                    prev_periodo_inicial=buscador_previo(periodo_inicial, stock_symbol)
            else:
                msj_error=str(f'La accion {stock_symbol} no se encontró')
                return render_template('index.html', error_message=msj_error)
                

        stock_symbols.append("^MXX")

        csv_filenames = []  # Lista para almacenar los nombres de archivo CSV generados

        for stock_symbol in stock_symbols:
            stock_symbol = stock_symbol.strip()

            historial = get_stock_history(prev_periodo_inicial, periodo_final, stock_symbol)

            # Guardar los datos en un archivo CSV
            if stock_symbol=='^MXX':
                stock_symbol='IPC'
            csv_filename = f'Historial_accion_from_{stock_symbol}_{periodo_inicial.strftime("%Y-%m-%d")}_to_{periodo_final.strftime("%Y-%m-%d")}.csv'
            historial.to_csv(csv_filename, index=True, sep=',',encoding='utf-8')

            # Verificar si el archivo se creó correctamente
            if os.path.exists(csv_filename):
                csv_filenames.append(csv_filename)  # Agregar el nombre del archivo a la lista

        return render_template('result.html', csv_filenames=csv_filenames)

    return render_template('index.html')

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
        fecha_inicial=datos[1]['Date']
        fecha_final=datos[-1]['Date']
        
        return render_template('display.html', datos=datos,nombre=csv_filename,fecha_inicial=fecha_inicial,fecha_final=fecha_final)
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
    print(matriz_correlacion)
    return render_template('matriz_correlacion.html', matriz_correlacion=matriz_correlacion)

@app.route('/rendimientos', methods=['GET'])
def rendimientos():
    csv_filenames = request.args.getlist('csv_filename')
    
    all_adj_close_data = leer_csv(csv_filenames)
    rendimientos_diarios = calcular_rendimientos_diarios(all_adj_close_data)

    # Calcular la desviación estándar de cada acción
    desviacion_estandar = {}
    for stock_symbol, rendimientos in rendimientos_diarios.items():
        desviacion_estandar[stock_symbol] = (np.std(rendimientos) / 100) * (np.sqrt(252))

    # Calcular el rendimiento anual de cada acción
    rendimientos_anuales = {}
    for stock_symbol, rendimientos in rendimientos_diarios.items():
        ultimos252=rendimientos[-252:]
        rendimientos_anuales[stock_symbol] = np.mean(ultimos252) * 252

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
    
    return render_template('rendimientos.html', data=all_adj_close_data, diarios=rendimientos_diarios, desviacion_estandar=desviacion_estandar, rendimientos_anuales=rendimientos_anuales, 
                           coeficiente=Cof_var, beta=betas, sistematico=sistematico, no_sistematico=no_sistematico, tlr=tlr, sharpes=sharpes)


@app.route('/download', methods=['GET'])
def download():
    csv_filename = request.args.get('csv_filename')
    historial = pd.read_csv(csv_filename)

    # Eliminar la primera fila (excepto los encabezados)
    historial = historial.iloc[1:]

    # Definir el nombre del archivo .xlsx para la conversión
    xlsx_filename = csv_filename[:-4] + '.xlsx'	

    # Guardar el DataFrame en un archivo Excel (.xlsx)
    historial.to_excel(xlsx_filename, index=False)

    if xlsx_filename:
        return send_file(xlsx_filename, as_attachment=True)
    else:
        return "Error: Nombre de archivo no proporcionado"


@app.route('/download_tabla', methods=['POST'])
def download_tabla():
    tableData = request.form.get('tableData')
    tableData = json.loads(tableData)
    del tableData[1]
    # Crear un archivo XLSX en memoria
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    
    for row_num, row in enumerate(tableData):
        for col_num, cell_value in enumerate(row):
            worksheet.write(row_num, col_num, cell_value)
    workbook.close()
    
    output.seek(0)

    # EL PROBLEMA ESTA AQUI
    response = Response(output.read(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=Precios.xlsx"
    
    return response

if __name__ == '__main__':
    app.run(debug=True)