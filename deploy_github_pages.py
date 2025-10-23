#!/usr/bin/env python3
"""
GitHub Pages Deployment Manager
Handles environment configuration and deployment for the trading client
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class GitHubPagesDeployer:
    def __init__(self):
        self.client_dir = Path(__file__).parent / 'client'
        self.project_root = Path(__file__).parent
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check if in client directory
        if not self.client_dir.exists():
            print("❌ Client directory not found")
            return False
            
        # Check if package.json exists
        package_json = self.client_dir / 'package.json'
        if not package_json.exists():
            print("❌ package.json not found")
            return False
            
        # Check if node_modules exists
        node_modules = self.client_dir / 'node_modules'
        if not node_modules.exists():
            print("⚠️ node_modules not found, installing dependencies...")
            self.install_dependencies()
            
        print("✅ Prerequisites check passed")
        return True
        
    def install_dependencies(self):
        """Install npm dependencies"""
        print("📦 Installing dependencies...")
        try:
            result = subprocess.run(
                ['npm', 'install'], 
                cwd=self.client_dir,
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    def update_api_url(self, new_url):
        """Update the production API URL in configuration files"""
        print(f"🔧 Updating API URL to: {new_url}")
        
        # Update vite.config.js
        vite_config = self.client_dir / 'vite.config.js'
        if vite_config.exists():
            content = vite_config.read_text()
            # Replace the __PRODUCTION_API_URL__ value
            import re
            pattern = r'__PRODUCTION_API_URL__:\s*JSON\.stringify\([\'"][^\'"]*[\'"]'
            replacement = f'__PRODUCTION_API_URL__: JSON.stringify(\'{new_url}\')'
            content = re.sub(pattern, replacement, content)
            vite_config.write_text(content)
            print("✅ Updated vite.config.js")
        
        # Update .env.production
        env_prod = self.client_dir / '.env.production'
        lines = [
            f'# Production environment for GitHub Pages\n',
            f'VITE_API_URL={new_url}\n',
            f'VITE_NODE_ENV=production\n'
        ]
        env_prod.write_text(''.join(lines))
        print("✅ Updated .env.production")
        
        # Update package.json scripts
        package_json = self.client_dir / 'package.json'
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            # Update build:github script
            data['scripts']['build:github'] = f'cross-env VITE_API_URL={new_url} vite build'
            
            with open(package_json, 'w') as f:
                json.dump(data, f, indent=2)
            print("✅ Updated package.json")
    
    def build_for_production(self):
        """Build the client for production"""
        print("🔨 Building for production...")
        try:
            result = subprocess.run(
                ['npm', 'run', 'build:github'], 
                cwd=self.client_dir,
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Production build completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False
    
    def preview_locally(self):
        """Start local preview server"""
        print("🌐 Starting local preview...")
        print("📁 Production build will be served at:")
        print("   http://localhost:4173/rag-project/")
        print("\n🔧 API Configuration:")
        print("   Production API: Uses ngrok tunnel URL")
        print("   Test the app and verify API calls work")
        print("\n⏹️ Press Ctrl+C to stop preview")
        
        try:
            subprocess.run(['npm', 'run', 'preview'], cwd=self.client_dir)
        except KeyboardInterrupt:
            print("\n✅ Preview stopped")
    
    def deploy_to_github_pages(self):
        """Deploy to GitHub Pages using gh-pages"""
        print("🚀 Deploying to GitHub Pages...")
        try:
            result = subprocess.run(
                ['npm', 'run', 'deploy'], 
                cwd=self.client_dir,
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Deployed to GitHub Pages successfully!")
            print("🌐 Your site will be available at:")
            print("   https://YOUR_USERNAME.github.io/rag-project/")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False
    
    def setup_github_actions(self):
        """Provide instructions for GitHub Actions setup"""
        print("\n🔧 GitHub Actions Setup:")
        print("1. Push your code to GitHub:")
        print("   git add .")
        print("   git commit -m 'Add GitHub Pages deployment'")
        print("   git push origin main")
        print("\n2. Enable GitHub Pages:")
        print("   - Go to repository Settings → Pages")
        print("   - Set Source to 'GitHub Actions'")
        print("   - The workflow will auto-deploy on push to main")
        print("\n3. Your deployed site will be at:")
        print("   https://YOUR_USERNAME.github.io/rag-project/")
    
    def interactive_setup(self):
        """Interactive setup process"""
        print("🚀 GITHUB PAGES DEPLOYMENT SETUP")
        print("=" * 50)
        
        if not self.check_prerequisites():
            return
        
        # Get current tunnel URL
        print("\n🔗 Current ngrok tunnel URL:")
        print("   https://uncurdling-joane-pantomimical.ngrok-free.dev")
        
        choice = input("\n📝 Do you want to update the API URL? (y/N): ").lower()
        if choice == 'y':
            new_url = input("🌐 Enter new API URL (or press Enter to keep current): ").strip()
            if new_url:
                self.update_api_url(new_url)
        
        # Build
        print("\n🔨 Building for production...")
        if not self.build_for_production():
            return
        
        # Choose deployment method
        print("\n🚀 Choose deployment method:")
        print("1. Preview locally first (recommended)")
        print("2. Deploy directly to GitHub Pages")
        print("3. Set up GitHub Actions (automatic)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            self.preview_locally()
        elif choice == '2':
            self.deploy_to_github_pages()
        elif choice == '3':
            self.setup_github_actions()
        else:
            print("Invalid choice")
            return
        
        print("\n✅ Setup completed!")

if __name__ == "__main__":
    deployer = GitHubPagesDeployer()
    deployer.interactive_setup()