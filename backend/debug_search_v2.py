import price_service

query = "SOL 금현물"
results = price_service.search_symbol(query)
print(f"Results for '{query}':")
for r in results:
    print(r)
