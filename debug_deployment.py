#!/usr/bin/env python3
"""
Debug the GitHub Pages deployment API configuration
"""
import requests
import json

def debug_deployed_app():
    """Check the deployed app and its API configuration"""
    url = "https://jaikumar88.github.io/algo-trading-app/"
    
    print("🔍 DEBUGGING GITHUB PAGES DEPLOYMENT")
    print("=" * 60)
    
    try:
        # Get the main HTML
        response = requests.get(url, timeout=10)
        content = response.text
        
        print(f"📄 Main page status: {response.status_code}")
        print(f"📏 Content length: {len(content)} characters")
        
        # Check for key indicators
        if 'id="root"' in content:
            print("✅ React root element found")
        else:
            print("❌ React root element missing")
            
        if '/algo-trading-app/assets/' in content:
            print("✅ Vite assets path found")
        else:
            print("❌ Vite assets path missing")
        
        # Try to find any JavaScript files to inspect
        import re
        js_files = re.findall(r'/algo-trading-app/assets/[^"\']+\.js', content)
        
        if js_files:
            print(f"\n📂 Found {len(js_files)} JS files:")
            for js_file in js_files[:3]:  # Check first 3 files
                js_url = f"https://jaikumar88.github.io{js_file}"
                print(f"   📄 Checking: {js_file}")
                
                try:
                    js_response = requests.get(js_url, timeout=5)
                    js_content = js_response.text
                    
                    # Check for API URL configuration
                    if 'uncurdling-joane-pantomimical.ngrok-free.dev' in js_content:
                        print("     ✅ ngrok URL found in JS")
                    else:
                        print("     ❌ ngrok URL NOT found in JS")
                        
                    if 'getApiBaseUrl' in js_content:
                        print("     ✅ API base URL function found")
                    else:
                        print("     ❌ API base URL function missing")
                        
                except Exception as e:
                    print(f"     ❌ Error loading JS: {e}")
        else:
            print("❌ No JavaScript files found!")
            
        # Show a snippet of the content for debugging
        print(f"\n📋 Content preview (first 500 chars):")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Check if backend is running
    print(f"\n🔌 Checking backend availability:")
    backend_url = "https://uncurdling-joane-pantomimical.ngrok-free.dev"
    
    try:
        backend_response = requests.get(backend_url, timeout=5, headers={
            'ngrok-skip-browser-warning': 'true'
        })
        print(f"   Status: {backend_response.status_code}")
        if backend_response.status_code == 200:
            print("   ✅ Backend is accessible")
        else:
            print("   ⚠️ Backend returned non-200 status")
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        print(f"   💡 Make sure to run: python start_flask.py")

if __name__ == "__main__":
    debug_deployed_app()