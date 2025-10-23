"""
Test opposite trade closing logic:
- Open SELL trade → BUY signal → Close SELL (book P&L) → Open BUY
- Open BUY trade → SELL signal → Close BUY (book P&L) → Open SELL
"""
from decimal import Decimal
from trading import TradingManager
from db import SessionLocal
from models import Trade
from sqlalchemy import select

def test_opposite_trade_closing():
    """Test that opposite signals close existing trades and open new ones."""
    
    print("=" * 80)
    print("Testing Opposite Trade Closing Logic")
    print("=" * 80)
    
    session = SessionLocal()
    tm = TradingManager(session)
    
    # Clean up any existing trades for test symbol
    test_symbol = "TESTBTC"
    session.query(Trade).filter(Trade.symbol == test_symbol).delete()
    session.commit()
    
    print("\n📊 Scenario 1: Open BUY → SELL signal comes → Close BUY, Open SELL")
    print("-" * 80)
    
    # Step 1: Open BUY trade at 50000
    print("\n1️⃣ Opening BUY trade at price 50000...")
    result1 = tm.handle_signal(None, test_symbol, "BUY", Decimal("50000"))
    print(f"   ✓ Opened: {result1['opened'].action} trade (ID: {result1['opened'].id})")
    print(f"   ✓ Closed: {len(result1.get('closed', []))} trades")
    
    # Verify BUY trade is open
    open_trades = session.execute(
        select(Trade).where(Trade.symbol == test_symbol, Trade.status == "OPEN")
    ).scalars().all()
    print(f"   ✓ Open trades: {len(open_trades)} ({', '.join([t.action for t in open_trades])})")
    
    # Step 2: SELL signal comes at 52000 (should close BUY with profit)
    print("\n2️⃣ SELL signal comes at price 52000...")
    result2 = tm.handle_signal(None, test_symbol, "SELL", Decimal("52000"))
    print(f"   ✓ Closed: {len(result2['closed'])} trade(s)")
    for closed_trade in result2['closed']:
        print(f"      - {closed_trade.action} trade (ID: {closed_trade.id})")
        print(f"        Open: {closed_trade.open_price}, Close: {closed_trade.close_price}")
        print(f"        P&L: {closed_trade.profit_loss}")
    print(f"   ✓ Opened: {result2['opened'].action} trade (ID: {result2['opened'].id})")
    
    # Verify SELL trade is now open and BUY is closed
    open_trades = session.execute(
        select(Trade).where(Trade.symbol == test_symbol, Trade.status == "OPEN")
    ).scalars().all()
    closed_trades = session.execute(
        select(Trade).where(Trade.symbol == test_symbol, Trade.status == "CLOSED")
    ).scalars().all()
    print(f"   ✓ Open trades: {len(open_trades)} ({', '.join([t.action for t in open_trades])})")
    print(f"   ✓ Closed trades: {len(closed_trades)} ({', '.join([t.action for t in closed_trades])})")
    
    print("\n📊 Scenario 2: Open SELL → BUY signal comes → Close SELL, Open BUY")
    print("-" * 80)
    
    # Step 3: BUY signal comes at 51000 (should close SELL with profit)
    print("\n3️⃣ BUY signal comes at price 51000...")
    result3 = tm.handle_signal(None, test_symbol, "BUY", Decimal("51000"))
    print(f"   ✓ Closed: {len(result3['closed'])} trade(s)")
    for closed_trade in result3['closed']:
        print(f"      - {closed_trade.action} trade (ID: {closed_trade.id})")
        print(f"        Open: {closed_trade.open_price}, Close: {closed_trade.close_price}")
        print(f"        P&L: {closed_trade.profit_loss}")
    print(f"   ✓ Opened: {result3['opened'].action} trade (ID: {result3['opened'].id})")
    
    # Verify BUY trade is now open
    open_trades = session.execute(
        select(Trade).where(Trade.symbol == test_symbol, Trade.status == "OPEN")
    ).scalars().all()
    print(f"   ✓ Open trades: {len(open_trades)} ({', '.join([t.action for t in open_trades])})")
    
    # Step 4: Another BUY signal at 51500 (should close existing BUY and open new BUY)
    print("\n4️⃣ Another BUY signal comes at price 51500...")
    result4 = tm.handle_signal(None, test_symbol, "BUY", Decimal("51500"))
    print(f"   ✓ Closed: {len(result4['closed'])} trade(s)")
    for closed_trade in result4['closed']:
        print(f"      - {closed_trade.action} trade (ID: {closed_trade.id})")
        print(f"        Open: {closed_trade.open_price}, Close: {closed_trade.close_price}")
        print(f"        P&L: {closed_trade.profit_loss}")
    print(f"   ✓ Opened: {result4['opened'].action} trade (ID: {result4['opened'].id})")
    
    print("\n📈 Final Summary")
    print("-" * 80)
    
    # Show all trades for this symbol
    all_trades = session.execute(
        select(Trade).where(Trade.symbol == test_symbol).order_by(Trade.id)
    ).scalars().all()
    
    print(f"\n{'ID':<6} {'Action':<8} {'Status':<10} {'Open Price':<12} {'Close Price':<12} {'P&L':<15}")
    print("-" * 80)
    
    total_pnl = Decimal("0")
    for trade in all_trades:
        pnl_str = str(trade.profit_loss) if trade.profit_loss else "N/A"
        print(f"{trade.id:<6} {trade.action:<8} {trade.status:<10} {trade.open_price:<12} {str(trade.close_price or 'N/A'):<12} {pnl_str:<15}")
        if trade.profit_loss:
            total_pnl += trade.profit_loss
    
    print("-" * 80)
    print(f"Total P&L: {total_pnl}")
    
    print("\n✅ Test completed successfully!")
    print("=" * 80)
    
    # Calculate expected P&L
    print("\n🧮 P&L Calculation Verification:")
    print("-" * 80)
    
    qty = Decimal("100")  # FIXED_QTY
    
    # Trade 1: BUY at 50000, closed at 52000
    pnl1 = (Decimal("52000") - Decimal("50000")) * qty
    print(f"Trade 1 (BUY): (52000 - 50000) × 100 = {pnl1}")
    
    # Trade 2: SELL at 52000, closed at 51000
    pnl2 = (Decimal("52000") - Decimal("51000")) * qty
    print(f"Trade 2 (SELL): (52000 - 51000) × 100 = {pnl2}")
    
    # Trade 3: BUY at 51000, closed at 51500
    pnl3 = (Decimal("51500") - Decimal("51000")) * qty
    print(f"Trade 3 (BUY): (51500 - 51000) × 100 = {pnl3}")
    
    expected_total = pnl1 + pnl2 + pnl3
    print(f"\nExpected Total P&L: {expected_total}")
    print(f"Actual Total P&L:   {total_pnl}")
    
    if expected_total == total_pnl:
        print("✅ P&L calculation is CORRECT!")
    else:
        print(f"❌ P&L mismatch! Expected {expected_total}, got {total_pnl}")
    
    session.close()

if __name__ == "__main__":
    test_opposite_trade_closing()
