import { useState, useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import Select from 'react-select';
import axios from 'axios';
import './Chart.css';

const Chart = () => {
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

  // Fetch available instruments
  useEffect(() => {
    fetchInstruments();
  }, []);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
      console.log('Initializing chart...');
      
      // Create chart
      const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 600,
      layout: {
        background: { color: '#1a1a1a' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#2a2a2a' },
        horzLines: { color: '#2a2a2a' },
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

    // Create candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
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
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
    } catch (err) {
      console.error('Error initializing chart:', err);
      setError('Failed to initialize chart: ' + err.message);
    }
  }, []);

  // Fetch chart data when instrument or timeframe changes
  useEffect(() => {
    console.log('Chart data effect triggered:', { selectedInstrument, timeframe });
    if (selectedInstrument) {
      console.log('Fetching chart data for:', selectedInstrument.value);
      fetchChartData(selectedInstrument.value, timeframe);
    } else {
      console.log('No instrument selected, skipping chart data fetch');
    }
  }, [selectedInstrument, timeframe]);

  // Update indicators when toggled
  useEffect(() => {
    if (selectedInstrument && chartRef.current) {
      updateIndicators();
    }
  }, [indicators]);

  const fetchInstruments = async () => {
    try {
      const response = await axios.get('/api/trading/instruments');
      const instrumentOptions = response.data.instruments
        .filter(inst => inst.enabled)
        .map(inst => ({
          value: inst.symbol,
          label: `${inst.symbol} - ${inst.name}`,
        }));
      setInstruments(instrumentOptions);
      
      // Set default instrument
      if (instrumentOptions.length > 0) {
        setSelectedInstrument(instrumentOptions[0]);
      }
    } catch (error) {
      console.error('Error fetching instruments:', error);
    }
  };

  const fetchChartData = async (symbol, tf) => {
    console.log('fetchChartData called with:', { symbol, tf });
    setIsLoading(true);
    try {
      // TODO: Replace with actual price data API
      // For now, generating sample data
      console.log('Generating sample data...');
      const data = generateSampleData(200);
      console.log('Sample data generated:', { candlesCount: data.candles.length, volumesCount: data.volumes.length });
      
      if (candlestickSeriesRef.current) {
        console.log('Setting candlestick data...');
        candlestickSeriesRef.current.setData(data.candles);
      } else {
        console.warn('candlestickSeriesRef.current is null');
      }

      if (volumeSeriesRef.current && indicators.volume) {
        console.log('Setting volume data...');
        volumeSeriesRef.current.setData(data.volumes);
      }

      if (data.candles.length > 0) {
        const latestCandle = data.candles[data.candles.length - 1];
        const firstCandle = data.candles[0];
        setLivePrice(latestCandle.close);
        
        const change = latestCandle.close - firstCandle.open;
        const changePercent = (change / firstCandle.open) * 100;
        setPriceChange({ value: change, percentage: changePercent });
        console.log('Price updated:', { livePrice: latestCandle.close, change, changePercent });
      }

      console.log('Updating indicators...');
      updateIndicators();
      console.log('Chart data loaded successfully');
    } catch (error) {
      console.error('Error fetching chart data:', error);
      setError('Failed to load chart data: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const generateSampleData = (count) => {
    const candles = [];
    const volumes = [];
    let basePrice = 50000;
    let baseTime = Math.floor(Date.now() / 1000) - (count * 60);

    for (let i = 0; i < count; i++) {
      const time = baseTime + (i * 60);
      const open = basePrice;
      const volatility = basePrice * 0.002;
      const close = open + (Math.random() - 0.5) * volatility * 2;
      const high = Math.max(open, close) + Math.random() * volatility;
      const low = Math.min(open, close) - Math.random() * volatility;
      
      candles.push({
        time,
        open,
        high,
        low,
        close,
      });

      volumes.push({
        time,
        value: Math.random() * 1000 + 500,
        color: close >= open ? '#26a69a80' : '#ef535080',
      });

      basePrice = close;
    }

    return { candles, volumes };
  };

  const calculateSMA = (data, period) => {
    const sma = [];
    for (let i = period - 1; i < data.length; i++) {
      const sum = data.slice(i - period + 1, i + 1).reduce((acc, d) => acc + d.close, 0);
      sma.push({
        time: data[i].time,
        value: sum / period,
      });
    }
    return sma;
  };

  const calculateEMA = (data, period) => {
    const ema = [];
    const multiplier = 2 / (period + 1);
    
    // Start with SMA for first value
    const firstSMA = data.slice(0, period).reduce((acc, d) => acc + d.close, 0) / period;
    ema.push({
      time: data[period - 1].time,
      value: firstSMA,
    });

    for (let i = period; i < data.length; i++) {
      const value = (data[i].close - ema[ema.length - 1].value) * multiplier + ema[ema.length - 1].value;
      ema.push({
        time: data[i].time,
        value,
      });
    }

    return ema;
  };

  const calculateBollingerBands = (data, period = 20, stdDev = 2) => {
    const sma = calculateSMA(data, period);
    const bands = { upper: [], middle: [], lower: [] };

    for (let i = 0; i < sma.length; i++) {
      const dataIndex = i + period - 1;
      const slice = data.slice(dataIndex - period + 1, dataIndex + 1);
      
      const mean = sma[i].value;
      const variance = slice.reduce((acc, d) => acc + Math.pow(d.close - mean, 2), 0) / period;
      const sd = Math.sqrt(variance);

      bands.upper.push({ time: sma[i].time, value: mean + stdDev * sd });
      bands.middle.push({ time: sma[i].time, value: mean });
      bands.lower.push({ time: sma[i].time, value: mean - stdDev * sd });
    }

    return bands;
  };

  const updateIndicators = () => {
    if (!candlestickSeriesRef.current || !chartRef.current) return;

    const data = candlestickSeriesRef.current.data();
    if (data.length === 0) return;

    // Clear existing indicators
    Object.values(indicatorSeriesRef.current).forEach(series => {
      if (series) {
        chartRef.current.removeSeries(series);
      }
    });
    indicatorSeriesRef.current = {};

    // Add SMA indicators
    if (indicators.sma20) {
      const sma20 = calculateSMA(data, 20);
      const series = chartRef.current.addLineSeries({
        color: '#2196F3',
        lineWidth: 2,
        title: 'SMA 20',
      });
      series.setData(sma20);
      indicatorSeriesRef.current.sma20 = series;
    }

    if (indicators.sma50) {
      const sma50 = calculateSMA(data, 50);
      const series = chartRef.current.addLineSeries({
        color: '#FF9800',
        lineWidth: 2,
        title: 'SMA 50',
      });
      series.setData(sma50);
      indicatorSeriesRef.current.sma50 = series;
    }

    if (indicators.sma200) {
      const sma200 = calculateSMA(data, 200);
      const series = chartRef.current.addLineSeries({
        color: '#9C27B0',
        lineWidth: 2,
        title: 'SMA 200',
      });
      series.setData(sma200);
      indicatorSeriesRef.current.sma200 = series;
    }

    // Add EMA indicators
    if (indicators.ema9) {
      const ema9 = calculateEMA(data, 9);
      const series = chartRef.current.addLineSeries({
        color: '#00BCD4',
        lineWidth: 2,
        title: 'EMA 9',
      });
      series.setData(ema9);
      indicatorSeriesRef.current.ema9 = series;
    }

    if (indicators.ema21) {
      const ema21 = calculateEMA(data, 21);
      const series = chartRef.current.addLineSeries({
        color: '#FFEB3B',
        lineWidth: 2,
        title: 'EMA 21',
      });
      series.setData(ema21);
      indicatorSeriesRef.current.ema21 = series;
    }

    // Add Bollinger Bands
    if (indicators.bb) {
      const bb = calculateBollingerBands(data, 20, 2);
      
      const upperSeries = chartRef.current.addLineSeries({
        color: '#F50057',
        lineWidth: 1,
        title: 'BB Upper',
      });
      upperSeries.setData(bb.upper);
      
      const middleSeries = chartRef.current.addLineSeries({
        color: '#FF5722',
        lineWidth: 1,
        title: 'BB Middle',
      });
      middleSeries.setData(bb.middle);
      
      const lowerSeries = chartRef.current.addLineSeries({
        color: '#F50057',
        lineWidth: 1,
        title: 'BB Lower',
      });
      lowerSeries.setData(bb.lower);

      indicatorSeriesRef.current.bbUpper = upperSeries;
      indicatorSeriesRef.current.bbMiddle = middleSeries;
      indicatorSeriesRef.current.bbLower = lowerSeries;
    }

    // Toggle volume visibility
    if (volumeSeriesRef.current) {
      volumeSeriesRef.current.applyOptions({
        visible: indicators.volume,
      });
    }
  };

  const toggleIndicator = (indicator) => {
    setIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator],
    }));
  };

  const timeframeOptions = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
  ];

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
          ⚠️ Error: {error}
        </div>
      )}
      <div className="chart-header">
        <div className="chart-title-section">
          <h1>📈 Live Price Chart</h1>
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
          <label>Instrument:</label>
          <Select
            value={selectedInstrument}
            onChange={setSelectedInstrument}
            options={instruments}
            className="instrument-select"
            classNamePrefix="select"
          />
        </div>

        <div className="control-group">
          <label>Timeframe:</label>
          <Select
            value={timeframeOptions.find(opt => opt.value === timeframe)}
            onChange={(option) => setTimeframe(option.value)}
            options={timeframeOptions}
            className="timeframe-select"
            classNamePrefix="select"
          />
        </div>

        <button className="refresh-btn" onClick={() => selectedInstrument && fetchChartData(selectedInstrument.value, timeframe)}>
          🔄 Refresh
        </button>
      </div>

      <div className="indicators-panel">
        <h3>Technical Indicators</h3>
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
        {isLoading && <div className="chart-loading">Loading chart data...</div>}
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
          <span className="info-value">{selectedInstrument?.value || 'None'}</span>
        </div>
        <div className="info-card">
          <span className="info-label">🔴 Status:</span>
          <span className="info-value live-badge">● LIVE</span>
        </div>
      </div>
    </div>
  );
};

export default Chart;
