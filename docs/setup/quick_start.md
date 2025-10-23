# 🚀 Quick Start Guide - Trading Management System

## Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- PostgreSQL (optional, uses SQLite by default)

---

## 📦 Installation

### 1. Backend Setup
```bash
# Navigate to project root
cd e:\workspace\python\rag-project

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (if not already done)
pip install -r requirements.txt

# Initialize database
python recreate_db.py

# Run test to populate sample data
python test_all_features.py
```

### 2. Frontend Setup
```bash
# Navigate to client directory
cd client

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

---

## ▶️ Running the Application

### Terminal 1: Backend (Flask)
```powershell
cd e:\workspace\python\rag-project
.\.venv\Scripts\Activate.ps1
python app.py
```
**Backend will run on:** `http://localhost:5000`

### Terminal 2: Frontend (React)
```powershell
cd e:\workspace\python\rag-project\client
npm run dev
```
**Frontend will run on:** `http://localhost:5173`

---

## 🎯 Accessing the Application

Open your browser and navigate to: **http://localhost:5173**

You'll see 7 main sections in the navigation:

1. **📈 Dashboard** - Main overview (existing)
2. **📡 Signals** - Webhook signals (existing)
3. **📊 Trade History** - View all trades with filters
4. **📍 Positions** - Monitor open positions with close buttons
5. **🎯 Instruments** - Manage allowed trading instruments
6. **⚙️ Control** - System settings and master switch
7. **🔧 Settings** - Application settings

---

## 🧪 Testing the New Features

### Test Trade History
1. Navigate to **Trade History**
2. See statistics cards at top
3. Use filters (Status, Symbol)
4. Click "Export CSV" to download
5. Try pagination

### Test Positions
1. Navigate to **Positions**
2. Toggle "Auto-refresh" on/off
3. See open positions (if any exist)
4. Click "🔒 Close Position" to test manual closing
5. Confirm the action

### Test Instruments
1. Navigate to **Instruments**
2. Click "➕ Add Instrument"
3. Add sample: BTCUSDT, Bitcoin
4. Toggle enable/disable
5. Try deleting an instrument

### Test System Control
1. Navigate to **Control**
2. Toggle "TURN ON/OFF" master switch
3. Edit "Total Fund" value
4. Edit "Risk Per Instrument" percentage
5. View fund allocations table
6. Check system overview cards

---

## 📊 Sample Data

The `test_all_features.py` script creates:
- ✅ 4 system settings
- ✅ 5 sample instruments (BTCUSDT, ETHUSDT, SOLUSDT, DOGEUSDT, ADAUSDT)
- ✅ 4 fund allocations ($25,000 each)
- ✅ 3 sample trades with P&L

---

## 🔧 Configuration

### Backend API Endpoint
Current: `http://localhost:5000/api/trading`

To change (in production):
- Update in each component (TradeHistory.jsx, Positions.jsx, etc.)
- Or create a config file: `client/src/config.js`

```javascript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/trading'
```

### Database
Default: SQLite (`dev_trading.db`)

To use PostgreSQL:
```bash
# Set environment variables
export DATABASE_URL=postgresql://user:pass@localhost/trading_db
# or
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASS=yourpassword
export DB_NAME=trading_db
```

---

## 🎨 Theme

The app supports Light/Dark themes:
- Click theme toggle (top right)
- Preference saved in localStorage
- Persists across sessions

---

## 📱 Mobile Access

The UI is fully responsive! Access from:
- Desktop (best experience)
- Tablet (optimized layout)
- Mobile (single column, touch-friendly)

---

## ⚠️ Troubleshooting

### Backend not starting?
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <process_id> /F

# Restart backend
python app.py
```

### Frontend not loading?
```bash
# Clear node_modules and reinstall
cd client
rm -rf node_modules
npm install
npm run dev
```

### API errors?
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify CORS is enabled in Flask
- Check network tab in DevTools

### Database errors?
```bash
# Recreate database from scratch
python recreate_db.py

# Run test to add sample data
python test_all_features.py
```

---

## 🔐 Security Notes (Production)

Before deploying to production:

1. **Remove test data**
2. **Add authentication** (JWT tokens)
3. **Enable HTTPS**
4. **Update CORS settings** (restrict origins)
5. **Use environment variables** for secrets
6. **Enable rate limiting**
7. **Add input validation**
8. **Use production database** (PostgreSQL)
9. **Set up logging and monitoring**
10. **Add backup strategy**

---

## 📚 API Documentation

Full API documentation available in:
- `TRADING_MANAGEMENT_SYSTEM.md` - Complete system docs
- `TEST_RESULTS.md` - Test results and validation
- `FRONTEND_IMPLEMENTATION.md` - Frontend details

---

## 🎯 Key Features

### Trade Management
- ✅ Automatic opposite position closing
- ✅ P&L calculation (BUY and SELL)
- ✅ Manual position closing from UI
- ✅ Complete trade history with filters
- ✅ CSV export

### Risk Management
- ✅ 2% risk limit per instrument
- ✅ Equal fund allocation
- ✅ Auto-stop loss protection
- ✅ Per-instrument trading control

### Admin Controls
- ✅ Instrument whitelist management
- ✅ Master trading on/off switch
- ✅ Fund and risk configuration
- ✅ System status dashboard

---

## 💡 Tips

1. **Use Auto-Refresh** on Positions page for live monitoring
2. **Export CSV** regularly for record keeping
3. **Monitor Risk Alerts** on Control page
4. **Test with Small Amounts** first
5. **Keep Master Switch OFF** when not trading
6. **Review Trade History** to analyze patterns
7. **Disable Unused Instruments** to focus trading

---

## 🆘 Support

For issues or questions:
1. Check console logs (browser and terminal)
2. Review documentation files
3. Check test results in `TEST_RESULTS.md`
4. Verify backend APIs with `test_trading_api.py`

---

## ✅ Health Check

Run these to verify everything works:

```bash
# Backend health
curl http://localhost:5000/api/trading/instruments

# Test all features
python test_all_features.py

# Test API endpoints
python test_trading_api.py
```

---

**Happy Trading! 📈💰**

Last Updated: October 14, 2025
