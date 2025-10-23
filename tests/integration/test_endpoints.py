import requests
import json

print('🔍 Testing API Endpoints...\n')

endpoints = [
    ('GET', '/api/trading/instruments'),
    ('GET', '/api/trading/trades'),
    ('GET', '/api/trading/positions'),
    ('GET', '/api/trading/settings')
]

all_passed = True

for method, endpoint in endpoints:
    try:
        r = requests.request(method, f'http://localhost:5000{endpoint}')
        if r.status_code in [200, 201]:
            data = r.json()
            keys = list(data.keys())
            count = len(data[keys[0]]) if isinstance(data[keys[0]], list) else 'N/A'
            print(f'✅ {method} {endpoint}')
            print(f'   Status: {r.status_code}')
            print(f'   Keys: {keys}')
            if isinstance(count, int):
                print(f'   Items: {count}')
            print()
        else:
            print(f'❌ {method} {endpoint}')
            print(f'   Status: {r.status_code}')
            print(f'   Error: {r.text}\n')
            all_passed = False
    except Exception as e:
        print(f'❌ {method} {endpoint}')
        print(f'   Failed: {e}\n')
        all_passed = False

if all_passed:
    print('✨ All endpoints are working correctly!')
    print('\n📊 Backend Status: HEALTHY')
else:
    print('⚠️ Some endpoints failed!')
    print('\n📊 Backend Status: ISSUES DETECTED')
