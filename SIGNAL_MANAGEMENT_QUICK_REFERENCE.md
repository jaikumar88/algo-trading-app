# 🎯 Signal Management Quick Reference

## Quick Start

### 1. Check Signal Statistics
```bash
GET http://localhost:5000/api/trading/signals/stats
```

### 2. Review Pending Signals
```bash
GET http://localhost:5000/api/trading/signals?status=PENDING&limit=20
```

### 3. Reject False Signal
```bash
POST http://localhost:5000/api/trading/signals/16/reject
Content-Type: application/json

{
  "reason": "False breakout",
  "rejected_by": "trader_john"
}
```

### 4. Validate Good Signal
```bash
POST http://localhost:5000/api/trading/signals/16/validate
Content-Type: application/json

{
  "is_valid": true,
  "confidence_score": 85,
  "notes": "Confirmed with volume",
  "validated_by": "trader_john"
}
```

### 5. Execute Validated Signal
```bash
POST http://localhost:5000/api/trading/signals/16/execute
Content-Type: application/json

{
  "quantity": 100.0
}
```

---

## Signal Status Flow

```
PENDING → VALIDATED → EXECUTED
       ↘ FALSE
       ↘ REJECTED
```

---

## All Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/trading/signals` | List all signals (with filters) |
| GET | `/api/trading/signals/:id` | Get single signal |
| POST | `/api/trading/signals/:id/validate` | Mark signal valid/false |
| POST | `/api/trading/signals/:id/reject` | Quick reject signal |
| POST | `/api/trading/signals/:id/execute` | Place trade from signal |
| GET | `/api/trading/signals/stats` | Get accuracy statistics |
| POST | `/api/trading/signals/bulk-validate` | Validate multiple signals |

---

## Filter Parameters

**GET /api/trading/signals**

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `symbol` | string | `BTCUSDT` | Filter by trading symbol |
| `action` | string | `BUY` or `SELL` | Filter by trade direction |
| `source` | string | `webhook` | Filter by signal source |
| `status` | string | `PENDING` | Filter by validation status |
| `limit` | number | `50` | Number of results |
| `offset` | number | `0` | Pagination offset |

---

## Validation Request Body

**POST /api/trading/signals/:id/validate**

```json
{
  "is_valid": true,           // Required: true = good, false = false signal
  "notes": "Your reason",     // Optional: Why validated/rejected
  "validated_by": "username", // Optional: Who validated
  "confidence_score": 85      // Optional: 0-100 confidence level
}
```

---

## Rejection Request Body

**POST /api/trading/signals/:id/reject**

```json
{
  "reason": "Why rejected",   // Required: Reason for rejection
  "rejected_by": "username"   // Optional: Who rejected
}
```

---

## Execute Request Body

**POST /api/trading/signals/:id/execute**

```json
{
  "quantity": 100.0           // Required: Trade quantity
}
```

---

## Bulk Validate Request Body

**POST /api/trading/signals/bulk-validate**

```json
{
  "signal_ids": [1, 2, 3],    // Required: Array of signal IDs
  "is_valid": false,          // Required: Mark all as valid/false
  "notes": "Batch reason",    // Optional: Reason for all
  "validated_by": "admin"     // Optional: Who validated
}
```

---

## Example Responses

### Signal Statistics Response
```json
{
  "stats": {
    "total": 100,
    "pending": 20,
    "validated": 45,
    "executed": 30,
    "rejected": 3,
    "false": 2
  },
  "accuracy": {
    "validation_accuracy": "90.00%",
    "false_signal_rate": "10.00%",
    "total_validated": 50
  }
}
```

### Validation Success Response
```json
{
  "signal_id": 16,
  "status": "VALIDATED",
  "message": "Signal validated successfully",
  "validation_notes": "Confirmed with volume",
  "validated_by": "trader_john"
}
```

### Execute Success Response
```json
{
  "signal_id": 16,
  "trade_id": 25,
  "status": "EXECUTED",
  "message": "Signal executed successfully",
  "trade": {
    "id": 25,
    "symbol": "BTCUSDT",
    "action": "BUY",
    "quantity": 100.0,
    "open_price": 50000.00,
    "status": "OPEN"
  }
}
```

---

## Common Workflows

### Daily Signal Review Workflow
1. Get pending signals: `GET /api/trading/signals?status=PENDING`
2. Review each signal
3. Validate good ones: `POST /signals/:id/validate`
4. Reject false ones: `POST /signals/:id/reject`
5. Execute validated ones: `POST /signals/:id/execute`
6. Check stats: `GET /api/trading/signals/stats`

### Automated Filter Workflow
1. Receive signal from webhook
2. Check price spike, volume, liquidity
3. Auto-validate or reject: `POST /signals/:id/validate`
4. If validated and high confidence: `POST /signals/:id/execute`
5. Log for review

### Batch Cleanup Workflow
1. Identify date range with issues
2. Get signals: `GET /signals?start_date=X&end_date=Y`
3. Review signal IDs
4. Bulk reject: `POST /signals/bulk-validate`
5. Verify: `GET /signals/stats`

---

## Testing in Postman

1. Import collection: `postman_collection.json`
2. Set variables:
   - `baseUrl`: `http://localhost:5000`
   - `apiPrefix`: `/api`
3. Navigate to **📡 Signals** folder
4. Test endpoints in order:
   - Get All Signals
   - Get Signal Statistics
   - Validate Signal
   - Reject False Signal
   - Execute Signal
   - Bulk Validate Signals

---

## Troubleshooting

**Error: "Signal already validated/rejected"**
- Solution: Check signal status first with GET /signals/:id

**Error: "Signal not found"**
- Solution: Verify signal_id exists with GET /signals

**Error: "Cannot execute rejected signal"**
- Solution: Only PENDING or VALIDATED signals can be executed

**Error: "Trade creation failed"**
- Solution: Check signal has required fields (symbol, action, price)

---

## Best Practices

✅ **Always provide validation notes** - Helps track decision making  
✅ **Use confidence scores** - Filter signals by quality  
✅ **Link signals to trades** - Use execute endpoint, not manual  
✅ **Review stats regularly** - Monitor signal quality trends  
✅ **Validate before execution** - Never auto-execute without validation  

❌ **Don't execute rejected signals** - System prevents this  
❌ **Don't skip validation notes** - Lost context  
❌ **Don't create trades manually** - Breaks signal→trade linkage  

---

## Database Schema

**New Signal Columns:**
- `status` - VARCHAR (PENDING, VALIDATED, EXECUTED, REJECTED, FALSE)
- `validated_by` - VARCHAR (user/system identifier)
- `validation_notes` - TEXT (reason for validation/rejection)
- `confidence_score` - FLOAT (0-100)
- `executed_at` - TIMESTAMP
- `trade_id` - INTEGER (FK to trades.id)
- `updated_at` - TIMESTAMP (auto-updated)

---

## Resources

- **Complete Guide**: `docs/FALSE_SIGNAL_MANAGEMENT.md`
- **API Documentation**: `docs/TRADING_CHART_API.md`
- **Postman Collection**: `postman_collection.json`
- **Testing Guide**: `POSTMAN_TESTING_GUIDE.md`
- **Migration Script**: `migrations/run_migration.py`

---

**Updated:** October 17, 2025  
**Version:** 1.0.0
