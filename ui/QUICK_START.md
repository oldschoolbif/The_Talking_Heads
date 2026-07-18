# Quick Start Guide

## Ports Used

- **Frontend**: Port 3001 (to avoid conflict with exponis-local on 3000)
- **API**: Port 8001 (to avoid conflict with exponis-local on 8000)

## One-Command Start (Recommended)

```powershell
cd ui
.\start-ui.ps1
```

This will:
1. Check prerequisites (Node.js, Python)
2. Install dependencies if needed
3. Start the Flask API server (port 8001)
4. Start the React dev server (port 3001)

## Manual Start (Two Terminals)

**Terminal 1 - Flask API Server:**
```powershell
cd ui
python server.py
```

**Terminal 2 - React Dev Server:**
```powershell
cd ui
$env:PORT="3001"
npm start
```

## Access the UI

Open your browser to: **http://localhost:3001**

The API is available at: **http://localhost:8001/api**

## Troubleshooting

### Port Already in Use

If port 3001 or 8001 is in use:
- Close other applications using those ports
- Or change ports in:
  - `ui/.env` (React port)
  - `ui/server.py` (Flask port, line ~34)

### Node.js Not Found

Install Node.js from https://nodejs.org/ (LTS version)

### Module Not Found

Run `npm install` in the `ui` directory
