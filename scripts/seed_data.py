"""
Populate PostgreSQL database with sample data for testing
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Force PostgreSQL connection
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/trading'

from db import SessionLocal
from models import SystemSettings, AllowedInstrument, Trade
from datetime import datetime, timedelta
from decimal import Decimal

print("🔄 Populating PostgreSQL database with sample data...\n")

session = SessionLocal()

try:
    # Clear existing data
    print("1️⃣ Clearing existing data...")
    session.query(Trade).delete()
    session.query(AllowedInstrument).delete()
    session.query(SystemSettings).delete()
    session.commit()
    print("   ✅ Cleared\n")
    
    # Add System Settings
    print("2️⃣ Adding system settings...")
    settings = [
        SystemSettings(key='trading_enabled', value='true', value_type='boolean',
                      description='Master switch for trading'),
        SystemSettings(key='total_fund', value='100000', value_type='float',
                      description='Total available fund'),
        SystemSettings(key='risk_per_instrument', value='0.02', value_type='float',
                      description='Risk percentage per instrument'),
        SystemSettings(key='auto_stop_loss', value='true', value_type='boolean',
                      description='Automatically set stop loss')
    ]
    session.add_all(settings)
    session.commit()
    print(f"   ✅ Added {len(settings)} settings\n")
    
    # Add Instruments
    print("3️⃣ Adding instruments...")
    instruments = [
        AllowedInstrument(symbol='BTCUSDT', name='Bitcoin', enabled=True),
        AllowedInstrument(symbol='ETHUSDT', name='Ethereum', enabled=True),
        AllowedInstrument(symbol='SOLUSDT', name='Solana', enabled=True),
        AllowedInstrument(symbol='DOGEUSDT', name='Dogecoin', enabled=True),
        AllowedInstrument(symbol='ADAUSDT', name='Cardano', enabled=False)
    ]
    session.add_all(instruments)
    session.commit()
    print(f"   ✅ Added {len(instruments)} instruments\n")
    
    # Add Sample Trades
    print("4️⃣ Adding sample trades...")
    now = datetime.now()
    trades = [
        Trade(
            action='BUY',
            symbol='BTCUSDT',
            quantity=Decimal('0.5'),
            open_price=Decimal('45000'),
            open_time=now - timedelta(days=2),
            close_price=Decimal('47000'),
            close_time=now - timedelta(days=1),
            status='CLOSED',
            total_cost=Decimal('22500'),
            profit_loss=Decimal('1000'),
            allocated_fund=Decimal('20000'),
            risk_amount=Decimal('400')
        ),
        Trade(
            action='SELL',
            symbol='ETHUSDT',
            quantity=Decimal('10'),
            open_price=Decimal('2500'),
            open_time=now - timedelta(days=1),
            close_price=Decimal('2450'),
            close_time=now - timedelta(hours=12),
            status='CLOSED',
            total_cost=Decimal('25000'),
            profit_loss=Decimal('500'),
            allocated_fund=Decimal('25000'),
            risk_amount=Decimal('500')
        ),
        Trade(
            action='BUY',
            symbol='SOLUSDT',
            quantity=Decimal('100'),
            open_price=Decimal('100'),
            open_time=now - timedelta(hours=6),
            close_price=Decimal('105'),
            close_time=now - timedelta(hours=2),
            status='CLOSED',
            total_cost=Decimal('10000'),
            profit_loss=Decimal('500'),
            allocated_fund=Decimal('10000'),
            risk_amount=Decimal('200')
        )
    ]
    session.add_all(trades)
    session.commit()
    print(f"   ✅ Added {len(trades)} sample trades\n")
    
    # Verify
    print("5️⃣ Verifying data...")
    settings_count = session.query(SystemSettings).count()
    instruments_count = session.query(AllowedInstrument).count()
    trades_count = session.query(Trade).count()
    
    print(f"   Settings: {settings_count}")
    print(f"   Instruments: {instruments_count}")
    print(f"   Trades: {trades_count}\n")
    
    print("✅ PostgreSQL database populated successfully!")
    print("\n🎉 Dashboard should now show data!")
    print("\nNext steps:")
    print("1. Refresh browser (F5)")
    print("2. Dashboard should now display stats and trades")
    
except Exception as e:
    print(f"❌ Error: {e}")
    session.rollback()
finally:
    session.close()
