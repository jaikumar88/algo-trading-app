# GitHub Pages Deployment Guide

This guide explains how to deploy your React trading client to GitHub Pages with automatic environment switching.

## 🚀 Quick Setup

### 1. Repository Setup
```bash
# Make sure you're in the project root
cd e:\workspace\python\rag-project

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/rag-project.git
git push -u origin main
```

### 2. Enable GitHub Pages
1. Go to your GitHub repository
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. The workflow will automatically deploy when you push to main

## 🔧 Environment Configuration

### Development (Local)
- **API Endpoint**: `http://localhost:5000` (via Vite proxy)
- **Usage**: `npm run dev` in client directory
- **Flask**: Run `python start_flask.py` first
- **Tunnel**: Run `python start_tunnel.py` for webhook access

### Production (GitHub Pages)
- **API Endpoint**: `https://uncurdling-joane-pantomimical.ngrok-free.dev`
- **Auto-deployment**: Triggered on push to main branch
- **Public URL**: `https://YOUR_USERNAME.github.io/rag-project/`

## 📝 Deployment Commands

### Automatic Deployment (Recommended)
```bash
# Just push to main branch
git add .
git commit -m "Update client"
git push origin main
# GitHub Actions will build and deploy automatically
```

### Manual Deployment
```bash
cd client

# Install dependencies
npm install

# Build for production
npm run build:github

# Deploy to GitHub Pages (if gh-pages is set up)
npm run deploy
```

## 🔄 API Endpoint Management

### Current Configuration
- **Local Development**: `http://localhost:5000`
- **Production**: `https://uncurdling-joane-pantomimical.ngrok-free.dev`

### Updating Production API URL
If your ngrok URL changes, update these files:

1. **Vite Config**: `client/vite.config.js`
```javascript
__PRODUCTION_API_URL__: JSON.stringify('YOUR_NEW_NGROK_URL')
```

2. **Environment File**: `client/.env.production`
```
VITE_API_URL=YOUR_NEW_NGROK_URL
```

3. **GitHub Actions**: `.github/workflows/deploy.yml`
```yaml
VITE_API_URL: YOUR_NEW_NGROK_URL
```

### Dynamic URL Update (Advanced)
You can also update the API URL at runtime by setting it in localStorage:
```javascript
localStorage.setItem('apiBaseUrl', 'https://your-new-url.ngrok-free.dev');
```

## 📊 Workflow Process

```
[Local Development] → [Git Push] → [GitHub Actions] → [GitHub Pages]
      ↓                    ↓              ↓              ↓
  localhost:5000     Auto-trigger    Build & Test    Deploy Site
```

### GitHub Actions Workflow
1. **Triggers**: Push to main, changes in `client/` directory
2. **Build**: Installs dependencies, runs `npm run build`
3. **Deploy**: Uploads to GitHub Pages
4. **Environment**: Uses production API URL automatically

## 🛠️ Troubleshooting

### Common Issues

#### Build Fails
```bash
# Check dependencies
cd client
npm install

# Test local build
npm run build
```

#### API Calls Fail on GitHub Pages
- ✅ Check CORS settings in Flask backend
- ✅ Verify ngrok tunnel is running: `python start_tunnel.py`
- ✅ Test API URL directly: `https://your-ngrok-url.ngrok-free.dev/api/health`

#### 404 on GitHub Pages
- ✅ Check repository name matches base path in `vite.config.js`
- ✅ Ensure GitHub Pages is enabled in repository settings
- ✅ Wait 5-10 minutes for deployment to complete

### CORS Configuration
Make sure your Flask backend allows GitHub Pages domain:

```python
# In your Flask app
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:5173",
    "https://YOUR_USERNAME.github.io"
])
```

## 🔐 Security Considerations

### Environment Variables
- ✅ **Public**: All `VITE_*` variables are exposed in the client bundle
- ✅ **Safe**: API URLs are public anyway (needed for browser requests)
- ❌ **Never**: Put secrets in `VITE_*` variables

### API Security
- Use HTTPS for production API (ngrok provides this)
- Implement proper authentication in your Flask backend
- Consider rate limiting for webhook endpoints

## 📱 Testing Deployment

### 1. Local Test
```bash
cd client
npm run build:github
npm run preview
# Test at http://localhost:4173
```

### 2. Production Test
1. Deploy to GitHub Pages
2. Visit: `https://YOUR_USERNAME.github.io/rag-project/`
3. Check browser console for API calls
4. Verify trading features work with production API

## 🎯 Benefits

### ✅ Automatic Deployment
- Push to main = automatic deployment
- No manual build/upload steps
- Consistent build environment

### ✅ Environment Separation
- Development uses localhost (fast, private)
- Production uses ngrok tunnel (public, webhook-ready)
- Easy switching between environments

### ✅ Professional URLs
- Clean GitHub Pages URL
- Custom domain possible (add CNAME file)
- SSL/HTTPS automatically provided

## 🚀 Next Steps

1. **Push to GitHub**: Deploy your first version
2. **Test Webhooks**: Verify TradingView webhooks work with GitHub Pages
3. **Custom Domain**: Optionally set up custom domain
4. **Monitoring**: Add error tracking and analytics

Your trading client is now ready for professional deployment! 🎉