from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=True)


class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String, nullable=False)  # BUY or SELL
    symbol = Column(String, nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    open_price = Column(Numeric(30, 8), nullable=False)
    open_time = Column(DateTime(timezone=True), server_default=func.now())
    close_price = Column(Numeric(30, 8), nullable=True)
    close_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default='OPEN')  # OPEN or CLOSED
    total_cost = Column(Numeric(40, 8), nullable=True)
    profit_loss = Column(Numeric(40, 8), nullable=True)
    # Stop Loss and Take Profit
    stop_loss = Column(Numeric(30, 8), nullable=True)
    take_profit = Column(Numeric(30, 8), nullable=True)
    # Risk management fields
    allocated_fund = Column(Numeric(40, 8), nullable=True)
    risk_amount = Column(Numeric(40, 8), nullable=True)  # Max 2% risk
    stop_loss_triggered = Column(Boolean, default=False)
    closed_by_user = Column(Boolean, default=False)  # Manual close vs automatic
    # Order details
    order_type = Column(String, default='MARKET')  # MARKET or LIMIT
    limit_price = Column(Numeric(30, 8), nullable=True)  # For limit orders


class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=True)
    symbol = Column(String, nullable=True)
    action = Column(String, nullable=True)
    price = Column(Numeric(30, 8), nullable=True)
    raw = Column(String, nullable=True)
    # Signal validation and management
    status = Column(String, default='PENDING')  # PENDING, VALIDATED, EXECUTED, REJECTED, FALSE
    validated_by = Column(String, nullable=True)  # User/system that validated
    validation_notes = Column(String, nullable=True)  # Reason for rejection/validation
    confidence_score = Column(Float, nullable=True)  # 0-100 confidence level
    executed_at = Column(DateTime(timezone=True), nullable=True)  # When trade was placed
    trade_id = Column(Integer, ForeignKey('trades.id'), nullable=True)  # Linked trade
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IdempotencyKey(Base):
    __tablename__ = 'idempotency_keys'
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AllowedInstrument(Base):
    """Admin-managed list of instruments allowed for trading."""
    __tablename__ = 'allowed_instruments'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)  # e.g., BTCUSDT
    name = Column(String, nullable=True)  # Display name, e.g., "Bitcoin"
    instrument_type = Column(String, default='crypto')  # crypto, forex, stock
    base_currency = Column(String, nullable=True)  # BTC, EUR, etc.
    quote_currency = Column(String, nullable=True)  # USDT, USD, etc.
    price_precision = Column(Integer, default=2)  # Decimal places for price
    quantity_precision = Column(Integer, default=8)  # Decimal places for qty
    min_quantity = Column(Numeric(20, 8), default=0.001)  # Min trade size
    max_quantity = Column(Numeric(20, 8), nullable=True)  # Max trade size
    enabled = Column(Boolean, default=True)  # Can be disabled without deletion
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SystemSettings(Base):
    """Global system configuration."""
    __tablename__ = 'system_settings'
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)
    value_type = Column(String, default='string')  # string, boolean, float, int
    description = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FundAllocation(Base):
    """Track fund allocation and risk per instrument."""
    __tablename__ = 'fund_allocations'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    allocated_amount = Column(Numeric(40, 8), nullable=False)
    used_amount = Column(Numeric(40, 8), default=0)  # Currently in open trades
    total_loss = Column(Numeric(40, 8), default=0)  # Cumulative loss for risk check
    risk_limit = Column(Numeric(40, 8), nullable=False)  # 2% of allocated
    trading_enabled = Column(Boolean, default=True)  # Auto-disabled if loss > risk_limit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PriceHistory(Base):
    """Store historical OHLCV (Open, High, Low, Low, Close, Volume) price data."""
    __tablename__ = 'price_history'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, index=True)  # e.g., BTCUSDT
    timeframe = Column(String, nullable=False, index=True)  # 1m, 5m, 15m, 1h, 4h, 1d
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Numeric(30, 8), nullable=False)
    high_price = Column(Numeric(30, 8), nullable=False)
    low_price = Column(Numeric(30, 8), nullable=False)
    close_price = Column(Numeric(30, 8), nullable=False)
    volume = Column(Numeric(40, 8), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite unique constraint to prevent duplicates
    __table_args__ = (
        {'schema': None, 'extend_existing': True},
    )


class HistoricalPrice(Base):
    """Store real-time tick data (every second) for enabled symbols."""
    __tablename__ = 'historical_prices'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, index=True)  # e.g., BTCUSD, ETHUSD
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    bid_price = Column(Numeric(30, 8), nullable=False)  # Best bid
    ask_price = Column(Numeric(30, 8), nullable=False)  # Best ask
    mid_price = Column(Numeric(30, 8), nullable=False)  # (bid + ask) / 2
    spread = Column(Numeric(30, 8), nullable=False)  # ask - bid
    spread_pct = Column(Numeric(10, 4), nullable=False)  # spread / mid * 100
    volume_bid = Column(Numeric(40, 8), nullable=True)  # Volume at best bid
    volume_ask = Column(Numeric(40, 8), nullable=True)  # Volume at best ask
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite unique constraint to prevent duplicates
    __table_args__ = (
        {'schema': None, 'extend_existing': True},
    )

