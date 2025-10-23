#!/usr/bin/env python3
"""
Test script for Enhanced Signal Handling
Demonstrates the new logic: ignore same direction, act on opposite
"""
import requests
import time
import json

# Test webhook URL
WEBHOOK_URL = "http://localhost:5000/webhook"

def send_signal(action, symbol, price, description):
    """Send a trading signal to the webhook"""
    payload = {
        "action": action,
        "symbol": symbol,
        "price": price,
        "timestamp": time.time()
    }
    
    print(f"\n🔄 {description}")
    print(f"   Sending: {action} {symbol} @ {price}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"   ✅ Response: {response.status_code}")
            result = response.json()
            if result.get('signal'):
                print(f"   📊 Signal processed: {result['signal']}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    time.sleep(2)  # Wait between signals

def main():
    print("🚀 Testing Enhanced Signal Handling")
    print("=" * 50)
    print("Logic:")
    print("  - Same direction signals → IGNORED")
    print("  - Opposite direction signals → CLOSE existing + OPEN new")
    print("  - No existing trades → OPEN new")
    print("=" * 50)
    
    # Test scenario
    symbol = "BTCUSDT"
    base_price = 65000
    
    # Test 1: First BUY signal (should open new trade)
    send_signal("BUY", symbol, base_price, "Test 1: First BUY signal - should OPEN new trade")
    
    # Test 2: Second BUY signal (should be IGNORED - same direction)
    send_signal("BUY", symbol, base_price + 100, "Test 2: Second BUY signal - should be IGNORED (same direction)")
    
    # Test 3: Third BUY signal (should be IGNORED - same direction)
    send_signal("BUY", symbol, base_price + 200, "Test 3: Third BUY signal - should be IGNORED (same direction)")
    
    # Test 4: SELL signal (should CLOSE BUY and OPEN SELL - opposite direction)
    send_signal("SELL", symbol, base_price + 300, "Test 4: SELL signal - should CLOSE BUY and OPEN SELL (opposite direction)")
    
    # Test 5: Another SELL signal (should be IGNORED - same direction)
    send_signal("SELL", symbol, base_price + 250, "Test 5: Second SELL signal - should be IGNORED (same direction)")
    
    # Test 6: BUY signal again (should CLOSE SELL and OPEN BUY - opposite direction)
    send_signal("BUY", symbol, base_price + 400, "Test 6: BUY signal - should CLOSE SELL and OPEN BUY (opposite direction)")
    
    print("\n" + "=" * 50)
    print("✅ Test sequence completed!")
    print("Check the Flask logs to see the enhanced signal processing")
    print("Check Telegram for notifications with action statuses")
    print("=" * 50)

if __name__ == "__main__":
    main()