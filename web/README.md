# IoT Network Selection - Web UI Visualization 🗺️

Interactive map visualization cho IoT Network Selection System với real-time simulation và decision making.

## 🎯 Features

### 📊 **Map Visualization**
- **2D Map**: 1000x1000 grid với base stations
- **IoT Device**: Real-time device movement tracking
- **Base Stations**: 12 stations (Wi-Fi, 5G, BLE) distributed across map
- **Coverage Areas**: Visual network coverage based on signal strength
- **Network Connections**: Live visualization của selected network

### 🎮 **Interactive Controls**
- **Simulation Step**: Manual advancement của IoT simulation
- **Make Decision**: Test MCDM algorithm với current network conditions
- **Auto-run Mode**: Continuous simulation với 2-second intervals
- **Reset**: Quay về initial state
- **Manual Placement**: Click trên map để set device position

### 📱 **Real-time Information**
- **Device Status**: Position, simulation step, current task
- **Available Networks**: Live list với bandwidth/latency stats
- **Decision Result**: Selected network với cost analysis
- **System Status**: API connection và performance metrics

## 🚀 Quick Start

### Method 1: Demo Script (Recommended)
```bash
# Chạy demo với auto-browser opening
python demo_web_ui.py
```

### Method 2: Manual Server Start
```bash
# Terminal 1: Start API server
conda activate comsys-project
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Open browser
# Navigate to: http://localhost:8000/ui
```

## 🗺️ Map Layout

### **Base Stations Distribution**
```
Wi-Fi Stations (Blue - #2196F3):
  📶 (200, 200)   📶 (800, 200)
  📶 (200, 800)   📶 (800, 800)

5G Stations (Purple - #9C27B0):  
  📡 (500, 150)   📡 (850, 500)
  📡 (150, 500)   📡 (500, 850)

BLE Stations (Orange - #FF9800):
  🔵 (350, 350)   🔵 (650, 350)
  🔵 (350, 650)   🔵 (650, 650)
```

### **Visual Elements**
- **Red Circle**: IoT Device với task indicator
- **Colored Circles**: Base stations theo network type
- **Semi-transparent Areas**: Network coverage zones
- **Dashed Lines**: Connection to selected network
- **Grid Background**: 100x100 unit grid lines

## 🧠 Decision Algorithm Visualization

### **Task-based Network Selection**
```
IDLE_MONITORING (Blue Badge):
  ⚡ Priority: Energy efficiency (w_energy=0.8)
  🎯 Expected: BLE selection for low power

DATA_BURST_ALERT (Orange Badge):
  ⚖️ Priority: Balanced (w_energy=0.6, w_qos=0.4) 
  🎯 Expected: Wi-Fi selection for reliable throughput

VIDEO_STREAMING (Pink Badge):
  📊 Priority: QoS performance (w_qos=0.7)
  🎯 Expected: 5G selection for high bandwidth
```

### **Cost Visualization**
- **Selected Network**: Highlighted với connection line
- **Cost Comparison**: Real-time cost analysis panel
- **Winner Badge**: Visual indicator của optimal choice

## 🎮 Usage Guide

### **1. Basic Operation**
1. **Start Server**: Run `python demo_web_ui.py`
2. **Check Status**: Verify "API Status: ✅ Online"
3. **Run Simulation**: Click "▶️ Simulation Step"
4. **Make Decision**: Click "🧠 Make Decision" 
5. **Observe Results**: Check decision panel và map connections

### **2. Auto-run Mode**
1. **Enable Auto-run**: Toggle switch in control panel
2. **Observe Continuous Movement**: Device moves every 2 seconds
3. **Track Decisions**: Real-time network selection updates
4. **Disable**: Toggle switch off để stop auto-run

### **3. Manual Testing**
1. **Click on Map**: Set device position manually
2. **Test Different Positions**: Try corners, center, near base stations
3. **Observe Network Changes**: Available networks update based on proximity
4. **Test Edge Cases**: Click far corners để test no-network scenarios

### **4. Algorithm Analysis**
1. **Different Task States**: Observe task changes during simulation
2. **Cost Comparison**: Check cost analysis panel
3. **Network Performance**: Monitor bandwidth/latency changes
4. **Decision Logic**: Verify algorithm selects expected networks

## 📊 Performance Monitoring

### **Real-time Metrics**
- **Simulation Step Time**: Displayed in status bar
- **Decision Making Time**: API response monitoring
- **Network Count**: Available networks at current position
- **Algorithm Performance**: Cost calculation timing

### **Expected Performance**
```
✅ Good Performance:
  - Simulation Step: < 500ms
  - Decision Making: < 1000ms  
  - Map Rendering: < 100ms
  - UI Updates: < 50ms

⚠️ Performance Issues:
  - API Status: ❌ Offline
  - Response Time: > 5 seconds
  - Connection Errors in status bar
```

## 🛠️ Technical Details

### **Frontend Architecture**
- **HTML5 Canvas**: High-performance 2D rendering
- **Vanilla JavaScript**: No framework dependencies
- **Responsive Design**: Adaptive layout với CSS Grid
- **Real-time Updates**: WebSocket-style polling simulation

### **API Integration**
```javascript
// Key API endpoints used:
GET  /health           // Server status check
GET  /status           // Simulation state
POST /simulation/step  // Device movement
POST /decision         // Network selection  
GET  /map             // Map data with base stations
```

### **Data Flow**
```
User Action → JavaScript → FastAPI → Simulation Engine → Decision Logic → UI Update
    ↓            ↓           ↓            ↓               ↓              ↓
 Click Step → API Call → Run Simulation → Update State → Make Decision → Render Map
```

## 🎨 Customization

### **Colors & Styling**
```css
/* Network colors in map-visualization.js */
networkColors = {
    'Wi-Fi': '#2196F3',    // Blue
    '5G': '#9C27B0',       // Purple  
    'BLE': '#FF9800',      // Orange
    '4G': '#4CAF50'        // Green
}

/* Task badge colors in index.html */
.task-idle { color: #1976d2; }      // Blue
.task-burst { color: #f57c00; }     // Orange
.task-video { color: #c2185b; }     // Pink
```

### **Map Configuration**
```javascript
// Modify in map-visualization.js
mapSize: { width: 1000, height: 1000 }     // Simulation space
canvasSize: { width: 800, height: 600 }    // Display size
autoRunInterval: 2000                       // Auto-run timing (ms)
```

## 🐛 Troubleshooting

### **Common Issues**

**1. API Status: ❌ Offline**
```bash
# Solution: Start the API server
conda activate comsys-project
uvicorn app.main:app --reload --port 8000
```

**2. Web UI Not Loading**
```bash
# Check if web directory exists
ls web/
# Should show: index.html, map-visualization.js

# Alternative: Access via static files
http://localhost:8000/static/index.html
```

**3. CORS Errors**
```
✅ Already configured in app/main.py:
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

**4. JavaScript Errors**
```javascript
// Check browser console (F12)
// Common fixes:
- Refresh page
- Clear browser cache
- Check API server is running
```

### **Debug Mode**
```bash
# Enable detailed logging
uvicorn app.main:app --reload --log-level debug

# Check browser developer tools
F12 → Console tab → Check for errors
F12 → Network tab → Monitor API calls
```

## 🎉 Demo Scenarios

### **Scenario 1: Office Environment**
1. **Reset** simulation to (200, 200) - Near Wi-Fi station
2. **Observe** high Wi-Fi signal strength
3. **Run Steps** để see task changes
4. **Expected**: Wi-Fi selection for most tasks

### **Scenario 2: Mobile Coverage**
1. **Click** on map corners (far from base stations)
2. **Observe** limited network availability
3. **Make Decision** with poor coverage
4. **Expected**: High cost values, best available selection

### **Scenario 3: Algorithm Comparison**
1. **Enable Auto-run** mode
2. **Watch** decision changes với different tasks
3. **Observe** cost comparison panel
4. **Expected**: Different networks selected per task type

## 📈 Advanced Features

### **Future Enhancements**
- [ ] **Historical Tracking**: Device movement trail
- [ ] **Performance Charts**: Real-time metrics visualization  
- [ ] **3D Visualization**: Height-based signal strength
- [ ] **Multiple Devices**: Multi-device simulation
- [ ] **ML Model Integration**: AI-based decision comparison

### **Integration Points**
- **Postman Collection**: API testing synchronization
- **ML Training**: Data collection from UI interactions
- **Real Hardware**: Integration với actual IoT devices
- **Cloud Deployment**: Scalable multi-user environment

---

🎯 **Ready to explore IoT Network Selection!** Start với `python demo_web_ui.py` và enjoy interactive visualization! 🗺️