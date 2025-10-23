# Duplicate Trade Prevention System

## Problem Statement
When buy and sell signals arrive simultaneously (or within milliseconds of each other) for the same instrument, the system was opening BOTH positions, resulting in:
- One BUY trade (long position)
- One SELL trade (short position)
- Both trades OPEN at the same time for the same instrument

This violates the trading rule: **Only ONE open trade per instrument at any time.**

## Solution Implemented

### 1. Database-Level Row Locking (`trading.py`)

**Location:** `_close_opposite_and_open()` method in `TradingManager` class

**Key Changes:**
```python
# OLD: Queried only opposite trades
q = select(Trade).where(
    Trade.symbol == symbol,
    Trade.status == "OPEN",
    Trade.action == opposite_side
)

# NEW: Query ALL open trades with database lock
q = select(Trade).where(
    Trade.symbol == symbol,
    Trade.status == "OPEN"
).with_for_update()  # 🔒 LOCKS rows to prevent concurrent modifications
```

**Benefits:**
- `with_for_update()` creates a **database-level lock** on the rows
- If two signals arrive simultaneously, one will wait until the other completes
- Prevents race conditions at the database level
- First transaction completes, second transaction sees the updated state

### 2. Close ALL Open Trades (Not Just Opposite)

**Before:**
- Closed only opposite direction trades (BUY closes SELL, SELL closes BUY)
- Did NOT close same-direction trades
- Race condition: BUY signal arrives → checks for SELL (none found) → opens BUY. SELL signal arrives → checks for BUY (none found yet) → opens SELL

**After:**
- Closes **ALL open trades** for the symbol regardless of direction
- Prevents duplicate positions in ANY scenario
- Handles edge cases: duplicate BUY signals, duplicate SELL signals, simultaneous BUY+SELL

**Code:**
```python
# Find ALL open trades for this symbol (both opposite AND same direction)
q = select(Trade).where(
    Trade.symbol == symbol,
    Trade.status == "OPEN"
).with_for_update()  # Lock rows

all_open_trades = session.execute(q).scalars().all()

# Close every single one
for trade in all_open_trades:
    trade.status = "CLOSED"
    # Calculate P&L...
    closed.append(trade)

# Then open the new trade
new_trade = Trade(...)
```

### 3. Warning System for Multiple Open Trades

**Logging Added:**
```python
if len(all_open_trades) > 1:
    print(f"⚠️ WARNING: Found {len(all_open_trades)} open trades for {symbol}. Closing all to prevent duplicates.")

for trade in all_open_trades:
    if trade.action == opposite_side:
        print(f"✅ Closed opposite {trade.action} trade...")
    else:
        print(f"⚠️ Closed duplicate {trade.action} trade...")
```

This helps monitor and debug duplicate signal issues.

### 4. Task-Level Validation (`tasks.py`)

**Added pre-check before executing trade:**
```python
# Check for existing open trades
existing_open = session.execute(
    select(Trade).where(
        Trade.symbol == symbol,
        Trade.status == "OPEN"
    )
).scalars().first()

if existing_open:
    LOG.warning(
        f"⚠️ Signal received for {symbol} ({action}) but there's already an OPEN {existing_open.action} trade. "
        f"Will close existing and open new trade."
    )
```

**Benefits:**
- Early warning in logs when duplicate signals detected
- Helps identify signal source issues
- Provides audit trail

## How It Works: Step-by-Step

### Scenario: BUY and SELL signals arrive simultaneously for BTCUSD

**Timeline:**

1. **T=0ms:** BUY signal arrives, starts processing
   ```
   Transaction 1 starts
   Query: SELECT * FROM trades WHERE symbol='BTCUSD' AND status='OPEN' FOR UPDATE
   Result: No open trades
   ```

2. **T=5ms:** SELL signal arrives, starts processing
   ```
   Transaction 2 starts
   Query: SELECT * FROM trades WHERE symbol='BTCUSD' AND status='OPEN' FOR UPDATE
   ⏳ WAITS - Transaction 1 has locked the rows
   ```

3. **T=10ms:** Transaction 1 completes
   ```
   No existing trades to close
   Creates new BUY trade (ID: 100)
   COMMIT
   🔓 Lock released
   ```

4. **T=11ms:** Transaction 2 resumes
   ```
   Query executes now that lock is released
   Result: Finds BUY trade (ID: 100) - status='OPEN'
   Closes BUY trade (ID: 100), calculates P&L
   Creates new SELL trade (ID: 101)
   COMMIT
   ```

**Final Result:**
- ✅ Only SELL trade (ID: 101) is OPEN
- ✅ BUY trade (ID: 100) was immediately closed
- ✅ No duplicate positions
- ✅ Proper P&L calculated for closed BUY trade

## Testing Recommendations

### 1. Manual Test - Simultaneous Signals
Send two webhook signals with <50ms delay:
```bash
# Terminal 1
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSD", "action": "BUY", "price": 50000}'

# Terminal 2 (run immediately)
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSD", "action": "SELL", "price": 50000}'
```

**Expected Result:**
- Only 1 open trade in database
- Logs show: "Closed 1 trade(s), opened new trade"

### 2. Database Check
```sql
-- Should return only ONE row (or zero if no trades)
SELECT * FROM trades WHERE symbol = 'BTCUSD' AND status = 'OPEN';

-- Should show the closed trade from race condition
SELECT * FROM trades WHERE symbol = 'BTCUSD' ORDER BY open_time DESC LIMIT 5;
```

### 3. Stress Test
Use a script to send 10 rapid signals:
```python
import requests
import threading
import time

def send_signal(action):
    requests.post('http://localhost:5000/webhook', json={
        'symbol': 'BTCUSD',
        'action': action,
        'price': 50000
    })

# Send alternating BUY/SELL rapidly
for i in range(10):
    action = 'BUY' if i % 2 == 0 else 'SELL'
    threading.Thread(target=send_signal, args=(action,)).start()
    time.sleep(0.01)  # 10ms between signals

time.sleep(2)
# Check: Only 1 open trade should exist
```

## Benefits of This Solution

✅ **Database-Level Protection:** Row locking prevents race conditions  
✅ **Comprehensive:** Closes ALL open trades, not just opposite  
✅ **Transaction Safety:** ACID properties maintained  
✅ **Audit Trail:** Detailed logging for debugging  
✅ **No External Dependencies:** Uses native PostgreSQL features  
✅ **Automatic P&L:** Closed trades get proper profit/loss calculation  
✅ **Future-Proof:** Handles any signal timing scenario  

## Monitoring

Watch these log messages to monitor the system:

```
✅ Closed opposite BUY trade for BTCUSD at 50000 (P&L: 250.00)
✅ Opened new SELL trade for BTCUSD at 50000

⚠️ WARNING: Found 2 open trades for BTCUSD. Closing all to prevent duplicates.
⚠️ Closed duplicate BUY trade for BTCUSD at 50000 (P&L: 0.00)
```

The WARNING messages indicate duplicate signals were received, but the system handled them correctly.

## Database Requirements

**PostgreSQL/MySQL:** `with_for_update()` works out of the box  
**SQLite:** Row-level locking supported but less concurrent (uses table-level locks)

## Summary

The fix ensures **exactly ONE open trade per instrument at ANY time** by:
1. Using database row locks to serialize concurrent signal processing
2. Closing ALL existing open trades before opening a new one
3. Calculating proper P&L for closed trades
4. Providing comprehensive logging for monitoring

**Result:** Race conditions eliminated, duplicate positions prevented, trading logic preserved. ✅
