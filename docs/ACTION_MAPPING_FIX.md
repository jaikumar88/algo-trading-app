# Action Type Mapping Fix

## Issue
The webhook handler was not correctly mapping "Long" and "Short" to "Buy" and "Sell" in the Signal records.

## Root Cause
While the initial extraction logic (lines 229-237) correctly mapped "long" → "BUY" and "short" → "SELL", there was a secondary parsing section (lines 402-410) that attempted to extract the action from the summary text after Gemini processing. This secondary section only checked for "buy" and "sell", not "long" and "short".

## Solution
Updated the summary parsing logic to also check for "long" and "short":

```python
if not action:
    summary_lower = summary.lower()
    if 'buy' in summary_lower or 'long' in summary_lower:
        action = 'BUY'
    elif 'sell' in summary_lower or 'short' in summary_lower:
        action = 'SELL'
```

## Action Mapping Rules
The webhook handler now correctly maps:
- **"Long" or "long" → "BUY"**
- **"Short" or "short" → "SELL"**
- **"Buy" or "buy" → "BUY"**
- **"Sell" or "sell" → "SELL"**

This mapping is applied in two places:
1. **Initial extraction** (lines 229-237): Extracts from JSON fields or combined text
2. **Summary parsing** (lines 402-410): Extracts from Gemini-processed summary if initial extraction didn't find an action

## Testing
Use the `test_action_mapping.py` script to verify the fix:

```powershell
# Make sure Flask backend is running first
python test_action_mapping.py
```

Then check the database:
```sql
SELECT id, source, symbol, action, price, created_at 
FROM signals 
ORDER BY created_at DESC 
LIMIT 10;
```

You should see:
- Webhooks with "Long" → action = "BUY"
- Webhooks with "Short" → action = "SELL"

## Verification
1. Send test webhook with "Long": 
   ```json
   {"action": "Long", "symbol": "BTCUSDT", "price": 50000}
   ```
   Expected: Signal.action = "BUY"

2. Send test webhook with "Short":
   ```json
   {"action": "Short", "symbol": "ETHUSDT", "price": 3000}
   ```
   Expected: Signal.action = "SELL"

3. Check text parsing:
   ```json
   {"text": "Going long on BTCUSDT at 50000"}
   ```
   Expected: Signal.action = "BUY"

## Files Modified
- `app.py`: Updated summary parsing logic (lines 402-410)

## Related Files
- `test_action_mapping.py`: Test script to verify the fix
- `models.py`: Signal model with action field
- `db.py`: Database connection and init
