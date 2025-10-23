import React from 'react'

export default function SignalDetails({ signal, onClose }) {
  if (!signal) return null

  return (
    <div
      style={{
        position: 'fixed',
        left: 0,
        top: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 2000,
      }}
      onClick={onClose}
    >
      <div
        style={{ background: '#fff', padding: 16, borderRadius: 8, minWidth: 320, maxWidth: '90%' }}
        onClick={(e) => e.stopPropagation()}
      >
        <h4>Signal #{signal.id}</h4>
        <div>
          <strong>Symbol:</strong> {signal.symbol}
        </div>
        <div>
          <strong>Action:</strong> {signal.action}
        </div>
        <div>
          <strong>Price:</strong> {signal.price}
        </div>
        <div style={{ marginTop: 8 }}>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{signal.raw}</pre>
        </div>
        <div style={{ textAlign: 'right' }}>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  )
}
