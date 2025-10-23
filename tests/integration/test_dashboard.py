import requests
import json

print("🔍 Testing Dashboard API Endpoints...\n")

endpoints = [
    ('GET', '/api/trading/trades?limit=10', 'Trades'),
    ('GET', '/api/trading/positions', 'Positions'),
    ('GET', '/api/trading/instruments', 'Instruments'),
    ('GET', '/api/trading/settings', 'Settings')
]

for method, endpoint, name in endpoints:
    try:
        url = f'http://localhost:5000{endpoint}'
        r = requests.get(url)
        print(f"{'✅' if r.ok else '❌'} {name}")
        print(f"   Status: {r.status_code}")
        if r.ok:
            data = r.json()
            print(f"   Keys: {list(data.keys())}")
            # Show data summary
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"   {key}: dict with {len(value)} keys")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"   Error: {r.text[:200]}")
        print()
    except Exception as e:
        print(f"❌ {name}: {e}\n")

print("="*60)
print("Summary:")
print("If all endpoints show ✅, the backend is working.")
print("If Dashboard shows nothing, check browser console (F12).")
