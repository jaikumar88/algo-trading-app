"""
Diagnostic script to test ETHUSD price fetching
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from src.services.delta_exchange_service import get_delta_trader
from src.database.session import SessionLocal
from src.models.base import AllowedInstrument
from sqlalchemy import select


def test_ethusd_price():
    """Test fetching ETHUSD price from Delta Exchange"""
    print("\n" + "="*60)
    print("ETHUSD Price Diagnostic Test")
    print("="*60 + "\n")
    
    # Initialize trader
    print("[1] Initializing Delta Exchange trader...")
    trader = get_delta_trader()
    
    if not trader or not trader.client:
        print("[X] ERROR: Delta Exchange trader not initialized")
        return
    
    print("[OK] Trader initialized\n")
    
    # Check if ETHUSD is in database
    print("[2] Checking database for ETHUSD...")
    session = SessionLocal()
    ethusd_symbols = session.execute(
        select(AllowedInstrument).where(
            AllowedInstrument.symbol.like('%ETH%')
        )
    ).scalars().all()
    
    print(f"Found {len(ethusd_symbols)} ETH-related symbols:")
    for sym in ethusd_symbols:
        print(f"  - {sym.symbol} (enabled: {sym.enabled})")
    
    session.close()
    print()
    
    # Test different symbol variations
    test_symbols = ['ETHUSD', 'ETHUSDT', 'ETH-USD', 'ETHPERP']
    
    print("[3] Testing price fetch for different symbol formats...")
    print("-"*60)
    
    for symbol in test_symbols:
        print(f"\nTesting symbol: {symbol}")
        print(f"  Fetching orderbook...")
        
        try:
            orderbook = trader.client.get_orderbook(symbol)
            
            if not orderbook:
                print(f"  [X] No response from API")
                continue
            
            if not orderbook.get('success'):
                error = orderbook.get('error', 'Unknown error')
                print(f"  [X] API Error: {error}")
                continue
            
            result = orderbook.get('result', {})
            buy_orders = result.get('buy', [])
            sell_orders = result.get('sell', [])
            
            print(f"  [OK] Success!")
            print(f"  Buy orders: {len(buy_orders)}")
            print(f"  Sell orders: {len(sell_orders)}")
            
            if buy_orders and sell_orders:
                bid = float(buy_orders[0].get('price', 0))
                ask = float(sell_orders[0].get('price', 0))
                mid = (bid + ask) / 2
                
                print(f"  Bid: ${bid:.2f}")
                print(f"  Ask: ${ask:.2f}")
                print(f"  Mid: ${mid:.2f}")
                
                if mid == 0:
                    print(f"  [!] WARNING: Price is $0.00!")
                else:
                    print(f"  [OK] Valid price: ${mid:.2f}")
            else:
                print(f"  [X] No orders in orderbook")
                
        except Exception as e:
            print(f"  [X] Exception: {e}")
    
    print("\n" + "="*60)
    print("[4] Testing product search API...")
    print("-"*60)
    
    try:
        products = trader.client.get_products()
        
        if products.get('success'):
            all_products = products.get('result', [])
            print(f"Total products: {len(all_products)}\n")
            
            print("ETH-related perpetual futures:")
            eth_products = [
                p for p in all_products 
                if 'ETH' in p.get('symbol', '').upper() 
                and 'perpetual' in p.get('contract_type', '').lower()
            ]
            
            for product in eth_products[:10]:  # Show first 10
                symbol = product.get('symbol', 'N/A')
                product_id = product.get('id', 'N/A')
                settling_asset = product.get('settling_asset', {}).get('symbol', 'N/A')
                contract_type = product.get('contract_type', 'N/A')
                
                print(f"  {symbol} (ID: {product_id})")
                print(f"    Contract: {contract_type}")
                print(f"    Settling: {settling_asset}")
                print()
        else:
            print("[X] Failed to get products")
            
    except Exception as e:
        print(f"[X] Exception: {e}")
    
    print("="*60)
    print("\n[5] Recommendation:")
    print("-"*60)
    
    print("""
Based on Delta Exchange API:
1. Correct symbol format is likely 'ETHUSD' or product ID 139
2. Check if symbol exists in their products list
3. Verify you're using the correct contract_type
4. Some symbols might use 'ETHUSDT' instead

Try running this command to sync symbols:
  python tools/test_symbol_sync.py

Or manually check Delta Exchange API documentation:
  https://docs.delta.exchange
""")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    test_ethusd_price()
