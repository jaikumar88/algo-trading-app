"""
Database Seed Script for Mock Trading Data
Seeds instruments and OHLCV (candlestick) data
"""
import sys
import os

# Load .env file before anything else
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from datetime import datetime, timedelta
import random
from src.database.session import SessionLocal
from src.models.base import AllowedInstrument, PriceHistory


def seed_instruments():
    """Seed popular trading instruments."""
    session = SessionLocal()
    
    instruments = [
        # Crypto pairs
        {
            'symbol': 'BTCUSDT',
            'name': 'Bitcoin',
            'instrument_type': 'crypto',
            'base_currency': 'BTC',
            'quote_currency': 'USDT',
            'price_precision': 2,
            'quantity_precision': 6,
            'min_quantity': Decimal('0.00001'),
            'max_quantity': Decimal('100'),
            'enabled': True
        },
        {
            'symbol': 'ETHUSDT',
            'name': 'Ethereum',
            'instrument_type': 'crypto',
            'base_currency': 'ETH',
            'quote_currency': 'USDT',
            'price_precision': 2,
            'quantity_precision': 5,
            'min_quantity': Decimal('0.0001'),
            'max_quantity': Decimal('1000'),
            'enabled': True
        },
        {
            'symbol': 'BNBUSDT',
            'name': 'Binance Coin',
            'instrument_type': 'crypto',
            'base_currency': 'BNB',
            'quote_currency': 'USDT',
            'price_precision': 2,
            'quantity_precision': 4,
            'min_quantity': Decimal('0.001'),
            'max_quantity': Decimal('1000'),
            'enabled': True
        },
        {
            'symbol': 'XRPUSDT',
            'name': 'Ripple',
            'instrument_type': 'crypto',
            'base_currency': 'XRP',
            'quote_currency': 'USDT',
            'price_precision': 4,
            'quantity_precision': 2,
            'min_quantity': Decimal('1'),
            'max_quantity': Decimal('100000'),
            'enabled': True
        },
        {
            'symbol': 'SOLUSDT',
            'name': 'Solana',
            'instrument_type': 'crypto',
            'base_currency': 'SOL',
            'quote_currency': 'USDT',
            'price_precision': 2,
            'quantity_precision': 3,
            'min_quantity': Decimal('0.01'),
            'max_quantity': Decimal('10000'),
            'enabled': True
        },
        # Forex pairs
        {
            'symbol': 'EURUSD',
            'name': 'Euro / US Dollar',
            'instrument_type': 'forex',
            'base_currency': 'EUR',
            'quote_currency': 'USD',
            'price_precision': 5,
            'quantity_precision': 2,
            'min_quantity': Decimal('0.01'),
            'max_quantity': Decimal('10000'),
            'enabled': True
        },
        {
            'symbol': 'GBPUSD',
            'name': 'British Pound / US Dollar',
            'instrument_type': 'forex',
            'base_currency': 'GBP',
            'quote_currency': 'USD',
            'price_precision': 5,
            'quantity_precision': 2,
            'min_quantity': Decimal('0.01'),
            'max_quantity': Decimal('10000'),
            'enabled': True
        },
        {
            'symbol': 'USDJPY',
            'name': 'US Dollar / Japanese Yen',
            'instrument_type': 'forex',
            'base_currency': 'USD',
            'quote_currency': 'JPY',
            'price_precision': 3,
            'quantity_precision': 2,
            'min_quantity': Decimal('0.01'),
            'max_quantity': Decimal('10000'),
            'enabled': True
        },
        # Commodities
        {
            'symbol': 'XAUUSD',
            'name': 'Gold / US Dollar',
            'instrument_type': 'commodity',
            'base_currency': 'XAU',
            'quote_currency': 'USD',
            'price_precision': 2,
            'quantity_precision': 3,
            'min_quantity': Decimal('0.01'),
            'max_quantity': Decimal('1000'),
            'enabled': True
        },
        {
            'symbol': 'XAGUSD',
            'name': 'Silver / US Dollar',
            'instrument_type': 'commodity',
            'base_currency': 'XAG',
            'quote_currency': 'USD',
            'price_precision': 3,
            'quantity_precision': 2,
            'min_quantity': Decimal('0.1'),
            'max_quantity': Decimal('10000'),
            'enabled': True
        }
    ]
    
    added_count = 0
    for inst_data in instruments:
        # Check if already exists
        existing = session.query(AllowedInstrument).filter(
            AllowedInstrument.symbol == inst_data['symbol']
        ).first()
        
        if not existing:
            instrument = AllowedInstrument(**inst_data)
            session.add(instrument)
            added_count += 1
            print(f"✓ Added instrument: {inst_data['symbol']} - {inst_data['name']}")
        else:
            print(f"⊘ Skipped (exists): {inst_data['symbol']}")
    
    session.commit()
    session.close()
    
    print(f"\n✅ Seeded {added_count} new instruments")
    return added_count


def generate_realistic_candles(
    base_price,
    num_candles,
    volatility=0.02,
    trend=0.0001
):
    """
    Generate realistic OHLCV candlestick data.
    
    Args:
        base_price: Starting price
        num_candles: Number of candles to generate
        volatility: Price volatility (0.02 = 2% typical movement)
        trend: Upward/downward trend (0.0001 = slight uptrend)
    
    Returns:
        List of (open, high, low, close, volume) tuples
    """
    candles = []
    current_price = base_price
    
    for i in range(num_candles):
        # Add trend
        current_price *= (1 + trend)
        
        # Open price (with small gap from previous close)
        if i == 0:
            open_price = current_price
        else:
            gap = random.uniform(-0.001, 0.001)  # 0.1% gap
            open_price = current_price * (1 + gap)
        
        # Price movement during candle
        movement = random.uniform(-volatility, volatility)
        close_price = open_price * (1 + movement)
        
        # High and low
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.01)
        low_price = min(open_price, close_price) * random.uniform(0.99, 1.0)
        
        # Volume (random with some correlation to price movement)
        base_volume = random.uniform(100, 1000)
        volume_multiplier = 1 + abs(movement) * 10
        volume = base_volume * volume_multiplier
        
        candles.append((
            round(float(open_price), 2),
            round(float(high_price), 2),
            round(float(low_price), 2),
            round(float(close_price), 2),
            round(volume, 2)
        ))
        
        # Update current price for next candle
        current_price = close_price
    
    return candles


def seed_ohlcv_data(days_back=30):
    """
    Seed OHLCV data for all instruments.
    
    Args:
        days_back: Number of days of historical data to generate
    """
    session = SessionLocal()
    
    # Get all instruments
    instruments = session.query(AllowedInstrument).filter(
        AllowedInstrument.enabled == True
    ).all()
    
    if not instruments:
        print("❌ No instruments found. Run seed_instruments() first.")
        return
    
    # Timeframe configurations
    timeframes = {
        '1m': {'minutes': 1, 'candles_per_day': 1440},
        '5m': {'minutes': 5, 'candles_per_day': 288},
        '15m': {'minutes': 15, 'candles_per_day': 96},
        '1h': {'minutes': 60, 'candles_per_day': 24},
        '4h': {'minutes': 240, 'candles_per_day': 6},
        '1d': {'minutes': 1440, 'candles_per_day': 1}
    }
    
    # Base prices for each instrument type
    base_prices = {
        'BTCUSDT': 43000,
        'ETHUSDT': 2300,
        'BNBUSDT': 310,
        'XRPUSDT': 0.52,
        'SOLUSDT': 105,
        'EURUSD': 1.0850,
        'GBPUSD': 1.2650,
        'USDJPY': 148.50,
        'XAUUSD': 2050,
        'XAGUSD': 24.50
    }
    
    total_candles = 0
    
    for instrument in instruments:
        print(f"\n📊 Generating data for {instrument.symbol}...")
        
        base_price = base_prices.get(instrument.symbol, 100)
        
        for tf_name, tf_config in timeframes.items():
            # Calculate number of candles needed
            total_candles_needed = tf_config['candles_per_day'] * days_back
            
            # Check if data already exists
            existing_count = session.query(PriceHistory).filter(
                PriceHistory.symbol == instrument.symbol,
                PriceHistory.timeframe == tf_name
            ).count()
            
            if existing_count >= total_candles_needed * 0.8:
                print(f"  ⊘ Skipped {tf_name} (sufficient data exists)")
                continue
            
            # Generate candle data
            candles = generate_realistic_candles(
                base_price,
                total_candles_needed,
                volatility=0.02 if instrument.instrument_type == 'crypto' else 0.01,
                trend=0.0001  # Slight uptrend
            )
            
            # Calculate timestamps (going backwards from now)
            now = datetime.utcnow()
            
            for i, (open_p, high, low, close, volume) in enumerate(candles):
                # Calculate timestamp for this candle
                candle_index = total_candles_needed - i - 1
                timestamp = now - timedelta(
                    minutes=candle_index * tf_config['minutes']
                )
                
                # Check if this timestamp already exists
                existing = session.query(PriceHistory).filter(
                    PriceHistory.symbol == instrument.symbol,
                    PriceHistory.timeframe == tf_name,
                    PriceHistory.timestamp == timestamp
                ).first()
                
                if not existing:
                    candle_record = PriceHistory(
                        symbol=instrument.symbol,
                        timeframe=tf_name,
                        timestamp=timestamp,
                        open_price=Decimal(str(open_p)),
                        high_price=Decimal(str(high)),
                        low_price=Decimal(str(low)),
                        close_price=Decimal(str(close)),
                        volume=Decimal(str(volume))
                    )
                    session.add(candle_record)
                    total_candles += 1
            
            # Commit after each timeframe
            session.commit()
            print(f"  ✓ Generated {total_candles_needed} candles for {tf_name}")
    
    session.close()
    print(f"\n✅ Seeded {total_candles} total candles across all instruments and timeframes")


def main():
    """Run all seed functions."""
    print("🌱 Starting database seed...\n")
    print("=" * 60)
    
    # Seed instruments first
    print("\n📋 STEP 1: Seeding Instruments")
    print("-" * 60)
    seed_instruments()
    
    # Seed OHLCV data
    print("\n" + "=" * 60)
    print("📊 STEP 2: Seeding OHLCV Data (30 days)")
    print("-" * 60)
    print("⏳ This may take a few minutes...")
    seed_ohlcv_data(days_back=30)
    
    print("\n" + "=" * 60)
    print("✅ Database seeding complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
