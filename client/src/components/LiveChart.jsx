import { useState, useEffect, useRef, useCallback } from 'react';
import { createChart } from 'lightweight-charts';
import Select from 'react-select';
import axios from 'axios';
import './Chart.css';

const LiveChart = () => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const indicatorSeriesRef = useRef({});
  const websocketRef = useRef(null);
  const updateIntervalRef = useRef(null);

  const [instruments, setInstruments] = useState([]);
  const [selectedInstrument, setSelectedInstrument] = useState(null);
  const [timeframe, setTimeframe] = useState('1m');
  const [indicators, setIndicators] = useState({
    sma20: false,
    sma50: false,
    sma200: false,
    ema9: false,
    ema21: false,
    bb: false,
    volume: true
  });
  const [livePrice, setLivePrice] = useState(null);
  const [priceChange, setPriceChange] = useState({ value: 0, percentage: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isLive, setIsLive] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [candleData, setCandleData] = useState([]);
  const [currentCandle, setCurrentCandle] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  // Fetch available instruments from your database
  const fetchInstruments = async () => {
    try {
      const response = await axios.get('/api/trading/instruments');
      const instrumentOptions = response.data.map(inst => ({
        value: inst.symbol,
        label: `${inst.symbol} - ${inst.name}`
      }));
      setInstruments(instrumentOptions);
      
      // Auto-select first instrument if available
      if (instrumentOptions.length > 0 && !selectedInstrument) {
        setSelectedInstrument(instrumentOptions[0]);
      }
    } catch (error) {
      console.error('Error fetching instruments:', error);
      setError('Failed to load instruments');
    }
  };

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
      console.log('🎨 Initializing chart...');
      
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 600,
        layout: {
          background: { color: '#0f0f0f' },
          textColor: '#d1d4dc',
        },
        grid: {
          vertLines: { color: '#1a1a1a' },
          horzLines: { color: '#1a1a1a' },
        },
        crosshair: {
          mode: 1,
          vertLine: {
            width: 1,
            color: '#758696',
            style: 3,
          },
          horzLine: {
            width: 1,
            color: '#758696',
            style: 3,
          },
        },
        rightPriceScale: {
          borderColor: '#2b2b43',
          scaleMargins: {
            top: 0.1,
            bottom: 0.2,
          },
        },
        timeScale: {
          borderColor: '#2b2b43',
          timeVisible: true,
          secondsVisible: false,
        },
        handleScroll: {
          vertTouchDrag: true,
        },
        handleScale: {
          axisPressedMouseMove: true,
          mouseWheel: true,
          pinch: true,
        },
      });

      // Create candlestick series
      const candleSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      });

      // Create volume series
      const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });

      chartRef.current = chart;
      candlestickSeriesRef.current = candleSeries;
      volumeSeriesRef.current = volumeSeries;

      // Handle resize
      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chart.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener('resize', handleResize);

      console.log('✅ Chart initialized successfully');

      return () => {
        window.removeEventListener('resize', handleResize);
        if (chartRef.current) {
          chart.remove();
        }
      };
    } catch (err) {
      console.error('❌ Error initializing chart:', err);
      setError('Failed to initialize chart: ' + err.message);
    }
  }, []);

  // Fetch instruments on mount
  useEffect(() => {
    fetchInstruments();
  }, []);

  // Generate realistic live data using Binance API
  const fetchLiveData = async (symbol, interval) => {
    try {
      console.log(`📊 Fetching live data for ${symbol} (${interval})...`);
      setIsLoading(true);
      setError(null);

      // Convert timeframe to Binance interval
      const binanceInterval = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d'
      }[interval] || '1m';

      // Use Binance API for real crypto data
      // For stocks, you'd use Alpha Vantage, IEX Cloud, or your backend API
      const binanceSymbol = symbol.replace('USD', 'USDT'); // Convert BTCUSD to BTCUSDT
      const apiUrl = `https://api.binance.com/api/v3/klines?symbol=${binanceSymbol}&interval=${binanceInterval}&limit=500`;
      
      console.log(`🌐 Calling Binance API: ${apiUrl}`);
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Binance API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform Binance data to our format
      const candles = data.map(item => ({
        time: Math.floor(item[0] / 1000), // Convert ms to seconds
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));

      const volumes = data.map(item => ({
        time: Math.floor(item[0] / 1000),
        value: parseFloat(item[5]),
        color: parseFloat(item[4]) >= parseFloat(item[1]) ? '#26a69a80' : '#ef535080'
      }));

      console.log(`✅ Fetched ${candles.length} candles`);
      
      // Update chart
      if (candlestickSeriesRef.current && candles.length > 0) {
        candlestickSeriesRef.current.setData(candles);
        setCandleData(candles);
        setCurrentCandle(candles[candles.length - 1]);
        
        // Update live price
        const latest = candles[candles.length - 1];
        const first = candles[0];
        setLivePrice(latest.close);
        
        const change = latest.close - first.open;
        const changePercent = (change / first.open) * 100;
        setPriceChange({ value: change, percentage: changePercent });
      }

      if (volumeSeriesRef.current && volumes.length > 0 && indicators.volume) {
        volumeSeriesRef.current.setData(volumes);
      }

      // Update indicators
      updateIndicators(candles);
      
      setLastUpdate(new Date());
      setConnectionStatus('connected');

    } catch (error) {
      console.error('❌ Error fetching live data:', error);
      setError(`Failed to fetch data: ${error.message}`);
      setConnectionStatus('error');
      
      // Fallback to sample data if API fails
      generateSampleData();
    } finally {
      setIsLoading(false);
    }
  };

  // Generate sample data as fallback
  const generateSampleData = () => {
    console.log('📊 Generating sample data...');
    const now = Math.floor(Date.now() / 1000);
    const candles = [];
    const volumes = [];
    let price = 50000 + Math.random() * 10000;

    for (let i = 200; i >= 0; i--) {
      const time = now - i * 60;
      const change = (Math.random() - 0.5) * 200;
      const open = price;
      price += change;
      const high = Math.max(open, price) + Math.random() * 100;
      const low = Math.min(open, price) - Math.random() * 100;
      const close = price;
      const volume = 1000000 + Math.random() * 5000000;

      candles.push({ time, open, high, low, close });
      volumes.push({
        time,
        value: volume,
        color: close >= open ? '#26a69a80' : '#ef535080'
      });
    }

    if (candlestickSeriesRef.current) {
      candlestickSeriesRef.current.setData(candles);
      setCandleData(candles);
    }

    if (volumeSeriesRef.current && indicators.volume) {
      volumeSeriesRef.current.setData(volumes);
    }

    const latest = candles[candles.length - 1];
    setLivePrice(latest.close);
    setConnectionStatus('sample');
  };

  // WebSocket for live updates (Binance WebSocket)
  const connectWebSocket = useCallback((symbol) => {
    if (websocketRef.current) {
      websocketRef.current.close();
    }

    try {
      const binanceSymbol = symbol.replace('USD', 'USDT').toLowerCase();
      const wsUrl = `wss://stream.binance.com:9443/ws/${binanceSymbol}@kline_${timeframe}`;
      
      console.log(`🔌 Connecting WebSocket: ${wsUrl}`);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setConnectionStatus('live');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const kline = data.k;
          
          if (!kline) return;

          const candle = {
            time: Math.floor(kline.t / 1000),
            open: parseFloat(kline.o),
            high: parseFloat(kline.h),
            low: parseFloat(kline.l),
            close: parseFloat(kline.c)
          };

          const volume = {
            time: Math.floor(kline.t / 1000),
            value: parseFloat(kline.v),
            color: candle.close >= candle.open ? '#26a69a80' : '#ef535080'
          };

          // Update chart with live candle
          if (candlestickSeriesRef.current) {
            candlestickSeriesRef.current.update(candle);
          }

          if (volumeSeriesRef.current && indicators.volume) {
            volumeSeriesRef.current.update(volume);
          }

          // Update live price
          setLivePrice(candle.close);
          setLastUpdate(new Date());
          setCurrentCandle(candle);

          // Update indicators if needed
          if (kline.x) { // Candle is closed
            setCandleData(prev => [...prev.slice(-499), candle]);
          }

        } catch (err) {
          console.error('Error processing WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setConnectionStatus('error');
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setConnectionStatus('disconnected');
      };

      websocketRef.current = ws;

    } catch (error) {
      console.error('❌ Failed to connect WebSocket:', error);
      setConnectionStatus('error');
    }
  }, [timeframe, indicators.volume]);

  // Fetch data when instrument or timeframe changes
  useEffect(() => {
    if (selectedInstrument && isLive) {
      console.log(`🔄 Data fetch triggered: ${selectedInstrument.value} @ ${timeframe}`);
      fetchLiveData(selectedInstrument.value, timeframe);
      
      // Connect WebSocket for live updates
      connectWebSocket(selectedInstrument.value);

      // Also refresh data every 30 seconds
      updateIntervalRef.current = setInterval(() => {
        if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
          console.log('🔄 Refreshing data (WebSocket not active)...');
          fetchLiveData(selectedInstrument.value, timeframe);
        }
      }, 30000);

      return () => {
        if (updateIntervalRef.current) {
          clearInterval(updateIntervalRef.current);
        }
        if (websocketRef.current) {
          websocketRef.current.close();
        }
      };
    }
  }, [selectedInstrument, timeframe, isLive, connectWebSocket]);

  // Calculate and update technical indicators
  const updateIndicators = (candles) => {
    if (!candles || candles.length === 0) return;

    try {
      // Clear existing indicators
      Object.values(indicatorSeriesRef.current).forEach(series => {
        if (series && chartRef.current) {
          try {
            chartRef.current.removeSeries(series);
          } catch (e) {
            // Series might already be removed - ignore error
            console.warn('Could not remove series:', e.message);
          }
        }
      });
      indicatorSeriesRef.current = {};

      // SMA 20
      if (indicators.sma20) {
        const sma20Data = calculateSMA(candles, 20);
        const sma20Series = chartRef.current.addLineSeries({
          color: '#2196F3',
          lineWidth: 2,
          title: 'SMA 20',
        });
        sma20Series.setData(sma20Data);
        indicatorSeriesRef.current.sma20 = sma20Series;
      }

      // SMA 50
      if (indicators.sma50) {
        const sma50Data = calculateSMA(candles, 50);
        const sma50Series = chartRef.current.addLineSeries({
          color: '#FF9800',
          lineWidth: 2,
          title: 'SMA 50',
        });
        sma50Series.setData(sma50Data);
        indicatorSeriesRef.current.sma50 = sma50Series;
      }

      // SMA 200
      if (indicators.sma200) {
        const sma200Data = calculateSMA(candles, 200);
        const sma200Series = chartRef.current.addLineSeries({
          color: '#9C27B0',
          lineWidth: 2,
          title: 'SMA 200',
        });
        sma200Series.setData(sma200Data);
        indicatorSeriesRef.current.sma200 = sma200Series;
      }

      // EMA 9
      if (indicators.ema9) {
        const ema9Data = calculateEMA(candles, 9);
        const ema9Series = chartRef.current.addLineSeries({
          color: '#00BCD4',
          lineWidth: 2,
          title: 'EMA 9',
        });
        ema9Series.setData(ema9Data);
        indicatorSeriesRef.current.ema9 = ema9Series;
      }

      // EMA 21
      if (indicators.ema21) {
        const ema21Data = calculateEMA(candles, 21);
        const ema21Series = chartRef.current.addLineSeries({
          color: '#FFC107',
          lineWidth: 2,
          title: 'EMA 21',
        });
        ema21Series.setData(ema21Data);
        indicatorSeriesRef.current.ema21 = ema21Series;
      }

      // Bollinger Bands
      if (indicators.bb) {
        const bbData = calculateBollingerBands(candles, 20, 2);
        
        const upperSeries = chartRef.current.addLineSeries({
          color: '#FF6B6B',
          lineWidth: 1,
          lineStyle: 2,
          title: 'BB Upper',
        });
        upperSeries.setData(bbData.upper);
        indicatorSeriesRef.current.bbUpper = upperSeries;

        const middleSeries = chartRef.current.addLineSeries({
          color: '#4ECDC4',
          lineWidth: 1,
          lineStyle: 2,
          title: 'BB Middle',
        });
        middleSeries.setData(bbData.middle);
        indicatorSeriesRef.current.bbMiddle = middleSeries;

        const lowerSeries = chartRef.current.addLineSeries({
          color: '#FF6B6B',
          lineWidth: 1,
          lineStyle: 2,
          title: 'BB Lower',
        });
        lowerSeries.setData(bbData.lower);
        indicatorSeriesRef.current.bbLower = lowerSeries;
      }

    } catch (error) {
      console.error('Error updating indicators:', error);
    }
  };

  // Update indicators when toggled
  useEffect(() => {
    if (candleData.length > 0 && chartRef.current) {
      updateIndicators(candleData);
    }
  }, [indicators, candleData]);

  // Technical indicator calculations
  const calculateSMA = (data, period) => {
    const result = [];
    for (let i = period - 1; i < data.length; i++) {
      const sum = data.slice(i - period + 1, i + 1).reduce((acc, candle) => acc + candle.close, 0);
      result.push({
        time: data[i].time,
        value: sum / period
      });
    }
    return result;
  };

  const calculateEMA = (data, period) => {
    const result = [];
    const multiplier = 2 / (period + 1);
    
    // Start with SMA for first value
    const firstSMA = data.slice(0, period).reduce((acc, candle) => acc + candle.close, 0) / period;
    result.push({ time: data[period - 1].time, value: firstSMA });
    
    let ema = firstSMA;
    for (let i = period; i < data.length; i++) {
      ema = (data[i].close - ema) * multiplier + ema;
      result.push({ time: data[i].time, value: ema });
    }
    
    return result;
  };

  const calculateBollingerBands = (data, period, stdDev) => {
    const sma = calculateSMA(data, period);
    const upper = [];
    const middle = [];
    const lower = [];
    
    for (let i = 0; i < sma.length; i++) {
      const dataSlice = data.slice(i, i + period);
      const mean = sma[i].value;
      const variance = dataSlice.reduce((acc, candle) => acc + Math.pow(candle.close - mean, 2), 0) / period;
      const std = Math.sqrt(variance);
      
      middle.push({ time: sma[i].time, value: mean });
      upper.push({ time: sma[i].time, value: mean + (stdDev * std) });
      lower.push({ time: sma[i].time, value: mean - (stdDev * std) });
    }
    
    return { upper, middle, lower };
  };

  const toggleIndicator = (indicator) => {
    setIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator],
    }));
  };

  const toggleLive = () => {
    setIsLive(!isLive);
    if (!isLive && selectedInstrument) {
      // Reconnect when turning live mode back on
      fetchLiveData(selectedInstrument.value, timeframe);
      connectWebSocket(selectedInstrument.value);
    } else if (isLive && websocketRef.current) {
      // Disconnect when turning off
      websocketRef.current.close();
    }
  };

  const refreshData = () => {
    if (selectedInstrument) {
      fetchLiveData(selectedInstrument.value, timeframe);
    }
  };

  const timeframeOptions = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
  ];

  const getConnectionStatusBadge = () => {
    const badges = {
      live: { text: '🟢 LIVE', color: '#26a69a' },
      connected: { text: '🟢 CONNECTED', color: '#26a69a' },
      disconnected: { text: '🔴 DISCONNECTED', color: '#ef5350' },
      error: { text: '⚠️ ERROR', color: '#ff9800' },
      sample: { text: '📊 SAMPLE DATA', color: '#2196f3' }
    };
    const badge = badges[connectionStatus] || badges.disconnected;
    return <span style={{ color: badge.color, fontWeight: 'bold' }}>{badge.text}</span>;
  };

  return (
    <div className="chart-container-wrapper">
      {error && (
        <div style={{
          background: '#ef5350',
          color: 'white',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          fontWeight: '600'
        }}>
          ⚠️ {error}
        </div>
      )}

      <div className="chart-header">
        <div className="chart-title-section">
          <h1>📈 Live Trading Chart</h1>
          {livePrice && (
            <div className="price-info">
              <span className="live-price">${livePrice.toFixed(2)}</span>
              <span className={`price-change ${priceChange.value >= 0 ? 'positive' : 'negative'}`}>
                {priceChange.value >= 0 ? '▲' : '▼'} ${Math.abs(priceChange.value).toFixed(2)} 
                ({priceChange.percentage >= 0 ? '+' : ''}{priceChange.percentage.toFixed(2)}%)
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="chart-controls">
        <div className="control-group">
          <label>Instrument</label>
          <Select
            options={instruments}
            value={selectedInstrument}
            onChange={setSelectedInstrument}
            className="instrument-select"
            classNamePrefix="select"
            placeholder="Select instrument..."
            isSearchable
          />
        </div>

        <div className="control-group">
          <label>Timeframe</label>
          <Select
            options={timeframeOptions}
            value={timeframeOptions.find(opt => opt.value === timeframe)}
            onChange={(option) => setTimeframe(option.value)}
            className="timeframe-select"
            classNamePrefix="select"
          />
        </div>

        <button 
          className={`refresh-btn ${isLive ? 'live-active' : ''}`}
          onClick={toggleLive}
          style={{ 
            background: isLive ? 'linear-gradient(135deg, #26a69a 0%, #1b8577 100%)' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}
        >
          {isLive ? '⏸️ Pause Live' : '▶️ Resume Live'}
        </button>

        <button 
          className="refresh-btn"
          onClick={refreshData}
          disabled={isLoading}
        >
          {isLoading ? '⏳ Loading...' : '🔄 Refresh'}
        </button>
      </div>

      <div className="indicators-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3>Technical Indicators</h3>
          <div style={{ fontSize: '14px' }}>
            {getConnectionStatusBadge()}
            {lastUpdate && (
              <span style={{ marginLeft: '15px', color: '#9ca3af' }}>
                Last update: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
        <div className="indicators-grid">
          <button
            className={`indicator-btn ${indicators.sma20 ? 'active' : ''}`}
            onClick={() => toggleIndicator('sma20')}
          >
            SMA 20
          </button>
          <button
            className={`indicator-btn ${indicators.sma50 ? 'active' : ''}`}
            onClick={() => toggleIndicator('sma50')}
          >
            SMA 50
          </button>
          <button
            className={`indicator-btn ${indicators.sma200 ? 'active' : ''}`}
            onClick={() => toggleIndicator('sma200')}
          >
            SMA 200
          </button>
          <button
            className={`indicator-btn ${indicators.ema9 ? 'active' : ''}`}
            onClick={() => toggleIndicator('ema9')}
          >
            EMA 9
          </button>
          <button
            className={`indicator-btn ${indicators.ema21 ? 'active' : ''}`}
            onClick={() => toggleIndicator('ema21')}
          >
            EMA 21
          </button>
          <button
            className={`indicator-btn ${indicators.bb ? 'active' : ''}`}
            onClick={() => toggleIndicator('bb')}
          >
            Bollinger Bands
          </button>
          <button
            className={`indicator-btn ${indicators.volume ? 'active' : ''}`}
            onClick={() => toggleIndicator('volume')}
          >
            Volume
          </button>
        </div>
      </div>

      <div className="chart-wrapper">
        {isLoading && <div className="chart-loading">⏳ Loading chart data...</div>}
        <div ref={chartContainerRef} className="chart-container" />
      </div>

      <div className="chart-info">
        <div className="info-card">
          <span className="info-label">📊 Chart Type:</span>
          <span className="info-value">Candlestick</span>
        </div>
        <div className="info-card">
          <span className="info-label">⏱️ Timeframe:</span>
          <span className="info-value">{timeframeOptions.find(opt => opt.value === timeframe)?.label}</span>
        </div>
        <div className="info-card">
          <span className="info-label">📈 Symbol:</span>
          <span className="info-value">{selectedInstrument?.label || 'None'}</span>
        </div>
        <div className="info-card">
          <span className="info-label">🔌 Status:</span>
          <span className="info-value">{getConnectionStatusBadge()}</span>
        </div>
        {currentCandle && (
          <>
            <div className="info-card">
              <span className="info-label">Open:</span>
              <span className="info-value">${currentCandle.open.toFixed(2)}</span>
            </div>
            <div className="info-card">
              <span className="info-label">High:</span>
              <span className="info-value" style={{ color: '#26a69a' }}>${currentCandle.high.toFixed(2)}</span>
            </div>
            <div className="info-card">
              <span className="info-label">Low:</span>
              <span className="info-value" style={{ color: '#ef5350' }}>${currentCandle.low.toFixed(2)}</span>
            </div>
            <div className="info-card">
              <span className="info-label">Close:</span>
              <span className="info-value">${currentCandle.close.toFixed(2)}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default LiveChart;
