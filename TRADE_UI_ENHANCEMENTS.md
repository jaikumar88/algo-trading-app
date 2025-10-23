# Trade History UI Enhancements

## Overview
Enhanced the Trade History page in the React client to display Stop Loss, Take Profit, and Unrealized P&L for all trades (especially open positions).

## Changes Made

### 1. Added New Table Columns
**File:** `client/src/features/trading/components/TradeHistory.jsx`

Added two new columns to the trade history table:
- **Stop Loss**: Displays in red when set, shows "Not Set" when missing
- **Target Price** (Take Profit): Displays in green when set, shows "Not Set" when missing

### 2. Enhanced P&L Display
- **Closed Trades**: Shows realized P&L from database
- **Open Trades**: Calculates and displays unrealized P&L in real-time
  - Formula: `(Current Price - Entry Price) × Quantity × Direction`
  - Shows percentage gain/loss below dollar amount
  - Updates every 3 seconds with live prices

### 3. Real-Time Price Updates
Added price polling functionality:
```javascript
// Fetches current prices from /api/trading/prices every 3 seconds
const fetchCurrentPrices = async () => {
  const response = await axios.get('/api/trading/prices');
  setCurrentPrices(response.data.prices);
};
```

### 4. Risk Management Stats Card
Added a new statistics card showing:
- **SL Set**: How many open trades have stop loss configured (e.g., "5/10")
- **TP Set**: How many open trades have take profit configured (e.g., "7/10")
- Only appears when there are open positions

### 5. Enhanced CSV Export
Updated export to include new fields:
- Stop Loss
- Take Profit
- Unrealized P&L (for open trades)

## Visual Improvements

### Color Coding
- **Stop Loss**: Bold red text (`#dc3545`)
- **Take Profit**: Bold green text (`#28a745`)
- **Profit P&L**: Green color
- **Loss P&L**: Red color
- **Not Set**: Gray muted text (`#999`)

### Layout Updates
- P&L now displays on two lines:
  - Line 1: Dollar amount (bold)
  - Line 2: Percentage (for open trades)

## API Integration

### Existing Endpoints Used
1. **GET `/api/trading/trades`** - Returns trade data with:
   - `stop_loss`
   - `take_profit`
   - `profit_loss` (for closed trades)
   - All other trade fields

2. **GET `/api/trading/prices`** - Returns current market prices:
   ```json
   {
     "prices": {
       "BTCUSD": 67234.50,
       "ETHUSD": 3745.59
     }
   }
   ```

## How It Works

### For Open Trades
1. Fetch trade data from `/api/trading/trades?status=OPEN`
2. Poll `/api/trading/prices` every 3 seconds
3. Calculate unrealized P&L:
   ```javascript
   const multiplier = trade.action === 'BUY' ? 1 : -1;
   const unrealizedPnL = multiplier * (currentPrice - openPrice) * quantity;
   const pnlPercent = (unrealizedPnL / (openPrice * quantity)) * 100;
   ```
4. Display SL/TP values from trade record
5. Show risk management stats

### For Closed Trades
1. Display final P&L from database
2. Show SL/TP values (historical data)
3. Mark as "Not Set" if they were never configured

## Testing

### To Test the Changes:
1. Navigate to the React client (usually `http://localhost:5173` or similar)
2. Open the "Trade History" page
3. For open trades, verify:
   - Stop Loss column shows values or "Not Set"
   - Target Price column shows values or "Not Set"
   - P&L shows unrealized amount with percentage
   - Risk Management card appears at top
4. Watch P&L update in real-time (every 3 seconds)
5. Test CSV export includes new columns

### Example Display

**Open Trade:**
| Stop Loss | Target Price | P&L |
|-----------|--------------|-----|
| **$3,700.00** | **$3,800.00** | **$456.78**<br/>(12.34%) |

**Trade Without SL/TP:**
| Stop Loss | Target Price | P&L |
|-----------|--------------|-----|
| Not Set | Not Set | **-$123.45**<br/>(-3.45%) |

## Files Modified
- `client/src/features/trading/components/TradeHistory.jsx`

## Dependencies
- React hooks: `useState`, `useEffect`
- axios for API calls
- Existing backend API endpoints (no changes needed)

## Notes
- Price updates occur every 3 seconds to balance real-time data with API load
- Unrealized P&L calculation uses mark price (current market price)
- SL/TP values are stored in the database and don't require calculation
- The backend API already provides all necessary fields
