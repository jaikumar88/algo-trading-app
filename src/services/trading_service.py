from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.session import SessionLocal
from src.models.base import Trade


FIXED_QTY = Decimal("100")

# Risk Management Parameters
STOP_LOSS_PERCENT = Decimal("0.01")  # 1% stop loss
TAKE_PROFIT_PERCENT = Decimal("0.02")  # 2% take profit


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
        """Handle incoming trade signal with enhanced same-direction logic.
        
        Enhanced Logic:
        1. If signal is same direction as existing open trade → IGNORE (no action)
        2. If signal is opposite direction → CLOSE existing + OPEN new
        3. If no existing trade → OPEN new trade
        """
        session = self._get_session()
        side = side.upper()
        
        if side not in ("BUY", "SELL"):
            raise ValueError(f"Unknown side: {side}. Must be BUY or SELL.")
        
        # Check existing trades and apply enhanced logic
        return self._smart_signal_handler(session, user_id, symbol, side, price)

    def _smart_signal_handler(
        self,
        session: Session,
        user_id: int | None,
        symbol: str,
        new_side: str,
        price: Decimal,
    ):
        """Enhanced signal handling - ALWAYS close opposite trades immediately.
        
        Logic:
        1. If existing trade is SAME direction as signal → IGNORE signal
        2. If existing trade is OPPOSITE direction → IMMEDIATELY CLOSE existing + OPEN new (ignore SL/TP)
        3. If NO existing trade → OPEN new trade
        
        IMPORTANT: When opposite signal is received, the system IMMEDIATELY closes the open trade
        at current market price, bypassing stop loss and take profit levels.
        
        Args:
            session: Database session
            user_id: User ID (optional)
            symbol: Trading instrument symbol
            new_side: New signal side (BUY or SELL)
            price: Current price (used as immediate close price for opposite trades)
            
        Returns:
            dict with action taken and details
        """
        created_locally = self._session is None
        
        try:
            if created_locally:
                session.begin()
            
            # Find existing open trades for this symbol
            q = select(Trade).where(
                Trade.symbol == symbol,
                Trade.status == "OPEN"
            ).with_for_update()
            existing_trades = session.execute(q).scalars().all()
            
            if not existing_trades:
                # No existing trades - open new trade
                new_trade = self._open_new_trade(session, user_id, symbol, new_side, price)
                if created_locally:
                    session.commit()
                    session.refresh(new_trade)
                else:
                    session.flush()
                    session.refresh(new_trade)
                
                return {
                    "action": "opened",
                    "closed": [],
                    "opened": new_trade,
                    "message": f"No existing trades - opened new {new_side} position for {symbol}"
                }
            
            # Check if any existing trade is in the same direction
            same_direction_trades = [t for t in existing_trades if t.action == new_side]
            opposite_trades = [t for t in existing_trades if t.action != new_side]
            
            if same_direction_trades:
                # Same direction signal - IGNORE
                if created_locally:
                    session.rollback()  # No changes needed
                
                return {
                    "action": "ignored",
                    "closed": [],
                    "opened": None,
                    "message": f"Ignored {new_side} signal - already have {len(same_direction_trades)} open {new_side} position(s) for {symbol}"
                }
            
            elif opposite_trades:
                # Opposite direction - IMMEDIATELY close existing at current price and open new
                print(f"[SIGNAL] Opposite {new_side} signal received - IMMEDIATELY closing {len(opposite_trades)} open {opposite_trades[0].action} trade(s) at current price {price}")
                return self._close_opposite_and_open_new(session, user_id, symbol, new_side, price, opposite_trades, created_locally)
                
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

    def _close_opposite_and_open_new(
        self,
        session: Session,
        user_id: int | None,
        symbol: str,
        new_side: str,
        price: Decimal,
        opposite_trades: list,
        created_locally: bool
    ):
        """IMMEDIATELY close opposite trades at current market price and open new trade.
        
        This method bypasses stop loss and take profit levels - when an opposite signal
        is received, it IMMEDIATELY closes the existing trade at the current market price.
        """
        closed = []
        
        # Close all opposite trades IMMEDIATELY at current market price
        for trade in opposite_trades:
            # Store original SL/TP for logging
            original_sl = trade.stop_loss
            original_tp = trade.take_profit
            
            # IMMEDIATE CLOSE at current market price (bypass SL/TP)
            trade.close_price = price
            trade.close_time = datetime.utcnow()
            trade.status = "CLOSED"
            
            # Calculate P&L based on actual close price
            close_amount = price * trade.quantity
            open_amount = trade.total_cost or (trade.open_price * trade.quantity)
            
            if trade.action == "BUY":
                trade.profit_loss = close_amount - open_amount
            else:
                trade.profit_loss = open_amount - close_amount
            
            session.add(trade)
            closed.append(trade)
            
            # Enhanced logging to show immediate closure
            print(f"[IMMEDIATE CLOSE] {trade.action} trade for {symbol}")
            print(f"  - Entry Price: {trade.open_price}")
            print(f"  - Original SL: {original_sl} | Original TP: {original_tp}")
            print(f"  - CLOSED AT: {price} (MARKET PRICE - BYPASSED SL/TP)")
            print(f"  - P&L: {trade.profit_loss}")
        
        # Open new trade with fresh SL/TP levels
        new_trade = self._open_new_trade(session, user_id, symbol, new_side, price)
        
        if created_locally:
            session.commit()
            session.refresh(new_trade)
        else:
            session.flush()
            session.refresh(new_trade)
        
        return {
            "action": "immediate_close_and_open",
            "closed": closed,
            "opened": new_trade,
            "message": f"IMMEDIATELY closed {len(closed)} opposite {opposite_trades[0].action} trade(s) at market price {price}, opened new {new_side} trade for {symbol}"
        }

    def _open_new_trade(self, session: Session, user_id: int | None, symbol: str, side: str, price: Decimal):
        """Create and add a new trade to the session with SL/TP."""
        # Calculate Stop Loss and Take Profit based on direction
        if side == "BUY":
            # For BUY: SL below entry, TP above entry
            stop_loss = price * (Decimal("1") - STOP_LOSS_PERCENT)
            take_profit = price * (Decimal("1") + TAKE_PROFIT_PERCENT)
        else:  # SELL
            # For SELL: SL above entry, TP below entry
            stop_loss = price * (Decimal("1") + STOP_LOSS_PERCENT)
            take_profit = price * (Decimal("1") - TAKE_PROFIT_PERCENT)
        
        new_trade = Trade(
            user_id=user_id,
            action=side,
            symbol=symbol,
            quantity=FIXED_QTY,
            open_price=price,
            total_cost=price * FIXED_QTY,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status="OPEN",
        )
        session.add(new_trade)
        print(f"[UP] Opened new {side} trade for {symbol} at {price} (SL: {stop_loss}, TP: {take_profit})")
        return new_trade

    def _close_opposite_and_open(
        self,
        session: Session,
        user_id: int | None,
        symbol: str,
        new_side: str,
        price: Decimal,
    ):
        """DEPRECATED: Close any open trades with opposite action, then open new trade.
        
        This is the old method - kept for compatibility but not used in new logic.
        Use _smart_signal_handler instead.
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
                print(f"[WARN] WARNING: Found {len(all_open_trades)} open trades for {symbol}. Closing all to prevent duplicates.")
            
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
                    print(f"[OK] Closed opposite {trade.action} trade for {symbol} at {price} (P&L: {trade.profit_loss})")
                else:
                    print(f"[WARN] Closed duplicate {trade.action} trade for {symbol} at {price} (P&L: {trade.profit_loss})")
            
            # Open new trade with the new signal
            # Calculate Stop Loss and Take Profit
            if new_side == "BUY":
                stop_loss = price * (Decimal("1") - STOP_LOSS_PERCENT)
                take_profit = price * (Decimal("1") + TAKE_PROFIT_PERCENT)
            else:  # SELL
                stop_loss = price * (Decimal("1") + STOP_LOSS_PERCENT)
                take_profit = price * (Decimal("1") - TAKE_PROFIT_PERCENT)
            
            new_trade = Trade(
                user_id=user_id,
                action=new_side,
                symbol=symbol,
                quantity=FIXED_QTY,
                open_price=price,
                total_cost=price * FIXED_QTY,
                stop_loss=stop_loss,
                take_profit=take_profit,
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

