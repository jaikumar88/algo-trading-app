# Test PostgreSQL Connection and Configuration

Write-Host "🔍 PostgreSQL Configuration Test" -ForegroundColor Cyan
Write-Host "=" * 60

# Load environment variables
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "✅ Loaded .env file" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
}

# Display configuration
Write-Host "`n📋 Configuration:" -ForegroundColor Cyan
$DATABASE_URL = [System.Environment]::GetEnvironmentVariable("DATABASE_URL")
$DB_HOST = [System.Environment]::GetEnvironmentVariable("DB_HOST")
$DB_NAME = [System.Environment]::GetEnvironmentVariable("DB_NAME")
$DB_USER = [System.Environment]::GetEnvironmentVariable("DB_USER")

if ($DATABASE_URL) {
    Write-Host "  DATABASE_URL: $DATABASE_URL" -ForegroundColor White
} elseif ($DB_HOST -and $DB_NAME) {
    Write-Host "  DB_HOST: $DB_HOST" -ForegroundColor White
    Write-Host "  DB_NAME: $DB_NAME" -ForegroundColor White
    Write-Host "  DB_USER: $DB_USER" -ForegroundColor White
} else {
    Write-Host "  ⚠️  No PostgreSQL configuration found (will use SQLite)" -ForegroundColor Yellow
}

# Test Python can import psycopg2
Write-Host "`n🐍 Testing Python dependencies..." -ForegroundColor Cyan
$pythonTest = @"
import sys
try:
    import psycopg2
    print('✅ psycopg2 installed:', psycopg2.__version__)
except ImportError as e:
    print('❌ psycopg2 not found:', e)
    sys.exit(1)

try:
    import sqlalchemy
    print('✅ SQLAlchemy installed:', sqlalchemy.__version__)
except ImportError as e:
    print('❌ SQLAlchemy not found:', e)
    sys.exit(1)
"@

python -c $pythonTest
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n⚠️  Missing dependencies. Run:" -ForegroundColor Yellow
    Write-Host "  pip install psycopg2-binary SQLAlchemy" -ForegroundColor White
}

# Test database connection
Write-Host "`n🔌 Testing database connection..." -ForegroundColor Cyan
$connectionTestFile = "test_db_connection.py"
$connectionTest = @'
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'trading')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    if os.getenv('DB_HOST') or os.getenv('DB_NAME'):
        DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        
if DATABASE_URL and DATABASE_URL.startswith('postgresql'):
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version()'))
            version = result.fetchone()[0]
            print(f'✅ Connected to PostgreSQL')
            print(f'   Version: {version[:50]}...')
            
            # Check if tables exist
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            tables = [row[0] for row in result]
            if tables:
                print(f'✅ Tables found: {len(tables)}')
                for table in tables:
                    print(f'   - {table}')
            else:
                print('⚠️  No tables found. Run: alembic upgrade head')
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        print('\nTroubleshooting:')
        print('1. Check PostgreSQL is running')
        print('2. Verify database exists: psql -U postgres -l')
        print('3. Check credentials in .env')
        exit(1)
else:
    print('ℹ️  Using SQLite (no PostgreSQL config found)')
'@

$connectionTest | Out-File -FilePath $connectionTestFile -Encoding UTF8
python $connectionTestFile
$exitCode = $LASTEXITCODE
Remove-Item $connectionTestFile -ErrorAction SilentlyContinue

Write-Host "`n" + "=" * 60
Write-Host "🎯 Summary:" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ PostgreSQL is configured and working!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. Start the app: python app.py"
    Write-Host "  2. Look for: '📊 Using PostgreSQL: trading @ localhost:5432'"
    Write-Host "  3. Test webhook: See POSTGRES_SETUP.md"
} else {
    Write-Host "⚠️  PostgreSQL connection issues detected" -ForegroundColor Yellow
    Write-Host "`nTo fix:" -ForegroundColor Yellow
    Write-Host "  1. Install PostgreSQL if not installed"
    Write-Host "  2. Create database: psql -U postgres -c 'CREATE DATABASE trading;'"
    Write-Host "  3. Run setup: .\setup_postgres.ps1"
    Write-Host "  4. Or see: POSTGRES_SETUP.md for manual steps"
}

Write-Host "`n📚 Documentation: POSTGRES_SETUP.md" -ForegroundColor Cyan
