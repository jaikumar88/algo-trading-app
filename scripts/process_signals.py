"""
Process existing signals that weren't converted to trades
"""
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/trading'

from db import SessionLocal
from models import Signal, Trade
from trading import TradingManager
from decimal import Decimal

session = SessionLocal()

try:
    # Get all signals that have action defined
    signals_with_action = session.query(Signal).filter(
        Signal.action.isnot(None)
    ).order_by(Signal.created_at).all()
    
    print(f"\n📊 PROCESSING {len(signals_with_action)} SIGNALS INTO TRADES")
    print("="*80)
    
    tm = TradingManager(session)
    
    # Delete sample trades first
    print("\n🗑️  Removing sample trades...")
    sample_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    deleted = session.query(Trade).filter(
        Trade.symbol.in_(sample_symbols),
        Trade.profit_loss.in_([1000, 500])  # Sample P&L values
    ).delete(synchronize_session=False)
    session.commit()
    print(f"   ✅ Removed {deleted} sample trades\n")
    
    results = []
    for sig in signals_with_action:
        if not sig.symbol or not sig.action or not sig.price:
            print(f"⏭️  Skipping signal {sig.id} - missing data")
            continue
            
        print(f"\n🔄 Processing Signal #{sig.id}")
        print(f"   Symbol: {sig.symbol}")
        print(f"   Action: {sig.action}")
        print(f"   Price: ${sig.price:,.2f}")
        print(f"   Time: {sig.created_at}")
        
        try:
            result = tm.handle_signal(
                user_id=None,
                symbol=sig.symbol,
                side=sig.action,
                price=Decimal(str(sig.price))
            )
            
            if 'opened' in result:
                print(f"   ✅ Opened {result['opened'].action} trade (ID: {result['opened'].id})")
            
            if 'closed' in result and result['closed']:
                for closed_trade in result['closed']:
                    pnl = closed_trade.profit_loss
                    print(f"   💰 Closed {closed_trade.action} trade with P&L: ${pnl:,.2f}")
            
            results.append(result)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            session.rollback()
            continue
    
    session.commit()
    
    # Show final statistics
    print("\n\n📈 FINAL STATISTICS")
    print("="*80)
    
    total_trades = session.query(Trade).count()
    open_trades = session.query(Trade).filter(Trade.status == 'OPEN').count()
    closed_trades = session.query(Trade).filter(Trade.status == 'CLOSED').count()
    
    from sqlalchemy import func
    total_pnl = session.query(func.sum(Trade.profit_loss)).filter(
        Trade.status == 'CLOSED'
    ).scalar() or 0
    
    print(f"Total Trades: {total_trades}")
    print(f"Open Positions: {open_trades}")
    print(f"Closed Trades: {closed_trades}")
    print(f"Total P&L: ${total_pnl:,.2f}")
    
    # Show current open trades
    if open_trades > 0:
        print("\n\n🔹 CURRENT OPEN POSITIONS:")
        print("-"*80)
        open_positions = session.query(Trade).filter(Trade.status == 'OPEN').all()
        for trade in open_positions:
            print(f"   {trade.symbol} {trade.action} - Qty: {trade.quantity} @ ${trade.open_price:,.2f}")
            print(f"   Opened: {trade.open_time}")

finally:
    session.close()

print("\n✅ DONE! Check your dashboard now - it should show REAL trading data!")
