# UI Setup Instructions

## Prerequisites

You need **Node.js** installed to run the React UI.

### Install Node.js

1. **Download Node.js**:
   - Go to https://nodejs.org/
   - Download the LTS version (recommended)
   - Run the installer and follow the setup wizard

2. **Verify Installation**:
   ```powershell
   node --version
   npm --version
   ```
   Both commands should show version numbers.

## Quick Start

Once Node.js is installed:

```powershell
cd ui

# Install dependencies (first time only)
npm install

# Start the servers
.\start.ps1
```

Or start manually in two terminals:

**Terminal 1** (Flask API server):
```powershell
cd ui
python server.py
```

**Terminal 2** (React dev server):
```powershell
cd ui
npm start
```

The UI will be available at:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:5001

## Troubleshooting

### "node is not recognized"
- Node.js is not installed or not in PATH
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

### "npm is not recognized"
- Same as above - install Node.js

### "Cannot find module"
- Run `npm install` in the `ui` directory

### Port 3000 or 5001 already in use
- Close other applications using those ports
- Or change ports in `package.json` (React) and `server.py` (Flask)

