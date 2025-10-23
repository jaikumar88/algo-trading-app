"""
Check actual trading data in PostgreSQL database
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Force PostgreSQL connection
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/trading'

from db import SessionLocal
from models import Trade, Signal, AllowedInstrument, SystemSettings
from sqlalchemy import func, desc

print("📊 REAL TRADING DATA IN POSTGRESQL\n")
print("="*70)

session = SessionLocal()

try:
    # Get all trades (real trading data)
    print("\n🔹 TRADES (Real Trading Activity)")
    print("-"*70)
    trades = session.query(Trade).order_by(desc(Trade.open_time)).limit(20).all()
    
    if trades:
        for trade in trades:
            status_icon = "🟢" if trade.status == "OPEN" else "🔴"
            action_icon = "📈" if trade.action == "BUY" else "📉"
            pnl = f"${trade.profit_loss:,.2f}" if trade.profit_loss else "N/A"
            
            print(f"{status_icon} {action_icon} {trade.symbol}")
            print(f"   Action: {trade.action} | Status: {trade.status}")
            print(f"   Qty: {trade.quantity} @ ${trade.open_price}")
            print(f"   Opened: {trade.open_time}")
            if trade.close_time:
                print(f"   Closed: {trade.close_time} | P&L: {pnl}")
            print()
    else:
        print("   ⚠️  No trades found")
        print("   Trades will appear here when signals are processed\n")
    
    # Get trade statistics
    total_trades = session.query(Trade).count()
    open_trades = session.query(Trade).filter(Trade.status == 'OPEN').count()
    closed_trades = session.query(Trade).filter(Trade.status == 'CLOSED').count()
    
    total_pnl = session.query(func.sum(Trade.profit_loss)).filter(
        Trade.status == 'CLOSED'
    ).scalar() or 0
    
    print("\n📊 STATISTICS")
    print("-"*70)
    print(f"Total Trades: {total_trades}")
    print(f"Open Positions: {open_trades}")
    print(f"Closed Trades: {closed_trades}")
    print(f"Total P&L: ${total_pnl:,.2f}")
    
    # Get signals (incoming trading signals)
    print("\n\n🔹 SIGNALS (Incoming from Telegram)")
    print("-"*70)
    signals = session.query(Signal).order_by(desc(Signal.received_at)).limit(10).all()
    
    if signals:
        for sig in signals:
            status_icon = "✅" if sig.processed else "⏳"
            print(f"{status_icon} {sig.symbol} - {sig.action}")
            print(f"   Received: {sig.received_at}")
            print(f"   Processed: {'Yes' if sig.processed else 'Pending'}")
            if sig.error_message:
                print(f"   Error: {sig.error_message}")
            print()
    else:
        print("   ℹ️  No signals yet")
        print("   Signals will appear here when received from Telegram\n")
    
    # Get instruments
    print("\n🔹 ALLOWED INSTRUMENTS")
    print("-"*70)
    instruments = session.query(AllowedInstrument).all()
    
    if instruments:
        enabled = [i for i in instruments if i.enabled]
        disabled = [i for i in instruments if not i.enabled]
        
        print(f"Enabled ({len(enabled)}):")
        for inst in enabled:
            print(f"   ✅ {inst.symbol} - {inst.name}")
        
        if disabled:
            print(f"\nDisabled ({len(disabled)}):")
            for inst in disabled:
                print(f"   ❌ {inst.symbol} - {inst.name}")
    else:
        print("   ⚠️  No instruments configured")
        print("   Add instruments via the UI or admin panel\n")
    
    # Get system settings
    print("\n\n🔹 SYSTEM SETTINGS")
    print("-"*70)
    settings = session.query(SystemSettings).all()
    
    if settings:
        for setting in settings:
            print(f"   {setting.key}: {setting.value}")
    else:
        print("   ⚠️  No system settings")
        print("   System will use default values\n")
    
    print("\n" + "="*70)
    print("📝 SUMMARY")
    print("="*70)
    
    if total_trades > 0:
        print(f"✅ You have {total_trades} real trades in the database")
        print(f"✅ Dashboard will show actual trading data")
        print(f"✅ Total P&L: ${total_pnl:,.2f}")
    else:
        print("ℹ️  No trades yet - they will appear when signals are processed")
    
    if len(signals) > 0:
        processed = len([s for s in signals if s.processed])
        print(f"ℹ️  {len(signals)} signals received ({processed} processed)")
    
    print("\n🚀 Dashboard will use this REAL data (not mock data)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
