"""
Quick test to demonstrate visible price verification logging
"""
import sys
import os
import requests
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

print("\n" + "=" * 80)
print("TESTING VISIBLE PRICE VERIFICATION LOGS")
print("=" * 80)
print()
print("This will send a test webhook and you should see:")
print("  📊 STEP 1: VERIFYING REAL-TIME PRICE FROM DELTA EXCHANGE")
print("  📊 Market data for BTCUSD: Bid=..., Ask=..., Mid=...")
print("  ✅ PRICE VERIFICATION PASSED")
print()
print("=" * 80)
print()

# Get current price first
print("Fetching current BTCUSD price from Delta Exchange...")
try:
    from tools.TradingClient import DeltaExchangeClient
    api_key = os.getenv('DELTA_API_KEY')
    api_secret = os.getenv('DELTA_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Delta Exchange credentials not configured")
        exit(1)
    
    client = DeltaExchangeClient(api_key, api_secret)
    orderbook = client.get_orderbook('BTCUSD')
    
    if orderbook.get('success'):
        result = orderbook['result']
        best_bid = float(result['buy'][0]['price'])
        best_ask = float(result['sell'][0]['price'])
        current_price = (best_bid + best_ask) / 2
        
        print(f"✅ Current BTCUSD Price: ${current_price:.2f}")
        print()
        
        # Send webhook with current price
        webhook_url = "http://localhost:5000/webhook"
        
        signal = {
            "action": "BUY",
            "symbol": "BTCUSD",
            "price": current_price,
            "message": "Test signal with current market price"
        }
        
        print("=" * 80)
        print("SENDING WEBHOOK REQUEST")
        print("=" * 80)
        print(f"Signal: {json.dumps(signal, indent=2)}")
        print()
        print("🔍 Watch the Flask terminal for price verification logs...")
        print("=" * 80)
        print()
        
        response = requests.post(
            webhook_url,
            json=signal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print("=" * 80)
        print("WEBHOOK RESPONSE")
        print("=" * 80)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("=" * 80)
        print()
        
    else:
        print(f"❌ Failed to fetch orderbook: {orderbook.get('error')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print()
print("Check Flask terminal output above for:")
print("  ✅ Real-time price verification logs")
print("  ✅ Market data (Bid/Ask/Mid)")
print("  ✅ Price comparison results")
print()
