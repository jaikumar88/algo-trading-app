# 🔧 Quick Fix Guide - PostgreSQL Setup

## ✅ Current Status

- **Backend**: Running on http://localhost:5000
- **Database**: PostgreSQL configured (`postgresql://postgres:postgres@localhost:5432/trading`)
- **Schema**: Updated with all new columns
- **Issue**: Database is empty (needs seeding)

## 🚀 Quick Fix Steps

### Step 1: Seed the PostgreSQL Database

Run this command in PowerShell:

```powershell
$env:PYTHONIOENCODING="utf-8"; python scripts/seed_mock_data.py
```

This will:
- ✅ Add 10 trading instruments
- ✅ Generate 556,500+ candles (30 days × 6 timeframes × 10 symbols)
- ⏱️ Takes ~2-3 minutes

### Step 2: Verify Data Loaded

Test the APIs:

```powershell
# Test instruments
Invoke-RestMethod -Uri "http://localhost:5000/api/chart/instruments"

# Test chart data
Invoke-RestMethod -Uri "http://localhost:5000/api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=10"

# Test latest price
Invoke-RestMethod -Uri "http://localhost:5000/api/chart/latest-price?symbol=BTCUSDT"
```

### Step 3: Test Your Client App

Once APIs return data, your React client at `http://localhost:5173` should work!

---

## 📊 Available API Endpoints

### Chart Data APIs

```
GET  /api/chart/instruments
GET  /api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=100
GET  /api/chart/latest-price?symbol=BTCUSDT
POST /api/chart/multi-symbol-prices
```

### Trading APIs

```
POST  /api/trading/orders
POST  /api/trading/trades/{id}/close
POST  /api/trading/trades/{id}/reverse
GET   /api/trading/positions
PATCH /api/trading/trades/{id}/modify
GET   /api/trading/history
```

---

## 🔍 Troubleshooting

### If Client Shows "No Data"

**Check 1: Backend is running**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health"
```

**Check 2: Data is seeded**
```powershell
$r = Invoke-RestMethod -Uri "http://localhost:5000/api/chart/instruments"
$r.instruments.Count  # Should show 10
```

**Check 3: CORS is enabled**
Your backend has CORS enabled for:
- http://localhost:5173 (Vite default)
- http://localhost:3000 (React default)

### If Seeding Fails

Try without emoji output:
```powershell
# Set UTF-8 encoding
$env:PYTHONIOENCODING="utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Run seed script
python scripts/seed_mock_data.py
```

Or manually seed from Python:
```python
from src.database.session import SessionLocal
from src.models.base import AllowedInstrument
from decimal import Decimal

session = SessionLocal()

# Add one instrument manually
inst = AllowedInstrument(
    symbol='BTCUSDT',
    name='Bitcoin',
    instrument_type='crypto',
    base_currency='BTC',
    quote_currency='USDT',
    price_precision=2,
    quantity_precision=6,
    min_quantity=Decimal('0.00001'),
    enabled=True
)
session.add(inst)
session.commit()
print("Added BTCUSDT")
```

---

## ✅ Expected Result After Seeding

When you call:
```
GET http://localhost:5000/api/chart/instruments
```

You should see:
```json
{
  "instruments": [
    {"symbol": "BTCUSDT", "name": "Bitcoin", "enabled": true},
    {"symbol": "ETHUSDT", "name": "Ethereum", "enabled": true},
    {"symbol": "BNBUSDT", "name": "Binance Coin", "enabled": true},
    {"symbol": "XRPUSDT", "name": "Ripple", "enabled": true},
    {"symbol": "SOLUSDT", "name": "Solana", "enabled": true},
    {"symbol": "EURUSD", "name": "Euro / US Dollar", "enabled": true},
    {"symbol": "GBPUSD", "name": "British Pound / US Dollar", "enabled": true},
    {"symbol": "USDJPY", "name": "US Dollar / Japanese Yen", "enabled": true},
    {"symbol": "XAUUSD", "name": "Gold / US Dollar", "enabled": true},
    {"symbol": "XAGUSD", "name": "Silver / US Dollar", "enabled": true}
  ]
}
```

And when you call:
```
GET http://localhost:5000/api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=5
```

You should see 5 candlesticks with OHLCV data!

---

## 🎯 Next Steps

1. ✅ Run seed command with UTF-8 encoding
2. ✅ Verify data in database
3. ✅ Test APIs return data
4. ✅ Refresh your React client
5. ✅ Chart should display!

---

## 💡 Pro Tip

If you keep having encoding issues, you can run the seed script from Python directly:

```python
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
exec(open('scripts/seed_mock_data.py').read())
```

---

**Your backend is ready! Just need to seed the data.** 🚀
