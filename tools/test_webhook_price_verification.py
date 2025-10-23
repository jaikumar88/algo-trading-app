"""
Test webhook with real-time price verification
Shows detailed logging of price checking before trade opening
"""
import sys
import os
import requests
import json
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv()


def test_webhook_with_price_verification():
    """Test webhook endpoint with price verification logging"""
    
    webhook_url = "http://localhost:5000/webhook"
    
    print("=" * 80)
    print("TESTING WEBHOOK WITH REAL-TIME PRICE VERIFICATION")
    print("=" * 80)
    print()
    print("This test will:")
    print("1. Send a BUY signal to webhook")
    print("2. Show real-time price verification from Delta Exchange")
    print("3. Display whether trade was blocked or allowed")
    print()
    print("Watch the Flask app logs for detailed price verification!")
    print("=" * 80)
    print()
    
    # Test 1: BUY signal with current market price
    print("\n" + "=" * 80)
    print("TEST 1: BUY Signal with Current Market Price")
    print("=" * 80)
    
    # Get current price first
    print("Fetching current BTCUSD price from Delta Exchange...")
    try:
        from tools.TradingClient import DeltaExchangeClient
        api_key = os.getenv('DELTA_API_KEY')
        api_secret = os.getenv('DELTA_API_SECRET')
        
        if not api_key or not api_secret:
            print("❌ Delta Exchange credentials not configured")
            return
        
        client = DeltaExchangeClient(api_key, api_secret)
        orderbook = client.get_orderbook('BTCUSD')
        
        if orderbook.get('success'):
            result = orderbook['result']
            best_bid = float(result['buy'][0]['price'])
            best_ask = float(result['sell'][0]['price'])
            current_price = (best_bid + best_ask) / 2
            
            print(f"✅ Current BTCUSD Price: ${current_price:.2f}")
            print(f"   Bid: ${best_bid:.2f}, Ask: ${best_ask:.2f}")
            print()
            
            # Test with current price (should pass)
            signal_1 = {
                "action": "BUY",
                "symbol": "BTCUSD",
                "price": current_price,
                "message": "Test signal with current market price"
            }
            
            print(f"Sending BUY signal with price: ${current_price:.2f}")
            print("This should PASS price verification...")
            print()
            
            response = requests.post(
                webhook_url,
                json=signal_1,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print()
            
            # Wait a bit
            time.sleep(2)
            
            # Test 2: BUY signal with outdated price (should fail)
            print("\n" + "=" * 80)
            print("TEST 2: BUY Signal with Outdated Price (5% difference)")
            print("=" * 80)
            
            outdated_price = current_price * 0.95  # 5% lower
            
            signal_2 = {
                "action": "BUY",
                "symbol": "BTCUSD",
                "price": outdated_price,
                "message": "Test signal with outdated price"
            }
            
            print(f"Sending BUY signal with price: ${outdated_price:.2f}")
            print(f"Current market price: ${current_price:.2f}")
            print(f"Difference: {((current_price - outdated_price) / current_price * 100):.2f}%")
            print("This should FAIL price verification (>2% tolerance)...")
            print()
            
            response = requests.post(
                webhook_url,
                json=signal_2,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print()
            
            # Test 3: BUY signal with slightly different price (should pass)
            print("\n" + "=" * 80)
            print("TEST 3: BUY Signal with Slightly Different Price (1% difference)")
            print("=" * 80)
            
            slight_diff_price = current_price * 0.99  # 1% lower
            
            signal_3 = {
                "action": "BUY",
                "symbol": "BTCUSD",
                "price": slight_diff_price,
                "message": "Test signal with slight price difference"
            }
            
            print(f"Sending BUY signal with price: ${slight_diff_price:.2f}")
            print(f"Current market price: ${current_price:.2f}")
            print(f"Difference: {((current_price - slight_diff_price) / current_price * 100):.2f}%")
            print("This should PASS price verification (<2% tolerance)...")
            print()
            
            response = requests.post(
                webhook_url,
                json=signal_3,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print()
            
        else:
            print(f"❌ Failed to fetch orderbook: {orderbook.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
    print()
    print("Check Flask app logs for detailed price verification process!")
    print("Look for:")
    print("  📊 STEP 1: VERIFYING REAL-TIME PRICE FROM DELTA EXCHANGE")
    print("  ✅ PRICE VERIFICATION PASSED")
    print("  ❌ PRICE VERIFICATION FAILED - TRADE BLOCKED")
    print()


if __name__ == "__main__":
    print()
    print("Make sure Flask app is running: python app.py")
    print()
    input("Press Enter to start test...")
    print()
    
    test_webhook_with_price_verification()
