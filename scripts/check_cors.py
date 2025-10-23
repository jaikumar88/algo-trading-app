#!/usr/bin/env python
"""
Quick test to verify Flask-CORS is working
"""
import sys

print("🔍 Checking Flask-CORS installation...\n")

# Test 1: Import
try:
    from flask_cors import CORS
    print("✅ flask-cors is installed and importable")
except ImportError as e:
    print(f"❌ flask-cors import failed: {e}")
    print("\nRun: pip install flask-cors")
    sys.exit(1)

# Test 2: Check app.py imports
print("✅ Checking app.py configuration...")
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'from flask_cors import CORS' in content:
            print("✅ CORS imported in app.py")
        if 'CORS(app' in content:
            print("✅ CORS initialized in app.py")
except Exception as e:
    print(f"⚠️  Could not read app.py: {e}")

# Test 3: Check if Flask is running
print("\n🔍 Testing Flask server...")
try:
    import requests
    response = requests.get('http://localhost:5000/api/trading/instruments')
    
    # Check for CORS headers
    if 'Access-Control-Allow-Origin' in response.headers:
        print(f"✅ CORS header present: {response.headers['Access-Control-Allow-Origin']}")
    else:
        print("❌ CORS header missing!")
        print("   Flask needs to be restarted to apply CORS changes")
        
    print(f"\n📊 Response Status: {response.status_code}")
    
except requests.exceptions.ConnectionError:
    print("❌ Flask is not running on port 5000")
    print("\nStart Flask with: python app.py")
except Exception as e:
    print(f"⚠️  Test failed: {e}")

print("\n" + "="*60)
print("📝 NEXT STEPS:")
print("="*60)
print("\n1. Restart Flask server:")
print("   - Press Ctrl+C in Flask terminal")
print("   - Run: python app.py")
print("\n2. Refresh browser (F5)")
print("\n3. Try adding instrument again")
print("\n✨ CORS should now work!")
