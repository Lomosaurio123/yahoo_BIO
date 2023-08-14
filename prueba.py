import yfinance as yf

stock_symbols="AAPL, T, PLUG, TSLA, LCID, F, NIO,NU ,VZ, WFC".replace(" ", "").split(",")

def validacion(stock_symbol):
    try:
        info=yf.Ticker(stock_symbol).info
        return True
    except Exception as e:
        return False

for stock_symbol in stock_symbols:
    print(stock_symbol)
    if validacion(stock_symbol):
        print("la accion existe")
    else:
        print("La accion no existe")
