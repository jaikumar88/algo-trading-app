# 🐘 PostgreSQL Integration Guide

## Overview

Your RAG Trading Assistant now uses **PostgreSQL** instead of SQLite for production-grade data persistence.

**Database Configuration:**
- **Database Name:** `trading`
- **User:** `postgres`
- **Password:** `postgres`
- **Host:** `localhost`
- **Port:** `5432`

---

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the PowerShell setup script:

```powershell
.\setup_postgres.ps1
```

This script will:
- ✅ Check PostgreSQL installation
- ✅ Start PostgreSQL service if needed
- ✅ Create `trading` database
- ✅ Test connection
- ✅ Install Python dependencies (psycopg2, SQLAlchemy)
- ✅ Run database migrations
- ✅ Verify .env configuration

### Option 2: Manual Setup

#### 1. Install PostgreSQL

**Windows:**
```powershell
# Using Chocolatey
choco install postgresql

# Or download from
https://www.postgresql.org/download/windows/
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### 2. Create Database

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database (in psql prompt)
CREATE DATABASE trading;

# Exit
\q
```

#### 3. Install Python Dependencies

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install PostgreSQL adapter
pip install psycopg2-binary==2.9.9 SQLAlchemy==2.0.23

# Or install all requirements
pip install -r requirements.txt
```

#### 4. Run Migrations

```powershell
alembic upgrade head
```

---

## ⚙️ Configuration

### .env File

Your `.env` file has been updated with PostgreSQL settings:

```bash
# PostgreSQL Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading

# Or use individual components:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading
DB_USER=postgres
DB_PASSWORD=postgres
```

### Connection Priority

The app uses this priority for database connection:

1. **DATABASE_URL** environment variable
2. **Individual DB_* variables** (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
3. **SQLite fallback** (dev_trading.db) if none provided

---

## ✅ Verification

### 1. Check Database Connection

```powershell
# Test connection
psql -U postgres -d trading -c "SELECT version();"
```

### 2. Start the Application

```powershell
python app.py
```

**Look for this message in the console:**
```
📊 Using PostgreSQL: trading @ localhost:5432
```

### 3. Verify Tables

```powershell
# Connect to database
psql -U postgres -d trading

# List tables
\dt

# Should show:
# - signals
# - trades
# - users
# - idempotency_keys
# - alembic_version

# View schema
\d signals

# Exit
\q
```

### 4. Test Data Insertion

```powershell
# Send a test webhook
Invoke-WebRequest -Uri "http://localhost:5000/webhook" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"action":"buy","symbol":"BTCUSDT","price":50000}'

# Check database
psql -U postgres -d trading -c "SELECT * FROM signals ORDER BY created_at DESC LIMIT 5;"
```

---

## 🗄️ Database Schema

### Tables Created

#### **signals**
Stores all incoming trade signals from webhooks.

```sql
Column        | Type                  | Description
--------------|-----------------------|------------------
id            | INTEGER (PRIMARY KEY) | Auto-increment ID
symbol        | VARCHAR               | Trading pair (e.g., BTCUSDT)
action        | VARCHAR               | buy/sell/long/short
price         | NUMERIC(18,8)         | Signal price
raw           | TEXT                  | Raw webhook data (JSON)
image_path    | VARCHAR               | Path to saved image
created_at    | TIMESTAMP             | Signal timestamp
```

#### **trades**
Stores executed trades based on signals.

```sql
Column        | Type                  | Description
--------------|-----------------------|------------------
id            | INTEGER (PRIMARY KEY) | Auto-increment ID
signal_id     | INTEGER (FOREIGN KEY) | Reference to signal
user_id       | INTEGER (FOREIGN KEY) | Reference to user
symbol        | VARCHAR               | Trading pair
side          | VARCHAR               | buy/sell
price         | NUMERIC(18,8)         | Execution price
quantity      | NUMERIC(18,8)         | Trade quantity
status        | VARCHAR               | pending/filled/cancelled
created_at    | TIMESTAMP             | Trade timestamp
```

#### **idempotency_keys**
Prevents duplicate webhook processing.

```sql
Column        | Type                  | Description
--------------|-----------------------|------------------
id            | INTEGER (PRIMARY KEY) | Auto-increment ID
key           | VARCHAR (UNIQUE)      | Idempotency key (hash)
created_at    | TIMESTAMP             | First seen timestamp
```

#### **users**
User accounts and settings.

```sql
Column        | Type                  | Description
--------------|-----------------------|------------------
id            | INTEGER (PRIMARY KEY) | Auto-increment ID
telegram_id   | VARCHAR (UNIQUE)      | Telegram user ID
username      | VARCHAR               | Display name
created_at    | TIMESTAMP             | Registration time
```

---

## 🔧 Useful Commands

### PostgreSQL CLI

```powershell
# Connect to database
psql -U postgres -d trading

# List all databases
\l

# List tables
\dt

# Describe table structure
\d signals

# View table data
SELECT * FROM signals LIMIT 10;

# Count records
SELECT COUNT(*) FROM signals;
SELECT COUNT(*) FROM trades;

# Recent signals
SELECT id, symbol, action, price, created_at 
FROM signals 
ORDER BY created_at DESC 
LIMIT 20;

# Filter by symbol
SELECT * FROM signals WHERE symbol = 'BTCUSDT';

# Trades with signal info
SELECT t.*, s.raw 
FROM trades t 
JOIN signals s ON t.signal_id = s.id 
ORDER BY t.created_at DESC 
LIMIT 10;

# Exit
\q
```

### Database Management

```powershell
# Backup database
pg_dump -U postgres trading > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Restore database
psql -U postgres -d trading < backup_20251014_120000.sql

# Drop and recreate (WARNING: deletes all data)
psql -U postgres -c "DROP DATABASE IF EXISTS trading;"
psql -U postgres -c "CREATE DATABASE trading;"
alembic upgrade head

# Reset tables but keep database
psql -U postgres -d trading -c "DROP TABLE IF EXISTS signals, trades, users, idempotency_keys, alembic_version CASCADE;"
alembic upgrade head
```

### Migrations

```powershell
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Run migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

## 🔍 Troubleshooting

### Issue: PostgreSQL not found

**Solution:**
```powershell
# Check if installed
Get-Command psql

# If not found, install:
choco install postgresql
# Or download from postgresql.org
```

### Issue: Service not running

**Solution:**
```powershell
# Find service
Get-Service -Name "*postgresql*"

# Start service
Start-Service postgresql-x64-14  # Replace with your service name

# Or use PostgreSQL directly
pg_ctl -D "C:\Program Files\PostgreSQL\14\data" start
```

### Issue: Authentication failed

**Solution:**
```powershell
# Edit pg_hba.conf to allow password authentication
# Location: C:\Program Files\PostgreSQL\14\data\pg_hba.conf
# Change METHOD from 'scram-sha-256' to 'md5' or 'trust' for localhost

# Restart PostgreSQL after editing
Restart-Service postgresql-x64-14
```

### Issue: Database doesn't exist

**Solution:**
```powershell
# Create database manually
psql -U postgres -c "CREATE DATABASE trading;"

# Or use createdb
createdb -U postgres trading
```

### Issue: Tables not created

**Solution:**
```powershell
# Run migrations
alembic upgrade head

# If migration fails, check:
# 1. DATABASE_URL is correct in .env
# 2. Database exists
# 3. User has permissions

# Force recreate tables (WARNING: deletes data)
psql -U postgres -d trading -c "DROP TABLE IF EXISTS alembic_version CASCADE;"
alembic upgrade head
```

### Issue: Connection refused

**Solution:**
```powershell
# Check if PostgreSQL is listening
netstat -an | Select-String "5432"

# Check postgresql.conf
# Ensure: listen_addresses = '*' or 'localhost'

# Restart PostgreSQL
Restart-Service postgresql-x64-14
```

### Issue: Python psycopg2 error

**Solution:**
```powershell
# Install binary version (easier, no compilation needed)
pip uninstall psycopg2
pip install psycopg2-binary

# Or install build dependencies for source version
# (Requires PostgreSQL dev libraries and C compiler)
```

---

## 🔐 Security Notes

### Development Settings (Current)

⚠️ **Current credentials are for development only:**
- User: `postgres`
- Password: `postgres`
- Database: `trading`

### Production Recommendations

For production deployment:

1. **Create dedicated user:**
   ```sql
   CREATE USER trading_app WITH PASSWORD 'strong_random_password_here';
   GRANT ALL PRIVILEGES ON DATABASE trading TO trading_app;
   ```

2. **Update .env:**
   ```bash
   DATABASE_URL=postgresql://trading_app:strong_random_password_here@localhost:5432/trading
   ```

3. **Restrict access in pg_hba.conf:**
   ```
   # Only allow from specific IPs
   host    trading    trading_app    192.168.1.0/24    md5
   ```

4. **Use environment variables in production:**
   - Don't commit .env to version control
   - Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
   - Set DATABASE_URL in production environment

5. **Enable SSL:**
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

---

## 📊 Performance Tips

### Indexes

Add indexes for frequently queried columns:

```sql
CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_created_at ON signals(created_at);
CREATE INDEX idx_trades_signal_id ON trades(signal_id);
CREATE INDEX idx_trades_created_at ON trades(created_at);
```

### Connection Pooling

For high traffic, configure connection pooling in `db.py`:

```python
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_size=10,          # Max connections
    max_overflow=20,       # Extra connections when needed
    pool_recycle=3600      # Recycle connections after 1 hour
)
```

### Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'trading';

-- Database size
SELECT pg_size_pretty(pg_database_size('trading'));

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🎯 Next Steps

1. ✅ **Run setup:** `.\setup_postgres.ps1`
2. ✅ **Verify connection:** Check app logs for "📊 Using PostgreSQL"
3. ✅ **Test webhooks:** Send test data and verify in database
4. ✅ **Monitor:** Check tables with `psql` commands
5. ✅ **Backup:** Set up regular backups with `pg_dump`

---

## 📚 Additional Resources

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Alembic Documentation:** https://alembic.sqlalchemy.org/
- **psycopg2 Documentation:** https://www.psycopg.org/docs/

---

**Status:** 🟢 PostgreSQL integration complete!
**Database:** `trading` @ `localhost:5432`
**User:** `postgres` / `postgres` (change for production!)
