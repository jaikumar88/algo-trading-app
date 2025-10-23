Quick React client examples

This project exposes simple endpoints you can call from a React frontend during development.

1) Install and run the Flask backend (from project root):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

2) Example fetches from React (use fetch or axios). These assume the backend is at http://localhost:5000

- Fetch signals:

```js
// example using fetch inside React (e.g., in useEffect)
async function getSignals(date, symbol) {
  const params = new URLSearchParams();
  if (date) params.set('date', date);
  if (symbol) params.set('symbol', symbol);
  const res = await fetch('http://localhost:5000/api/signals?' + params.toString());
  const data = await res.json();
  return data;
}

// usage
useEffect(() => {
  getSignals().then(data => setSignals(data.signals));
}, []);
```

- Fetch metrics (for dashboard charts):

```js
async function getMetrics(){
  const res = await fetch('http://localhost:5000/api/metrics');
  return await res.json();
}
```

Development tips
- If your React dev server runs on a different port, CORS is enabled for all origins in the backend (development setting). In production restrict allowed origins.
- To proxy API calls during development with Vite/CRA, add a `proxy` setting or configure vite.config.js to forward `/api` to `http://localhost:5000`.

If you'd like, I can scaffold a small Vite React app in `client/` and wire a proxy for dev-time convenience.
