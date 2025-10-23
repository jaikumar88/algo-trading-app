# RAG Trading Assistant - React Client

A modern React + Vite client for the RAG Trading Assistant backend.

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 8+ (or pnpm/yarn)
- Backend Flask server running on http://localhost:5000

## Quick Start

### 1. Install Dependencies

```powershell
cd client
npm install
```

**If you encounter the "Missing script: devnpm" error:**
```powershell
npm cache clean --force
# Remove node_modules and package-lock.json if present
npm install --legacy-peer-deps
```

### 2. Start Development Server

```powershell
npm run dev
```

The Vite dev server runs on **http://localhost:5173** by default. It automatically proxies `/api` and `/webhook` requests to http://localhost:5000 (see `vite.config.js`).

### 3. Using the Helper Script

From the project root:

```powershell
.\start_client.ps1
```

This script:
- Changes to the client directory
- Runs npm install (if needed)
- Starts the dev server

## Production Build

### Build the Client

```powershell
npm run build
```

This creates an optimized production build in the `dist/` folder.

### Preview the Build Locally

```powershell
npm run preview
```

Runs a local static server on http://localhost:4173 to preview the production build.

## Deployment Options

### Option 1: Serve from Flask (Recommended)

Serve the built React client directly from your Flask backend:

1. **Build the client:**
   ```powershell
   cd client
   npm run build
   ```

2. **Copy dist to Flask static:**
   ```powershell
   # From project root
   Remove-Item -Recurse -Force .\static\client -ErrorAction SilentlyContinue
   Copy-Item -Recurse .\client\dist .\static\client
   ```

3. **Add a Flask route to serve the client** (in `app.py`):
   ```python
   @app.route('/')
   @app.route('/client')
   @app.route('/client/<path:path>')
   def serve_client(path='index.html'):
       return send_from_directory('static/client', path)
   ```

4. **Access the client at:** http://localhost:5000/client

### Option 2: Deploy Separately

Deploy the client to a static hosting service (Vercel, Netlify, GitHub Pages, etc.):

1. **Build the client:**
   ```powershell
   npm run build
   ```

2. **Update API Base URL:**
   - In production, users can configure the backend URL via the Settings page in the client UI
   - Or set `apiBaseUrl` in localStorage before the app loads
   - Or modify `src/api.js` to use an environment variable:
     ```javascript
     export function getApiBaseUrl() {
       return import.meta.env.VITE_API_BASE_URL || 
              localStorage.getItem('apiBaseUrl') || 
              'http://localhost:5000'
     }
     ```

3. **Deploy the `dist/` folder** to your hosting service

4. **Enable CORS on Flask backend** (already configured in `app.py` for development)

## Configuration

### Backend API URL

The client uses the backend URL from:
1. User Settings page (stored in `localStorage.apiBaseUrl`)
2. Default: `http://localhost:5000`

To change the backend URL:
- Navigate to **Settings** in the client UI
- Update the "Backend URL" field
- Click "Save Configuration"

### Theme

The client supports Light and Dark themes:
- Toggle via the theme button in the header
- Or set in Settings page
- Preference is saved to localStorage

## Project Structure

```
client/
├── index.html          # HTML entry point
├── package.json        # Dependencies and scripts
├── vite.config.js      # Vite config with dev proxy
├── src/
│   ├── main.jsx        # React entry point
│   ├── App.jsx         # Main app with routing
│   ├── Layout.jsx      # Header, nav, theme toggle
│   ├── api.js          # API base URL helper
│   ├── styles.css      # Global styles and theme
│   └── components/
│       ├── Dashboard.jsx      # Metrics and charts
│       ├── Signals.jsx        # Signals table
│       ├── SignalDetails.jsx  # Signal detail modal
│       └── Settings.jsx       # Settings page
└── dist/               # Production build output (created by npm run build)
```

## Available Scripts

- **`npm run dev`** - Start development server with hot reload
- **`npm run build`** - Build optimized production bundle
- **`npm run preview`** - Preview production build locally

## Troubleshooting

### npm install fails

Try:
```powershell
npm cache clean --force
Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install --legacy-peer-deps
```

### API calls fail

- Ensure Flask backend is running on http://localhost:5000
- Check the backend URL in Settings
- Check browser console for CORS errors (CORS is enabled in dev mode)

### Theme not persisting

- Check browser localStorage is enabled
- Clear localStorage and refresh: `localStorage.clear()`

## Development Notes

- The dev server uses Vite's proxy feature to avoid CORS issues during development
- In production, either serve from Flask or enable CORS on the backend
- The client is a single-page app (SPA) with client-side routing
- All state is managed with React hooks (no Redux/etc needed for this demo)

## License

Same as parent project.
