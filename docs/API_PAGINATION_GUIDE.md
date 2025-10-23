# API Pagination Guide

## Updated Endpoints with Flexible Pagination

### `/api/trading/trades` - Now supports both pagination styles!

#### Method 1: Page-based Pagination (Recommended for Frontend)
```
GET /api/trading/trades?page=1&limit=50
GET /api/trading/trades?page=2&limit=50
```

#### Method 2: Offset-based Pagination
```
GET /api/trading/trades?offset=0&limit=50
GET /api/trading/trades?offset=50&limit=50
```

---

## Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `limit` | integer | 100 | Items per page |
| `offset` | integer | 0 | Number of items to skip (alternative to page) |
| `status` | string | - | Filter: "OPEN" or "CLOSED" |
| `symbol` | string | - | Filter: e.g., "ETHUSD", "BTCUSDT" |

---

## Response Format

```json
{
  "trades": [
    {
      "id": 18,
      "symbol": "ETHUSD",
      "action": "BUY",
      "quantity": 100.0,
      "open_price": 3774.4,
      "open_time": "2025-10-17T08:20:01.131211-05:00",
      "close_price": null,
      "close_time": null,
      "status": "OPEN",
      "profit_loss": null,
      "allocated_fund": null,
      "risk_amount": null,
      "stop_loss_triggered": false,
      "closed_by_user": false
    }
  ],
  "summary": {
    "total": 18,
    "open": 1,
    "closed": 17,
    "total_pnl": -13793.0
  },
  "pagination": {
    "page": 1,
    "limit": 50,
    "offset": 0,
    "total": 18,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

## Pagination Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `page` | integer | Current page number |
| `limit` | integer | Items per page |
| `offset` | integer | Offset used in query |
| `total` | integer | Total number of trades |
| `total_pages` | integer | Total number of pages |
| `has_next` | boolean | Whether next page exists |
| `has_prev` | boolean | Whether previous page exists |

---

## Example Usage

### Get first page (50 items)
```bash
curl "http://localhost:5000/api/trading/trades?page=1&limit=50"
```

### Get only open trades
```bash
curl "http://localhost:5000/api/trading/trades?status=OPEN&limit=50"
```

### Get trades for specific symbol
```bash
curl "http://localhost:5000/api/trading/trades?symbol=ETHUSD&page=1&limit=50"
```

### PowerShell Example
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/trading/trades?page=1&limit=50"
Write-Host "Total trades: $($response.summary.total)"
Write-Host "Page $($response.pagination.page) of $($response.pagination.total_pages)"
$response.trades | Format-Table id, symbol, action, status, open_price
```

---

## Client Integration Tips

### JavaScript/TypeScript
```typescript
async function getTrades(page: number = 1, limit: number = 50) {
  const response = await fetch(
    `http://localhost:5000/api/trading/trades?page=${page}&limit=${limit}`
  );
  const data = await response.json();
  
  return {
    trades: data.trades,
    totalTrades: data.summary.total,
    currentPage: data.pagination.page,
    totalPages: data.pagination.total_pages,
    hasNext: data.pagination.has_next,
    hasPrev: data.pagination.has_prev
  };
}
```

### React Hook Example
```tsx
const [trades, setTrades] = useState([]);
const [page, setPage] = useState(1);
const [pagination, setPagination] = useState(null);

useEffect(() => {
  fetch(`http://localhost:5000/api/trading/trades?page=${page}&limit=50`)
    .then(res => res.json())
    .then(data => {
      setTrades(data.trades);
      setPagination(data.pagination);
    });
}, [page]);
```

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 500 | Internal server error |

---

## Notes

- **Page numbers start at 1** (not 0)
- Default limit is 100 if not specified
- Trades are ordered by `open_time` descending (newest first)
- Both `page` and `offset` parameters work (page takes precedence)
- All numeric fields (price, quantity, P&L) are returned as floats for JSON compatibility

---

## Current Database Status

✅ **18 trades** in database:
- 1 OPEN trade
- 17 CLOSED trades
- Total P&L: -$13,793

✅ **Available symbols**: ETHUSD, BTCUSDT, ETHUSDT (and 7 more from mock data)

---

Last Updated: October 17, 2025
