"""
Simple test to fetch Delta Exchange products
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.delta_exchange_service import get_delta_trader


trader = get_delta_trader()

print("=" * 80)
print("FETCHING DELTA EXCHANGE PRODUCTS")
print("=" * 80)
print()

products = trader.fetch_all_products()

print(f"\nTotal products fetched: {len(products)}")

if products:
    print("\nFirst 5 products:")
    for i, product in enumerate(products[:5], 1):
        print(f"\n{i}. {product.get('symbol')}")
        print(f"   Description: {product.get('description')}")
        print(f"   Type: {product.get('product_type')}")
        print(f"   State: {product.get('state')}")
