"""
Real-world webhook test: Demonstrate opposite trade closing via webhook
"""
import requests
import json
from time import sleep

WEBHOOK_URL = "http://127.0.0.1:5000/webhook"

print("=" * 80)
print("🚀 Real-World Webhook Test: Opposite Trade Closing")
print("=" * 80)

# Test sequence
test_sequence = [
    {
        "step": "1",
        "description": "Open BUY position on BTCUSDT at $50,000",
        "payload": {
            "action": "Long",
            "symbol": "BTCUSDT",
            "price": 50000
        },
        "expected": "Opens new BUY trade"
    },
    {
        "step": "2",
        "description": "SELL signal comes at $52,000 (opposite)",
        "payload": {
            "action": "Short",
            "symbol": "BTCUSDT",
            "price": 52000
        },
        "expected": "Closes BUY (profit $200k), Opens SELL"
    },
    {
        "step": "3",
        "description": "BUY signal comes at $51,000 (opposite)",
        "payload": {
            "action": "Long",
            "symbol": "BTCUSDT",
            "price": 51000
        },
        "expected": "Closes SELL (profit $100k), Opens BUY"
    },
    {
        "step": "4",
        "description": "Another BUY at $51,500 (same direction)",
        "payload": {
            "action": "Long",
            "symbol": "BTCUSDT",
            "price": 51500
        },
        "expected": "Closes previous BUY (profit $50k), Opens new BUY"
    }
]

print("\nSending webhook sequence...\n")

for test in test_sequence:
    print(f"Step {test['step']}: {test['description']}")
    print(f"Expected: {test['expected']}")
    print(f"Payload: {json.dumps(test['payload'], indent=2)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=test['payload'],
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"   Summary: {data.get('summary', 'N/A')}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("-" * 80)
    sleep(1)  # Small delay between requests

print("\n✅ Webhook sequence completed!")
print("\n📊 To view the results:")
print("   1. Check signals: python check_signals.py")
print("   2. Check trades: SELECT * FROM trades WHERE symbol='BTCUSDT' ORDER BY id DESC;")
print("   3. View dashboard: http://localhost:5173")
print("\n" + "=" * 80)
