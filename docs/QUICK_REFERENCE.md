# 🔄 Quick Reference: Opposite Trade Closing

## What Happens When?

| Current Open Position | Signal Arrives | System Action |
|----------------------|----------------|---------------|
| **SELL @ $52k** | BUY @ $51k | Close SELL (profit $100k) → Open BUY @ $51k |
| **BUY @ $50k** | SELL @ $52k | Close BUY (profit $200k) → Open SELL @ $52k |
| **BUY @ $50k** | BUY @ $51k | Close BUY (profit $100k) → Open BUY @ $51k |
| **SELL @ $52k** | SELL @ $51k | Close SELL (loss $100k) → Open SELL @ $51k |
| **No open trade** | BUY @ $50k | Open BUY @ $50k |
| **No open trade** | SELL @ $52k | Open SELL @ $52k |

## P&L Formula Quick Reference

### BUY Trade
```
Profit/Loss = (Close Price - Open Price) × Quantity
```

### SELL Trade
```
Profit/Loss = (Open Price - Close Price) × Quantity
```

### Examples
```
BUY:  Open $50k → Close $52k = ($52k - $50k) × 100 = $200k profit ✅
SELL: Open $52k → Close $51k = ($52k - $51k) × 100 = $100k profit ✅
BUY:  Open $52k → Close $50k = ($50k - $52k) × 100 = -$200k loss ❌
SELL: Open $51k → Close $52k = ($51k - $52k) × 100 = -$100k loss ❌
```

## Webhook Examples

### Close SELL, Open BUY
```json
POST /webhook
{
  "action": "Long",
  "symbol": "BTCUSDT",
  "price": 51000
}
```
Result: Any open SELL trades closed → New BUY opened

### Close BUY, Open SELL
```json
POST /webhook
{
  "action": "Short",
  "symbol": "ETHUSDT",
  "price": 3000
}
```
Result: Any open BUY trades closed → New SELL opened

## Testing Commands

```powershell
# Test the feature
python test_opposite_trades.py

# Check database
python check_signals.py

# View trades
python -c "from db import SessionLocal; from models import Trade; s = SessionLocal(); [print(f'{t.id} {t.symbol} {t.action} {t.status} {t.profit_loss}') for t in s.query(Trade).all()]"
```

## Database Queries

```sql
-- View all trades
SELECT id, symbol, action, status, open_price, close_price, profit_loss
FROM trades ORDER BY id DESC;

-- Total P&L
SELECT SUM(profit_loss) FROM trades WHERE status = 'CLOSED';

-- Open positions
SELECT symbol, action, open_price, quantity FROM trades WHERE status = 'OPEN';

-- Closed positions (last 10)
SELECT symbol, action, open_price, close_price, profit_loss, close_time
FROM trades WHERE status = 'CLOSED' ORDER BY close_time DESC LIMIT 10;
```

## Key Benefits

✅ Automatic position reversal
✅ Accurate P&L calculation
✅ No conflicting positions
✅ Transaction-safe operations
✅ Complete audit trail

## Feature Status

🟢 **FULLY OPERATIONAL**

The system automatically handles:
- ✅ Opposite trade detection
- ✅ Position closing
- ✅ P&L calculation
- ✅ New position opening
- ✅ Database persistence

## Support

- 📖 Full documentation: `OPPOSITE_TRADES_FEATURE.md`
- 🧪 Test suite: `test_opposite_trades.py`
- 💾 Database model: `models.py` (Trade class)
- ⚙️ Core logic: `trading.py` (TradingManager class)
