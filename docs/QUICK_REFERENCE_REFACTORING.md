# 🚀 Quick Reference Card - Project Refactoring

## One-Command Migration
```bash
python migrate_to_new_structure.py
```

## Import Changes Quick Reference

### Backend Imports

| Old | New |
|-----|-----|
| `from db import SessionLocal` | `from database.session import SessionLocal` |
| `from models import Trade` | `from models.trade import Trade` |
| `from trading import TradingManager` | `from services.trading_service import TradingService` |
| `from price_history_service import PriceHistoryService` | `from services.price_service import PriceHistoryService` |
| `from telegram_bot import *` | `from services.telegram_service import *` |
| `from openai_client import chat_completion` | `from services.llm_service import chat_completion` |

### Frontend Imports

| Old | New |
|-----|-----|
| `'./components/Dashboard'` | `'./features/dashboard/components/Dashboard'` |
| `'./components/LiveChart'` | `'./features/charts/components/LiveChart'` |
| `'./components/Signals'` | `'./features/signals/components/Signals'` |
| `'./Layout'` | `'./shared/layouts/Layout'` |
| `'./api'` | `'./services/api'` |

## File Locations

### Backend Structure
```
backend/src/
├── api/          → All blueprints (trading.py, signals.py, etc.)
├── services/     → Business logic (trading_service.py, etc.)
├── models/       → Database models (trade.py, signal.py, etc.)
├── database/     → DB setup (session.py, migrations/)
├── tasks/        → Celery tasks (signal_tasks.py, etc.)
├── utils/        → Helpers (logger.py, validators.py, etc.)
├── config/       → Settings (settings.py, constants.py)
└── schemas/      → Pydantic schemas (trade.py, etc.)
```

### Frontend Structure
```
frontend/src/
├── features/
│   ├── dashboard/    → Dashboard.jsx
│   ├── trading/      → TradeHistory.jsx, Positions.jsx
│   ├── charts/       → LiveChart.jsx, HistoricalChart.jsx
│   ├── signals/      → Signals.jsx
│   └── settings/     → Settings.jsx
├── shared/
│   ├── layouts/      → Layout.jsx
│   └── components/   → Reusable components
├── services/         → api.js
└── styles/           → global.css
```

## Common Commands

### After Migration
```bash
# Update Python imports (use IDE search/replace)
# Find: "from db import"
# Replace: "from database.session import"

# Update JS imports (use IDE search/replace)
# Find: "./components/"
# Replace: "./features/[feature]/components/"

# Test backend
cd backend && pytest

# Test frontend
cd frontend && npm run dev
```

## Verification Checklist
- [ ] Migration script completed successfully
- [ ] Python imports updated
- [ ] JavaScript imports updated
- [ ] Backend tests passing
- [ ] Frontend builds without errors
- [ ] Application starts successfully
- [ ] API endpoints responding
- [ ] Database connections working

## Quick Fixes

### Import Error
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend/src"
```

### Module Not Found
```bash
cd backend && pip install -e .
```

### Frontend Build Error
```bash
cd frontend && rm -rf node_modules && npm install
```

## File Mappings Summary

### High Priority (Update First)
- `app.py` → Use `app_factory_template.py`
- `models.py` → Split into `backend/src/models/*.py`
- `db.py` → `backend/src/database/session.py`
- All `components/*.jsx` → `frontend/src/features/*/components/`

### Configuration
- `.env` → Update paths if needed
- `requirements.txt` → `backend/requirements/base.txt`
- Copy `config_settings_template.py` → `backend/src/config/settings.py`

## Time Estimates
- Migration script: 5 min
- Import updates: 30 min
- Testing: 30 min
- **Total: ~1 hour**

## Documentation
- 📖 **REFACTORING_PLAN.md** - Overview
- 📚 **COMPLETE_REFACTORING_GUIDE.md** - Detailed guide
- 📦 **REFACTORING_PACKAGE_README.md** - Package summary
- 🚀 **THIS FILE** - Quick reference

---
**Remember: Files are copied, not deleted. Verify before cleanup!** ✅
