# ✅ Opposite Trade Closing Feature - IMPLEMENTED

## Feature Summary
Automatically close existing open trades when an opposite signal comes for the same instrument, book profit/loss, and open a new trade with the new signal.

## How It Works

### Scenario 1: BUY Signal with Open SELL Trade
1. **Open SELL trade** exists for BTCUSDT at $52,000
2. **BUY signal** arrives at $51,000
3. **System automatically:**
   - ✅ Closes the SELL trade at $51,000
   - ✅ Books profit: ($52,000 - $51,000) × 100 = $100,000 profit
   - ✅ Opens new BUY trade at $51,000

### Scenario 2: SELL Signal with Open BUY Trade
1. **Open BUY trade** exists for BTCUSDT at $50,000
2. **SELL signal** arrives at $52,000
3. **System automatically:**
   - ✅ Closes the BUY trade at $52,000
   - ✅ Books profit: ($52,000 - $50,000) × 100 = $200,000 profit
   - ✅ Opens new SELL trade at $52,000

### Scenario 3: Same Direction Signal
1. **Open BUY trade** exists for BTCUSDT at $50,000
2. **Another BUY signal** arrives at $51,000
3. **System automatically:**
   - ✅ Closes the previous BUY trade at $51,000
   - ✅ Books profit: ($51,000 - $50,000) × 100 = $100,000 profit
   - ✅ Opens new BUY trade at $51,000

## Profit/Loss Calculation

### BUY Trade P&L
```
P&L = (Close Price - Open Price) × Quantity
```

**Example:**
- Open BUY at $50,000
- Close at $52,000
- P&L = ($52,000 - $50,000) × 100 = **$200,000 profit** ✅

### SELL Trade P&L
```
P&L = (Open Price - Close Price) × Quantity
```

**Example:**
- Open SELL at $52,000
- Close at $51,000
- P&L = ($52,000 - $51,000) × 100 = **$100,000 profit** ✅

## Test Results

```
================================================================================
Testing Opposite Trade Closing Logic
================================================================================

📊 Scenario 1: Open BUY → SELL signal comes → Close BUY, Open SELL
--------------------------------------------------------------------------------

1️⃣ Opening BUY trade at price 50000...
   ✓ Opened: BUY trade (ID: 13)
   ✓ Closed: 0 trades
   ✓ Open trades: 1 (BUY)

2️⃣ SELL signal comes at price 52000...
   ✓ Closed: 1 trade(s)
      - BUY trade (ID: 13)
        Open: 50000.00, Close: 52000
        P&L: 200000.00 ✅
   ✓ Opened: SELL trade (ID: 14)
   ✓ Open trades: 1 (SELL)

📊 Scenario 2: Open SELL → BUY signal comes → Close SELL, Open BUY
--------------------------------------------------------------------------------

3️⃣ BUY signal comes at price 51000...
   ✓ Closed: 1 trade(s)
      - SELL trade (ID: 14)
        Open: 52000.00, Close: 51000
        P&L: 100000.00 ✅
   ✓ Opened: BUY trade (ID: 15)

4️⃣ Another BUY signal comes at price 51500...
   ✓ Closed: 1 trade(s)
      - BUY trade (ID: 15)
        Open: 51000.00, Close: 51500
        P&L: 50000.00 ✅
   ✓ Opened: BUY trade (ID: 16)

📈 Final Summary
--------------------------------------------------------------------------------
Total P&L: 350000.00 ✅
✅ P&L calculation is CORRECT!
```

## Technical Implementation

### TradingManager Logic
The `TradingManager.handle_signal()` method now:

1. **Identifies opposite trades**: Finds all open trades for the same symbol with opposite action
2. **Closes opposite trades**: Sets close_price, close_time, status='CLOSED'
3. **Books P&L**: Calculates profit/loss based on open/close prices
4. **Closes same direction trades**: Prevents multiple open positions in same direction
5. **Opens new trade**: Creates new trade with the incoming signal
6. **Returns result**: Dictionary with closed trades list and newly opened trade

### Key Features
- ✅ **Atomic transactions**: All operations in single database transaction
- ✅ **Accurate P&L**: Correct calculation for both BUY and SELL trades
- ✅ **No duplicate positions**: Automatically closes same-direction trades
- ✅ **Error handling**: Rollback on failure, safe session management
- ✅ **Comprehensive logging**: Returns detailed results with message

## Usage Examples

### Example 1: Webhook Triggers Opposite Trade Close

**Webhook Payload:**
```json
POST /webhook
{
  "action": "Long",
  "symbol": "BTCUSDT",
  "price": 50000
}
```

**If open SELL trade exists:**
```
✓ Closed SELL trade at $50,000
✓ Booked P&L: $X
✓ Opened new BUY trade at $50,000
```

### Example 2: Manual Signal via API

```python
from trading import TradingManager
from decimal import Decimal

tm = TradingManager()

# Send BUY signal
result = tm.handle_signal(
    user_id=None,
    symbol="ETHUSDT",
    side="BUY",
    price=Decimal("3000")
)

print(f"Closed: {len(result['closed'])} trades")
print(f"Opened: {result['opened'].action} trade")
print(f"Message: {result['message']}")
```

**Output:**
```
Closed: 1 trades
Opened: BUY trade
Message: Closed 1 opposite trade(s), opened new BUY trade
```

## Database Schema

### Trade Model
```python
class Trade(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String)           # 'BUY' or 'SELL'
    symbol = Column(String)           # e.g. 'BTCUSDT'
    quantity = Column(Numeric)        # Fixed at 100
    open_price = Column(Numeric)      # Entry price
    open_time = Column(DateTime)      # Entry timestamp
    close_price = Column(Numeric)     # Exit price
    close_time = Column(DateTime)     # Exit timestamp
    status = Column(String)           # 'OPEN' or 'CLOSED'
    total_cost = Column(Numeric)      # open_price × quantity
    profit_loss = Column(Numeric)     # Calculated P&L
```

### Sample Data
```sql
SELECT id, symbol, action, status, open_price, close_price, profit_loss
FROM trades
ORDER BY id DESC;

ID  Symbol    Action  Status   Open Price  Close Price  P&L
--  --------  ------  -------  ----------  -----------  ----------
16  TESTBTC   BUY     OPEN     51500       NULL         NULL
15  TESTBTC   BUY     CLOSED   51000       51500        50000.00
14  TESTBTC   SELL    CLOSED   52000       51000        100000.00
13  TESTBTC   BUY     CLOSED   50000       52000        200000.00
```

## API Response Format

### Success Response
```json
{
  "closed": [
    {
      "id": 13,
      "action": "BUY",
      "symbol": "BTCUSDT",
      "open_price": 50000,
      "close_price": 52000,
      "profit_loss": 200000,
      "status": "CLOSED"
    }
  ],
  "opened": {
    "id": 14,
    "action": "SELL",
    "symbol": "BTCUSDT",
    "open_price": 52000,
    "status": "OPEN"
  },
  "message": "Closed 1 opposite trade(s), opened new SELL trade"
}
```

## Testing

### Run Comprehensive Test
```powershell
python test_opposite_trades.py
```

### Verify in Database
```powershell
python check_signals.py
```

Or directly:
```sql
-- Check open trades
SELECT * FROM trades WHERE status = 'OPEN';

-- Check closed trades with P&L
SELECT symbol, action, open_price, close_price, profit_loss, status
FROM trades
WHERE status = 'CLOSED'
ORDER BY close_time DESC;

-- Calculate total P&L
SELECT SUM(profit_loss) as total_pnl
FROM trades
WHERE status = 'CLOSED';
```

## Benefits

✅ **Automatic risk management**: No manual intervention needed
✅ **Instant position reversal**: React immediately to market changes
✅ **Accurate P&L tracking**: Every trade's profit/loss is recorded
✅ **Prevent conflicting positions**: Only one open trade per symbol
✅ **Transaction safety**: Atomic database operations
✅ **Audit trail**: Complete history of all trades and P&L

## Files Modified

- ✅ `trading.py` - Implemented opposite trade closing logic
- ✅ `test_opposite_trades.py` - Comprehensive test suite
- ✅ `OPPOSITE_TRADES_FEATURE.md` - This documentation

## Next Steps

The feature is **fully implemented and tested**. The system will now automatically:

1. ✅ Close opposite positions when new signals arrive
2. ✅ Book profit/loss for all closed trades
3. ✅ Open new positions with incoming signals
4. ✅ Maintain only one open position per instrument
5. ✅ Track complete trading history in database

Send any webhook signal and the system will handle position management automatically! 🚀
