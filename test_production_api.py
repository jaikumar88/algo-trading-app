#!/usr/bin/env python3
"""
Test production API calls to diagnose the GitHub Pages issue
"""
import requests
import json

def test_production_api():
    """Test API calls as they would be made from GitHub Pages"""
    
    print("🔍 TESTING PRODUCTION API CONFIGURATION")
    print("=" * 60)
    
    # The ngrok URL that should be used in production
    api_base = "https://uncurdling-joane-pantomimical.ngrok-free.dev"
    
    print(f"🌐 Testing API: {api_base}")
    print()
    
    # Test endpoints that the dashboard uses
    endpoints = [
        "/api/trading/trades?limit=10",
        "/api/trading/positions",
        "/api/trading/instruments",
        "/api/trading/settings"
    ]
    
    for endpoint in endpoints:
        url = f"{api_base}{endpoint}"
        print(f"📡 Testing: {endpoint}")
        
        try:
            # Make request with ngrok headers to avoid browser warning
            response = requests.get(url, timeout=10, headers={
                'ngrok-skip-browser-warning': 'true',
                'User-Agent': 'Mozilla/5.0 (Trading Client Test)'
            })
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success - Response size: {len(json.dumps(data))} chars")
                
                # Show sample data
                if 'trades' in data:
                    print(f"   📊 Trades count: {len(data.get('trades', []))}")
                elif 'positions' in data:
                    print(f"   📊 Positions count: {len(data.get('positions', []))}")
                elif 'instruments' in data:
                    print(f"   📊 Instruments count: {len(data.get('instruments', []))}")
                elif 'settings' in data:
                    print(f"   📊 Settings count: {len(data.get('settings', {}))}")
                    
            else:
                print(f"   ❌ Failed - Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout - Backend may not be running")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - Check if ngrok tunnel is active")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Check CORS headers
    print("🔒 Checking CORS Configuration:")
    try:
        response = requests.options(f"{api_base}/api/trading/trades", headers={
            'Origin': 'https://jaikumar88.github.io',
            'Access-Control-Request-Method': 'GET',
            'ngrok-skip-browser-warning': 'true'
        })
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
        
        if cors_headers.get('Access-Control-Allow-Origin'):
            print("   ✅ CORS appears to be configured")
        else:
            print("   ⚠️ CORS headers may be missing - this could block GitHub Pages")
            
    except Exception as e:
        print(f"   ⚠️ Could not check CORS: {e}")
    
    print()
    print("💡 Common Issues:")
    print("   1. Backend not running: python start_flask.py")
    print("   2. Tunnel not active: python start_tunnel.py")
    print("   3. CORS not configured for GitHub Pages origin")
    print("   4. ngrok URL changed (tunnel restarted)")

if __name__ == "__main__":
    test_production_api()
