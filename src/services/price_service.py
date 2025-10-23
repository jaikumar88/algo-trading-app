"""
Service for collecting and managing historical price data.
Supports both real Binance API and mock data generation.
"""
import requests
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.base import PriceHistory, AllowedInstrument


class PriceHistoryService:
    """Service to fetch, store, and retrieve historical price data."""
    
    BINANCE_API_BASE = "https://api.binance.com/api/v3"
    
    TIMEFRAME_INTERVALS = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440,
    }
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def fetch_binance_klines(self, symbol: str, timeframe: str = '1h', limit: int = 500) -> List[Dict]:
        """
        Fetch real historical data from Binance API.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch (max 1000)
        
        Returns:
            List of OHLCV dictionaries
        """
        try:
            url = f"{self.BINANCE_API_BASE}/klines"
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': min(limit, 1000)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            klines = response.json()
            parsed_data = []
            
            for kline in klines:
                parsed_data.append({
                    'timestamp': datetime.fromtimestamp(kline[0] / 1000),
                    'open': Decimal(str(kline[1])),
                    'high': Decimal(str(kline[2])),
                    'low': Decimal(str(kline[3])),
                    'close': Decimal(str(kline[4])),
                    'volume': Decimal(str(kline[5])),
                })
            
            return parsed_data
            
        except Exception as e:
            print(f"Error fetching Binance data for {symbol}: {e}")
            return []
    
    def generate_mock_data(self, symbol: str, timeframe: str = '1h', 
                          candles: int = 500, base_price: float = 50000.0) -> List[Dict]:
        """
        Generate realistic mock OHLCV data for testing.
        
        Args:
            symbol: Trading pair
            timeframe: Candle interval
            candles: Number of candles to generate
            base_price: Starting price
        
        Returns:
            List of OHLCV dictionaries
        """
        interval_minutes = self.TIMEFRAME_INTERVALS.get(timeframe, 60)
        mock_data = []
        
        current_time = datetime.utcnow() - timedelta(minutes=interval_minutes * candles)
        current_price = base_price
        
        for i in range(candles):
            # Random walk with trending behavior
            trend = random.choice([-0.5, 0, 0, 0.5])  # Slight upward bias
            change_percent = (random.random() - 0.5 + trend) * 0.02  # ±2% change
            
            open_price = current_price
            close_price = open_price * (1 + change_percent)
            
            # Generate high and low
            high_price = max(open_price, close_price) * (1 + random.random() * 0.01)
            low_price = min(open_price, close_price) * (1 - random.random() * 0.01)
            
            # Generate volume (random between 10-1000 BTC equivalent)
            volume = Decimal(str(random.uniform(10, 1000)))
            
            mock_data.append({
                'timestamp': current_time,
                'open': Decimal(str(round(open_price, 2))),
                'high': Decimal(str(round(high_price, 2))),
                'low': Decimal(str(round(low_price, 2))),
                'close': Decimal(str(round(close_price, 2))),
                'volume': volume,
            })
            
            current_price = close_price
            current_time += timedelta(minutes=interval_minutes)
        
        return mock_data
    
    def save_price_data(self, symbol: str, timeframe: str, data: List[Dict]) -> int:
        """
        Save price data to database, avoiding duplicates.
        
        Args:
            symbol: Trading pair
            timeframe: Candle interval
            data: List of OHLCV dictionaries
        
        Returns:
            Number of records saved
        """
        saved_count = 0
        
        for candle in data:
            # Check if record already exists
            existing = self.db.query(PriceHistory).filter(
                PriceHistory.symbol == symbol,
                PriceHistory.timeframe == timeframe,
                PriceHistory.timestamp == candle['timestamp']
            ).first()
            
            if not existing:
                price_record = PriceHistory(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=candle['timestamp'],
                    open_price=candle['open'],
                    high_price=candle['high'],
                    low_price=candle['low'],
                    close_price=candle['close'],
                    volume=candle['volume']
                )
                self.db.add(price_record)
                saved_count += 1
        
        self.db.commit()
        return saved_count
    
    def get_historical_data(self, symbol: str, timeframe: str = '1h', 
                           limit: int = 500) -> List[Dict]:
        """
        Retrieve historical price data from database.
        
        Args:
            symbol: Trading pair
            timeframe: Candle interval
            limit: Maximum number of candles to return
        
        Returns:
            List of OHLCV dictionaries
        """
        records = self.db.query(PriceHistory).filter(
            PriceHistory.symbol == symbol,
            PriceHistory.timeframe == timeframe
        ).order_by(PriceHistory.timestamp.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        records = list(reversed(records))
        
        result = []
        for record in records:
            result.append({
                'time': int(record.timestamp.timestamp()),
                'timestamp': record.timestamp.isoformat(),
                'open': float(record.open_price),
                'high': float(record.high_price),
                'low': float(record.low_price),
                'close': float(record.close_price),
                'volume': float(record.volume),
            })
        
        return result
    
    def collect_data_for_instrument(self, symbol: str, timeframe: str = '1h', 
                                    use_mock: bool = False) -> Dict:
        """
        Collect and save data for a single instrument.
        
        Args:
            symbol: Trading pair
            timeframe: Candle interval
            use_mock: If True, generate mock data instead of fetching from API
        
        Returns:
            Dictionary with status and count
        """
        try:
            if use_mock:
                # Determine base price based on symbol
                base_prices = {
                    'BTCUSDT': 65000.0,
                    'ETHUSDT': 3500.0,
                    'BNBUSDT': 600.0,
                    'SOLUSDT': 150.0,
                    'XRPUSDT': 0.55,
                }
                base_price = base_prices.get(symbol, 1000.0)
                data = self.generate_mock_data(symbol, timeframe, candles=500, base_price=base_price)
            else:
                data = self.fetch_binance_klines(symbol, timeframe, limit=500)
            
            if not data:
                return {'status': 'error', 'message': 'No data retrieved', 'count': 0}
            
            saved_count = self.save_price_data(symbol, timeframe, data)
            
            return {
                'status': 'success',
                'symbol': symbol,
                'timeframe': timeframe,
                'total_candles': len(data),
                'saved_count': saved_count,
                'message': f'Saved {saved_count} new candles for {symbol}'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'count': 0}
    
    def collect_all_instruments(self, timeframe: str = '1h', use_mock: bool = False) -> List[Dict]:
        """
        Collect data for all enabled instruments.
        
        Args:
            timeframe: Candle interval
            use_mock: If True, generate mock data
        
        Returns:
            List of collection results for each instrument
        """
        instruments = self.db.query(AllowedInstrument).filter(
            AllowedInstrument.enabled == True
        ).all()
        
        results = []
        for instrument in instruments:
            result = self.collect_data_for_instrument(instrument.symbol, timeframe, use_mock)
            results.append(result)
        
        return results
    
    def get_latest_price(self, symbol: str, timeframe: str = '1h') -> Optional[Dict]:
        """
        Get the most recent price data for a symbol.
        
        Args:
            symbol: Trading pair
            timeframe: Candle interval
        
        Returns:
            Latest OHLCV dictionary or None
        """
        latest = self.db.query(PriceHistory).filter(
            PriceHistory.symbol == symbol,
            PriceHistory.timeframe == timeframe
        ).order_by(PriceHistory.timestamp.desc()).first()
        
        if latest:
            return {
                'time': int(latest.timestamp.timestamp()),
                'timestamp': latest.timestamp.isoformat(),
                'open': float(latest.open_price),
                'high': float(latest.high_price),
                'low': float(latest.low_price),
                'close': float(latest.close_price),
                'volume': float(latest.volume),
            }
        return None
