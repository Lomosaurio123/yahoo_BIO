import os
import yfinance as yf,csv, io, datetime
import pandas as pd

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
    stock_symbol = csv_filename.split('/')[2]
    stock_symbol=stock_symbol.split('_')[3]
    adj_close_data = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = clean_keys(row)
            adj_close_data.append({'date': row['Date'], 'adj_close': float(cleaned_row['Adj_Close'])})
    return stock_symbol, adj_close_data

def calcular_matriz_correlacion(rendimientos_diarios):
    data_dict = {}
    min_length = min([len(rendimientos) for rendimientos in rendimientos_diarios.values()])  # Encuentra la longitud mínima

    for stock_symbol, rendimientos in rendimientos_diarios.items():
        data_dict[stock_symbol] = rendimientos[:min_length]  # Limita los rendimientos a la longitud mínima

    df_rendimientos = pd.DataFrame(data_dict)
    matriz_correlacion = df_rendimientos.corr()
    return matriz_correlacion


def leer_csv(csv_filenames):
    all_adj_close_data = [] 

    for csv_filename in csv_filenames:
        ruta_csv = f'./Historial_accion_csv_xlsx/{csv_filename}'
        if os.path.exists(ruta_csv):
            stock_symbol, adj_close_data = get_adj_close(ruta_csv)
            all_adj_close_data.append({'stock_symbol': stock_symbol, 'adj_close_data': adj_close_data})

    return all_adj_close_data

def calcular_rendimientos_diarios(all_adj_close_data):
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

    return rendimientos_diarios