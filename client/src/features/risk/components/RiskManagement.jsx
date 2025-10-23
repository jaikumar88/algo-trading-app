import { useState, useEffect } from 'react';
import axios from 'axios';
import './RiskManagement.css';
import { apiUrl } from '../../../services/api'

const RiskManagement = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    // Basic Risk Settings
    stop_loss_percent: 1.0,
    take_profit_percent: 2.0,
    max_position_size: 100,
    max_daily_loss: 1000,
    max_daily_trades: 50,
    
    // Advanced Risk Settings
    trailing_stop_enabled: false,
    trailing_stop_type: 'percent',
    trailing_stop_percent: 0.5,
    trailing_stop_amount: 50,
    max_open_positions: 10,
    max_risk_per_trade: 100,
    risk_reward_ratio: 2.0,
    
    // Portfolio Risk
    max_portfolio_risk_percent: 5.0,
    max_correlation_exposure: 3,
    daily_loss_limit_enabled: true,
    auto_close_on_daily_limit: true,
    
    // Symbol-Specific Risk
    symbol_max_exposure: {},
    blacklisted_symbols: [],
    
    // Time-Based Controls
    trading_hours_enabled: false,
    trading_start_hour: 9,
    trading_end_hour: 17,
    avoid_news_events: false,
    
    // Emergency Controls
    panic_mode: false,
    emergency_close_all: false,
  });

  const [stats, setStats] = useState({
    current_daily_loss: 0,
    current_daily_trades: 0,
    current_open_positions: 0,
    total_exposure: 0,
    available_risk_budget: 1000,
  });

  useEffect(() => {
    fetchRiskSettings();
    fetchRiskStats();
    
    // Refresh stats every 10 seconds
    const interval = setInterval(fetchRiskStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchRiskSettings = async () => {
    try {
      const response = await axios.get(apiUrl('/api/risk/settings'));
      if (response.data.settings) {
        setSettings(prev => ({ ...prev, ...response.data.settings }));
      }
      setLoading(false);
    } catch (err) {
      console.error('Error fetching risk settings:', err);
      setLoading(false);
    }
  };

  const fetchRiskStats = async () => {
    try {
      const response = await axios.get(apiUrl('/api/risk/stats'));
      if (response.data) {
        setStats(response.data);
      }
    } catch (err) {
      console.error('Error fetching risk stats:', err);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await axios.post(apiUrl('/api/risk/settings'), settings);
      alert('Risk management settings saved successfully!');
    } catch (err) {
      alert('Failed to save settings: ' + (err.response?.data?.error || err.message));
    }
    setSaving(false);
  };

  const handleInputChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEmergencyClose = async () => {
    if (!window.confirm('⚠️ EMERGENCY: Close all open positions immediately?')) {
      return;
    }
    
    try {
      await axios.post(apiUrl('/api/risk/emergency-close'));
      alert('All positions closed successfully!');
      fetchRiskStats();
    } catch (err) {
      alert('Failed to close positions: ' + (err.response?.data?.error || err.message));
    }
  };

  const handlePanicMode = async () => {
    const newMode = !settings.panic_mode;
    
    if (newMode && !window.confirm('⚠️ Enable PANIC MODE? This will stop all new trades and apply maximum risk protection.')) {
      return;
    }
    
    try {
      await axios.post(apiUrl('/api/risk/panic-mode'), { enabled: newMode });
      setSettings(prev => ({ ...prev, panic_mode: newMode }));
      alert(newMode ? 'Panic mode ENABLED' : 'Panic mode DISABLED');
    } catch (err) {
      alert('Failed to toggle panic mode: ' + (err.response?.data?.error || err.message));
    }
  };

  const getRiskLevel = () => {
    const riskPercent = (stats.current_daily_loss / settings.max_daily_loss) * 100;
    if (riskPercent >= 90) return { level: 'CRITICAL', color: '#dc3545' };
    if (riskPercent >= 70) return { level: 'HIGH', color: '#fd7e14' };
    if (riskPercent >= 50) return { level: 'MODERATE', color: '#ffc107' };
    return { level: 'LOW', color: '#28a745' };
  };

  const risk = getRiskLevel();

  if (loading) {
    return <div className="loading">Loading risk management settings...</div>;
  }

  return (
    <div className="risk-management-container">
      <div className="risk-header">
        <h1>🛡️ Risk Management</h1>
        <div className="header-actions">
          <button 
            className={`panic-btn ${settings.panic_mode ? 'active' : ''}`}
            onClick={handlePanicMode}
          >
            {settings.panic_mode ? '🔴 PANIC MODE ON' : '⚠️ Panic Mode'}
          </button>
          <button className="save-btn" onClick={handleSaveSettings} disabled={saving}>
            {saving ? '⏳ Saving...' : '💾 Save Settings'}
          </button>
        </div>
      </div>

      {/* Risk Dashboard */}
      <div className="risk-dashboard">
        <div className="dashboard-card">
          <h3>Current Risk Level</h3>
          <div className="risk-indicator" style={{ backgroundColor: risk.color }}>
            {risk.level}
          </div>
        </div>
        
        <div className="dashboard-card">
          <h3>Daily Loss</h3>
          <div className="stat-value">
            ${stats.current_daily_loss.toFixed(2)} / ${settings.max_daily_loss.toFixed(2)}
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${Math.min((stats.current_daily_loss / settings.max_daily_loss) * 100, 100)}%`,
                backgroundColor: risk.color
              }}
            />
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Daily Trades</h3>
          <div className="stat-value">
            {stats.current_daily_trades} / {settings.max_daily_trades}
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Open Positions</h3>
          <div className="stat-value">
            {stats.current_open_positions} / {settings.max_open_positions}
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Available Risk Budget</h3>
          <div className="stat-value" style={{ color: '#28a745' }}>
            ${stats.available_risk_budget.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="settings-grid">
        
        {/* Basic Risk Settings */}
        <div className="settings-section">
          <h2>📊 Basic Risk Settings</h2>
          
          <div className="form-group">
            <label>Stop Loss Percentage</label>
            <input 
              type="number" 
              step="0.1"
              value={settings.stop_loss_percent}
              onChange={(e) => handleInputChange('stop_loss_percent', parseFloat(e.target.value))}
            />
            <small>Default stop loss for all trades (e.g., 1.0 = 1%)</small>
          </div>

          <div className="form-group">
            <label>Take Profit Percentage</label>
            <input 
              type="number" 
              step="0.1"
              value={settings.take_profit_percent}
              onChange={(e) => handleInputChange('take_profit_percent', parseFloat(e.target.value))}
            />
            <small>Default take profit for all trades (e.g., 2.0 = 2%)</small>
          </div>

          <div className="form-group">
            <label>Max Position Size</label>
            <input 
              type="number" 
              value={settings.max_position_size}
              onChange={(e) => handleInputChange('max_position_size', parseFloat(e.target.value))}
            />
            <small>Maximum size for a single position</small>
          </div>

          <div className="form-group">
            <label>Max Daily Loss ($)</label>
            <input 
              type="number" 
              value={settings.max_daily_loss}
              onChange={(e) => handleInputChange('max_daily_loss', parseFloat(e.target.value))}
            />
            <small>Stop trading when daily loss reaches this amount</small>
          </div>

          <div className="form-group">
            <label>Max Daily Trades</label>
            <input 
              type="number" 
              value={settings.max_daily_trades}
              onChange={(e) => handleInputChange('max_daily_trades', parseInt(e.target.value))}
            />
            <small>Maximum number of trades allowed per day</small>
          </div>
        </div>

        {/* Advanced Risk Settings */}
        <div className="settings-section">
          <h2>⚙️ Advanced Risk Settings</h2>
          
          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={settings.trailing_stop_enabled}
                onChange={(e) => handleInputChange('trailing_stop_enabled', e.target.checked)}
              />
              Enable Trailing Stop Loss
            </label>
          </div>

          {settings.trailing_stop_enabled && (
            <>
              <div className="form-group indent">
                <label>Trailing Stop Type</label>
                <select
                  value={settings.trailing_stop_type}
                  onChange={(e) => handleInputChange('trailing_stop_type', e.target.value)}
                >
                  <option value="percent">Percentage</option>
                  <option value="amount">Fixed Amount ($)</option>
                </select>
                <small>Choose to trail by percentage or fixed dollar amount</small>
              </div>

              {settings.trailing_stop_type === 'percent' ? (
                <div className="form-group indent">
                  <label>Trailing Stop Percentage</label>
                  <input 
                    type="number" 
                    step="0.1"
                    value={settings.trailing_stop_percent}
                    onChange={(e) => handleInputChange('trailing_stop_percent', parseFloat(e.target.value))}
                  />
                  <small>Trail stop loss by this % as profit increases (e.g., 0.5 = 0.5%)</small>
                </div>
              ) : (
                <div className="form-group indent">
                  <label>Trailing Stop Amount ($)</label>
                  <input 
                    type="number" 
                    step="10"
                    value={settings.trailing_stop_amount}
                    onChange={(e) => handleInputChange('trailing_stop_amount', parseFloat(e.target.value))}
                  />
                  <small>Trail stop loss by this $ amount (e.g., 50 = $50)</small>
                </div>
              )}
            </>
          )}

          <div className="form-group">
            <label>Max Open Positions</label>
            <input 
              type="number" 
              value={settings.max_open_positions}
              onChange={(e) => handleInputChange('max_open_positions', parseInt(e.target.value))}
            />
            <small>Maximum number of concurrent open positions</small>
          </div>

          <div className="form-group">
            <label>Max Risk Per Trade ($)</label>
            <input 
              type="number" 
              value={settings.max_risk_per_trade}
              onChange={(e) => handleInputChange('max_risk_per_trade', parseFloat(e.target.value))}
            />
            <small>Maximum amount to risk on a single trade</small>
          </div>

          <div className="form-group">
            <label>Risk/Reward Ratio</label>
            <input 
              type="number" 
              step="0.1"
              value={settings.risk_reward_ratio}
              onChange={(e) => handleInputChange('risk_reward_ratio', parseFloat(e.target.value))}
            />
            <small>Minimum risk/reward ratio (e.g., 2.0 = 2:1 reward)</small>
          </div>
        </div>

        {/* Portfolio Risk */}
        <div className="settings-section">
          <h2>💼 Portfolio Risk</h2>
          
          <div className="form-group">
            <label>Max Portfolio Risk (%)</label>
            <input 
              type="number" 
              step="0.1"
              value={settings.max_portfolio_risk_percent}
              onChange={(e) => handleInputChange('max_portfolio_risk_percent', parseFloat(e.target.value))}
            />
            <small>Maximum percentage of portfolio at risk at any time</small>
          </div>

          <div className="form-group">
            <label>Max Correlation Exposure</label>
            <input 
              type="number" 
              value={settings.max_correlation_exposure}
              onChange={(e) => handleInputChange('max_correlation_exposure', parseInt(e.target.value))}
            />
            <small>Maximum positions in correlated instruments</small>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={settings.daily_loss_limit_enabled}
                onChange={(e) => handleInputChange('daily_loss_limit_enabled', e.target.checked)}
              />
              Enable Daily Loss Limit
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={settings.auto_close_on_daily_limit}
                onChange={(e) => handleInputChange('auto_close_on_daily_limit', e.target.checked)}
              />
              Auto-Close All Positions on Daily Limit
            </label>
          </div>
        </div>

        {/* Time-Based Controls */}
        <div className="settings-section">
          <h2>⏰ Time-Based Controls</h2>
          
          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={settings.trading_hours_enabled}
                onChange={(e) => handleInputChange('trading_hours_enabled', e.target.checked)}
              />
              Restrict Trading Hours
            </label>
          </div>

          {settings.trading_hours_enabled && (
            <>
              <div className="form-group indent">
                <label>Trading Start Hour (24h format)</label>
                <input 
                  type="number" 
                  min="0" 
                  max="23"
                  value={settings.trading_start_hour}
                  onChange={(e) => handleInputChange('trading_start_hour', parseInt(e.target.value))}
                />
              </div>

              <div className="form-group indent">
                <label>Trading End Hour (24h format)</label>
                <input 
                  type="number" 
                  min="0" 
                  max="23"
                  value={settings.trading_end_hour}
                  onChange={(e) => handleInputChange('trading_end_hour', parseInt(e.target.value))}
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={settings.avoid_news_events}
                onChange={(e) => handleInputChange('avoid_news_events', e.target.checked)}
              />
              Avoid Trading During News Events
            </label>
          </div>
        </div>

      </div>

      {/* Emergency Controls */}
      <div className="emergency-section">
        <h2>🚨 Emergency Controls</h2>
        <div className="emergency-buttons">
          <button 
            className="emergency-btn close-all"
            onClick={handleEmergencyClose}
          >
            ⛔ CLOSE ALL POSITIONS
          </button>
          <div className="emergency-info">
            <p>Use this button to immediately close all open positions.</p>
            <p>⚠️ This action cannot be undone!</p>
          </div>
        </div>
      </div>

    </div>
  );
};

export default RiskManagement;
