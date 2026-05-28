import yfinance as yf

ticker = yf.Ticker("486600.KS")
hist = ticker.history(period='1d')
print(hist)
