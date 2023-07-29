import yfinance as yf
import csv
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