# 📦 Historical Price Data System

## Overview

The RAG Trading System now includes a comprehensive historical price data collection and display system. This allows you to store OHLCV (Open, High, Low, Close, Volume) data in the database and visualize it with beautiful, smooth charts.

## 🎯 Features

### 1. Database Storage
- **PriceHistory Model**: Stores OHLCV data with timestamps
- **Multi-Timeframe Support**: 1m, 5m, 15m, 30m, 1h, 4h, 1d
- **Efficient Indexing**: Symbol, timeframe, and timestamp indexes for fast queries
- **Duplicate Prevention**: Unique constraints prevent data duplication

### 2. Data Sources
- **Real Binance API**: Fetch live historical data from Binance
- **Mock Data Generator**: Realistic simulated data for development/testing
- **Configurable**: Switch between real and mock data via API parameter

### 3. API Endpoints

#### Get Historical Prices
```bash
GET /api/historical-prices/<symbol>?timeframe=1h&limit=500&use_mock=true
```

**Parameters:**
- `symbol` (required): Trading pair (e.g., BTCUSDT)
- `timeframe` (optional): 1m, 5m, 15m, 30m, 1h, 4h, 1d (default: 1h)
- `limit` (optional): Number of candles (default: 500, max: 1000)
- `use_mock` (optional): true/false (default: true)

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "count": 500,
  "data": [
    {
      "time": 1697472000,
      "timestamp": "2024-10-16T12:00:00",
      "open": 65000.00,
      "high": 65500.00,
      "low": 64800.00,
      "close": 65200.00,
      "volume": 125.50
    }
  ]
}
```

#### Collect Price Data
```bash
POST /api/collect-price-data
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "use_mock": true
}
```

**Collect All Instruments:**
```json
{
  "timeframe": "1h",
  "use_mock": true
}
```

#### Get Latest Price
```bash
GET /api/latest-price/<symbol>?timeframe=1h
```

## 🎨 Chart Component

### Historical Chart (New!)
Navigate to **📦 Historical** to view the new chart.

**Features:**
- 📊 Candlestick chart with volume bars
- 🎯 Multi-instrument selection
- ⏱️ Multi-timeframe support
- 📈 Live price statistics
- 🔄 Manual refresh button
- 📱 Responsive design
- ✨ Premium animations

**Data Stats Display:**
- Total candles loaded
- Latest price
- Price change & percentage
- Volume

## 🔧 Service Layer

### PriceHistoryService

The `PriceHistoryService` class handles all data operations:

```python
from price_history_service import PriceHistoryService
from db import SessionLocal

session = SessionLocal()
service = PriceHistoryService(session)

# Fetch from Binance
data = service.fetch_binance_klines('BTCUSDT', '1h', 500)

# Generate mock data
mock_data = service.generate_mock_data('BTCUSDT', '1h', 500, 65000.0)

# Save to database
service.save_price_data('BTCUSDT', '1h', data)

# Retrieve from database
historical = service.get_historical_data('BTCUSDT', '1h', 500)

# Collect data for instrument
result = service.collect_data_for_instrument('BTCUSDT', '1h', use_mock=True)

# Collect for all enabled instruments
results = service.collect_all_instruments('1h', use_mock=True)
```

## 📊 Mock Data Generation

The mock data generator creates realistic price data:

**Algorithm:**
- Random walk with slight upward bias
- ±2% price changes per candle
- Realistic high/low spreads
- Random volume (10-1000 units)
- Time-based progression

**Base Prices:**
- BTCUSDT: $65,000
- ETHUSDT: $3,500
- BNBUSDT: $600
- SOLUSDT: $150
- XRPUSDT: $0.55
- Others: $1,000

## 🔄 Background Tasks

### Celery Task for Data Collection

Add to your Celery beat schedule:

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('rag_trading')

app.conf.beat_schedule = {
    'collect-hourly-data': {
        'task': 'tasks.collect_price_data_task',
        'schedule': crontab(minute=5),  # Every hour at 5 minutes past
        'args': (True, '1h'),  # use_mock=True, timeframe='1h'
    },
    'collect-daily-data': {
        'task': 'tasks.collect_price_data_task',
        'schedule': crontab(hour=0, minute=10),  # Daily at 00:10
        'args': (True, '1d'),
    },
}
```

### Manual Collection

Trigger data collection via API:

```bash
# Collect for all instruments
curl -X POST http://localhost:5000/api/collect-price-data \
  -H "Content-Type: application/json" \
  -d '{"timeframe": "1h", "use_mock": true}'

# Collect for specific instrument
curl -X POST http://localhost:5000/api/collect-price-data \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h", "use_mock": false}'
```

## 🚀 Getting Started

### 1. Initialize Database

The `PriceHistory` model will be automatically created when you run:

```bash
python app.py
```

Or manually:

```python
from db import init_db
init_db()
```

### 2. Collect Initial Data

Use the API or Python directly:

```python
from db import SessionLocal
from price_history_service import PriceHistoryService

session = SessionLocal()
service = PriceHistoryService(session)

# Collect mock data for all enabled instruments
results = service.collect_all_instruments('1h', use_mock=True)
print(f"Collected data for {len(results)} instruments")

session.close()
```

### 3. View in Chart

1. Start your application: `npm run dev` (client) and `python app.py` (backend)
2. Navigate to **📦 Historical** in the navigation
3. Select an instrument and timeframe
4. Click **🔄 Refresh Data** to load

## 📈 Next Steps

### Switch to Real Data

Change `use_mock=false` in API calls:

```javascript
// In HistoricalChart.jsx, line 122
const response = await fetch(
  `http://localhost:5000/api/historical-prices/${selectedSymbol}?timeframe=${timeframe}&limit=500&use_mock=false`
);
```

### Add Technical Indicators

Extend the chart with indicators:

```javascript
// Moving Average
const maSeries = chart.addLineSeries({
  color: '#2196F3',
  lineWidth: 2,
});

const maData = calculateMA(candleData, 20);
maSeries.setData(maData);
```

### Enable WebSocket Updates

Combine with LiveChart's WebSocket for real-time updates:

```javascript
const ws = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@kline_1h');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update chart with new candle
};
```

## 🎯 Use Cases

### 1. Backtesting
Use historical data to test trading strategies:
```python
# Get 1 year of daily data
historical = service.get_historical_data('BTCUSDT', '1d', 365)
# Run backtest algorithm
```

### 2. Pattern Recognition
Analyze candlestick patterns:
```python
# Fetch 4-hour data for pattern detection
data = service.get_historical_data('ETHUSDT', '4h', 200)
# Detect doji, hammer, engulfing patterns
```

### 3. Performance Analysis
Compare multiple instruments:
```python
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
for symbol in symbols:
    latest = service.get_latest_price(symbol, '1d')
    # Calculate daily returns
```

## 🛠️ Troubleshooting

### No Data Displayed

1. Check if data exists in database:
```python
from db import SessionLocal
from models import PriceHistory

session = SessionLocal()
count = session.query(PriceHistory).filter(
    PriceHistory.symbol == 'BTCUSDT'
).count()
print(f"Found {count} records")
```

2. Manually trigger data collection:
```bash
curl -X POST http://localhost:5000/api/collect-price-data \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h", "use_mock": true}'
```

### Binance API Errors

If using real data (`use_mock=false`):

1. Check Binance API status: https://www.binance.com/en/support/announcement
2. Verify symbol format (must be uppercase, no spaces)
3. Check rate limits (1200 requests/minute)
4. Use VPN if Binance is restricted in your region

### Chart Not Loading

1. Check browser console for errors
2. Verify Flask backend is running on port 5000
3. Check CORS settings in `app.py`
4. Clear browser cache and reload

## 📚 References

- **Binance API Docs**: https://binance-docs.github.io/apidocs/spot/en/
- **Lightweight Charts**: https://tradingview.github.io/lightweight-charts/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

## 💡 Tips

1. **Performance**: Use appropriate timeframes for your use case (1m for scalping, 1d for swing trading)
2. **Storage**: Monitor database size; implement data retention policy if needed
3. **Accuracy**: Mock data is for development only; use real data for production
4. **Updates**: Schedule hourly tasks for 1h data, daily tasks for 1d data
5. **Backup**: Regular database backups recommended for critical historical data

---

**Created**: October 2024  
**Version**: 1.0  
**Status**: ✅ Fully Functional with Mock Data
