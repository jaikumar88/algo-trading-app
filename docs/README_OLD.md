# RAG Trading Assistant

A comprehensive trading assistant that integrates:
- **TradingView webhooks** for receiving trade signals
- **OCR** (Tesseract/EasyOCR) for extracting trade data from images
- **Gemini AI** (optional) for structured trade parsing
- **Telegram** forwarding for real-time notifications
- **Flask backend** with REST API
- **React frontend** (Vite) with dashboard, signals table, and settings
- **RAG pipeline** with in-memory vector store
- **SQLAlchemy ORM** with SQLite/PostgreSQL support
- **Background jobs** via Redis + RQ (optional)

---

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Client (React) Setup](#client-react-setup)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Backend
- **Webhook ingestion** with idempotency protection
- **Image OCR** with fallback to EasyOCR
- **Gemini AI integration** for structured trade extraction
- **Telegram bot** for forwarding signals
- **SQLAlchemy models**: Signal, Trade, IdempotencyKey, User
- **Background processing** with Redis + RQ (optional)
- **RAG query endpoint** with in-memory vector store
- **RESTful API** for metrics, signals, and queries
- **Alembic migrations** for database schema management

### Frontend (Server-rendered)
- **Dashboard** with Bootstrap + Chart.js
- **Signals page** with responsive table
- **Mobile-friendly** with offcanvas sidebar

### Frontend (React Client)
- **Modern React + Vite** SPA
- **Dashboard** with real-time metrics and charts
- **Signals table** with detail modal
- **Settings page** for theme and API configuration
- **Dark/Light theme** with localStorage persistence
- **Configurable backend URL** for flexible deployment

---

## 📦 Prerequisites

### Backend
- Python 3.12+
- pip and virtualenv
- (Optional) Tesseract OCR installed and in PATH
- (Optional) Redis for background jobs

### Frontend (React Client)
- Node.js 18+ (LTS recommended)
- npm 8+ (or pnpm/yarn)

### External Services (Optional)
- OpenAI API key (for RAG queries in non-mock mode)
- Google Gemini API key (for structured trade parsing)
- Telegram Bot Token and Chat ID (for forwarding)

---

## 🚀 Quick Start

### 1. Clone and Setup Backend

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
Copy-Item .env.example .env
# Edit .env and add your API keys
```

### 2. Initialize Database

```powershell
# Run Alembic migrations
alembic upgrade head
```

### 3. Start Backend

```powershell
# Start Flask server
python app.py
```

Backend runs on **http://localhost:5000**

### 4. Setup and Start Client (Optional)

```powershell
# Install client dependencies
cd client
npm install

# Start dev server
npm run dev
```

Client runs on **http://localhost:5173**

### 5. Use Helper Scripts

```powershell
# Start backend + expose via ngrok
.\start_all.ps1

# Start client dev server
.\start_client.ps1

# Build and copy client to Flask static
.\build_client.ps1
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# OpenAI (for RAG queries)
OPENAI_API_KEY=sk-...
MOCK_OPENAI=false

# Gemini (for structured trade parsing)
GEMINI_API_KEY=your-gemini-key

# Telegram (for forwarding)
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789

# Redis (optional, for background jobs)
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_URL=sqlite:///signals.db
# For PostgreSQL: postgresql://user:pass@localhost/dbname
```

### Client Configuration

The React client can be configured via:
1. **Settings page** in the UI (stores in localStorage)
2. **Environment variables** in `.env.local` (Vite):
   ```bash
   VITE_API_BASE_URL=http://localhost:5000
   ```

---

## 🏃 Running the Application

### Development Mode

#### Backend Only
```powershell
python app.py
```

#### Backend + Redis Worker (Background Jobs)
```powershell
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start RQ worker
rq worker

# Terminal 3: Start Flask
python app.py
```

#### Backend + Client (Separate)
```powershell
# Terminal 1: Backend
python app.py

# Terminal 2: Client
cd client
npm run dev
```

#### Use Helper Script
```powershell
.\start_all.ps1
```

### Production Mode

See [Deployment](#deployment) section.

---

## 💻 Client (React) Setup

### Install Dependencies

```powershell
cd client
npm install
```

If you encounter errors:
```powershell
npm cache clean --force
npm install --legacy-peer-deps
```

### Development Server

```powershell
npm run dev
```

Access at **http://localhost:5173**

### Build for Production

```powershell
npm run build
```

Output in `client/dist/`

### Serve from Flask

```powershell
# Build and copy to Flask static
.\build_client.ps1
```

Then access at **http://localhost:5000/client**

See [client/README.md](client/README.md) for detailed client documentation.

---

## 🌐 Deployment

### Option 1: Serve Client from Flask (Recommended)

1. Build the client:
   ```powershell
   cd client
   npm run build
   ```

2. Copy to Flask static (or use helper script):
   ```powershell
   .\build_client.ps1
   ```

3. Access client at: **http://your-domain.com/client**

### Option 2: Deploy Client Separately

1. Build client:
   ```powershell
   cd client
   npm run build
   ```

2. Deploy `client/dist/` to:
   - **Vercel**: `vercel --prod`
   - **Netlify**: Drag `dist/` to Netlify dashboard
   - **GitHub Pages**: Push `dist/` to gh-pages branch
   - **AWS S3 + CloudFront**: Upload to S3 bucket

3. Update backend URL in client Settings page or set `VITE_API_BASE_URL`

4. Enable CORS on Flask backend (already enabled for development)

### Backend Deployment

#### Docker
```powershell
docker build -t rag-trading .
docker run -p 5000:5000 --env-file .env rag-trading
```

#### Heroku / Railway / Render
- Set environment variables in platform dashboard
- Configure PostgreSQL database
- Run migrations: `alembic upgrade head`

---

## 📚 API Documentation

### Endpoints

#### `POST /webhook`
Receive TradingView webhook with trade signal.

**Action Mapping:**
The webhook automatically maps trading terms to standard action types:
- `"Long"` or `"long"` → `"BUY"`
- `"Short"` or `"short"` → `"SELL"`
- `"Buy"` or `"buy"` → `"BUY"`
- `"Sell"` or `"sell"` → `"SELL"`

**Body:**
```json
{
  "action": "Long",
  "symbol": "BTCUSDT",
  "price": 50000,
  "image_url": "https://..."
}
```

Or as plain text:
```
Going long on BTCUSDT at price 50000
```

#### `GET /api/signals`
Get list of signals.

**Response:**
```json
{
  "count": 10,
  "signals": [
    {
      "id": 1,
      "symbol": "BTCUSDT",
      "action": "buy",
      "price": 50000,
      "created_at": "2025-10-14T12:00:00"
    }
  ]
}
```

#### `GET /api/metrics`
Get dashboard metrics (trades today, weekly PnL, etc.).

#### `POST /api/query`
RAG query endpoint.

**Body:**
```json
{
  "question": "What are recent BTC trades?"
}
```

#### `GET /dashboard`
Server-rendered dashboard (Bootstrap + Chart.js).

#### `GET /client`
Serve React client (if built and copied to static).

---

## 📁 Project Structure

```
rag-project/
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy models
├── db.py                   # Database session management
├── tasks.py                # Background tasks (RQ)
├── gemini_client.py        # Gemini AI integration
├── telegram_helpers.py     # Telegram forwarding
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── alembic/                # Database migrations
│   ├── env.py
│   └── versions/
├── templates/              # Server-rendered HTML
│   ├── base.html
│   ├── dashboard.html
│   └── signals.html
├── static/                 # Static assets
│   ├── css/
│   ├── js/
│   └── client/            # Built React client (after build_client.ps1)
├── tests/                  # Pytest tests
├── client/                 # React frontend (separate)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Layout.jsx
│   │   ├── api.js
│   │   ├── styles.css
│   │   └── components/
│   │       ├── Dashboard.jsx
│   │       ├── Signals.jsx
│   │       ├── SignalDetails.jsx
│   │       └── Settings.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
├── start_all.ps1           # Start backend + ngrok
├── start_client.ps1        # Start React dev server
└── build_client.ps1        # Build and copy client to Flask static
```

---

## 🧪 Testing

### Run Tests

```powershell
pytest
```

### Run Specific Test

```powershell
pytest tests/test_analyze_trade_text.py
```

### Test Webhook Action Mapping

Test that "Long" and "Short" are correctly mapped to "BUY" and "SELL":

```powershell
# Make sure Flask backend is running first
python test_action_mapping.py

# Check the results in database
python check_signals.py
```

You should see:
- Webhooks with `"action": "Long"` → saved as `action = "BUY"`
- Webhooks with `"action": "Short"` → saved as `action = "SELL"`

See [ACTION_MAPPING_FIX.md](ACTION_MAPPING_FIX.md) for more details.

### Mock Mode (No API Keys Required)

```powershell
$env:MOCK_OPENAI = 'true'
python smoke_test.py
```

---

## 🔧 Troubleshooting

### Backend Issues

#### "No module named 'flask_cors'"
```powershell
pip install flask-cors
```

#### Database errors
```powershell
# Reset database
Remove-Item signals.db
alembic upgrade head
```

#### Alembic KeyError
Fixed in `alembic/env.py` (simplified logging config).

### Client Issues

#### npm install fails
```powershell
npm cache clean --force
Remove-Item node_modules -Recurse -Force
npm install --legacy-peer-deps
```

#### API calls fail (CORS errors)
- Ensure Flask backend is running
- Check backend URL in Settings page
- CORS is enabled for development in `app.py`

#### Theme not persisting
- Check localStorage is enabled in browser
- Clear and refresh: `localStorage.clear()`

### Webhook Issues

#### Webhooks not received
- Check ngrok is running: `.\start_all.ps1`
- Get public URL: `(Invoke-RestMethod http://127.0.0.1:4040/api/tunnels).tunnels[0].public_url`
- Configure TradingView alert with ngrok URL + `/webhook`

---

## 📝 Notes

- **Idempotency**: Webhook processing is idempotent via transactional insert of IdempotencyKey
- **Background Jobs**: Optional Redis + RQ for async processing; falls back to synchronous if Redis unavailable
- **OCR**: Tesseract preferred; EasyOCR fallback if Tesseract fails
- **Mock Mode**: Set `MOCK_OPENAI=true` to run without OpenAI API (useful for development)
- **Production**: Use PostgreSQL instead of SQLite for production deployments

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Check [Troubleshooting](#troubleshooting) section
- Review client-specific docs in [client/README.md](client/README.md)
