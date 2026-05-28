import price_service

queries = ["sol 국제금", "sol 금"]
for query in queries:
    results = price_service.search_symbol(query)
    print(f"Results for '{query}':")
    for r in results:
        print(r)
    print("-" * 20)
