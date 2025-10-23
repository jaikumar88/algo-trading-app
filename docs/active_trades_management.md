# Active Trades Management - Feature Summary

## Overview
New comprehensive trades management interface with real-time tracking, stop-loss/target price editing, and trailing stop-loss monitoring.

## Features Implemented

### 1. Active Trades Dashboard (`/trades`)
- **Real-time monitoring** of all open positions
- **Auto-refresh** every 5 seconds
- **Live P&L calculation** with percentage display
- **Position duration tracking**
- **Summary cards**: Open trades count, total position value, unrealized P&L, today's closed P&L

### 2. Stop Loss & Target Price Management
- **Edit modal** for modifying SL/TP on running trades
- **Visual indicators**:
  - Current stop loss price
  - Target price (take profit)
  - Trailing SL status (Active/Inactive badge)
- **Real-time validation** before saving
- **Instant application** to trade monitor

### 3. Trade Information Display

#### Open Trades Table Columns:
- **ID**: Trade identifier
- **Symbol**: Trading pair (e.g., BTCUSD, ETHUSD)
- **Direction**: LONG (Buy) / SHORT (Sell) with color badges
- **Quantity**: Position size
- **Entry Price**: Opening price
- **Current Price**: Live market price
- **P&L**: Real-time profit/loss with percentage
- **Stop Loss**: Current SL price or "-"
- **Target Price**: Current TP price or "-"
- **Trailing SL**: Active/Inactive status badge
- **Duration**: How long the trade has been open
- **Actions**: Edit and Close buttons

### 4. Closed Trades History
- Shows recent closed trades for the current day
- Displays: Entry, Exit, P&L, Duration, Close time
- Automatic summary calculation for daily P&L

### 5. Quick Actions
- **Edit Button**: Opens modal to modify SL/TP
- **Close Button**: Manual trade closure with confirmation
- **Refresh Button**: Force reload of all data

## API Endpoints Used

### Existing Endpoints:
```
GET  /api/trading/trades?status=OPEN      # Get open trades
GET  /api/trading/trades?status=CLOSED    # Get closed trades
PATCH /api/trading/trades/:id/modify      # Update SL/TP
POST /api/trading/trades/:id/close        # Close trade
GET  /api/trading/prices                  # Get current market prices
```

### New Endpoint Added:
```
GET /api/trading/prices
Response: {
  "prices": {
    "BTCUSD": 43250.50,
    "ETHUSD": 2280.75,
    ...
  }
}
```

## Usage Guide

### Access the Trades Page
1. Open browser: `http://localhost:5000/trades`
2. Or click "Trades" in the navigation menu

### Edit Stop Loss / Target Price
1. Click the **Edit** button (pencil icon) on any open trade
2. Modal shows current trade details
3. Enter new values:
   - **Stop Loss**: Price at which to automatically close if market moves against you
   - **Target Price**: Price at which to automatically take profit
4. Click **Save Changes**
5. Changes apply immediately to the trade monitor

### Close a Trade Manually
1. Click the **Close** button (X icon) on any open trade
2. Review trade details and estimated P&L
3. Click **Close Trade** to confirm
4. Trade closes at current market price

### Understanding Trailing Stop Loss
- **Active Badge**: Stop loss is set and will trail the price
- **Inactive Badge**: No stop loss set or it's at entry price
- Trailing SL automatically adjusts as price moves in your favor
- Protects profits while allowing upside potential

## Technical Details

### Files Created/Modified:
1. **templates/trades.html** (NEW)
   - Full-featured trades management UI
   - Bootstrap 5 responsive design
   - Real-time updates with JavaScript
   - Edit and close modals

2. **src/ui/routes.py** (MODIFIED)
   - Added `/trades` route

3. **src/api/trading.py** (MODIFIED)
   - Added `/api/trading/prices` endpoint

4. **templates/base.html** (ALREADY HAD)
   - Navigation already included trades link

### Trade Model Fields Used:
```python
- id: Trade identifier
- symbol: Trading pair
- action: BUY or SELL
- quantity: Position size
- open_price: Entry price
- close_price: Exit price (if closed)
- status: OPEN or CLOSED
- stop_loss: Stop loss price
- take_profit: Target price (take profit)
- profit_loss: Realized P&L
- open_time: When trade opened
- close_time: When trade closed
```

## Performance Analytics Integration

This trades page complements the performance analytics system:
- **Real-time**: Trades page shows current active positions
- **Historical**: Performance analytics analyzes closed trades
- **Combined**: Use both for complete trading oversight

### Workflow:
1. **Monitor** active trades on `/trades` page
2. **Adjust** SL/TP based on market conditions
3. **Review** performance metrics on `/api/performance/dashboard`
4. **Improve** based on suggestions from analytics

## Best Practices

### Setting Stop Loss:
- **Long trades**: Set SL below entry (e.g., 2-3% below)
- **Short trades**: Set SL above entry (e.g., 2-3% above)
- Use risk/reward ratio of at least 1:2

### Setting Target Price:
- Calculate based on support/resistance levels
- Use Fibonacci extensions for targets
- Consider taking partial profits at intermediate levels

### Trailing Stop Loss:
- Allow trailing SL to activate after trade is profitable
- Don't set trailing SL too tight (allow for normal volatility)
- Adjust based on symbol volatility

## Troubleshooting

### No trades showing:
- Check if any trades are actually open in database
- Verify trade monitor service is running
- Check console for API errors

### Prices not updating:
- Verify Delta Exchange API is responding
- Check `/api/trading/prices` endpoint directly
- Ensure symbols are enabled in database

### Can't edit SL/TP:
- Verify trade is still OPEN status
- Check browser console for errors
- Ensure `/api/trading/trades/:id/modify` endpoint is accessible

## Future Enhancements

Potential improvements:
1. **Price alerts**: Set custom price alerts for symbols
2. **Advanced charting**: Integrate TradingView charts
3. **Batch operations**: Close multiple trades at once
4. **Trade notes**: Add personal notes to trades
5. **Export history**: Download trade history as CSV/Excel
6. **Mobile optimization**: Improved mobile interface
7. **WebSocket prices**: Real-time price streaming
8. **Risk calculator**: Calculate position size based on risk

## Summary

The active trades management interface provides:
- ✅ **Real-time monitoring** of all open positions
- ✅ **Easy editing** of stop loss and target prices
- ✅ **Visual indicators** for trailing SL status
- ✅ **Quick actions** for closing trades
- ✅ **Historical view** of closed trades
- ✅ **Auto-refresh** to stay updated
- ✅ **Responsive design** for all devices

Access it at: **http://localhost:5000/trades**
