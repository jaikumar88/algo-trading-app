import React from 'react'
import './SignalDetails.css'

export default function SignalDetails({ signal, onClose }) {
  if (!signal) return null

  function formatDate(dateString) {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    })
  }

  function getActionColor(action) {
    if (!action) return '#6b7280'
    const actionLower = action.toLowerCase()
    if (actionLower === 'buy') return '#10b981'
    if (actionLower === 'sell') return '#ef4444'
    return '#6b7280'
  }

  return (
    <div className="signal-modal-overlay" onClick={onClose}>
      <div className="signal-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-section">
            <h3>📊 Signal Details</h3>
            <span className="signal-id-badge">#{signal.id}</span>
          </div>
          <button className="btn-close" onClick={onClose} title="Close">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="modal-body">
          <div className="detail-grid">
            {/* Symbol */}
            <div className="detail-item">
              <div className="detail-label">💹 Symbol</div>
              <div className="detail-value symbol-value">
                {signal.symbol || 'N/A'}
              </div>
            </div>

            {/* Action */}
            <div className="detail-item">
              <div className="detail-label">⚡ Action</div>
              <div className="detail-value">
                <span 
                  className="action-badge-large"
                  style={{ 
                    background: `${getActionColor(signal.action)}20`,
                    color: getActionColor(signal.action)
                  }}
                >
                  {signal.action || 'N/A'}
                </span>
              </div>
            </div>

            {/* Price */}
            <div className="detail-item">
              <div className="detail-label">💰 Price</div>
              <div className="detail-value price-value">
                {signal.price ? `$${parseFloat(signal.price).toLocaleString()}` : 'N/A'}
              </div>
            </div>

            {/* Source */}
            <div className="detail-item">
              <div className="detail-label">📡 Source</div>
              <div className="detail-value">
                <span className="source-badge-large">
                  {signal.source || 'Unknown'}
                </span>
              </div>
            </div>

            {/* Created Time */}
            <div className="detail-item full-width">
              <div className="detail-label">🕐 Created At</div>
              <div className="detail-value time-value">
                {formatDate(signal.created_at)}
              </div>
            </div>
          </div>

          {/* Raw Signal Data */}
          {signal.raw && (
            <div className="raw-signal-section">
              <div className="section-header">
                <span className="section-icon">📄</span>
                <span className="section-title">Raw Signal Data</span>
              </div>
              <pre className="raw-signal-content">{signal.raw}</pre>
            </div>
          )}

          {/* Summary (if available) */}
          {signal.summary && (
            <div className="summary-section">
              <div className="section-header">
                <span className="section-icon">📝</span>
                <span className="section-title">Summary</span>
              </div>
              <p className="summary-content">{signal.summary}</p>
            </div>
          )}

          {/* Additional Info */}
          {(signal.instrument_id || signal.confidence) && (
            <div className="additional-info">
              {signal.instrument_id && (
                <div className="info-chip">
                  <span className="info-label">Instrument ID:</span>
                  <span className="info-value">{signal.instrument_id}</span>
                </div>
              )}
              {signal.confidence && (
                <div className="info-chip">
                  <span className="info-label">Confidence:</span>
                  <span className="info-value">{signal.confidence}%</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn-close-large" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
