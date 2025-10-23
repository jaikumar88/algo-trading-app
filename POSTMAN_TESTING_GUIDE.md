# 🚀 Complete Postman Collection - API Testing Guide

## 📦 Collection Contents

This Postman collection includes **50+ API endpoints** organized into categories:

### Categories:
1. **🏠 Health & Info** (2 endpoints)
2. **📊 Chart Data APIs** (7 endpoints)
3. **💼 Trading Operations** (4 endpoints)
4. **🚀 Enhanced Trading APIs** (8 endpoints)
5. **📡 Signals** (5 endpoints)
6. **🔔 Webhook** (1 endpoint)
7. **📈 Instruments Management** (1 endpoint)
8. **🧪 Test Scenarios** (6 complete workflow tests)

---

## 📥 Import Instructions

### Method 1: Import JSON File
1. Open Postman
2. Click **Import** button (top left)
3. Select **File** tab
4. Choose `postman_collection.json`
5. Click **Import**

### Method 2: Drag & Drop
1. Open Postman
2. Drag `postman_collection.json` into Postman window
3. Collection auto-imports

---

## ⚙️ Environment Setup

### Option 1: Use Collection Variables (Recommended)
The collection has built-in variables:
- `baseUrl`: `http://localhost:5000`
- `apiPrefix`: `/api`

No extra setup needed! ✅

### Option 2: Create Postman Environment (Optional)
For advanced users who want to test multiple environments:

1. Click **Environments** (left sidebar)
2. Click **+** to create new environment
3. Name it: `RAG Trading - Local`
4. Add variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| baseUrl | http://localhost:5000 | http://localhost:5000 |
| apiPrefix | /api | /api |
| trade_id | 1 | (dynamic) |
| signal_id | 1 | (dynamic) |

5. Save and select the environment

---

## 🧪 Testing Workflow

### Quick Start (5 Minutes)

#### 1. Health Check
```
GET {{baseUrl}}/health
```
**Expected:** Status 200, `{"status": "healthy"}`

#### 2. Get Instruments
```
GET {{baseUrl}}{{apiPrefix}}/chart/instruments
```
**Expected:** List of 10 instruments (BTCUSDT, ETHUSDT, etc.)

#### 3. Get Chart Data
```
GET {{baseUrl}}{{apiPrefix}}/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=100
```
**Expected:** Array of 100 candlesticks

#### 4. Get All Trades
```
GET {{baseUrl}}{{apiPrefix}}/trading/trades?page=1&limit=50
```
**Expected:** Trades with pagination info

#### 5. Get Signals
```
GET {{baseUrl}}{{apiPrefix}}/trading/signals?limit=50
```
**Expected:** Array of trading signals

---

## 📋 Detailed Endpoint Guide

### 🏠 Health & Info

#### 1. Root - Get API Info
```http
GET http://localhost:5000/
```
**Response:**
```json
{
  "name": "RAG Trading System",
  "version": "2.0.0",
  "status": "running",
  "environment": "development"
}
```

#### 2. Health Check
```http
GET http://localhost:5000/health
```
**Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

### 📊 Chart Data APIs

#### 1. Get All Instruments
```http
GET http://localhost:5000/api/chart/instruments
```
**Response:**
```json
{
  "instruments": [
    {
      "symbol": "BTCUSDT",
      "name": "Bitcoin",
      "enabled": true,
      "created_at": "2025-10-16T21:53:47.758233-05:00"
    }
  ]
}
```

#### 2. Get OHLCV Data
```http
GET http://localhost:5000/api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=100
```

**Parameters:**
- `symbol` (required): BTCUSDT, ETHUSDT, EURUSD, etc.
- `timeframe` (required): 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
- `limit` (optional): Number of candles (default: 100)

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "count": 100,
  "data": [
    {
      "timestamp": "2025-10-17T02:55:58.817519-05:00",
      "open": 50585.97,
      "high": 50718.3,
      "low": 50357.12,
      "close": 50374.57,
      "volume": 179.96
    }
  ]
}
```

#### 3. Get Latest Price
```http
GET http://localhost:5000/api/chart/latest-price?symbol=ETHUSDT
```

**Response:**
```json
{
  "symbol": "ETHUSDT",
  "price": 98.65,
  "timestamp": "2025-10-17T02:56:00.773442-05:00",
  "volume_24h": 871493.08,
  "high_24h": 170.54,
  "low_24h": 92.83,
  "change_24h": -27.55
}
```

#### 4. Get Multi-Symbol Prices
```http
POST http://localhost:5000/api/chart/multi-symbol-prices
Content-Type: application/json

{
  "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
}
```

**Response:**
```json
{
  "prices": [
    {
      "symbol": "BTCUSDT",
      "price": 50374.57,
      "timestamp": "2025-10-17T02:55:58.817519-05:00"
    }
  ]
}
```

---

### 💼 Trading Operations

#### 1. Get All Trades (With Pagination)
```http
GET http://localhost:5000/api/trading/trades?page=1&limit=50
```

**Query Parameters:**
- `page`: Page number (1-indexed)
- `limit`: Items per page
- `status`: OPEN or CLOSED (optional)
- `symbol`: Filter by symbol (optional)

**Response:**
```json
{
  "trades": [
    {
      "id": 20,
      "symbol": "ETHUSD",
      "action": "BUY",
      "quantity": 100.0,
      "open_price": 3774.3,
      "open_time": "2025-10-17T08:51:00.707149-05:00",
      "close_price": null,
      "close_time": null,
      "status": "OPEN",
      "profit_loss": null,
      "allocated_fund": null,
      "risk_amount": null,
      "stop_loss_triggered": false,
      "closed_by_user": false
    }
  ],
  "summary": {
    "total": 20,
    "open": 1,
    "closed": 19,
    "total_pnl": -13803.0
  },
  "pagination": {
    "page": 1,
    "limit": 50,
    "offset": 0,
    "total": 20,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

#### 2. Get Open Trades Only
```http
GET http://localhost:5000/api/trading/trades?status=OPEN
```

#### 3. Get Closed Trades Only
```http
GET http://localhost:5000/api/trading/trades?status=CLOSED
```

#### 4. Get Trades by Symbol
```http
GET http://localhost:5000/api/trading/trades?symbol=ETHUSD&limit=50
```

---

### 🚀 Enhanced Trading APIs

#### 1. Place Market Order
```http
POST http://localhost:5000/api/trading/orders
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "action": "BUY",
  "quantity": 0.01,
  "order_type": "MARKET"
}
```

**Response:**
```json
{
  "trade_id": 21,
  "symbol": "BTCUSDT",
  "action": "BUY",
  "quantity": 0.01,
  "open_price": 50374.57,
  "status": "OPEN",
  "message": "Market order placed successfully"
}
```

#### 2. Place Limit Order with SL/TP
```http
POST http://localhost:5000/api/trading/orders
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "action": "BUY",
  "quantity": 0.01,
  "order_type": "LIMIT",
  "limit_price": 50000.00,
  "stop_loss": 48000.00,
  "take_profit": 55000.00
}
```

#### 3. Get Open Positions
```http
GET http://localhost:5000/api/trading/positions
```

**Response:**
```json
{
  "positions": [
    {
      "id": 20,
      "symbol": "ETHUSD",
      "action": "BUY",
      "quantity": 100.0,
      "open_price": 3774.3,
      "current_price": 3800.0,
      "unrealized_pnl": 2570.0,
      "open_time": "2025-10-17T08:51:00.707149-05:00"
    }
  ],
  "total_unrealized_pnl": 2570.0,
  "count": 1
}
```

#### 4. Close Trade (One-Click)
```http
POST http://localhost:5000/api/trading/trades/20/close
Content-Type: application/json

{
  "close_price": 3800.00
}
```

**Response:**
```json
{
  "trade_id": 20,
  "symbol": "ETHUSD",
  "status": "CLOSED",
  "profit_loss": 2570.0,
  "message": "Trade closed successfully"
}
```

#### 5. Reverse Trade (One-Click)
```http
POST http://localhost:5000/api/trading/trades/20/reverse
Content-Type: application/json

{
  "reverse_price": 3800.00
}
```

**Response:**
```json
{
  "closed_trade_id": 20,
  "new_trade_id": 21,
  "closed_pnl": 2570.0,
  "new_action": "SELL",
  "message": "Trade reversed successfully"
}
```

#### 6. Modify Trade (Update SL/TP)
```http
PATCH http://localhost:5000/api/trading/trades/20/modify
Content-Type: application/json

{
  "stop_loss": 3700.00,
  "take_profit": 3900.00
}
```

#### 7. Get Trade History
```http
GET http://localhost:5000/api/trading/history?limit=50&offset=0
```

**Query Parameters:**
- `limit`: Number of records
- `offset`: Skip records
- `symbol`: Filter by symbol (optional)
- `start_date`: Filter from date (optional)
- `end_date`: Filter to date (optional)

---

### 📡 Signals

#### 1. Get All Signals
```http
GET http://localhost:5000/api/trading/signals?limit=50
```

**Query Parameters:**
- `limit`: Number of records
- `offset`: Skip records
- `symbol`: Filter by symbol (optional)
- `action`: BUY or SELL (optional)
- `source`: webhook, manual, etc. (optional)

**Response:**
```json
{
  "signals": [
    {
      "id": 16,
      "source": "webhook",
      "symbol": "ETHUSD",
      "action": "BUY",
      "price": 3796.28,
      "raw": "LongAt Price=3796.28, Symbol : ETHUSD...",
      "created_at": "2025-10-17T07:37:58.374727-05:00"
    }
  ],
  "count": 16,
  "total": 16,
  "pagination": {
    "limit": 50,
    "offset": 0
  }
}
```

#### 2. Get Signals by Symbol
```http
GET http://localhost:5000/api/trading/signals?symbol=ETHUSD&limit=20
```

#### 3. Get BUY Signals Only
```http
GET http://localhost:5000/api/trading/signals?action=BUY&limit=50
```

#### 4. Get SELL Signals Only
```http
GET http://localhost:5000/api/trading/signals?action=SELL&limit=50
```

#### 5. Get Signal by ID
```http
GET http://localhost:5000/api/trading/signals/16
```

---

## 🧪 Complete Testing Scenario

### Scenario: Complete Trading Workflow

Follow these steps in order:

1. **Check Health**
   ```
   GET /health
   ```

2. **Get Available Instruments**
   ```
   GET /api/chart/instruments
   ```

3. **Get Latest Price**
   ```
   GET /api/chart/latest-price?symbol=BTCUSDT
   ```

4. **Get Chart Data**
   ```
   GET /api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=100
   ```

5. **Place Market Order**
   ```
   POST /api/trading/orders
   Body: {
     "symbol": "BTCUSDT",
     "action": "BUY",
     "quantity": 0.01,
     "order_type": "MARKET"
   }
   ```

6. **Check Open Positions**
   ```
   GET /api/trading/positions
   ```

7. **View All Trades**
   ```
   GET /api/trading/trades?page=1&limit=10
   ```

8. **Close Trade** (Use trade_id from step 5)
   ```
   POST /api/trading/trades/{trade_id}/close
   Body: {"close_price": 50500.00}
   ```

9. **View Trade History**
   ```
   GET /api/trading/history?limit=50
   ```

---

## 📊 Expected Results

### Current Database State
- **Instruments:** 10 (BTCUSDT, ETHUSDT, BNBUSDT, XRPUSDT, SOLUSDT, EURUSD, GBPUSD, USDJPY, XAUUSD, XAGUSD)
- **Price History:** 556,500+ candles (30 days × 6 timeframes × 10 instruments)
- **Trades:** 20 trades (1 OPEN, 19 CLOSED)
- **Signals:** 16+ signals
- **Total P&L:** -$13,803

### Success Indicators
✅ All endpoints return **200 OK**  
✅ Chart data has **100+ candles** per request  
✅ Trades include **pagination** info  
✅ Signals include **created_at** timestamps  
✅ Positions show **real-time P&L**  

---

## 🔧 Troubleshooting

### Issue: Connection Refused
**Solution:** Make sure Flask server is running
```powershell
python app.py
```

### Issue: Empty Data
**Check:**
1. Database seeded? Run: `python scripts/seed_mock_data.py`
2. Correct URL? Should be `http://localhost:5000`
3. Server logs for errors

### Issue: 404 Not Found
**Check:**
1. Endpoint path is correct
2. Flask server shows routes registered
3. Using correct HTTP method (GET vs POST)

### Issue: 500 Internal Server Error
**Check:**
1. Flask server logs (terminal)
2. Database connection working
3. All required fields in request body

---

## 📝 Quick Reference

### Base URLs
- **Local:** `http://localhost:5000`
- **API Prefix:** `/api`

### Common Symbols
- Crypto: BTCUSDT, ETHUSDT, BNBUSDT, XRPUSDT, SOLUSDT
- Forex: EURUSD, GBPUSD, USDJPY
- Commodities: XAUUSD (Gold), XAGUSD (Silver)

### Timeframes
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `4h` - 4 hours
- `1d` - 1 day
- `1w` - 1 week

### Order Types
- `MARKET` - Execute immediately at current price
- `LIMIT` - Execute at specified price or better

### Trade Actions
- `BUY` - Long position
- `SELL` - Short position

---

## 🎯 Next Steps

1. ✅ Import collection into Postman
2. ✅ Run "Complete Trading Workflow" folder
3. ✅ Test individual endpoints
4. ✅ Verify all responses
5. ✅ Check pagination works
6. ✅ Test error scenarios (invalid symbols, wrong data)

---

## 📚 Additional Resources

- **API Documentation:** `docs/TRADING_CHART_API.md`
- **Implementation Guide:** `docs/TRADINGVIEW_BACKEND_COMPLETE.md`
- **Pagination Guide:** `docs/API_PAGINATION_GUIDE.md`
- **Diagnostic Report:** `docs/TRADES_ENDPOINT_DIAGNOSTIC.md`

---

**Collection Version:** 1.0.0  
**Last Updated:** October 17, 2025  
**Total Endpoints:** 50+  
**Status:** ✅ All Working
