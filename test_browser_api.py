#!/usr/bin/env python3
"""
Test API calls exactly as they would be made from the browser
"""
import requests
import json

def test_browser_api_calls():
    """Simulate browser API calls with proper headers"""
    
    print("🌐 SIMULATING BROWSER API CALLS FROM GITHUB PAGES")
    print("=" * 60)
    
    api_base = "https://uncurdling-joane-pantomimical.ngrok-free.dev"
    origin = "https://jaikumar88.github.io"
    
    # Dashboard endpoints
    endpoints = [
        "/api/trading/trades?limit=10",
        "/api/trading/positions",
        "/api/trading/instruments",
        "/api/trading/settings"
    ]
    
    print(f"Origin: {origin}")
    print(f"API Base: {api_base}\n")
    
    for endpoint in endpoints:
        url = f"{api_base}{endpoint}"
        print(f"📡 Testing: {endpoint}")
        
        try:
            # Simulate browser request with CORS headers
            response = requests.get(url, headers={
                'Origin': origin,
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
                # Note: Don't send ngrok-skip-browser-warning from browser
            }, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   CORS Header: {response.headers.get('Access-Control-Allow-Origin')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   ❌ Not valid JSON: {response.text[:200]}")
            else:
                print(f"   ❌ Response: {response.text[:500]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_browser_api_calls()
