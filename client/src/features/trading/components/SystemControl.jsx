import { useState, useEffect } from 'react';
import axios from 'axios';
import './SystemControl.css';

const SystemControl = () => {
  const [settings, setSettings] = useState({});
  const [fundAllocations, setFundAllocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [settingsRes, allocationsRes] = await Promise.all([
        axios.get('/api/trading/settings'),
        axios.get('/api/trading/fund-allocations')
      ]);

      // Convert settings array to object
      const settingsObj = {};
      settingsRes.data.settings.forEach(s => {
        settingsObj[s.key] = {
          value: s.value,
          type: s.value_type,
          description: s.description
        };
      });

      setSettings(settingsObj);
      setFundAllocations(allocationsRes.data.allocations || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.response?.data?.error || 'Failed to fetch system data');
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key, value) => {
    setSaving(true);
    try {
      await axios.put(`/api/trading/settings/${key}`, { value: String(value) });
      await fetchData(); // Refresh all data
      alert('Setting updated successfully!');
    } catch (err) {
      console.error('Error updating setting:', err);
      alert(err.response?.data?.error || 'Failed to update setting');
    } finally {
      setSaving(false);
    }
  };

  const toggleTradingEnabled = async () => {
    const currentValue = settings.trading_enabled?.value === 'true';
    await updateSetting('trading_enabled', !currentValue);
  };

  const handleTotalFundChange = (e) => {
    const value = e.target.value;
    if (value && parseFloat(value) > 0) {
      updateSetting('total_fund', value);
    }
  };

  const handleRiskPercentChange = (e) => {
    const value = e.target.value;
    if (value && parseFloat(value) > 0 && parseFloat(value) <= 100) {
      updateSetting('risk_per_instrument', parseFloat(value) / 100);
    }
  };

  const tradingEnabled = settings.trading_enabled?.value === 'true';
  const totalFund = parseFloat(settings.total_fund?.value || 0);
  const riskPercent = (parseFloat(settings.risk_per_instrument?.value || 0) * 100).toFixed(1);
  const autoStopLoss = settings.auto_stop_loss?.value === 'true';

  const totalAllocated = fundAllocations.reduce((sum, a) => sum + parseFloat(a.allocated_amount || 0), 0);
  const totalUsed = fundAllocations.reduce((sum, a) => sum + parseFloat(a.used_amount || 0), 0);
  const totalLoss = fundAllocations.reduce((sum, a) => sum + parseFloat(a.total_loss || 0), 0);
  const activeInstruments = fundAllocations.filter(a => a.trading_enabled).length;

  return (
    <div className="system-control-container">
      <div className="control-header">
        <h1>⚙️ System Control</h1>
        <div className={`system-status ${tradingEnabled ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <span className="status-text">{tradingEnabled ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}</span>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading system data...</div>
      ) : error ? (
        <div className="error-message">
          ❌ {error}
          <button onClick={fetchData}>Retry</button>
        </div>
      ) : (
        <>
          {/* Master Control */}
          <div className="control-section master-control">
            <div className="section-header">
              <h2>🎛️ Master Control</h2>
              <p>Emergency stop for all trading activities</p>
            </div>
            
            <div className="master-switch-container">
              <div className="switch-info">
                <h3>Trading System</h3>
                <p>{tradingEnabled ? 'All trading operations are active' : 'All trading operations are paused'}</p>
              </div>
              <button 
                className={`master-switch ${tradingEnabled ? 'on' : 'off'}`}
                onClick={toggleTradingEnabled}
                disabled={saving}
              >
                <span className="switch-icon">{tradingEnabled ? '🟢' : '🔴'}</span>
                <span className="switch-text">{tradingEnabled ? 'TURN OFF' : 'TURN ON'}</span>
              </button>
            </div>
          </div>

          {/* Fund Management */}
          <div className="control-section">
            <div className="section-header">
              <h2>💰 Fund Management</h2>
              <p>Configure total fund and risk parameters</p>
            </div>

            <div className="fund-settings">
              <div className="setting-card">
                <label>Total Fund (USD)</label>
                <div className="input-group">
                  <span className="input-prefix">$</span>
                  <input 
                    type="number" 
                    defaultValue={totalFund}
                    onBlur={handleTotalFundChange}
                    min="1000"
                    step="1000"
                    disabled={saving}
                  />
                </div>
                <small>Total capital available for trading</small>
              </div>

              <div className="setting-card">
                <label>Risk Per Instrument (%)</label>
                <div className="input-group">
                  <input 
                    type="number" 
                    defaultValue={riskPercent}
                    onBlur={handleRiskPercentChange}
                    min="0.1"
                    max="100"
                    step="0.1"
                    disabled={saving}
                  />
                  <span className="input-suffix">%</span>
                </div>
                <small>Maximum loss allowed per instrument</small>
              </div>

              <div className="setting-card checkbox-card">
                <label>
                  <input 
                    type="checkbox" 
                    checked={autoStopLoss}
                    onChange={(e) => updateSetting('auto_stop_loss', e.target.checked)}
                    disabled={saving}
                  />
                  <span>Auto-Stop Loss Protection</span>
                </label>
                <small>Automatically disable trading when risk limit is reached</small>
              </div>
            </div>
          </div>

          {/* System Overview */}
          <div className="control-section">
            <div className="section-header">
              <h2>📊 System Overview</h2>
              <p>Current system status and metrics</p>
            </div>

            <div className="overview-grid">
              <div className="overview-card">
                <div className="overview-icon">💵</div>
                <div className="overview-content">
                  <div className="overview-label">Total Fund</div>
                  <div className="overview-value">${totalFund.toLocaleString()}</div>
                </div>
              </div>

              <div className="overview-card">
                <div className="overview-icon">📦</div>
                <div className="overview-content">
                  <div className="overview-label">Allocated</div>
                  <div className="overview-value">${totalAllocated.toLocaleString()}</div>
                </div>
              </div>

              <div className="overview-card">
                <div className="overview-icon">💼</div>
                <div className="overview-content">
                  <div className="overview-label">In Use</div>
                  <div className="overview-value">${totalUsed.toLocaleString()}</div>
                </div>
              </div>

              <div className="overview-card">
                <div className="overview-icon">⚠️</div>
                <div className="overview-content">
                  <div className="overview-label">Total Loss</div>
                  <div className="overview-value loss">${totalLoss.toLocaleString()}</div>
                </div>
              </div>

              <div className="overview-card">
                <div className="overview-icon">🎯</div>
                <div className="overview-content">
                  <div className="overview-label">Active Instruments</div>
                  <div className="overview-value">{activeInstruments}</div>
                </div>
              </div>

              <div className="overview-card">
                <div className="overview-icon">🛡️</div>
                <div className="overview-content">
                  <div className="overview-label">Risk Limit</div>
                  <div className="overview-value">{riskPercent}%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Fund Allocations */}
          {fundAllocations.length > 0 && (
            <div className="control-section">
              <div className="section-header">
                <h2>📈 Fund Allocations by Instrument</h2>
                <p>Detailed breakdown of funds per instrument</p>
              </div>

              <div className="allocations-table-container">
                <table className="allocations-table">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Allocated</th>
                      <th>Used</th>
                      <th>Available</th>
                      <th>Total Loss</th>
                      <th>Risk Limit</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fundAllocations.map(alloc => {
                      const available = parseFloat(alloc.allocated_amount) - parseFloat(alloc.used_amount);
                      const lossPercent = (parseFloat(alloc.total_loss) / parseFloat(alloc.allocated_amount) * 100).toFixed(1);
                      
                      return (
                        <tr key={alloc.symbol}>
                          <td className="symbol-cell">
                            <span className="symbol-badge">{alloc.symbol}</span>
                          </td>
                          <td>${parseFloat(alloc.allocated_amount).toLocaleString()}</td>
                          <td>${parseFloat(alloc.used_amount).toLocaleString()}</td>
                          <td className="available-cell">${available.toLocaleString()}</td>
                          <td className="loss-cell">
                            ${parseFloat(alloc.total_loss).toLocaleString()} ({lossPercent}%)
                          </td>
                          <td className="risk-cell">${parseFloat(alloc.risk_limit).toLocaleString()}</td>
                          <td>
                            <span className={`status-indicator ${alloc.trading_enabled ? 'active' : 'inactive'}`}>
                              {alloc.trading_enabled ? '✅ Active' : '❌ Paused'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Risk Warnings */}
          {totalLoss > 0 && (
            <div className="risk-alert">
              <div className="alert-icon">⚠️</div>
              <div className="alert-content">
                <strong>Risk Alert:</strong> Total system loss is ${totalLoss.toLocaleString()}. 
                Monitor your positions carefully and consider adjusting risk parameters if needed.
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SystemControl;
