#!/usr/bin/env python3
"""
Check GitHub Pages deployment status
"""
import time
import requests

def check_github_pages():
    """Check if GitHub Pages site is accessible"""
    url = "https://jaikumar88.github.io/algo-trading-app/"
    
    print("🌐 GITHUB PAGES DEPLOYMENT CHECK")
    print("=" * 50)
    print(f"🔗 Target URL: {url}")
    print("⏱️ Checking deployment status...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ SUCCESS: GitHub Pages is live!")
            print(f"📱 Your trading client: {url}")
            print("🎯 Features available:")
            print("   - Multi-symbol TradingView charts")
            print("   - Real-time trading positions")
            print("   - Trade history and analytics")
            print("   - Signal management")
            return True
        else:
            print(f"⚠️ Site responding with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Site not accessible yet: {e}")
        print("💡 This is normal for new deployments")
        return False

def check_github_actions():
    """Provide instructions to check GitHub Actions"""
    print("\n🔧 TO CHECK DEPLOYMENT PROGRESS:")
    print("1. Go to: https://github.com/jaikumar88/algo-trading-app")
    print("2. Click 'Actions' tab")
    print("3. Look for 'Deploy React App to GitHub Pages' workflow")
    print("4. Check if it's running or completed")
    
    print("\n⚠️ IF NO DEPLOYMENT STARTED:")
    print("1. Go to Settings → Pages")
    print("2. Set Source to 'GitHub Actions'")
    print("3. Save and wait for deployment")

def main():
    print("🚀 GITHUB PAGES DEPLOYMENT STATUS")
    print("=" * 50)
    
    # Check if site is already live
    if check_github_pages():
        print("\n🎉 DEPLOYMENT COMPLETE!")
        print("\n📋 NEXT STEPS:")
        print("1. 🌐 Visit your trading client")
        print("2. 🔗 Update TradingView webhook to:")
        print("   https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook")
        print("3. 🚀 Start trading with your professional platform!")
        return
    
    print("\n⏳ DEPLOYMENT IN PROGRESS...")
    check_github_actions()
    
    print("\n🕐 TYPICAL DEPLOYMENT TIME: 3-5 minutes")
    print("💡 Run this script again in a few minutes to check status")
    
    print("\n📱 YOUR URLS:")
    print("🌐 Client: https://jaikumar88.github.io/algo-trading-app/")
    print("🔗 API: https://uncurdling-joane-pantomimical.ngrok-free.dev")

if __name__ == "__main__":
    main()