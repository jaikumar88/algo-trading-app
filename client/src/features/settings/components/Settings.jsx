import React from 'react'

export default function Settings({ theme, onThemeChange }) {
  const [apiUrl, setApiUrl] = React.useState(() => {
    return localStorage.getItem('apiBaseUrl') || 'http://localhost:5000'
  })
  const [saved, setSaved] = React.useState(false)

  const handleSave = () => {
    localStorage.setItem('apiBaseUrl', apiUrl)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    const defaultUrl = 'http://localhost:5000'
    setApiUrl(defaultUrl)
    localStorage.setItem('apiBaseUrl', defaultUrl)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="settings-container">
      <h2>Settings</h2>
      
      <div className="settings-section">
        <h3>Appearance</h3>
        <div className="setting-item">
          <label>
            <span className="setting-label">Theme</span>
            <select 
              value={theme} 
              onChange={(e) => onThemeChange(e.target.value)}
              className="theme-select"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </label>
        </div>
      </div>

      <div className="settings-section">
        <h3>API Configuration</h3>
        <div className="setting-item">
          <label>
            <span className="setting-label">Backend URL</span>
            <input 
              type="text" 
              value={apiUrl} 
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:5000"
              className="api-input"
            />
          </label>
          <small className="help-text">
            The base URL for the Flask backend API. Change this if deploying remotely.
          </small>
        </div>
        <div className="button-group">
          <button onClick={handleSave} className="btn-primary">
            Save Configuration
          </button>
          <button onClick={handleReset} className="btn-secondary">
            Reset to Default
          </button>
        </div>
        {saved && <div className="save-message">✓ Settings saved successfully!</div>}
      </div>

      <div className="settings-section">
        <h3>About</h3>
        <p className="about-text">
          <strong>RAG Trading Assistant</strong><br />
          Version 1.0.0<br />
          A demo application for processing TradingView webhooks with RAG and Telegram integration.
        </p>
      </div>
    </div>
  )
}
