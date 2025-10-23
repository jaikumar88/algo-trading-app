from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Trade


FIXED_QTY = Decimal("100")


class TradingManager:
    """Advanced trading manager with opposite position closing logic.

    When a signal arrives:
    1. Check for existing OPEN trades for the same instrument
    2. If an opposite position exists (BUY signal with open SELL, or vice versa):
       - Close the opposite position
       - Book profit/loss
    3. Open a new trade with the new signal
    
    Examples:
    - Open SELL trade exists → BUY signal comes → Close SELL, book P&L, open BUY
    - Open BUY trade exists → SELL signal comes → Close BUY, book P&L, open SELL
    """

    def __init__(self, session: Session | None = None):
        self._session = session

    def _get_session(self):
        return self._session or SessionLocal()

    def handle_signal(self,
                      user_id: int | None,
                      symbol: str,
                      side: str,
                      price: Decimal,
                      ):
        """Handle incoming trade signal with opposite position closing logic."""
        session = self._get_session()
        side = side.upper()
        
        if side not in ("BUY", "SELL"):
            raise ValueError(f"Unknown side: {side}. Must be BUY or SELL.")
        
        # Close any opposite open trades first, then open new trade
        return self._close_opposite_and_open(session, user_id, symbol, side, price)

    def _close_opposite_and_open(
        self,
        session: Session,
        user_id: int | None,
        symbol: str,
        new_side: str,
        price: Decimal,
    ):
        """Close any open trades with opposite action, then open new trade.
        
        CRITICAL: This method ensures only ONE open trade per instrument at any time.
        It closes ALL existing open trades (both opposite and same direction) before
        opening a new trade to prevent race conditions and duplicate positions.
        
        Args:
            session: Database session
            user_id: User ID (optional)
            symbol: Trading instrument symbol
            new_side: New signal side (BUY or SELL)
            price: Current price
            
        Returns:
            dict with 'closed' (list of closed trades) and 'opened' (new trade)
        """
        created_locally = self._session is None
        closed = []
        
        try:
            # Only start a new transaction if we created the session locally
            if created_locally:
                session.begin()
            
            # Determine opposite side
            opposite_side = "SELL" if new_side == "BUY" else "BUY"
            
            # Find ALL open trades for this symbol (both opposite AND same direction)
            # This prevents race conditions where BUY and SELL signals arrive simultaneously
            q = select(Trade).where(
                Trade.symbol == symbol,
                Trade.status == "OPEN"
            ).with_for_update()  # Lock rows to prevent concurrent modifications
            all_open_trades = session.execute(q).scalars().all()
            
            # Log warning if multiple trades detected
            if len(all_open_trades) > 1:
                print(f"⚠️ WARNING: Found {len(all_open_trades)} open trades for {symbol}. Closing all to prevent duplicates.")
            
            # Find opposite trades specifically for logging
            opposite_trades = [t for t in all_open_trades if t.action == opposite_side]
            
            # Close ALL open trades for this symbol (prevents duplicate positions)
            
            # Close ALL open trades for this symbol (prevents duplicate positions)
            for trade in all_open_trades:
                trade.close_price = price
                trade.close_time = datetime.utcnow()
                trade.status = "CLOSED"
                
                # Calculate P&L
                close_amount = price * trade.quantity
                open_amount = trade.total_cost or (trade.open_price * trade.quantity)
                
                if trade.action == "BUY":
                    # BUY trade: profit = (close_price - open_price) * quantity
                    trade.profit_loss = close_amount - open_amount
                else:
                    # SELL trade: profit = (open_price - close_price) * quantity
                    trade.profit_loss = open_amount - close_amount
                
                session.add(trade)
                closed.append(trade)
                
                if trade.action == opposite_side:
                    print(f"✅ Closed opposite {trade.action} trade for {symbol} at {price} (P&L: {trade.profit_loss})")
                else:
                    print(f"⚠️ Closed duplicate {trade.action} trade for {symbol} at {price} (P&L: {trade.profit_loss})")
            
            # Open new trade with the new signal
            new_trade = Trade(
                user_id=user_id,
                action=new_side,
                symbol=symbol,
                quantity=FIXED_QTY,
                open_price=price,
                total_cost=price * FIXED_QTY,
                status="OPEN",
            )
            session.add(new_trade)
            
            # Commit if we created the session locally
            if created_locally:
                session.commit()
                session.refresh(new_trade)
            else:
                # If using external session, flush to get IDs but don't commit
                session.flush()
                session.refresh(new_trade)
            
            return {
                "closed": closed,
                "opened": new_trade,
                "message": f"Closed {len(closed)} opposite trade(s), opened new {new_side} trade"
            }
        except Exception:
            if created_locally:
                session.rollback()
            raise
        finally:
            if created_locally:
                try:
                    session.close()
                except Exception:
                    pass

