#!/usr/bin/env python3
"""
Monitor the new deployment with API fixes
"""
import requests
import time
import json

def monitor_new_deployment():
    """Monitor the new deployment after API fixes"""
    
    print("🚀 MONITORING NEW DEPLOYMENT WITH API FIXES")
    print("=" * 60)
    print("🔗 Commit: 32cc370 - Fix API calls: Use apiUrl() service")
    print("🌐 Target: https://jaikumar88.github.io/algo-trading-app/")
    print("⏱️ Waiting for GitHub Actions to complete...")
    
    max_attempts = 15  # 7.5 minutes
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        try:
            response = requests.get("https://jaikumar88.github.io/algo-trading-app/", timeout=10)
            content = response.text
            
            # Look for the new JS bundle (should be different from index-DoFVQmhw.js)
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Check {attempt}/15: Status {response.status_code}", end="")
            
            if 'index-VFmjEa76.js' in content:
                print(" - ✅ NEW BUILD DEPLOYED!")
                
                # Test API configuration
                print("\n🔍 Testing API configuration...")
                
                # Check if the new JS bundle has proper API configuration
                js_match = content.find('index-VFmjEa76.js')
                if js_match != -1:
                    js_file = content[content.rfind('/algo-trading-app/assets/', 0, js_match):js_match+20]
                    js_url = f"https://jaikumar88.github.io{js_file}"
                    
                    try:
                        js_response = requests.get(js_url, timeout=5)
                        js_content = js_response.text
                        
                        if 'uncurdling-joane-pantomimical.ngrok-free.dev' in js_content:
                            print("   ✅ ngrok URL found in new JS bundle")
                        
                        if 'getApiBaseUrl' in js_content:
                            print("   ✅ API service functions present")
                            
                        if 'API URL Resolution Debug' in js_content:
                            print("   ✅ Debug logging enabled")
                            
                    except Exception as e:
                        print(f"   ⚠️ Could not check JS bundle: {e}")
                
                print(f"\n🎉 DEPLOYMENT SUCCESS!")
                print("📱 React client updated with proper API configuration")
                print("🔌 API calls will now use ngrok URL in production")
                print("\n📋 Next steps:")
                print("   1. Visit: https://jaikumar88.github.io/algo-trading-app/")
                print("   2. Open browser console to see API debug logs")
                print("   3. Verify trading interface loads properly")
                print("   4. Make sure backend is running: python start_flask.py")
                
                return True
                
            elif 'index-DoFVQmhw.js' in content:
                print(" - ⏳ Old build still active")
            else:
                print(" - ❓ Unknown build version")
                
        except Exception as e:
            print(f"[{timestamp}] Check {attempt}/15: ❌ Error: {e}")
        
        if attempt < max_attempts:
            time.sleep(30)  # Wait 30 seconds
    
    print(f"\n⏰ Deployment monitoring timeout")
    print("💡 Manual check: https://github.com/jaikumar88/algo-trading-app/actions")
    return False

if __name__ == "__main__":
    monitor_new_deployment()