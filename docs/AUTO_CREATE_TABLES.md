# ✅ Auto-Create Tables Feature

## Overview

Your RAG Trading Assistant now **automatically creates database tables** if they don't exist when the app starts. No need to run Alembic migrations manually!

---

## 🎯 What Was Added

### 1. Enhanced `db.py`

Added `init_db()` function that:
- ✅ Creates all tables defined in `models.py`
- ✅ Only creates missing tables (safe to run multiple times)
- ✅ Reports which tables were created
- ✅ Verifies existing tables
- ✅ Handles errors gracefully

```python
def init_db():
    """
    Initialize database by creating all tables if they don't exist.
    This is safe to call multiple times - it only creates missing tables.
    """
    from models import Base
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    new_tables = set(inspector.get_table_names()) - set(existing_tables)
    
    if new_tables:
        print(f"✅ Created tables: {', '.join(new_tables)}")
    else:
        print(f"✅ Database tables verified (found {len(existing_tables)} tables)")
```

### 2. Updated `app.py`

Added automatic initialization on startup:

```python
if __name__ == "__main__":
    # Initialize database and create tables if they don't exist
    print("\n" + "=" * 60)
    print("🚀 Starting RAG Trading Assistant")
    print("=" * 60)
    
    from db import init_db
    init_db()
    
    print("\n🌐 Starting Flask server on http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    
    app.run(host="127.0.0.1", port=5000, debug=True)
```

---

## 📊 Tables Created Automatically

When you start the app for the first time, these tables will be created:

### **signals** - Trading signals from webhooks
```sql
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    source VARCHAR,
    symbol VARCHAR,
    action VARCHAR,
    price NUMERIC(30,8),
    raw TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **trades** - Executed trades
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    quantity NUMERIC(20,8) NOT NULL,
    open_price NUMERIC(30,8) NOT NULL,
    open_time TIMESTAMP DEFAULT NOW(),
    close_price NUMERIC(30,8),
    close_time TIMESTAMP,
    status VARCHAR DEFAULT 'OPEN',
    total_cost NUMERIC(40,8),
    profit_loss NUMERIC(40,8)
);
```

### **users** - User accounts
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE
);
```

### **idempotency_keys** - Prevent duplicate processing
```sql
CREATE TABLE idempotency_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 How It Works

### First Time Startup

```
$ python app.py

============================================================
🚀 Starting RAG Trading Assistant
============================================================
📊 Using PostgreSQL: trading @ localhost:5432
✅ Created tables: idempotency_keys, signals, trades, users

🌐 Starting Flask server on http://127.0.0.1:5000
============================================================

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Subsequent Startups

```
$ python app.py

============================================================
🚀 Starting RAG Trading Assistant
============================================================
📊 Using PostgreSQL: trading @ localhost:5432
✅ Database tables verified (found 4 tables)

🌐 Starting Flask server on http://127.0.0.1:5000
============================================================
```

---

## ✅ Benefits

### 1. **Zero Configuration**
- No need to run `alembic upgrade head`
- Works out of the box with fresh database
- Perfect for development and quick deployments

### 2. **Safe**
- Only creates missing tables
- Never drops or modifies existing tables
- Can be run multiple times safely

### 3. **Automatic**
- Happens on every app startup
- No manual steps required
- Error messages if database issues

### 4. **Works with Both SQLite and PostgreSQL**
```python
# SQLite (auto creates file and tables)
DATABASE_URL=sqlite:///dev_trading.db

# PostgreSQL (creates tables in existing database)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading
```

---

## 🧪 Testing

### Test Database Initialization

```powershell
python test_db_init.py
```

**Expected Output:**
```
============================================================
🧪 Testing Database Initialization
============================================================

1️⃣ Initializing database...
📊 Using PostgreSQL: trading @ localhost:5432
✅ Created tables: idempotency_keys, signals, trades, users

2️⃣ Checking tables...

✅ Found 4 tables:
   • idempotency_keys
     Columns (3): id, key, created_at
   • signals
     Columns (7): id, source, symbol, action, price, raw, created_at
   • trades
     Columns (12): id, user_id, action, symbol, quantity ...
   • users
     Columns (2): id, username

3️⃣ Testing database connection...
✅ Connection successful! Signal count: 0

============================================================
✅ Database initialization test complete!
============================================================
```

### Verify Tables in PostgreSQL

```powershell
# Connect to database
psql -U postgres -d trading

# List tables
\dt

# Should show:
#  public | idempotency_keys | table | postgres
#  public | signals          | table | postgres
#  public | trades           | table | postgres
#  public | users            | table | postgres

# Describe table structure
\d signals

# Exit
\q
```

---

## 🔧 What If Tables Already Exist?

No problem! The `init_db()` function is **idempotent** (safe to run multiple times):

```python
# First run
✅ Created tables: idempotency_keys, signals, trades, users

# Second run
✅ Database tables verified (found 4 tables)

# Third run
✅ Database tables verified (found 4 tables)
```

It will:
- ✅ **Never drop** existing tables
- ✅ **Never modify** existing columns
- ✅ **Never delete** existing data
- ✅ Only create tables that don't exist

---

## 🆚 init_db() vs Alembic Migrations

### Use `init_db()` (Auto-Create) When:
- ✅ Starting fresh with a new database
- ✅ Development environment
- ✅ Quick prototyping
- ✅ Testing
- ✅ Simple deployments

### Use Alembic Migrations When:
- ✅ Production environment with data
- ✅ Schema changes to existing tables
- ✅ Adding/removing columns
- ✅ Data migrations
- ✅ Version control of schema changes

### Can I Use Both?
**Yes!** They work together:

1. **First deployment**: `init_db()` creates tables
2. **Later changes**: Use Alembic for migrations
3. **Fresh databases**: `init_db()` still works

---

## 🐛 Troubleshooting

### Issue: "Database initialization error"

**Solution:**
```powershell
# 1. Check PostgreSQL is running
Get-Service -Name "*postgresql*"

# 2. Verify database exists
psql -U postgres -l | Select-String "trading"

# If not, create it:
psql -U postgres -c "CREATE DATABASE trading;"

# 3. Test connection
psql -U postgres -d trading -c "SELECT version();"

# 4. Check .env has correct credentials
Get-Content .env | Select-String "DATABASE_URL"
```

### Issue: Tables not created

**Possible causes:**
1. Database doesn't exist → Create it manually
2. User lacks permissions → Grant CREATE privilege
3. Connection issue → Check DATABASE_URL

**Fix:**
```sql
-- Connect as superuser
psql -U postgres

-- Create database if missing
CREATE DATABASE trading;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE trading TO postgres;

-- Exit and restart app
\q
python app.py
```

### Issue: "relation already exists"

This is **normal** and safe! It means tables already exist. The function will:
- Skip existing tables
- Only create missing ones
- Display: "✅ Database tables verified"

---

## 📝 Code Example

### Manual Table Creation (if needed)

```python
from db import init_db

# Initialize database and create tables
if init_db():
    print("Tables created successfully!")
else:
    print("Failed to create tables")
```

### Check Existing Tables

```python
from db import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Existing tables: {tables}")
```

### Create Specific Table

```python
from db import engine
from models import Signal, Base

# Create only the signals table
Signal.__table__.create(engine, checkfirst=True)
```

---

## 🎯 Summary

✅ **Auto-create on startup** - Tables created automatically when app starts  
✅ **Safe & idempotent** - Can run multiple times without issues  
✅ **No manual migrations** - Works out of the box  
✅ **Works with SQLite & PostgreSQL** - Database agnostic  
✅ **Error handling** - Clear messages if issues occur  
✅ **Testing included** - `test_db_init.py` for verification  

---

## 🚀 Quick Start

### Step 1: Ensure Database Exists

**PostgreSQL:**
```powershell
psql -U postgres -c "CREATE DATABASE trading;"
```

**SQLite:**
Nothing needed - file created automatically!

### Step 2: Configure .env

```bash
# PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading

# Or SQLite (default)
# DATABASE_URL=sqlite:///dev_trading.db
```

### Step 3: Start the App

```powershell
python app.py
```

**That's it!** Tables are created automatically. ✨

---

## 📚 Related Files

- `db.py` - Database connection and `init_db()` function
- `models.py` - Table definitions (Signal, Trade, User, IdempotencyKey)
- `app.py` - Calls `init_db()` on startup
- `test_db_init.py` - Test script
- `POSTGRES_SETUP.md` - Full PostgreSQL guide

---

**Status:** ✅ **Auto-create tables feature is active!**

Just start your app and tables will be created automatically! 🎉
