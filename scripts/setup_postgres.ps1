# PostgreSQL Setup Script for RAG Trading Assistant
# Run this script to create the PostgreSQL database and user

Write-Host "🐘 PostgreSQL Setup for RAG Trading Assistant" -ForegroundColor Cyan
Write-Host "=" * 60

# Configuration
$DB_NAME = "trading"
$DB_USER = "postgres"
$DB_PASSWORD = "postgres"
$DB_HOST = "localhost"
$DB_PORT = "5432"

Write-Host "`nConfiguration:" -ForegroundColor Yellow
Write-Host "  Database: $DB_NAME"
Write-Host "  User: $DB_USER"
Write-Host "  Password: $DB_PASSWORD"
Write-Host "  Host: $DB_HOST"
Write-Host "  Port: $DB_PORT"

Write-Host "`n" + "=" * 60

# Check if PostgreSQL is installed
Write-Host "`n1️⃣ Checking PostgreSQL installation..." -ForegroundColor Cyan
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $psqlPath) {
    Write-Host "❌ PostgreSQL not found in PATH" -ForegroundColor Red
    Write-Host "`nPlease install PostgreSQL:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://www.postgresql.org/download/windows/"
    Write-Host "  2. Or use Chocolatey: choco install postgresql"
    Write-Host "  3. Or use Scoop: scoop install postgresql"
    Write-Host "`nAfter installation, add PostgreSQL bin to PATH and restart terminal"
    exit 1
}

Write-Host "✅ PostgreSQL found at: $($psqlPath.Source)" -ForegroundColor Green

# Check if PostgreSQL service is running
Write-Host "`n2️⃣ Checking PostgreSQL service..." -ForegroundColor Cyan
$service = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1

if ($service) {
    if ($service.Status -eq "Running") {
        Write-Host "✅ PostgreSQL service is running: $($service.Name)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  PostgreSQL service is not running: $($service.Name)" -ForegroundColor Yellow
        Write-Host "Attempting to start service..." -ForegroundColor Yellow
        Start-Service $service.Name -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        $service.Refresh()
        if ($service.Status -eq "Running") {
            Write-Host "✅ Service started successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to start service. Please start it manually." -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "⚠️  PostgreSQL service not found. It may be running but not detected." -ForegroundColor Yellow
}

# Create database
Write-Host "`n3️⃣ Creating database '$DB_NAME'..." -ForegroundColor Cyan
Write-Host "   (You may be prompted for the postgres user password)" -ForegroundColor Gray

# Check if database exists
$checkDb = "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';"
$env:PGPASSWORD = $DB_PASSWORD
$dbExists = psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -t -c $checkDb 2>$null

if ($dbExists -match "1") {
    Write-Host "ℹ️  Database '$DB_NAME' already exists" -ForegroundColor Yellow
} else {
    psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -c "CREATE DATABASE $DB_NAME;" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database '$DB_NAME' created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create database. Trying alternative method..." -ForegroundColor Red
        # Try using createdb command
        createdb -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database '$DB_NAME' created successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create database. Please create manually:" -ForegroundColor Red
            Write-Host "   psql -U postgres" -ForegroundColor White
            Write-Host "   CREATE DATABASE trading;" -ForegroundColor White
        }
    }
}

# Test connection
Write-Host "`n4️⃣ Testing connection..." -ForegroundColor Cyan
$testQuery = "SELECT version();"
$result = psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -t -c $testQuery 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Connection successful!" -ForegroundColor Green
    Write-Host "   PostgreSQL version: $($result.Trim().Substring(0, 50))..." -ForegroundColor Gray
} else {
    Write-Host "❌ Connection failed" -ForegroundColor Red
    Write-Host "`nPlease check:" -ForegroundColor Yellow
    Write-Host "  1. PostgreSQL is running"
    Write-Host "  2. User '$DB_USER' exists"
    Write-Host "  3. Password is correct"
    Write-Host "  4. Database '$DB_NAME' exists"
    exit 1
}

# Install Python dependencies
Write-Host "`n5️⃣ Installing Python dependencies..." -ForegroundColor Cyan
if (Test-Path ".venv/Scripts/Activate.ps1") {
    Write-Host "   Activating virtual environment..." -ForegroundColor Gray
    & .\.venv\Scripts\Activate.ps1
    
    Write-Host "   Installing psycopg2-binary and SQLAlchemy..." -ForegroundColor Gray
    pip install psycopg2-binary==2.9.9 SQLAlchemy==2.0.23 --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Write-Host "   Run manually: pip install -r requirements.txt" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Run: python -m venv .venv" -ForegroundColor White
    Write-Host "   Then: .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   Then: pip install -r requirements.txt" -ForegroundColor White
}

# Run migrations
Write-Host "`n6️⃣ Running database migrations..." -ForegroundColor Cyan
if (Test-Path "alembic/versions") {
    alembic upgrade head 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations completed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Migration issues (this is normal for first run)" -ForegroundColor Yellow
        Write-Host "   Run manually: alembic upgrade head" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  Alembic not configured" -ForegroundColor Yellow
}

# Update .env file reminder
Write-Host "`n7️⃣ Environment configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    Write-Host "   Verify these settings in .env:" -ForegroundColor Gray
    Write-Host "   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading" -ForegroundColor White
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "   Copy .env.example to .env and add:" -ForegroundColor White
    Write-Host "   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading" -ForegroundColor White
}

Write-Host "`n" + "=" * 60
Write-Host "🎉 PostgreSQL Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Verify .env has: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading"
Write-Host "  2. Run: alembic upgrade head (if not done automatically)"
Write-Host "  3. Start the app: python app.py"
Write-Host "  4. Check logs for: '📊 Using PostgreSQL: trading @ localhost:5432'"

Write-Host "`n🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "  # Connect to database:"
Write-Host "  psql -U postgres -d trading"
Write-Host ""
Write-Host "  # List tables:"
Write-Host "  \dt"
Write-Host ""
Write-Host "  # View signals:"
Write-Host "  SELECT * FROM signals;"
Write-Host ""
Write-Host "  # Reset database:"
Write-Host "  DROP DATABASE trading; CREATE DATABASE trading;"

Write-Host "`n✅ Setup complete! Your app will now use PostgreSQL." -ForegroundColor Green
