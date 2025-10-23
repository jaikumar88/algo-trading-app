from db import SessionLocal
from models import SystemSettings, AllowedInstrument, Trade

session = SessionLocal()

print("📊 Database Status Check\n")

# Check settings
settings_count = session.query(SystemSettings).count()
print(f"System Settings: {settings_count}")
for setting in session.query(SystemSettings).all():
    print(f"  - {setting.key} = {setting.value}")

# Check instruments
instruments_count = session.query(AllowedInstrument).count()
print(f"\nInstruments: {instruments_count}")
for inst in session.query(AllowedInstrument).all():
    print(f"  - {inst.symbol} ({inst.name}) - {'Enabled' if inst.enabled else 'Disabled'}")

# Check trades
trades_count = session.query(Trade).count()
open_trades = session.query(Trade).filter(Trade.status == 'OPEN').count()
closed_trades = session.query(Trade).filter(Trade.status == 'CLOSED').count()
print(f"\nTrades: {trades_count} total ({open_trades} open, {closed_trades} closed)")

session.close()

if settings_count == 0:
    print("\n⚠️  No system settings found!")
    print("   Run: python recreate_db.py OR python test_all_features.py")
