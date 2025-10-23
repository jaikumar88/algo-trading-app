from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
import os

# Priority: DATABASE_URL > Individual components > SQLite fallback
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')

if not DATABASE_URL:
    # Try to build from individual components
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'trading')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    
    # Check if PostgreSQL components are provided (not defaults)
    if os.getenv('DB_HOST') or os.getenv('DB_NAME'):
        DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        print(f"📊 Using PostgreSQL: {db_name} @ {db_host}:{db_port}")
    else:
        # Fallback to local sqlite for development
        DATABASE_URL = 'sqlite:///dev_trading.db'
        print(f"📊 Using SQLite: dev_trading.db (set DATABASE_URL or DB_* env vars for PostgreSQL)")

# echo disabled by default; can be enabled via env SQL_ECHO=true
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=(os.getenv('SQL_ECHO') == 'true'))
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables if they don't exist.
    This is safe to call multiple times - it only creates missing tables.
    """
    from models import Base  # Import here to avoid circular dependency
    
    try:
        # Check if database is accessible
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        
        # Check which tables were created
        new_tables = set(inspector.get_table_names()) - set(existing_tables)
        
        if new_tables:
            print(f"✅ Created tables: {', '.join(new_tables)}")
        else:
            print(f"✅ Database tables verified (found {len(existing_tables)} tables)")
            
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print(f"   Make sure database exists and credentials are correct")
        return False
