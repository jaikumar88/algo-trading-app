"""
Test Delta Exchange integration with webhook system
"""
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_delta_trader():
    """Test Delta Exchange trader initialization and methods"""
    from src.services.delta_exchange_service import get_delta_trader
    
    print("=" * 60)
    print("Testing Delta Exchange Trader Integration")
    print("=" * 60)
    
    # Initialize trader
    trader = get_delta_trader()
    
    # Test 1: Check status
    print("\n1. Trading System Status:")
    status = trader.get_status()
    print(json.dumps(status, indent=2))
    
    if not status['client_ready']:
        print("\n❌ Client not ready. Set environment variables:")
        print("   DELTA_API_KEY")
        print("   DELTA_API_SECRET")
        print("   DELTA_TRADING_ENABLED=true (to enable live trading)")
        return
    
    # Test 2: Get product ID
    print("\n2. Testing Product ID Lookup:")
    symbols = ['BTCUSD', 'ETHUSD', 'BTCUSDT']
    for symbol in symbols:
        product_id = trader.get_product_id(symbol)
        print(f"   {symbol}: Product ID = {product_id}")
    
    # Test 3: Price verification
    print("\n3. Testing Price Verification:")
    test_symbol = 'BTCUSD'
    test_price = 108000.0  # Example price
    
    is_valid, current_price, msg = trader.verify_price(test_symbol, test_price)
    print(f"   Symbol: {test_symbol}")
    print(f"   Expected Price: ${test_price:,.2f}")
    print(f"   Current Price: ${current_price:,.2f}")
    print(f"   Valid: {is_valid}")
    print(f"   Message: {msg}")
    
    # Test 4: Simulate order placement (dry run if not enabled)
    print("\n4. Testing Order Placement:")
    order_result = trader.place_order(
        symbol='BTCUSD',
        side='buy',
        price=current_price if current_price > 0 else 108000.0,
        size=1
    )
    
    print("   Success:", order_result.get('success'))
    print("   Message:", order_result.get('message'))
    if order_result.get('dry_run'):
        print("   [!] Dry run mode - no actual order placed")
    if order_result.get('order_id'):
        print("   Order ID:", order_result.get('order_id'))
    if order_result.get('error'):
        print("   Error:", order_result.get('error'))
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


def test_webhook_integration():
    """Test the full webhook signal processing flow"""
    print("\n" + "=" * 60)
    print("Testing Webhook Integration")
    print("=" * 60)
    
    # Import webhook processor
    from src.api.webhook import process_trade_signal
    
    # Test signal data
    test_signals = [
        {
            'action': 'buy',
            'symbol': 'BTCUSD',
            'price': 108000.0,
            'size': 1
        },
        {
            'action': 'sell',
            'symbol': 'BTCUSD',
            'price': 108500.0,
            'size': 1
        }
    ]
    
    for i, signal in enumerate(test_signals, 1):
        print(f"\nTest Signal {i}:")
        print(f"   Action: {signal['action']}")
        print(f"   Symbol: {signal['symbol']}")
        print(f"   Price: ${signal['price']:,.2f}")
        
        result = process_trade_signal(signal)
        
        print(f"\nResult:")
        print(f"   Action: {result.get('action')}")
        print(f"   Message: {result.get('message')}")
        
        delta_order = result.get('delta_order')
        if delta_order:
            print(f"\nDelta Exchange Order:")
            print(f"   Success: {delta_order.get('success')}")
            print(f"   Message: {delta_order.get('message')}")
            if delta_order.get('order_id'):
                print(f"   Order ID: {delta_order.get('order_id')}")
        
        print("-" * 60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Delta Exchange integration')
    parser.add_argument('--full', action='store_true', help='Run full webhook integration test')
    args = parser.parse_args()
    
    # Run trader tests
    test_delta_trader()
    
    # Run webhook integration if requested
    if args.full:
        test_webhook_integration()
    else:
        print("\nℹ️  To test full webhook integration, run with --full flag")
