#!/usr/bin/env python3
"""
Check current BTCUSD futures price
"""
from TradingClient import DeltaExchangeClient

# Initialize client
api_key = 'j2ydI3WbKAuIF6GrXJhUO8y05qknh6'
api_secret = 'vY13i5LGd3v3s6TWnRZy9fvdjK1HvfiwgK6SjdKjJMROjpIgeeglrLXSN3MK'
client = DeltaExchangeClient(api_key, api_secret)

print("📊 Fetching BTCUSD Perpetual Futures Price")
print("=" * 60)

# Get ticker data
print("\n🔍 Getting ticker data...")
ticker = client.get_ticker('BTCUSD')

if ticker.get('success'):
    result = ticker.get('result', [])
    if result and len(result) > 0:
        btc_data = result[0]
        
        print("\n💰 BTCUSD Price Information:")
        print(f"   Symbol: {btc_data.get('symbol')}")
        print(f"   Mark Price: ${btc_data.get('mark_price', 'N/A')}")
        print(f"   Last Price: ${btc_data.get('close', 'N/A')}")
        print(f"   24h High: ${btc_data.get('high', 'N/A')}")
        print(f"   24h Low: ${btc_data.get('low', 'N/A')}")
        print(f"   24h Volume: {btc_data.get('volume', 'N/A')}")
        print(f"   24h Change: {btc_data.get('price_change', 'N/A')}%")
        print(f"   Open Interest: {btc_data.get('oi', 'N/A')}")
        print(f"   Funding Rate: {btc_data.get('funding_rate', 'N/A')}")
    else:
        print("⚠️  No ticker data found")
else:
    print(f"❌ Failed: {ticker.get('error', 'Unknown error')}")

# Get orderbook
print("\n\n📖 Getting orderbook data...")
orderbook = client.get_orderbook(symbol='BTCUSD', depth=5)

if orderbook.get('success'):
    result = orderbook.get('result', {})
    buy_orders = result.get('buy', [])
    sell_orders = result.get('sell', [])
    
    print("\n📈 Order Book (Top 5 levels):")
    print("\n   ASKS (Sell Orders):")
    for ask in reversed(sell_orders[-5:]):
        print(f"   ${ask.get('price'):>10} | Size: {ask.get('size'):>10}")
    
    print("\n   " + "-" * 40)
    
    if buy_orders:
        best_bid = buy_orders[0].get('price')
        print(f"   Best Bid: ${best_bid}")
    if sell_orders:
        best_ask = sell_orders[0].get('price')
        print(f"   Best Ask: ${best_ask}")
    print("   " + "-" * 40)
    
    print("\n   BIDS (Buy Orders):")
    for bid in buy_orders[:5]:
        print(f"   ${bid.get('price'):>10} | Size: {bid.get('size'):>10}")
else:
    print(f"❌ Failed: {orderbook.get('error', 'Unknown error')}")

print("\n" + "=" * 60)
print("✅ Price check completed!")
