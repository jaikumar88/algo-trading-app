#!/usr/bin/env python3
"""
Monitor GitHub Pages deployment progress
"""
import requests
import time
import sys

def check_deployment_status():
    """Check current deployment status"""
    url = "https://jaikumar88.github.io/algo-trading-app/"
    
    try:
        response = requests.get(url, timeout=10)
        content = response.text.lower()
        
        print(f"⏱️ Status: {response.status_code} | Size: {len(content)} chars")
        
        if response.status_code == 404:
            return "not_ready"
        elif 'id="root"' in content and '/algo-trading-app/assets/' in content:
            return "react_deployed"
        elif 'jekyll' in content or 'github.io' in content:
            return "jekyll_still_active"
        else:
            return "unknown"
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return "error"

def monitor_deployment():
    """Monitor deployment with real-time updates"""
    print("🚀 MONITORING GITHUB ACTIONS DEPLOYMENT")
    print("=" * 60)
    print("🔗 Repository: https://github.com/jaikumar88/algo-trading-app")
    print("🌐 Target URL: https://jaikumar88.github.io/algo-trading-app/")
    print("⏱️ Started monitoring...")
    print("\n📊 Status Updates:")
    
    max_attempts = 20  # 10 minutes maximum
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        status = check_deployment_status()
        
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Attempt {attempt}/20: ", end="")
        
        if status == "react_deployed":
            print("✅ SUCCESS! React client is deployed!")
            print("\n🎉 DEPLOYMENT COMPLETE!")
            print("📱 Your trading client is now live!")
            print("\n🎯 Available features:")
            print("   - Multi-symbol TradingView charts")
            print("   - Real-time position monitoring") 
            print("   - Trade history and analytics")
            print("   - Signal management dashboard")
            print("\n🔗 URLs:")
            print("   Client: https://jaikumar88.github.io/algo-trading-app/")
            print("   API: https://uncurdling-joane-pantomimical.ngrok-free.dev")
            return True
            
        elif status == "not_ready":
            print("⏳ Deploying...")
        elif status == "jekyll_still_active": 
            print("⚠️ Jekyll still active (config may need time)")
        elif status == "unknown":
            print("❓ Unknown status")
        else:
            print("❌ Connection issue")
        
        if attempt < max_attempts:
            time.sleep(30)  # Wait 30 seconds between checks
        
    print(f"\n⏰ Timeout after {max_attempts} attempts")
    print("💡 Manual checks:")
    print("   1. Go to https://github.com/jaikumar88/algo-trading-app/actions")
    print("   2. Check if 'Deploy React App to GitHub Pages' is running")
    print("   3. If failed, check the error logs")
    return False

if __name__ == "__main__":
    print("🔍 GITHUB PAGES DEPLOYMENT MONITOR")
    print("=" * 50)
    
    # Quick status check first
    initial_status = check_deployment_status()
    if initial_status == "react_deployed":
        print("✅ React client already deployed!")
        sys.exit(0)
    
    # Start monitoring
    monitor_deployment()