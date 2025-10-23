import React, { useState, useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import './HistoricalChart.css';

const HistoricalChart = () => {
  const [instruments, setInstruments] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dataStats, setDataStats] = useState(null);
  
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);

  // Fetch available instruments
  useEffect(() => {
    fetch('/api/trading/instruments')
      .then(res => res.json())
      .then(data => {
        const instList = data.instruments || data || [];
        setInstruments(instList);
        if (instList.length > 0 && !selectedSymbol) {
          setSelectedSymbol(instList[0].symbol);
        }
      })
      .catch(err => console.error('Error fetching instruments:', err));
  }, []);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 600,
      layout: {
        background: { type: 'solid', color: '#0f0f0f' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#1f1f1f' },
        horzLines: { color: '#1f1f1f' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#2a2a2a',
      },
      timeScale: {
        borderColor: '#2a2a2a',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Candlestick series - v5 API
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });
    candleSeriesRef.current = candleSeries;

    // Volume series - v5 API
    const volumeSeries = chart.addHistogramSeries({
      color: '#385263',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Fetch and display historical data
  const loadHistoricalData = async () => {
    if (!selectedSymbol) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/historical-prices/${selectedSymbol}?timeframe=${timeframe}&limit=500&use_mock=true`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.error) {
        throw new Error(result.error);
      }

      const { data, count } = result;

      if (!data || data.length === 0) {
        setError('No historical data available');
        return;
      }

      // Transform data for candlestick chart
      const candleData = data.map(candle => ({
        time: candle.time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }));

      // Transform data for volume chart
      const volumeData = data.map(candle => ({
        time: candle.time,
        value: candle.volume,
        color: candle.close >= candle.open ? '#26a69a80' : '#ef535080',
      }));

      // Update chart
      if (candleSeriesRef.current && volumeSeriesRef.current) {
        candleSeriesRef.current.setData(candleData);
        volumeSeriesRef.current.setData(volumeData);
        chartRef.current.timeScale().fitContent();
      }

      // Calculate stats
      const latestCandle = data[data.length - 1];
      const firstCandle = data[0];
      const priceChange = latestCandle.close - firstCandle.close;
      const priceChangePercent = ((priceChange / firstCandle.close) * 100).toFixed(2);

      setDataStats({
        count,
        latest: latestCandle,
        firstPrice: firstCandle.close,
        priceChange,
        priceChangePercent,
        timeRange: `${new Date(firstCandle.timestamp).toLocaleString()} - ${new Date(latestCandle.timestamp).toLocaleString()}`
      });

    } catch (err) {
      console.error('Error loading historical data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Load data when symbol or timeframe changes
  useEffect(() => {
    if (selectedSymbol) {
      loadHistoricalData();
    }
  }, [selectedSymbol, timeframe]);

  const timeframes = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '30m', label: '30 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
  ];

  return (
    <div className="historical-chart-container">
      <div className="chart-header">
        <h2>📊 Historical Price Data</h2>
        <p className="chart-subtitle">View stored OHLCV data from database</p>
      </div>

      <div className="chart-controls">
        <div className="control-group">
          <label>Instrument:</label>
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            disabled={loading}
          >
            {instruments.map(inst => (
              <option key={inst.id} value={inst.symbol}>
                {inst.symbol} {inst.name && `- ${inst.name}`}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Timeframe:</label>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            disabled={loading}
          >
            {timeframes.map(tf => (
              <option key={tf.value} value={tf.value}>
                {tf.label}
              </option>
            ))}
          </select>
        </div>

        <button
          className="refresh-btn"
          onClick={loadHistoricalData}
          disabled={loading}
        >
          {loading ? '⏳ Loading...' : '🔄 Refresh Data'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {dataStats && (
        <div className="data-stats">
          <div className="stat-card">
            <span className="stat-label">Candles:</span>
            <span className="stat-value">{dataStats.count}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Latest Price:</span>
            <span className="stat-value">${dataStats.latest.close.toFixed(2)}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Change:</span>
            <span className={`stat-value ${dataStats.priceChange >= 0 ? 'positive' : 'negative'}`}>
              {dataStats.priceChange >= 0 ? '+' : ''}{dataStats.priceChange.toFixed(2)} 
              ({dataStats.priceChangePercent}%)
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Volume:</span>
            <span className="stat-value">{dataStats.latest.volume.toFixed(2)}</span>
          </div>
        </div>
      )}

      <div className="chart-wrapper">
        <div ref={chartContainerRef} className="chart-canvas" />
      </div>

      <div className="chart-info">
        <div className="info-section">
          <h4>💡 About This Chart</h4>
          <ul>
            <li>📦 <strong>Data Source:</strong> Historical OHLCV data stored in PostgreSQL database</li>
            <li>🎯 <strong>Mock Data:</strong> Currently using generated mock data for development</li>
            <li>⏱️ <strong>Timeframes:</strong> 1m, 5m, 15m, 30m, 1h, 4h, 1d intervals supported</li>
            <li>📊 <strong>Features:</strong> Candlestick patterns, volume bars, price analysis</li>
            <li>🔄 <strong>Auto-refresh:</strong> Data updates when switching symbols or timeframes</li>
          </ul>
        </div>

        <div className="info-section">
          <h4>🚀 Next Steps</h4>
          <ul>
            <li>Switch to real Binance API data by setting <code>use_mock=false</code></li>
            <li>Add technical indicators (MA, RSI, MACD, Bollinger Bands)</li>
            <li>Enable background data collection via Celery tasks</li>
            <li>Add real-time updates with WebSocket integration</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HistoricalChart;
