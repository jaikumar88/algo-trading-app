#!/usr/bin/env python3
"""
Check if GitHub Pages is now serving React client instead of README
"""
import requests
import time

def check_page_content():
    """Check what type of content is being served"""
    url = "https://jaikumar88.github.io/algo-trading-app/"
    
    try:
        response = requests.get(url, timeout=10)
        content = response.text.lower()
        
        # Check for React app indicators
        react_indicators = [
            'id="root"',
            'vite',
            'react',
            '/algo-trading-app/assets/',
            'trading',
            'dashboard'
        ]
        
        # Check for Jekyll/README indicators  
        jekyll_indicators = [
            'jekyll',
            'github.io/algo-trading-app/</title>',
            'begin jekyll seo tag',
            'advanced algorithmic trading system</title>'
        ]
        
        react_score = sum(1 for indicator in react_indicators if indicator in content)
        jekyll_score = sum(1 for indicator in jekyll_indicators if indicator in content)
        
        print("🔍 GITHUB PAGES CONTENT ANALYSIS")
        print("=" * 50)
        print(f"🌐 URL: {url}")
        print(f"📊 Status: {response.status_code}")
        
        if react_score > jekyll_score:
            print("✅ SUCCESS: React client is being served!")
            print("🎯 Features detected:")
            if 'id="root"' in content:
                print("   ✅ React root element")
            if '/algo-trading-app/assets/' in content:
                print("   ✅ Vite build assets")
            if 'trading' in content:
                print("   ✅ Trading functionality")
                
            print("\n🚀 Your trading client is now live!")
            print("📱 Test these features:")
            print("   - Multi-symbol charts")
            print("   - Trading dashboard")  
            print("   - Position monitoring")
            print("   - Signal management")
            return True
            
        elif jekyll_score > 0:
            print("❌ ISSUE: Still serving Jekyll/README content")
            print("🔧 Required fixes:")
            print("   1. Go to repository Settings → Pages")
            print("   2. Change source to 'GitHub Actions'")
            print("   3. Wait 5-10 minutes for redeployment")
            print("\n💡 Current content type: Jekyll-rendered README")
            return False
            
        else:
            print("⚠️ UNKNOWN: Unable to determine content type")
            print("🔍 Manual check needed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Cannot access site - {e}")
        print("💡 This might be normal if deployment is still in progress")
        return False

def main():
    print("🌐 GITHUB PAGES CONTENT CHECK")
    print("=" * 50)
    
    if check_page_content():
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("\n📋 NEXT STEPS:")
        print("1. 🔗 Update TradingView webhook:")
        print("   https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook")
        print("2. 🚀 Start backend services:")
        print("   python start_flask.py")
        print("   python start_tunnel.py")
        print("3. 📊 Start trading!")
    else:
        print("\n🔧 CONFIGURATION NEEDED:")
        print("📖 See GITHUB_PAGES_FIX.md for detailed instructions")
        print("⏱️ Run this script again after making changes")

if __name__ == "__main__":
    main()