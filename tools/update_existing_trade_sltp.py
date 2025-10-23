"""
Update existing open trades with Stop Loss and Take Profit values.
This is a one-time fix for trades that were created before SL/TP calculation was added.
"""

import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.session import SessionLocal
from src.models.base import Trade
from sqlalchemy import select

# Risk Management Parameters (same as trading_service.py)
STOP_LOSS_PERCENT = Decimal("0.01")  # 1% stop loss
TAKE_PROFIT_PERCENT = Decimal("0.02")  # 2% take profit


def update_open_trades_sltp():
    """Update all open trades that don't have SL/TP set."""
    session = SessionLocal()
    
    try:
        # Find all open trades without SL or TP
        query = select(Trade).where(
            Trade.status == "OPEN"
        )
        
        open_trades = session.execute(query).scalars().all()
        
        if not open_trades:
            print("No open trades found.")
            return
        
        print(f"Found {len(open_trades)} open trade(s):")
        print("-" * 80)
        
        updated_count = 0
        
        for trade in open_trades:
            needs_update = False
            
            # Check if SL/TP need to be set
            if trade.stop_loss is None or trade.take_profit is None:
                needs_update = True
                
                # Calculate SL/TP based on direction
                price = trade.open_price
                
                if trade.action == "BUY":
                    # For BUY: SL below entry, TP above entry
                    stop_loss = price * (Decimal("1") - STOP_LOSS_PERCENT)
                    take_profit = price * (Decimal("1") + TAKE_PROFIT_PERCENT)
                else:  # SELL
                    # For SELL: SL above entry, TP below entry
                    stop_loss = price * (Decimal("1") + STOP_LOSS_PERCENT)
                    take_profit = price * (Decimal("1") - TAKE_PROFIT_PERCENT)
                
                # Update the trade
                trade.stop_loss = stop_loss
                trade.take_profit = take_profit
                
                print(f"Trade ID: {trade.id}")
                print(f"  Symbol: {trade.symbol}")
                print(f"  Action: {trade.action}")
                print(f"  Entry Price: ${float(trade.open_price):,.2f}")
                print(f"  Stop Loss: ${float(stop_loss):,.2f} ({STOP_LOSS_PERCENT * 100}%)")
                print(f"  Take Profit: ${float(take_profit):,.2f} ({TAKE_PROFIT_PERCENT * 100}%)")
                print(f"  Status: UPDATED")
                print("-" * 80)
                
                updated_count += 1
            else:
                print(f"Trade ID: {trade.id} - Already has SL/TP set (skipped)")
        
        # Commit changes
        if updated_count > 0:
            session.commit()
            print(f"\nSuccessfully updated {updated_count} trade(s)!")
        else:
            print("\nNo trades needed updating.")
            
    except Exception as e:
        session.rollback()
        print(f"Error updating trades: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 80)
    print("Updating Open Trades with Stop Loss and Take Profit")
    print("=" * 80)
    update_open_trades_sltp()
