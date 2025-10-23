import requests

r = requests.get('https://api.india.delta.exchange/v2/products?page_size=100')
products = r.json()['result']

# Check field names
if products:
    print("First product fields:")
    for key in products[0].keys():
        print(f"  {key}: {products[0][key]}")
    
    print("\n" + "=" * 60)
    
    # Find perpetuals by contract_type
    perps = [p for p in products if p.get('contract_type') == 'perpetual_futures']
    print(f'\nPerpetual futures (contract_type): {len(perps)}')
    for p in perps[:5]:
        print(f"  {p['symbol']} - {p.get('description')}")
