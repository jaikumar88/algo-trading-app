import { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminInstruments.css';

const AdminInstruments = () => {
  const [instruments, setInstruments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    symbol: '',
    name: '',
    enabled: true
  });

  useEffect(() => {
    fetchInstruments();
  }, []);

  const fetchInstruments = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/trading/instruments');
      setInstruments(response.data.instruments || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching instruments:', err);
      setError(err.response?.data?.error || 'Failed to fetch instruments');
    } finally {
      setLoading(false);
    }
  };

  const handleAddInstrument = async (e) => {
    e.preventDefault();
    
    if (!formData.symbol || !formData.name) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      await axios.post('/api/trading/instruments', formData);
      alert('Instrument added successfully!');
      setShowAddModal(false);
      setFormData({ symbol: '', name: '', enabled: true });
      fetchInstruments();
    } catch (err) {
      console.error('Error adding instrument:', err);
      alert(err.response?.data?.error || 'Failed to add instrument');
    }
  };

  const handleUpdateInstrument = async (id, updates) => {
    try {
      await axios.put(`/api/trading/instruments/${id}`, updates);
      fetchInstruments();
    } catch (err) {
      console.error('Error updating instrument:', err);
      alert(err.response?.data?.error || 'Failed to update instrument');
    }
  };

  const handleDeleteInstrument = async (id, symbol) => {
    if (!confirm(`Are you sure you want to delete ${symbol}? This action cannot be undone.`)) {
      return;
    }

    try {
      await axios.delete(`/api/trading/instruments/${id}`);
      alert('Instrument deleted successfully!');
      fetchInstruments();
    } catch (err) {
      console.error('Error deleting instrument:', err);
      alert(err.response?.data?.error || 'Failed to delete instrument');
    }
  };

  const toggleEnabled = async (id, currentStatus) => {
    await handleUpdateInstrument(id, { enabled: !currentStatus });
  };

  const enabledCount = instruments.filter(i => i.enabled).length;
  const disabledCount = instruments.filter(i => !i.enabled).length;

  return (
    <div className="admin-instruments-container">
      <div className="instruments-header">
        <h1>🎯 Instrument Management</h1>
        <button className="add-btn" onClick={() => setShowAddModal(true)}>
          ➕ Add Instrument
        </button>
      </div>

      {/* Stats */}
      <div className="instruments-stats">
        <div className="stat-box">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <div className="stat-label">Total Instruments</div>
            <div className="stat-value">{instruments.length}</div>
          </div>
        </div>
        <div className="stat-box enabled">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-label">Enabled</div>
            <div className="stat-value">{enabledCount}</div>
          </div>
        </div>
        <div className="stat-box disabled">
          <div className="stat-icon">❌</div>
          <div className="stat-info">
            <div className="stat-label">Disabled</div>
            <div className="stat-value">{disabledCount}</div>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="info-box">
        <div className="info-icon">ℹ️</div>
        <div className="info-content">
          <strong>Instrument Whitelist:</strong> Only enabled instruments are allowed for trading. 
          Disable instruments to prevent new trades while keeping existing data.
        </div>
      </div>

      {/* Instruments List */}
      {loading ? (
        <div className="loading">Loading instruments...</div>
      ) : error ? (
        <div className="error-message">
          ❌ {error}
          <button onClick={fetchInstruments}>Retry</button>
        </div>
      ) : instruments.length === 0 ? (
        <div className="no-data">
          <div className="no-data-icon">📭</div>
          <h3>No Instruments Yet</h3>
          <p>Add your first instrument to start trading</p>
          <button className="add-first-btn" onClick={() => setShowAddModal(true)}>
            ➕ Add First Instrument
          </button>
        </div>
      ) : (
        <div className="instruments-grid">
          {instruments.map(instrument => (
            <div 
              key={instrument.id} 
              className={`instrument-card ${instrument.enabled ? 'enabled' : 'disabled'}`}
            >
              <div className="instrument-header">
                <div className="instrument-info">
                  <h3 className="instrument-symbol">{instrument.symbol}</h3>
                  <p className="instrument-name">{instrument.name}</p>
                </div>
                <div className={`status-badge ${instrument.enabled ? 'active' : 'inactive'}`}>
                  {instrument.enabled ? '✅ Active' : '❌ Inactive'}
                </div>
              </div>

              <div className="instrument-meta">
                <div className="meta-row">
                  <span className="meta-label">ID:</span>
                  <span className="meta-value">{instrument.id}</span>
                </div>
                {instrument.created_at && (
                  <div className="meta-row">
                    <span className="meta-label">Added:</span>
                    <span className="meta-value">
                      {new Date(instrument.created_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="instrument-actions">
                <button 
                  className={`toggle-btn ${instrument.enabled ? 'disable' : 'enable'}`}
                  onClick={() => toggleEnabled(instrument.id, instrument.enabled)}
                >
                  {instrument.enabled ? '🚫 Disable' : '✅ Enable'}
                </button>
                <button 
                  className="delete-btn"
                  onClick={() => handleDeleteInstrument(instrument.id, instrument.symbol)}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>➕ Add New Instrument</h2>
              <button className="close-modal" onClick={() => setShowAddModal(false)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleAddInstrument} className="instrument-form">
              <div className="form-group">
                <label htmlFor="symbol">
                  Symbol <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="symbol"
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                  placeholder="e.g., BTCUSDT"
                  required
                />
                <small>Trading pair symbol (e.g., BTCUSDT, ETHUSDT)</small>
              </div>

              <div className="form-group">
                <label htmlFor="name">
                  Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="e.g., Bitcoin"
                  required
                />
                <small>Friendly name for the instrument</small>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) => setFormData({...formData, enabled: e.target.checked})}
                  />
                  <span>Enable trading immediately</span>
                </label>
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="submit-btn">
                  ➕ Add Instrument
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminInstruments;
