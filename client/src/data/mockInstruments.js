// Mock instrument data - Backend will replace this later
// This provides sample data for chart functionality

export const INSTRUMENTS = [
  // Forex Pairs
  {
    id: 'EURUSD',
    symbol: 'EUR/USD',
    type: 'forex',
    description: 'Euro vs US Dollar',
    pipSize: 0.0001,
    lotSize: 100000,
    minLot: 0.01,
    maxLot: 100,
    spread: 1.5,
    commission: 0,
  },
  {
    id: 'GBPUSD',
    symbol: 'GBP/USD',
    type: 'forex',
    description: 'British Pound vs US Dollar',
    pipSize: 0.0001,
    lotSize: 100000,
    minLot: 0.01,
    maxLot: 100,
    spread: 2.0,
    commission: 0,
  },
  {
    id: 'USDJPY',
    symbol: 'USD/JPY',
    type: 'forex',
    description: 'US Dollar vs Japanese Yen',
    pipSize: 0.01,
    lotSize: 100000,
    minLot: 0.01,
    maxLot: 100,
    spread: 1.8,
    commission: 0,
  },
  {
    id: 'AUDUSD',
    symbol: 'AUD/USD',
    type: 'forex',
    description: 'Australian Dollar vs US Dollar',
    pipSize: 0.0001,
    lotSize: 100000,
    minLot: 0.01,
    maxLot: 100,
    spread: 1.6,
    commission: 0,
  },
  {
    id: 'USDCHF',
    symbol: 'USD/CHF',
    type: 'forex',
    description: 'US Dollar vs Swiss Franc',
    pipSize: 0.0001,
    lotSize: 100000,
    minLot: 0.01,
    maxLot: 100,
    spread: 1.9,
    commission: 0,
  },
  // Crypto
  {
    id: 'BTCUSD',
    symbol: 'BTC/USD',
    type: 'crypto',
    description: 'Bitcoin vs US Dollar',
    pipSize: 0.01,
    lotSize: 1,
    minLot: 0.001,
    maxLot: 10,
    spread: 50,
    commission: 0.1,
  },
  {
    id: 'ETHUSD',
    symbol: 'ETH/USD',
    type: 'crypto',
    description: 'Ethereum vs US Dollar',
    pipSize: 0.01,
    lotSize: 1,
    minLot: 0.01,
    maxLot: 50,
    spread: 5,
    commission: 0.1,
  },
  // Stocks
  {
    id: 'AAPL',
    symbol: 'AAPL',
    type: 'stock',
    description: 'Apple Inc.',
    pipSize: 0.01,
    lotSize: 1,
    minLot: 1,
    maxLot: 10000,
    spread: 0.02,
    commission: 1,
  },
  {
    id: 'GOOGL',
    symbol: 'GOOGL',
    type: 'stock',
    description: 'Alphabet Inc.',
    pipSize: 0.01,
    lotSize: 1,
    minLot: 1,
    maxLot: 10000,
    spread: 0.05,
    commission: 1,
  },
  {
    id: 'TSLA',
    symbol: 'TSLA',
    type: 'stock',
    description: 'Tesla Inc.',
    pipSize: 0.01,
    lotSize: 1,
    minLot: 1,
    maxLot: 10000,
    spread: 0.03,
    commission: 1,
  },
  // Indices
  {
    id: 'US500',
    symbol: 'US500',
    type: 'index',
    description: 'S&P 500 Index',
    pipSize: 0.01,
    lotSize: 1,
    minLot: 0.1,
    maxLot: 100,
    spread: 0.5,
    commission: 0,
  },
  {
    id: 'US30',
    symbol: 'US30',
    type: 'index',
    description: 'Dow Jones Industrial Average',
    pipSize: 0.01,
    lotSize: 1,
    minLot: 0.1,
    maxLot: 100,
    spread: 2,
    commission: 0,
  },
  // Commodities
  {
    id: 'XAUUSD',
    symbol: 'XAU/USD',
    type: 'commodity',
    description: 'Gold vs US Dollar',
    pipSize: 0.01,
    lotSize: 100,
    minLot: 0.01,
    maxLot: 100,
    spread: 0.3,
    commission: 0,
  },
  {
    id: 'XAGUSD',
    symbol: 'XAG/USD',
    type: 'commodity',
    description: 'Silver vs US Dollar',
    pipSize: 0.001,
    lotSize: 5000,
    minLot: 0.01,
    maxLot: 100,
    spread: 0.02,
    commission: 0,
  },
  {
    id: 'USOIL',
    symbol: 'US OIL',
    type: 'commodity',
    description: 'Crude Oil WTI',
    pipSize: 0.01,
    lotSize: 1000,
    minLot: 0.01,
    maxLot: 100,
    spread: 0.05,
    commission: 0,
  },
];

// Generate realistic OHLCV data for a given instrument
export function generateMockOHLCVData(instrument, bars = 1000, timeframe = '5m') {
  const data = [];
  const now = Date.now();
  
  // Timeframe in milliseconds
  const timeframes = {
    '1m': 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '30m': 30 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
  };
  
  const interval = timeframes[timeframe] || timeframes['5m'];
  
  // Base prices for different instrument types
  let basePrice;
  switch (instrument.type) {
    case 'forex':
      basePrice = instrument.id.includes('JPY') ? 110 : 1.1;
      break;
    case 'crypto':
      basePrice = instrument.id === 'BTCUSD' ? 45000 : 2500;
      break;
    case 'stock':
      basePrice = 150;
      break;
    case 'index':
      basePrice = instrument.id === 'US30' ? 35000 : 4500;
      break;
    case 'commodity':
      basePrice = instrument.id === 'XAUUSD' ? 2000 : (instrument.id === 'XAGUSD' ? 25 : 75);
      break;
    default:
      basePrice = 100;
  }
  
  let currentPrice = basePrice;
  let trend = Math.random() > 0.5 ? 1 : -1;
  let trendStrength = 0;
  
  for (let i = bars; i >= 0; i--) {
    const time = now - (i * interval);
    
    // Random walk with trending behavior
    if (Math.random() > 0.95) {
      trend *= -1; // Trend reversal
      trendStrength = Math.random() * 0.002;
    }
    
    const volatility = basePrice * 0.002; // 0.2% volatility
    const trendMove = basePrice * trendStrength * trend;
    
    const open = currentPrice;
    const change = (Math.random() - 0.5) * volatility + trendMove;
    const close = open + change;
    
    const high = Math.max(open, close) + Math.random() * volatility * 0.5;
    const low = Math.min(open, close) - Math.random() * volatility * 0.5;
    
    const volume = Math.floor(Math.random() * 1000000) + 100000;
    
    data.push({
      time: Math.floor(time / 1000), // Unix timestamp in seconds
      open: parseFloat(open.toFixed(instrument.id.includes('JPY') ? 3 : 5)),
      high: parseFloat(high.toFixed(instrument.id.includes('JPY') ? 3 : 5)),
      low: parseFloat(low.toFixed(instrument.id.includes('JPY') ? 3 : 5)),
      close: parseFloat(close.toFixed(instrument.id.includes('JPY') ? 3 : 5)),
      volume,
    });
    
    currentPrice = close;
  }
  
  return data;
}

// Get instrument by ID
export function getInstrument(instrumentId) {
  return INSTRUMENTS.find(inst => inst.id === instrumentId);
}

// Get instruments by type
export function getInstrumentsByType(type) {
  return INSTRUMENTS.filter(inst => inst.type === type);
}

// Get current price for instrument (last candle close)
export function getCurrentPrice(instrumentId, timeframe = '5m') {
  const instrument = getInstrument(instrumentId);
  if (!instrument) return null;
  
  const data = generateMockOHLCVData(instrument, 1, timeframe);
  return data[data.length - 1].close;
}
