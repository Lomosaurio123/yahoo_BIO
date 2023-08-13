import yfinance as yf
import datetime
accion='NU'
msft = yf.Ticker(accion)
info = msft.info
info=info['firstTradeDateEpochUtc']
info=datetime.datetime.utcfromtimestamp(info)


print(info)

stock_data = yf.download(accion, start="1000-01-01", end='2021-12-10')
print(stock_data)