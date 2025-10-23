# Delta Exchange Integration API

## Symbol Synchronization

The system can automatically sync symbols from Delta Exchange API and update the database.

### API Endpoints

All endpoints are under `/api/delta`:

#### 1. Sync All Symbols
```bash
POST /api/delta/sync/symbols
```

**Request body** (optional):
```json
{
  "auto_enable": true,
  "product_types": ["perpetual_futures", "call_options", "put_options"]
}
```

**Response**:
```json
{
  "success": true,
  "added": 10,
  "updated": 50,
  "total": 60,
  "timestamp": "2025-10-22T..."
}
```

#### 2. Sync Only Perpetual Futures (Auto-Enable)
```bash
POST /api/delta/sync/perpetuals
```

**Response**:
```json
{
  "success": true,
  "added": 5,
  "updated": 25,
  "total": 30
}
```

#### 3. Get All Products
```bash
GET /api/delta/products
```

**Response**:
```json
{
  "success": true,
  "products": [...],
  "count": 1269
}
```

#### 4. Get Delta Exchange Status
```bash
GET /api/delta/status
```

**Response**:
```json
{
  "enabled": true,
  "client_ready": true,
  "api_key_configured": true,
  "api_secret_configured": true
}
```

### Product Types

Delta Exchange has these contract types:
- `perpetual_futures` - Perpetual futures contracts
- `call_options` - Call options
- `put_options` - Put options
- `move_options` - Move options
- `futures` - Futures contracts
- `interest_rate_swaps` - Interest rate swaps
- `spreads` - Spread contracts

### Usage Examples

#### Sync perpetual futures and enable them automatically
```bash
curl -X POST http://localhost:5000/api/delta/sync/perpetuals
```

#### Sync all futures (perpetual + dated)
```bash
curl -X POST http://localhost:5000/api/delta/sync/symbols \
  -H "Content-Type: application/json" \
  -d '{
    "auto_enable": false,
    "product_types": ["perpetual_futures", "futures"]
  }'
```

#### Get Delta Exchange integration status
```bash
curl http://localhost:5000/api/delta/status
```

### Automated Daily Sync

You can set up a scheduled task to run daily sync:

**Windows Task Scheduler**:
```powershell
# Create daily task at 2 AM
$action = New-ScheduledTaskAction -Execute "curl.exe" -Argument "-X POST http://localhost:5000/api/delta/sync/perpetuals"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DeltaExchangeSync"
```

**Linux Cron**:
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * curl -X POST http://localhost:5000/api/delta/sync/perpetuals
```

### Manual Sync via Python

```python
from src.services.delta_exchange_service import get_delta_trader

trader = get_delta_trader()

# Sync only perpetual futures
result = trader.sync_symbols_to_db(
    auto_enable=True,
    product_types=['perpetual_futures']
)

print(f"Added: {result['added']}, Updated: {result['updated']}")
```

### Notes

- The sync process fetches ALL products from Delta Exchange (can be 1000+ products)
- Products are paginated automatically (100 per page)
- Existing enabled symbols will remain enabled
- New perpetual futures can be auto-enabled with `auto_enable=True`
- Database stores: symbol, name, contract_type, base_currency, quote_currency, enabled status
