# Death Star Management System Dashboard Local Setup Guide

## Directory Structure

```
├── Phase2.html           # Main frontend page
├── gauge-server.js       # WebSocket server (Node.js)
├── styles.css            # Stylesheet
├── main.js               # Other JS logic (if any)
```

## Environment Requirements
- Node.js (recommended 16+)
- Recommended: VSCode + Live Server plugin or Python/Node local server

---

## Step 1: Start WebSocket Server

1. Install dependencies (first time only):
   ```bash
   npm install ws
   ```
2. Start the server:
   ```bash
   node gauge-server.js
   ```
   You should see:
   ```
   WebSocket server running at ws://localhost:8080/updates
   ```

---

## Step 2: Launch Frontend Page Locally

**Do not open the HTML file directly with file:// protocol!**

Recommended Method 1: VSCode Live Server Plugin
1. Install Live Server plugin
2. Right-click `Phase2.html`, select "Open with Live Server"
3. Access `http://localhost:5500/Phase2.html` in your browser (port may vary)

Recommended Method 2: Python Local Server
```bash
python3 -m http.server 8000
```
Then access in browser:
```
http://localhost:8000/Phase2.html
```

Recommended Method 3: Node http-server
```bash
npx http-server .
```
Then access in browser:
```
http://localhost:8080/Phase2.html
```

---

## Step 3: Experience Real-time Dashboard

1. After opening the page, the Dashboard area will display three gauges: Energy, Droid, and Facilities.
2. The gauges will automatically receive random data via WebSocket every 2 seconds and update in real-time.
3. When a value falls below the threshold, a red warning toast will appear in the top-right corner.

---

## Common Issues

- **Page stuck loading?**
  > Make sure you've opened the page using a local server and replaced the dashboard area.

- **No data in gauges?**
  > Verify that gauge-server.js is running properly and the frontend WebSocket address is `ws://localhost:8080/updates`.

- **Port conflict?**
  > You can modify the port number in gauge-server.js, but remember to update the frontend WebSocket address accordingly.

---

## Additional Notes
- You can modify `gauge-server.js` to push real business data.
- Gauge styles and thresholds can be customized in Phase2.html.

---

For any issues, please contact the project maintainer. 