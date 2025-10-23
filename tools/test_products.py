#!/usr/bin/env python3
"""
Quick test script for Delta Exchange products
"""
import json
from TradingClient import DeltaExchangeClient

# Initialize client
api_key = 'j2ydI3WbKAuIF6GrXJhUO8y05qknh6'
api_secret = 'vY13i5LGd3v3s6TWnRZy9fvdjK1HvfiwgK6SjdKjJMROjpIgeeglrLXSN3MK'
client = DeltaExchangeClient(api_key, api_secret)

print("🔍 Searching for BTCUSD perpetual contracts...")
print("=" * 60)

# Get all products
products = client.get_products()

if products.get('success'):
    all_products = products.get('result', [])
    
    # Search for BTC perpetuals
    btc_perpetuals = [
        p for p in all_products 
        if 'BTC' in p.get('symbol', '') and 
        'perpetual' in p.get('contract_type', '').lower()
    ]
    
    print(f"\n📊 Found {len(btc_perpetuals)} BTC Perpetual contracts:\n")
    
    for product in btc_perpetuals[:5]:  # Show first 5
        print(f"ID: {product.get('id')}")
        print(f"Symbol: {product.get('symbol')}")
        print(f"Description: {product.get('description')}")
        print(f"Contract Type: {product.get('contract_type')}")
        print(f"Settlement Type: {product.get('settlement_time')}")
        print(f"Tick Size: {product.get('tick_size')}")
        print(f"Trading Status: {product.get('trading_status')}")
        print("-" * 60)

else:
    print(f"❌ Failed to get products: {products}")
