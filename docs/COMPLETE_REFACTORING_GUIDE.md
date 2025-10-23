# 🏗️ Complete Refactoring Guide - RAG Trading System

## 📋 Overview

This guide will help you refactor the RAG Trading System from a monolithic structure to a professional, maintainable codebase following industry best practices.

---

## 🎯 Goals

✅ **Proper folder structure** - Organized by feature and responsibility  
✅ **Separation of concerns** - API, services, models, utils  
✅ **Type hints** - Full Python typing support  
✅ **Configuration management** - Environment-based settings  
✅ **Error handling** - Centralized error management  
✅ **Testing** - Organized test suite  
✅ **Documentation** - Clear, comprehensive docs  
✅ **Production ready** - Scalable and maintainable  

---

## 📁 New Structure

```
rag-trading-system/
├── backend/
│   ├── src/
│   │   ├── api/              # API routes
│   │   ├── services/         # Business logic
│   │   ├── models/           # Database models
│   │   ├── database/         # DB configuration
│   │   ├── tasks/            # Background tasks
│   │   ├── utils/            # Utilities
│   │   ├── config/           # Configuration
│   │   └── schemas/          # Pydantic schemas
│   ├── tests/                # All tests
│   ├── scripts/              # Utility scripts
│   └── docs/                 # Documentation
├── frontend/
│   └── src/
│       ├── features/         # Feature modules
│       ├── shared/           # Shared components
│       ├── hooks/            # Custom hooks
│       └── services/         # API services
└── docs/                     # Project docs
```

---

## 🚀 Migration Steps

### Step 1: Run Migration Script

```bash
python migrate_to_new_structure.py
```

**What it does:**
- Creates new folder structure
- Copies files to new locations
- Preserves originals for safety

### Step 2: Update Imports (Backend)

#### Before:
```python
from db import SessionLocal
from models import Trade, Signal
from trading import TradingManager
```

#### After:
```python
from database.session import SessionLocal
from models.trade import Trade
from models.signal import Signal
from services.trading_service import TradingService
```

### Step 3: Update Imports (Frontend)

#### Before:
```javascript
import Dashboard from './components/Dashboard'
import Layout from './Layout'
```

#### After:
```javascript
import Dashboard from './features/dashboard/components/Dashboard'
import Layout from './shared/layouts/Layout'
```

### Step 4: Split Models

Create separate files for each model:

**backend/src/models/base.py:**
```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

**backend/src/models/trade.py:**
```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean
from sqlalchemy.sql import func
from .base import Base

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    # ... rest of fields
```

### Step 5: Create Configuration

Use the template in `config_settings_template.py`.

**backend/src/config/settings.py:**
- Copy content from template
- Adjust values for your needs
- Add validation as needed

### Step 6: Update app.py

Use the template in `app_factory_template.py`.

**backend/src/app.py:**
- Application factory pattern
- Blueprint registration
- Error handlers
- Logging setup

### Step 7: Create API Blueprints

**backend/src/api/trading.py:**
```python
from flask import Blueprint, request, jsonify
from services.trading_service import TradingService
from database.session import SessionLocal

trading_bp = Blueprint('trading', __name__)

@trading_bp.route('/positions', methods=['GET'])
def get_positions():
    """Get all open positions"""
    session = SessionLocal()
    try:
        service = TradingService(session)
        positions = service.get_open_positions()
        return jsonify(positions)
    finally:
        session.close()
```

### Step 8: Extract Services

**backend/src/services/trading_service.py:**
```python
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.trade import Trade
from models.instrument import AllowedInstrument

class TradingService:
    """Business logic for trading operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open trading positions"""
        trades = self.session.query(Trade).filter(
            Trade.status == 'OPEN'
        ).all()
        
        return [self._trade_to_dict(trade) for trade in trades]
    
    def _trade_to_dict(self, trade: Trade) -> Dict:
        """Convert Trade model to dictionary"""
        return {
            'id': trade.id,
            'symbol': trade.symbol,
            'action': trade.action,
            # ... more fields
        }
```

### Step 9: Add Type Hints

Add type hints to all functions:

```python
def process_signal(
    symbol: str,
    action: str,
    price: float
) -> Dict[str, any]:
    """Process trading signal"""
    # ... implementation
```

### Step 10: Add Docstrings

Use Google-style docstrings:

```python
def calculate_position_size(
    account_balance: float,
    risk_percentage: float,
    stop_loss_distance: float
) -> float:
    """
    Calculate position size based on risk management rules.
    
    Args:
        account_balance: Total account balance in USD
        risk_percentage: Risk as decimal (0.02 for 2%)
        stop_loss_distance: Distance to stop loss in price units
    
    Returns:
        Position size in base currency units
    
    Raises:
        ValueError: If any parameter is invalid
    
    Example:
        >>> calculate_position_size(10000, 0.02, 100)
        2.0
    """
    if account_balance <= 0:
        raise ValueError("Account balance must be positive")
    
    risk_amount = account_balance * risk_percentage
    position_size = risk_amount / stop_loss_distance
    
    return position_size
```

---

## 📦 Code Templates

### API Blueprint Template

```python
"""
[Feature] API endpoints.
"""
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

from services.[feature]_service import [Feature]Service
from database.session import SessionLocal
from utils.decorators import require_auth, rate_limit
from schemas.[feature] import [Feature]Schema

logger = logging.getLogger(__name__)
[feature]_bp = Blueprint('[feature]', __name__)


@[feature]_bp.route('/', methods=['GET'])
@rate_limit(limit=100, per=60)
def list_items() -> Dict[str, Any]:
    """
    Get all items.
    
    Returns:
        JSON response with items list
    """
    session = SessionLocal()
    try:
        service = [Feature]Service(session)
        items = service.get_all()
        return jsonify({
            'status': 'success',
            'data': items,
            'count': len(items)
        })
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        session.close()
```

### Service Template

```python
"""
[Feature] business logic service.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
import logging

from models.[model] import [Model]
from config.settings import settings

logger = logging.getLogger(__name__)


class [Feature]Service:
    """Service for [feature] operations."""
    
    def __init__(self, session: Session):
        """
        Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_all(self) -> List[Dict]:
        """
        Get all items.
        
        Returns:
            List of items as dictionaries
        """
        items = self.session.query([Model]).all()
        return [self._to_dict(item) for item in items]
    
    def get_by_id(self, item_id: int) -> Optional[Dict]:
        """
        Get item by ID.
        
        Args:
            item_id: Item ID
        
        Returns:
            Item dictionary or None if not found
        """
        item = self.session.query([Model]).filter(
            [Model].id == item_id
        ).first()
        
        return self._to_dict(item) if item else None
    
    def create(self, data: Dict) -> Dict:
        """
        Create new item.
        
        Args:
            data: Item data dictionary
        
        Returns:
            Created item dictionary
        
        Raises:
            ValueError: If data is invalid
        """
        # Validate data
        self._validate_data(data)
        
        # Create model instance
        item = [Model](**data)
        
        # Save to database
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        
        self.logger.info(f"Created item {item.id}")
        return self._to_dict(item)
    
    def _to_dict(self, item: [Model]) -> Dict:
        """Convert model to dictionary."""
        return {
            'id': item.id,
            # ... other fields
        }
    
    def _validate_data(self, data: Dict) -> None:
        """Validate item data."""
        required_fields = ['field1', 'field2']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
```

### Model Template

```python
"""
[Model] database model.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    Boolean,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


class [Model](Base):
    """[Model description]."""
    
    __tablename__ = '[table_name]'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Fields
    name = Column(String, nullable=False)
    value = Column(Numeric(20, 8), nullable=False)
    status = Column(String, default='active')
    is_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
    
    # Relationships
    # related_items = relationship("RelatedModel", back_populates="parent")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(id={self.id}, name='{self.name}')>"
```

---

## 🧪 Testing Structure

### Test Organization

```
backend/tests/
├── unit/                  # Unit tests
│   ├── test_services.py
│   ├── test_models.py
│   └── test_utils.py
├── integration/           # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── e2e/                   # End-to-end tests
    └── test_workflows.py
```

### Test Template

```python
"""
Unit tests for [Feature]Service.
"""
import pytest
from decimal import Decimal
from datetime import datetime

from services.[feature]_service import [Feature]Service
from models.[model] import [Model]


class Test[Feature]Service:
    """Test suite for [Feature]Service."""
    
    @pytest.fixture
    def service(self, db_session):
        """Create service instance."""
        return [Feature]Service(db_session)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        return {
            'name': 'Test Item',
            'value': Decimal('100.50')
        }
    
    def test_get_all(self, service):
        """Test getting all items."""
        items = service.get_all()
        assert isinstance(items, list)
    
    def test_create(self, service, sample_data):
        """Test creating an item."""
        result = service.create(sample_data)
        
        assert result['name'] == sample_data['name']
        assert result['value'] == float(sample_data['value'])
        assert 'id' in result
    
    def test_create_invalid_data(self, service):
        """Test creating with invalid data."""
        with pytest.raises(ValueError):
            service.create({})
```

---

## 📝 Code Quality

### Add Linting

**pyproject.toml:**
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.pylint.messages_control]
max-line-length = 88
disable = ["C0111", "C0103"]
```

### Pre-commit Hooks

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## 🔧 Configuration Files

### .env.example

```ini
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trading_db

# API Keys
OPENAI_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here

# Trading
TRADING_ENABLED=false
DEFAULT_QUANTITY=0.001

# Security
SECRET_KEY=your_secret_key_here
```

### requirements/base.txt

```
flask==2.3.0
flask-cors==4.0.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.0
pydantic==2.0.0
python-dotenv==1.0.0
celery==5.3.0
redis==4.5.0
requests==2.31.0
```

### requirements/dev.txt

```
-r base.txt

pytest==7.4.0
pytest-cov==4.1.0
black==23.3.0
isort==5.12.0
pylint==2.17.0
pre-commit==3.3.0
```

---

## 📚 Documentation

### README.md Template

```markdown
# RAG Trading System

Professional trading system with AI-powered signal processing.

## Features

- 📊 Real-time price charts
- 🤖 AI signal analysis
- 💰 Automated trading
- 📈 Historical data tracking
- 🎯 Risk management

## Installation

\`\`\`bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements/dev.txt

# Frontend
cd frontend
npm install
\`\`\`

## Configuration

Copy `.env.example` to `.env` and configure:
\`\`\`bash
cp .env.example .env
# Edit .env with your values
\`\`\`

## Running

\`\`\`bash
# Backend
python backend/src/app.py

# Frontend
cd frontend
npm run dev
\`\`\`

## Testing

\`\`\`bash
cd backend
pytest
\`\`\`

## License

MIT
```

---

## ✅ Verification Checklist

After refactoring, verify:

- [ ] All imports updated
- [ ] Tests passing
- [ ] Application starts without errors
- [ ] API endpoints working
- [ ] Frontend loads correctly
- [ ] Database connections working
- [ ] Configuration loaded properly
- [ ] Logging configured
- [ ] Error handling working
- [ ] Documentation updated

---

## 🎯 Next Steps

1. **Run migration script**: `python migrate_to_new_structure.py`
2. **Update imports**: Search and replace old import paths
3. **Test thoroughly**: Run all tests and manual testing
4. **Update documentation**: Ensure docs reflect new structure
5. **Commit changes**: Version control the refactored code
6. **Deploy**: Test in staging before production

---

## 🆘 Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
```bash
# Add backend/src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend/src"
```

### Database Errors

If database connections fail:
```bash
# Check DATABASE_URL in .env
# Verify PostgreSQL is running
# Run migrations
alembic upgrade head
```

### Frontend Build Errors

If React build fails:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

**Good luck with your refactoring! 🚀**
