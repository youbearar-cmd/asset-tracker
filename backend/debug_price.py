import price_service

symbol = "411060.KS"
price = price_service.get_current_price(symbol)
print(f"Price for {symbol}: {price}")

symbol = "461580.KS"
price = price_service.get_current_price(symbol)
print(f"Price for {symbol}: {price}")
