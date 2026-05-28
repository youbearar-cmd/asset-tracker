import price_service

query = "486600"
results = price_service.search_symbol(query)
print(f"Results for '{query}':")
for r in results:
    print(r)
