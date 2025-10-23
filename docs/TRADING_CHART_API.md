# TradingView-Style Chart API Documentation

## 🎯 Overview

This backend provides a complete TradingView-style trading experience with:
- **Real-time OHLCV Chart Data** - Candlestick data for multiple timeframes
- **Order Placement** - Market and limit orders with SL/TP
- **One-Click Trading** - Close and reverse trades instantly
- **Position Management** - View, modify, and monitor open positions
- **10 Trading Instruments** - Crypto, Forex, and Commodities

---

## 📊 Chart & Market Data APIs

### 1. Get Available Instruments

Get list of all trading instruments.

**Endpoint:** `GET /api/chart/instruments`

**Query Parameters:**
- `enabled` (optional) - Filter by enabled status (`true`/`false`)

**Response:**
```json
{
  "instruments": [
    {
      "symbol": "BTCUSDT",
      "name": "Bitcoin",
      "enabled": true,
      "created_at": "2025-10-16T10:00:00Z"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:5000/api/chart/instruments?enabled=true
```

---

### 2. Get OHLCV Candlestick Data

Get historical candlestick data for charting.

**Endpoint:** `GET /api/chart/ohlcv`

**Query Parameters:**
- `symbol` (required) - Trading symbol (e.g., `BTCUSDT`)
- `timeframe` (required) - Candle timeframe: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`
- `from` (optional) - Start date (ISO format or Unix timestamp)
- `to` (optional) - End date (ISO format or Unix timestamp)
- `limit` (optional) - Max candles (default 500, max 1000)

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "count": 500,
  "data": [
    {
      "timestamp": "2025-10-16T10:00:00Z",
      "open": 43250.50,
      "high": 43580.25,
      "low": 43100.00,
      "close": 43450.75,
      "volume": 125.45
    }
  ]
}
```

**Examples:**
```bash
# Get last 100 1-hour candles for BTCUSDT
curl "http://localhost:5000/api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=100"

# Get candles for specific date range
curl "http://localhost:5000/api/chart/ohlcv?symbol=ETHUSDT&timeframe=15m&from=2025-10-01T00:00:00Z&to=2025-10-16T00:00:00Z"
```

---

### 3. Get Latest Price

Get current price with 24h stats for a symbol.

**Endpoint:** `GET /api/chart/latest-price`

**Query Parameters:**
- `symbol` (required) - Trading symbol
- `timeframe` (optional) - Timeframe (default `1m`)

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "price": 43450.75,
  "timestamp": "2025-10-16T10:00:00Z",
  "change_24h": 2.5,
  "volume_24h": 25000.50,
  "high_24h": 43800.00,
  "low_24h": 42800.00
}
```

**Example:**
```bash
curl "http://localhost:5000/api/chart/latest-price?symbol=BTCUSDT"
```

---

### 4. Get Multiple Symbol Prices

Get latest prices for multiple symbols in one request.

**Endpoint:** `POST /api/chart/multi-symbol-prices`

**Request Body:**
```json
{
  "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
  "timeframe": "1m"
}
```

**Response:**
```json
{
  "prices": {
    "BTCUSDT": {
      "price": 43450.75,
      "change_24h": 2.5,
      "timestamp": "2025-10-16T10:00:00Z"
    },
    "ETHUSDT": {
      "price": 2305.50,
      "change_24h": 1.8,
      "timestamp": "2025-10-16T10:00:00Z"
    }
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/chart/multi-symbol-prices \
  -H "Content-Type: application/json" \
  -d '{"symbols":["BTCUSDT","ETHUSDT"],"timeframe":"1m"}'
```

---

## 💰 Trading APIs

### 5. Place Order (Market/Limit)

Place a new trading order from the chart.

**Endpoint:** `POST /api/trading/orders`

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.1,
  "price": 43250.50,
  "stop_loss": 42000.00,
  "take_profit": 45000.00
}
```

**Fields:**
- `symbol` (required) - Trading symbol
- `side` (required) - `BUY` or `SELL`
- `type` (required) - `MARKET` or `LIMIT`
- `quantity` (required) - Order quantity
- `price` (required for LIMIT) - Limit price
- `stop_loss` (optional) - Stop loss price
- `take_profit` (optional) - Take profit price

**Response:**
```json
{
  "success": true,
  "trade_id": 123,
  "order": {
    "id": 123,
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": 0.1,
    "price": 43250.50,
    "stop_loss": 42000.00,
    "take_profit": 45000.00,
    "status": "OPEN",
    "timestamp": "2025-10-16T10:00:00Z"
  }
}
```

**Examples:**
```bash
# Market Buy
curl -X POST http://localhost:5000/api/trading/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol":"BTCUSDT",
    "side":"BUY",
    "type":"MARKET",
    "quantity":0.1,
    "stop_loss":42000,
    "take_profit":45000
  }'

# Limit Sell
curl -X POST http://localhost:5000/api/trading/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol":"ETHUSDT",
    "side":"SELL",
    "type":"LIMIT",
    "price":2350.00,
    "quantity":1.5,
    "stop_loss":2400,
    "take_profit":2250
  }'
```

---

### 6. Close Trade (One-Click)

Close a specific trade instantly at market price.

**Endpoint:** `POST /api/trading/trades/{trade_id}/close`

**Path Parameters:**
- `trade_id` - ID of the trade to close

**Response:**
```json
{
  "success": true,
  "trade_id": 123,
  "symbol": "BTCUSDT",
  "close_price": 43500.75,
  "profit_loss": 250.25,
  "profit_loss_pct": 0.58,
  "timestamp": "2025-10-16T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/trading/trades/123/close
```

---

### 7. Reverse Trade

Close current position and open opposite position instantly.

**Endpoint:** `POST /api/trading/trades/{trade_id}/reverse`

**Path Parameters:**
- `trade_id` - ID of the trade to reverse

**Request Body (optional):**
```json
{
  "quantity": 0.15,
  "stop_loss": 42000.00,
  "take_profit": 45000.00
}
```

**Response:**
```json
{
  "success": true,
  "closed_trade": {
    "id": 123,
    "symbol": "BTCUSDT",
    "side": "BUY",
    "close_price": 43500.75,
    "profit_loss": 250.25,
    "timestamp": "2025-10-16T10:00:00Z"
  },
  "new_trade": {
    "id": 124,
    "symbol": "BTCUSDT",
    "side": "SELL",
    "price": 43500.75,
    "quantity": 0.1,
    "stop_loss": 42000.00,
    "take_profit": 45000.00,
    "timestamp": "2025-10-16T10:00:00Z"
  }
}
```

**Examples:**
```bash
# Reverse with same quantity
curl -X POST http://localhost:5000/api/trading/trades/123/reverse

# Reverse with different quantity and SL/TP
curl -X POST http://localhost:5000/api/trading/trades/123/reverse \
  -H "Content-Type: application/json" \
  -d '{
    "quantity":0.2,
    "stop_loss":42000,
    "take_profit":45000
  }'
```

---

### 8. Get Open Positions

View all open positions with current P&L.

**Endpoint:** `GET /api/trading/positions`

**Query Parameters:**
- `symbol` (optional) - Filter by symbol

**Response:**
```json
{
  "positions": [
    {
      "id": 123,
      "symbol": "BTCUSDT",
      "side": "BUY",
      "quantity": 0.1,
      "open_price": 43250.50,
      "current_price": 43500.75,
      "profit_loss": 25.025,
      "profit_loss_pct": 0.58,
      "stop_loss": 42000.00,
      "take_profit": 45000.00,
      "open_time": "2025-10-16T10:00:00Z"
    }
  ],
  "total_pnl": 25.025,
  "count": 1
}
```

**Example:**
```bash
# Get all open positions
curl http://localhost:5000/api/trading/positions

# Get positions for specific symbol
curl "http://localhost:5000/api/trading/positions?symbol=BTCUSDT"
```

---

### 9. Modify Trade (Update SL/TP)

Update stop loss and/or take profit for an open trade.

**Endpoint:** `PATCH /api/trading/trades/{trade_id}/modify`

**Path Parameters:**
- `trade_id` - ID of the trade to modify

**Request Body:**
```json
{
  "stop_loss": 42500.00,
  "take_profit": 46000.00
}
```

**Response:**
```json
{
  "success": true,
  "trade_id": 123,
  "stop_loss": 42500.00,
  "take_profit": 46000.00
}
```

**Examples:**
```bash
# Update both SL and TP
curl -X PATCH http://localhost:5000/api/trading/trades/123/modify \
  -H "Content-Type: application/json" \
  -d '{"stop_loss":42500,"take_profit":46000}'

# Remove stop loss
curl -X PATCH http://localhost:5000/api/trading/trades/123/modify \
  -H "Content-Type: application/json" \
  -d '{"stop_loss":null}'
```

---

### 10. Get Trade History

Get closed trades with filters.

**Endpoint:** `GET /api/trading/history`

**Query Parameters:**
- `symbol` (optional) - Filter by symbol
- `from` (optional) - Start date (ISO format)
- `to` (optional) - End date (ISO format)
- `limit` (optional) - Max results (default 50, max 500)
- `offset` (optional) - Pagination offset (default 0)

**Response:**
```json
{
  "trades": [
    {
      "id": 120,
      "symbol": "BTCUSDT",
      "side": "BUY",
      "quantity": 0.1,
      "open_price": 42800.00,
      "close_price": 43250.50,
      "profit_loss": 45.05,
      "open_time": "2025-10-15T10:00:00Z",
      "close_time": "2025-10-16T10:00:00Z"
    }
  ],
  "count": 1,
  "total_profit_loss": 45.05
}
```

**Example:**
```bash
# Get recent trade history
curl "http://localhost:5000/api/trading/history?limit=20"

# Get history for specific date range
curl "http://localhost:5000/api/trading/history?from=2025-10-01T00:00:00Z&to=2025-10-16T00:00:00Z"
```

---

## 📦 Available Instruments

The system comes pre-seeded with 10 popular instruments:

### Cryptocurrency
- **BTCUSDT** - Bitcoin / USDT
- **ETHUSDT** - Ethereum / USDT
- **BNBUSDT** - Binance Coin / USDT
- **XRPUSDT** - Ripple / USDT
- **SOLUSDT** - Solana / USDT

### Forex
- **EURUSD** - Euro / US Dollar
- **GBPUSD** - British Pound / US Dollar
- **USDJPY** - US Dollar / Japanese Yen

### Commodities
- **XAUUSD** - Gold / US Dollar
- **XAGUSD** - Silver / US Dollar

---

## 🚀 Setup & Usage

### 1. Seed Database

Run the seed script to populate instruments and OHLCV data:

```bash
python scripts/seed_mock_data.py
```

This will create:
- 10 trading instruments
- 30 days of historical data
- All timeframes (1m, 5m, 15m, 1h, 4h, 1d)

### 2. Start Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

### 3. Test Endpoints

```bash
# Check health
curl http://localhost:5000/health

# Get instruments
curl http://localhost:5000/api/chart/instruments

# Get chart data
curl "http://localhost:5000/api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=100"

# Place order
curl -X POST http://localhost:5000/api/trading/orders \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":0.1}'

# View positions
curl http://localhost:5000/api/trading/positions
```

---

## 🎨 Frontend Integration Guide

### Recommended Charting Library

Use **Lightweight Charts** by TradingView:
- https://tradingview.github.io/lightweight-charts/
- Free, lightweight, and performant
- Native candlestick support
- Easy integration

### Example Integration

```javascript
// Fetch OHLCV data
const response = await fetch(
  'http://localhost:5000/api/chart/ohlcv?symbol=BTCUSDT&timeframe=1h&limit=500'
);
const { data } = await response.json();

// Convert to Lightweight Charts format
const candlestickData = data.map(candle => ({
  time: new Date(candle.timestamp).getTime() / 1000,
  open: candle.open,
  high: candle.high,
  low: candle.low,
  close: candle.close
}));

// Create chart
const chart = LightweightCharts.createChart(document.getElementById('chart'));
const candlestickSeries = chart.addCandlestickSeries();
candlestickSeries.setData(candlestickData);

// Place order on chart click
chart.subscribeClick((param) => {
  if (param.time) {
    const price = param.seriesPrices.get(candlestickSeries);
    placeOrder('BTCUSDT', 'BUY', price);
  }
});
```

---

## 🔥 Key Features for Frontend

### 1. One-Click Trading
```javascript
// Close trade
await fetch(`/api/trading/trades/${tradeId}/close`, { method: 'POST' });

// Reverse trade
await fetch(`/api/trading/trades/${tradeId}/reverse`, { method: 'POST' });
```

### 2. Real-Time Position Updates
```javascript
// Poll positions every second
setInterval(async () => {
  const positions = await fetch('/api/trading/positions').then(r => r.json());
  updateUI(positions);
}, 1000);
```

### 3. Chart Controls
```javascript
// Symbol selector
symbols.forEach(symbol => {
  button.onclick = () => loadChart(symbol);
});

// Timeframe selector
['1m', '5m', '15m', '1h', '4h', '1d'].forEach(tf => {
  button.onclick = () => loadChart(currentSymbol, tf);
});
```

### 4. Trade Markers on Chart
```javascript
// Add markers for open positions
positions.forEach(pos => {
  candlestickSeries.createMarker({
    time: new Date(pos.open_time).getTime() / 1000,
    position: pos.side === 'BUY' ? 'belowBar' : 'aboveBar',
    color: pos.side === 'BUY' ? '#26a69a' : '#ef5350',
    shape: pos.side === 'BUY' ? 'arrowUp' : 'arrowDown',
    text: `${pos.side} ${pos.quantity} @ ${pos.open_price}`
  });
});
```

---

## ✅ Complete Trading Workflow

### Example: Complete Buy Trade

```bash
# 1. Get current price
curl "http://localhost:5000/api/chart/latest-price?symbol=BTCUSDT"

# 2. Place buy order
curl -X POST http://localhost:5000/api/trading/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol":"BTCUSDT",
    "side":"BUY",
    "type":"MARKET",
    "quantity":0.1,
    "stop_loss":42000,
    "take_profit":45000
  }'
# Returns: {"trade_id": 123, ...}

# 3. View open position
curl http://localhost:5000/api/trading/positions

# 4. Modify SL/TP
curl -X PATCH http://localhost:5000/api/trading/trades/123/modify \
  -H "Content-Type: application/json" \
  -d '{"stop_loss":42500,"take_profit":46000}'

# 5. Close position
curl -X POST http://localhost:5000/api/trading/trades/123/close
```

---

## 🎯 Error Handling

All endpoints return standardized error responses:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP Status Codes:
- `200` - Success
- `201` - Created (for new orders)
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (trade/instrument not found)
- `500` - Internal Server Error

---

## 📊 Performance Tips

1. **Pagination** - Use `limit` and `offset` for large datasets
2. **Caching** - Cache instrument list (rarely changes)
3. **Batch Requests** - Use multi-symbol price endpoint
4. **Timeframe Selection** - Lower timeframes = more data, use wisely
5. **WebSocket** - Implement WebSocket for real-time price updates (future enhancement)

---

## 🔐 Security Notes

For production deployment:
- Add authentication/authorization
- Implement rate limiting
- Use HTTPS only
- Validate all inputs
- Add CORS restrictions
- Implement API keys

---

## 📝 TODO (Future Enhancements)

- [ ] WebSocket for real-time price streaming
- [ ] Order book depth data
- [ ] Technical indicators (MA, RSI, MACD)
- [ ] Account balance management
- [ ] Risk management alerts
- [ ] Trade analytics dashboard
- [ ] Export trade history (CSV/PDF)

---

**Ready to build a world-class trading UI!** 🚀
