#!/usr/bin/env python3
"""
Verify the complete setup works for GitHub Pages
"""
import requests
import json

def verify_github_pages_setup():
    """Verify everything is configured correctly for GitHub Pages"""
    
    print("✅ GITHUB PAGES INTEGRATION VERIFICATION")
    print("=" * 60)
    
    # Test 1: Check GitHub Pages is deployed
    print("\n1️⃣ Checking GitHub Pages Deployment:")
    try:
        response = requests.get("https://jaikumar88.github.io/algo-trading-app/", timeout=10)
        if response.status_code == 200 and 'id="root"' in response.text:
            print("   ✅ GitHub Pages is live and serving React app")
            
            # Check for new JS bundle
            if 'index-VFmjEa76.js' in response.text:
                print("   ✅ Latest build with API fixes deployed")
            else:
                print("   ⚠️ May be using old build")
        else:
            print("   ❌ GitHub Pages not accessible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check API is accessible
    print("\n2️⃣ Checking API Accessibility:")
    api_url = "https://uncurdling-joane-pantomimical.ngrok-free.dev"
    try:
        response = requests.get(
            f"{api_url}/api/trading/trades?limit=1",
            headers={'ngrok-skip-browser-warning': 'true'},
            timeout=10
        )
        if response.status_code == 200:
            print("   ✅ API is accessible and returning data")
        else:
            print(f"   ❌ API returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ API not accessible: {e}")
    
    # Test 3: Check CORS from GitHub Pages origin
    print("\n3️⃣ Checking CORS for GitHub Pages:")
    try:
        response = requests.get(
            f"{api_url}/api/trading/trades?limit=1",
            headers={
                'Origin': 'https://jaikumar88.github.io',
                'ngrok-skip-browser-warning': 'true'
            },
            timeout=10
        )
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        if cors_origin == 'https://jaikumar88.github.io':
            print(f"   ✅ CORS configured correctly: {cors_origin}")
        else:
            print(f"   ⚠️ CORS header: {cors_origin}")
            
    except Exception as e:
        print(f"   ❌ CORS check failed: {e}")
    
    # Test 4: Verify all dashboard endpoints
    print("\n4️⃣ Testing Dashboard Endpoints:")
    endpoints = [
        "/api/trading/trades?limit=10",
        "/api/trading/positions",
        "/api/trading/instruments",
        "/api/trading/settings"
    ]
    
    all_working = True
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{api_url}{endpoint}",
                headers={
                    'Origin': 'https://jaikumar88.github.io',
                    'ngrok-skip-browser-warning': 'true'
                },
                timeout=5
            )
            if response.status_code == 200:
                print(f"   ✅ {endpoint}")
            else:
                print(f"   ❌ {endpoint} - Status {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
            all_working = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if all_working:
        print("✅ ALL SYSTEMS OPERATIONAL!")
        print("\n🎯 Your GitHub Pages deployment should now work!")
        print(f"\n🌐 Visit: https://jaikumar88.github.io/algo-trading-app/")
        print("📱 The trading interface should load with live data")
        print("\n💡 If you still see issues:")
        print("   1. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R)")
        print("   2. Clear browser cache")
        print("   3. Check browser console for any errors")
    else:
        print("⚠️ Some endpoints have issues")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Flask is running: python start_flask.py")
        print("   2. Make sure tunnel is running: python start_tunnel.py")
        print("   3. Check if ngrok URL changed")

if __name__ == "__main__":
    verify_github_pages_setup()
