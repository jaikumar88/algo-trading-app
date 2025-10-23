"""
Test webhook action mapping: Long → Buy, Short → Sell
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Test data
test_cases = [
    {
        "name": "Test Long → Buy (JSON field)",
        "payload": {
            "action": "Long",
            "symbol": "BTCUSDT",
            "price": 50000
        }
    },
    {
        "name": "Test Short → Sell (JSON field)",
        "payload": {
            "action": "Short",
            "symbol": "ETHUSDT",
            "price": 3000
        }
    },
    {
        "name": "Test long in text",
        "payload": {
            "text": "Going long on BTCUSDT at price 50000"
        }
    },
    {
        "name": "Test short in text",
        "payload": {
            "text": "Going short on ETHUSDT at price 3000"
        }
    }
]

WEBHOOK_URL = "http://127.0.0.1:5000/webhook"
SECRET = os.getenv("WEBHOOK_SECRET")

print("Testing webhook action mapping...")
print("=" * 60)

for test in test_cases:
    print(f"\n{test['name']}")
    print(f"Payload: {json.dumps(test['payload'], indent=2)}")
    
    headers = {}
    if SECRET:
        headers["X-WEBHOOK-SECRET"] = SECRET
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=test['payload'],
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ Success")
        else:
            print("✗ Failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Testing complete!")
print("\nTo verify the results, run:")
print("  python check_signals.py")
