import yfinance as yf,csv, io, datetime

def valiadcion_accion_existente(stock_symbol):
    #Verificamos que las acciones ingresadas existan
    try:
        name_action=yf.Ticker(stock_symbol).info
        return True
    except Exception as e:
        return False

def buscador_previo(start_date, stock_symbol):
    # Configuración de parámetros
    periodo_inicial = start_date
    dia_previo = start_date
    dias_maximos_busqueda = 10  # Número máximo de días a retroceder

    #Validamos el caso cuando la fecha de incio dada es menor a la fecha de inicio de operaciones de la accion
    fehca_inicio_operaciones=datetime.datetime.utcfromtimestamp(yf.Ticker(stock_symbol).info['firstTradeDateEpochUtc'])

    if fehca_inicio_operaciones>start_date:
        dia_previo=fehca_inicio_operaciones
        return dia_previo

    # Bucle hasta encontrar datos o alcanzar el límite de días
    for _ in range(dias_maximos_busqueda):
        stock_data = yf.download(stock_symbol, start=dia_previo, end=periodo_inicial)

        if not stock_data.empty:
            return dia_previo
        dia_previo = dia_previo - datetime.timedelta(days=1)



def get_stock_history(start_date, end_date, stock_symbol):
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    return stock_data

def clean_keys(row):
    # Elimina espacios y caracteres especiales de los nombres de las claves
    cleaned_row = {}
    for key, value in row.items():
        cleaned_key = key.replace(" ", "_").replace("-", "").replace(".", "")
        cleaned_row[cleaned_key] = value
    return cleaned_row

def get_adj_close(csv_filename):
    stock_symbol = csv_filename.split('_')[3]
    adj_close_data = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = clean_keys(row)
            adj_close_data.append({'date': row['Date'], 'adj_close': float(cleaned_row['Adj_Close'])})
    return stock_symbol, adj_close_data

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