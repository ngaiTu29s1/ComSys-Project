# 📘 PHÂN TÍCH CHI TIẾT CODEBASE - IoT Network Selection System

> **Tài liệu này**: Giải thích toàn bộ context, kiến trúc, và luồng hoạt động của hệ thống lựa chọn mạng tiết kiệm năng lượng cho thiết bị IoT.
> 
> **Ngôn ngữ**: Tiếng Việt
> 
> **Cập nhật**: December 1, 2025

---

## 🎯 MỤC ĐÍCH DỰ ÁN

### Vấn đề cần giải quyết
Thiết bị IoT hiện đại thường nằm trong vùng phủ sóng của nhiều loại mạng (Wi-Fi, 5G, BLE...). Việc lựa chọn mạng nào để kết nối trở nên phức tạp khi cần **TỐI THIỂU HÓA NĂNG LƯỢNG TIÊU THỤ** trong khi vẫn đảm bảo **CHẤT LƯỢNG DỊCH VỤ (QoS)**.

### Giải pháp
Xây dựng một **HỆ THỐNG MÔ PHỎNG** kết hợp với **MÔ HÌNH TRÍ TUỆ NHÂN TẠO** để:
1. Mô phỏng thiết bị IoT di chuyển trong môi trường có nhiều base stations
2. Thu thập dữ liệu về QoS (bandwidth, latency) theo vị trí và tác vụ
3. Sử dụng thuật toán MCDM (Multi-Criteria Decision Making) để chọn mạng tối ưu
4. Huấn luyện mô hình AI (Random Forest) học từ quyết định của thuật toán cơ sở
5. Cung cấp API và Web UI để demo và visualization

### Phạm vi dự án
- **MÔ PHỎNG**, không phải hệ thống thực tế
- Tập trung vào **MỘT THIẾT BỊ DUY NHẤT**
- AI chỉ ra quyết định **TỨC THỜI (REACTIVE)**, không dự báo
- Bỏ qua các vấn đề phức tạp ở tầng thấp (handoff, session management...)

---

## 🏗️ KIẾN TRÚC TỔNG QUAN

### Tech Stack

#### Backend
- **Python 3.11**: Ngôn ngữ chính
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation và serialization

#### AI/ML
- **Scikit-learn**: Machine Learning (Random Forest Classifier)
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **SimPy**: Event-driven simulation framework

#### Frontend
- **HTML5 + CSS3**: UI structure và styling
- **Vanilla JavaScript**: Logic và interaction
- **Canvas API**: Map visualization

#### DevOps
- **Conda**: Environment management
- **Docker**: Containerization (future)
- **Git**: Version control

### Cấu trúc thư mục

```
📦 CommunicationSystem/
│
├── 📁 app/                          # Backend FastAPI application
│   ├── 📄 __init__.py              
│   ├── 📄 main.py                   # ⭐ API endpoints chính
│   │
│   ├── 📁 models/                   # Data models
│   │   ├── 📄 __init__.py
│   │   └── 📄 schemas.py            # ⭐ Pydantic models (TaskState, NetworkState, DeviceState...)
│   │
│   ├── 📁 core/                     # Core business logic
│   │   ├── 📄 __init__.py
│   │   └── 📄 decision_logic.py     # ⭐ Thuật toán MCDM (cost function, network selection)
│   │
│   └── 📁 services/                 # Services layer
│       ├── 📄 __init__.py
│       └── 📄 simulation.py         # ⭐ Simulation engine (QoS calculation, device movement)
│
├── 📁 web/                          # Frontend web UI
│   ├── 📄 index.html                # ⭐ Map visualization UI
│   ├── 📄 map-visualization.js      # ⭐ JavaScript visualization logic
│   └── 📄 README.md
│
├── 📁 docs/                         # Documentation
│   ├── 📄 CODE_GUIDE.md             # Code guide (English)
│   ├── 📄 CODEBASE_BREAKDOWN_VI.md  # ⭐ File này
│   ├── 📄 POSTMAN_GUIDE.md          # Postman testing guide
│   └── 📄 IoT-Network-Selection.postman_collection.json
│
├── 📁 tests/                        # Unit tests
│   ├── 📄 test_api.py
│   ├── 📄 test_decision_logic.py
│   ├── 📄 test_simulation.py
│   ├── 📄 test_schemas.py
│   └── 📄 smoke_env.py              # Environment check
│
├── 📁 scripts/                      # Utility scripts
│   └── 📄 clean-conda-temp.ps1      # Clean Conda temp folders
│
├── 📁 src/                          # Legacy/experimental code
│   └── 📄 api.py                    # Prototype API (not used)
│
├── 📄 demo_main_api.py              # Demo script cho main API
├── 📄 demo_simulation.py            # Demo script cho simulation
├── 📄 demo_system.py                # Demo script cho system
├── 📄 demo_web_ui.py                # Demo script cho web UI
│
├── 📄 environment.yml               # ⭐ Conda environment definition
├── 📄 README.md                     # Project overview
└── 📄 .gitignore                    # Git ignore rules

```

---

## 📦 CÁC COMPONENT CHÍNH

### 1. Data Models (`app/models/schemas.py`)

Định nghĩa các cấu trúc dữ liệu cốt lõi sử dụng **Pydantic** để đảm bảo type safety và validation.

#### `TaskState` (Enum)
**Mục đích**: Định nghĩa các trạng thái tác vụ của thiết bị IoT.

```python
class TaskState(str, Enum):
    IDLE_MONITORING = "IDLE_MONITORING"        # Giám sát nhàn rỗi
    DATA_BURST_ALERT = "DATA_BURST_ALERT"      # Cảnh báo với burst data
    VIDEO_STREAMING = "VIDEO_STREAMING"        # Streaming video
```

**Đặc điểm**:
- Mỗi trạng thái có yêu cầu năng lượng và QoS khác nhau
- `IDLE_MONITORING`: Ưu tiên tiết kiệm năng lượng (w_energy=0.8)
- `DATA_BURST_ALERT`: Ưu tiên QoS - độ trễ thấp (w_qos=0.7)
- `VIDEO_STREAMING`: Cân bằng giữa năng lượng và QoS

#### `NetworkConfig` (BaseModel)
**Mục đích**: Cấu hình tĩnh của một loại mạng.

```python
class NetworkConfig(BaseModel):
    name: str                    # Tên mạng (Wi-Fi, 5G, BLE)
    energy_tx: float            # Năng lượng truyền (mJ/KB)
    energy_idle: float          # Năng lượng chờ (mW)
    energy_wakeup: float        # Năng lượng khởi động (mJ)
```

**Ví dụ thực tế**:
- **Wi-Fi**: `energy_tx=0.5`, `energy_idle=10.0`, `energy_wakeup=2.0`
- **5G**: `energy_tx=1.2`, `energy_idle=15.0`, `energy_wakeup=5.0`
- **BLE**: `energy_tx=0.1`, `energy_idle=2.0`, `energy_wakeup=0.5`

#### `NetworkState` (BaseModel)
**Mục đích**: Trạng thái động của mạng tại thời điểm hiện tại.

```python
class NetworkState(BaseModel):
    name: str                   # Tên mạng
    bandwidth: float            # Băng thông khả dụng (Mbps)
    latency: int               # Độ trễ (ms)
    is_available: bool         # Trạng thái khả dụng
```

**Cách tính**: Được tính toán dựa trên khoảng cách từ thiết bị đến base station gần nhất (xem `SimulationEngine._calculate_qos_by_distance()`).

#### `DeviceState` (BaseModel)
**Mục đích**: Trạng thái hiện tại của thiết bị IoT.

```python
class DeviceState(BaseModel):
    position: Tuple[int, int]           # Tọa độ (x, y)
    current_task: TaskState             # Tác vụ hiện tại
    available_networks: List[NetworkState]  # Danh sách mạng khả dụng
```

**Vai trò**: Đây là object trung tâm được truyền qua các API endpoints và được sử dụng bởi decision logic.

---

### 2. Simulation Engine (`app/services/simulation.py`)

**Mục đích**: Mô phỏng môi trường IoT với base stations, device movement, và QoS dynamics.

#### Khởi tạo (`__init__`)

```python
def __init__(self, map_size: Tuple[int, int] = (1000, 1000)):
    self.map_size = map_size
    self.simulation_step = 0
    self._init_network_configs()       # Khởi tạo config của Wi-Fi, 5G, BLE
    self._init_base_stations()         # Đặt base stations tại các vị trí cố định
    self.device_state = DeviceState(...)  # Khởi tạo thiết bị
    self._update_available_networks()  # Tính mạng khả dụng cho vị trí ban đầu
```

**Map layout**:
- Kích thước: 1000x1000 pixels
- 12 base stations tổng cộng:
  - 4 Wi-Fi routers tại: (100,100), (300,250), (600,400), (800,750)
  - 4 5G towers tại: (200,200), (500,300), (700,600), (900,100)
  - 4 BLE beacons tại: (150,150), (350,350), (550,550), (750,750)

#### QoS Calculation (`_calculate_qos_by_distance`)

**Công thức**: QoS giảm tuyến tính theo khoảng cách từ base station.

```python
distance_ratio = distance / max_range  # 0.0 -> 1.0

# Bandwidth giảm từ 100% xuống 10%
bandwidth = max_bandwidth * (1.0 - 0.9 * distance_ratio)

# Latency tăng từ min lên 10x
latency = min_latency * (1.0 + 9.0 * distance_ratio)
```

**Thông số max range**:
- Wi-Fi: 100m (max 100 Mbps, min 5ms latency)
- 5G: 500m (max 200 Mbps, min 10ms latency)
- BLE: 50m (max 2 Mbps, min 20ms latency)

**Noise**: Thêm ±20% random noise để mô phỏng biến động thực tế.

#### Simulation Step (`run_simulation_step`)

**Luồng hoạt động**:
1. **Di chuyển ngẫu nhiên**: Device di chuyển 10-50 pixels theo hướng ngẫu nhiên
2. **Giữ trong map**: Clamp vị trí trong bounds (0, 0) đến (1000, 1000)
3. **Thay đổi tác vụ**: 20% cơ hội chuyển sang tác vụ khác
4. **Cập nhật networks**: Tìm base station gần nhất cho từng loại mạng và tính QoS
5. **Tăng step counter**: `simulation_step += 1`

**Output**: Trả về `DeviceState` mới với position, task, available_networks đã cập nhật.

---

### 3. Decision Logic (`app/core/decision_logic.py`)

**Mục đích**: Implement thuật toán MCDM để chọn mạng tối ưu.

#### Hàm chi phí (Cost Function)

**Công thức MCDM**:
```
Total_Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty
```

**Trọng số theo tác vụ** (`TASK_WEIGHTS`):
| Task | w_energy | w_qos | Giải thích |
|------|----------|-------|-----------|
| IDLE_MONITORING | 0.8 | 0.2 | Ưu tiên tiết kiệm năng lượng |
| DATA_BURST_ALERT | 0.3 | 0.7 | Ưu tiên QoS (độ trễ thấp) |
| VIDEO_STREAMING | 0.4 | 0.6 | Cân bằng giữa năng lượng và QoS |

#### Energy Cost Calculation (`calculate_energy_cost`)

**Công thức**:
```python
total_energy = base_energy + transmission_energy + wakeup_energy

# Chi tiết:
base_energy = network_config.energy_idle  # mW (cho 1 giây)
transmission_energy = estimated_data_kb * network_config.energy_tx  # mJ
wakeup_energy = network_config.energy_wakeup  # mJ
```

**Ước tính kích thước dữ liệu**:
- IDLE_MONITORING: 1 KB (sensor data)
- DATA_BURST_ALERT: 50 KB (alert data)
- VIDEO_STREAMING: 1000 KB (video chunk)

#### QoS Penalty (`calculate_qos_penalty`)

**Yêu cầu QoS tối thiểu** (`QOS_REQUIREMENTS`):
| Task | Min Bandwidth | Max Latency |
|------|---------------|-------------|
| IDLE_MONITORING | 0.1 Mbps | 1000 ms |
| DATA_BURST_ALERT | 5.0 Mbps | 100 ms |
| VIDEO_STREAMING | 10.0 Mbps | 200 ms |

**Logic phạt**:
```python
# Nếu mạng không khả dụng
if not network_state.is_available:
    return 1000.0  # Phạt nặng

# Phạt bandwidth thiếu
if bandwidth < min_bandwidth:
    penalty += (min_bandwidth - bandwidth) * 50

# Phạt latency vượt ngưỡng
if latency > max_latency:
    penalty += (latency - max_latency) * 2

# Phạt nghiêm trọng nếu vi phạm lớn
if penalty > 500:
    return 1000.0
```

#### Network Selection (`select_best_network`)

**Thuật toán**: Greedy selection - chọn mạng có `total_cost` thấp nhất.

```python
def select_best_network(available_networks, network_configs, task):
    best_network = None
    min_cost = float('inf')
    
    for network in available_networks:
        cost = calculate_cost(network, network_configs[network.name], task)
        if cost < min_cost:
            min_cost = cost
            best_network = network
    
    return best_network, min_cost
```

**Output**: Tuple `(NetworkState, float)` - mạng được chọn và chi phí tương ứng.

---

### 4. FastAPI Backend (`app/main.py`)

**Mục đích**: Cung cấp REST API cho simulation và decision making.

#### Khởi tạo

```python
app = FastAPI(
    title="IoT Network Selection System",
    version="1.0.0",
    description="API for IoT device network selection using MCDM algorithm"
)

# CORS middleware cho web UI
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Mount static files
app.mount("/static", StaticFiles(directory="web"), name="static")

# Khởi tạo simulation engine
simulation_engine = SimulationEngine()
```

#### API Endpoints

##### `GET /` - Root
**Mục đích**: Thông tin tổng quan về hệ thống.

**Response**:
```json
{
  "message": "IoT Network Selection System API",
  "version": "1.0.0",
  "endpoints": {
    "simulation": "/simulation/step - Run simulation step",
    "decision": "/decision - Make network selection decision",
    "status": "/status - Get system status",
    "web_ui": "/ui - Access web-based map visualization"
  }
}
```

##### `GET /status` - System Status
**Mục đích**: Lấy trạng thái hiện tại của simulation engine và network configs.

**Response**:
```json
{
  "system_status": "operational",
  "simulation_engine": {
    "current_step": 0,
    "device_position": [0, 0],
    "current_task": "IDLE_MONITORING",
    "available_networks": ["Wi-Fi", "5G"],
    "map_size": [1000, 1000],
    "total_base_stations": 12
  },
  "network_configs": {
    "Wi-Fi": {"energy_tx": 0.5, "energy_idle": 10.0, ...},
    ...
  }
}
```

##### `POST /simulation/step` - Run Simulation Step
**Mục đích**: Chạy một bước mô phỏng (di chuyển device, cập nhật QoS).

**Request**: No body required.

**Response**:
```json
{
  "step_number": 1,
  "device_state": {
    "position": [45, 32],
    "current_task": "IDLE_MONITORING",
    "available_networks": [
      {
        "name": "Wi-Fi",
        "bandwidth": 85.3,
        "latency": 8,
        "is_available": true
      },
      ...
    ]
  },
  "simulation_info": {
    "networks_count": 2,
    "networks_list": ["Wi-Fi", "5G"]
  }
}
```

**Logic**:
```python
def simulation_step():
    new_device_state = simulation_engine.run_simulation_step()
    # Format và return response
    return {
        "step_number": simulation_engine.simulation_step,
        "device_state": {...},
        "simulation_info": {...}
    }
```

##### `POST /decision` - Make Network Decision
**Mục đích**: Ra quyết định chọn mạng tối ưu dựa trên MCDM.

**Request Body**:
```json
{
  "position": [100, 200],
  "current_task": "DATA_BURST_ALERT",
  "available_networks": [
    {"name": "Wi-Fi", "bandwidth": 50.0, "latency": 10, "is_available": true},
    {"name": "5G", "bandwidth": 100.0, "latency": 20, "is_available": true}
  ]
}
```

**Response**:
```json
{
  "selected_network": "Wi-Fi",
  "cost": 25.3,
  "all_costs": {
    "Wi-Fi": 25.3,
    "5G": 38.7
  },
  "decision_info": {
    "task": "DATA_BURST_ALERT",
    "weights": {"w_energy": 0.3, "w_qos": 0.7},
    "network_count": 2
  }
}
```

**Logic**:
```python
def make_decision(device_state: DeviceState):
    best_network, min_cost = select_best_network(
        device_state.available_networks,
        simulation_engine.network_configs,
        device_state.current_task
    )
    
    # Tính cost cho tất cả mạng để so sánh
    all_costs = {
        net.name: calculate_cost(net, config, device_state.current_task)
        for net in device_state.available_networks
    }
    
    return {
        "selected_network": best_network.name,
        "cost": min_cost,
        "all_costs": all_costs,
        ...
    }
```

##### `GET /ui` - Web UI
**Mục đích**: Serve file HTML cho map visualization.

**Response**: `FileResponse("web/index.html")`

##### `GET /map` - Map Data
**Mục đích**: Lấy dữ liệu base stations và device state cho visualization.

**Response**:
```json
{
  "map_size": [1000, 1000],
  "base_stations": [
    {"id": "wifi_0", "type": "Wi-Fi", "position": [100, 100], "color": "#2196F3"},
    {"id": "5g_0", "type": "5G", "position": [200, 200], "color": "#9C27B0"},
    ...
  ],
  "device_state": {
    "position": [150, 180],
    "current_task": "IDLE_MONITORING",
    "available_networks": ["Wi-Fi", "5G"]
  },
  "simulation_step": 5
}
```

---

### 5. Web UI (`web/index.html` + `web/map-visualization.js`)

**Mục đích**: Cung cấp giao diện visualization cho simulation.

#### HTML Structure (`index.html`)

**Layout**: Grid layout với 2 cột
- **Cột trái**: Map canvas (800x600px)
- **Cột phải**: Control panel

**Components**:
1. **Map Canvas**: `<canvas id="mapCanvas">` - hiển thị base stations và device
2. **Device Info**: Hiển thị vị trí, task, và available networks
3. **Control Panel**:
   - Task selector dropdown
   - Simulation controls (Step, Decision, Reset, Auto-run)
   - API status indicator
   - Status bar

**Styling**: Gradient background, card-based UI với border-radius và shadows.

#### JavaScript Logic (`map-visualization.js`)

##### Class: `MapVisualization`

**Constructor**: Khởi tạo canvas, API config, và simulation state.

```javascript
constructor() {
    this.canvas = document.getElementById('mapCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.apiBaseUrl = 'http://localhost:8000';
    this.mapSize = { width: 1000, height: 1000 };
    this.canvasSize = { width: 800, height: 600 };
    this.scale = {
        x: canvasSize.width / mapSize.width,   // 0.8
        y: canvasSize.height / mapSize.height  // 0.6
    };
    this.devicePosition = { x: 0, y: 0 };
    this.currentTask = 'IDLE_MONITORING';
    this.availableNetworks = [];
    this.baseStations = [];
    this.isAutoRunning = false;
    ...
}
```

##### Method: `initializeBaseStations()`

**Mục đích**: Khởi tạo vị trí base stations (matching với `simulation.py`).

```javascript
initializeBaseStations() {
    this.baseStations = [
        // Wi-Fi stations
        { x: 200, y: 200, type: 'Wi-Fi' },
        { x: 800, y: 200, type: 'Wi-Fi' },
        ...
        // 5G stations
        { x: 500, y: 150, type: '5G' },
        ...
        // BLE stations
        { x: 350, y: 350, type: 'BLE' },
        ...
    ];
}
```

##### Method: `runSimulationStep()`

**Mục đích**: Gọi API `/simulation/step` và cập nhật UI.

```javascript
async runSimulationStep() {
    const response = await fetch(`${this.apiBaseUrl}/simulation/step`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    });
    
    const data = await response.json();
    
    // Cập nhật state
    this.devicePosition = {
        x: data.device_state.position[0],
        y: data.device_state.position[1]
    };
    this.currentTask = data.device_state.current_task;
    this.availableNetworks = data.device_state.available_networks;
    this.simulationStep = data.step;
    
    // Redraw canvas
    this.updateUI();
    this.draw();
}
```

##### Method: `makeDecision()`

**Mục đích**: Gọi API `/decision` và hiển thị kết quả.

```javascript
async makeDecision() {
    const requestBody = {
        position: [this.devicePosition.x, this.devicePosition.y],
        current_task: this.currentTask,
        available_networks: this.availableNetworks
    };
    
    const response = await fetch(`${this.apiBaseUrl}/decision`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(requestBody)
    });
    
    const data = await response.json();
    
    // Hiển thị kết quả
    this.decisionResult = {
        selectedNetwork: data.selected_network,
        cost: data.cost
    };
    
    this.updateUI();
    this.updateStatusBar(`✅ Selected: ${data.selected_network} (Cost: ${data.cost.toFixed(2)})`);
}
```

##### Method: `draw()`

**Mục đích**: Render map lên canvas.

**Các bước vẽ**:
1. Clear canvas
2. Vẽ grid lines
3. Vẽ coverage circles cho từng base station (bán kính = max_range * scale)
4. Vẽ base station icons (hình vuông với màu theo loại mạng)
5. Vẽ device icon (hình tròn, màu thay đổi theo decision result)
6. Vẽ connection lines từ device đến available base stations

```javascript
draw() {
    // 1. Clear
    this.ctx.clearRect(0, 0, this.canvasSize.width, this.canvasSize.height);
    
    // 2. Grid
    this.drawGrid();
    
    // 3. Coverage circles
    this.baseStations.forEach(station => {
        this.drawCoverageCircle(station);
    });
    
    // 4. Base stations
    this.baseStations.forEach(station => {
        this.drawBaseStation(station);
    });
    
    // 5. Device
    this.drawDevice();
    
    // 6. Connection lines
    this.drawConnections();
}
```

##### Method: `handleCanvasClick(e)`

**Mục đích**: Cho phép user click vào canvas để đặt device position.

```javascript
handleCanvasClick(e) {
    const rect = this.canvas.getBoundingClientRect();
    const canvasX = e.clientX - rect.left;
    const canvasY = e.clientY - rect.top;
    
    // Chuyển đổi từ canvas coords sang map coords
    const mapX = Math.round(canvasX / this.scale.x);
    const mapY = Math.round(canvasY / this.scale.y);
    
    // Clamp trong bounds
    this.devicePosition.x = Math.max(0, Math.min(this.mapSize.width, mapX));
    this.devicePosition.y = Math.max(0, Math.min(this.mapSize.height, mapY));
    
    // Update networks cho vị trí mới
    this.updateNetworksForPosition();
    this.draw();
}
```

##### Method: `toggleAutoRun()`

**Mục đích**: Bật/tắt chế độ auto-run (chạy simulation step tự động mỗi 2 giây).

```javascript
toggleAutoRun() {
    this.isAutoRunning = !this.isAutoRunning;
    
    if (this.isAutoRunning) {
        this.autoRunInterval = setInterval(() => {
            this.runSimulationStep();
        }, 2000);
    } else {
        clearInterval(this.autoRunInterval);
    }
    
    this.updateUI();
}
```

---

## 🔄 LUỒNG HOẠT ĐỘNG CHÍNH

### Workflow 1: Manual Simulation

```
User clicks "Step" button
    ↓
[Web UI] map-visualization.js: runSimulationStep()
    ↓
[API] POST /simulation/step
    ↓
[Backend] simulation_engine.run_simulation_step()
    ↓
    1. Move device randomly (10-50 pixels)
    2. Clamp position in bounds
    3. Random task change (20% chance)
    4. Update available networks:
       - Find closest base station for each network type
       - Calculate QoS based on distance
       - Filter by max_range
    5. simulation_step += 1
    ↓
[Backend] Return DeviceState
    ↓
[API] Format response JSON
    ↓
[Web UI] Update devicePosition, currentTask, availableNetworks
    ↓
[Web UI] Redraw canvas
    ↓
User sees updated device position and networks
```

### Workflow 2: Decision Making

```
User clicks "Decision" button
    ↓
[Web UI] map-visualization.js: makeDecision()
    ↓
[API] POST /decision
    Body: { position, current_task, available_networks }
    ↓
[Backend] app/main.py: make_decision()
    ↓
[Core Logic] decision_logic.select_best_network()
    ↓
    For each available network:
        1. Get network config (energy_tx, energy_idle, energy_wakeup)
        2. Calculate energy_cost = calculate_energy_cost(network, task)
           - Estimate data size based on task
           - energy = base + transmission + wakeup
        3. Calculate qos_penalty = calculate_qos_penalty(network, task)
           - Check if bandwidth >= min_bandwidth
           - Check if latency <= max_latency
           - Apply penalty factors
        4. Calculate total_cost = w_energy * energy_cost + w_qos * qos_penalty
    ↓
    Select network with minimum total_cost
    ↓
[Backend] Return { selected_network, cost, all_costs, decision_info }
    ↓
[Web UI] Display decision result
    - Highlight selected network in UI
    - Show cost in status bar
    - Color device icon green
    ↓
User sees which network was selected and why
```

### Workflow 3: Auto-Run Mode

```
User clicks "Auto-Run" toggle
    ↓
[Web UI] toggleAutoRun()
    ↓
    isAutoRunning = true
    Start interval timer (2000ms)
    ↓
Every 2 seconds:
    ↓
    runSimulationStep()
    ↓
    (Same as Workflow 1)
    ↓
    Device moves continuously
    Networks update dynamically
    ↓
User observes simulation running automatically
    ↓
User clicks "Auto-Run" again to stop
```

### Workflow 4: Manual Device Placement

```
User clicks on canvas at position (canvasX, canvasY)
    ↓
[Web UI] handleCanvasClick(event)
    ↓
    1. Get click coordinates relative to canvas
    2. Convert canvas coords to map coords:
       mapX = canvasX / scale.x
       mapY = canvasY / scale.y
    3. Clamp position in bounds (0-1000, 0-1000)
    4. Update devicePosition
    ↓
[Web UI] updateNetworksForPosition()
    ↓
    For each base station:
        - Calculate distance to device
        - Calculate QoS by distance
        - Add to availableNetworks if in range
    ↓
[Web UI] Redraw canvas
    ↓
User sees device at clicked position with updated networks
```

---

## 🧪 TESTING & DEMO

### Unit Tests (`tests/`)

#### `test_decision_logic.py`
**Coverage**:
- `test_calculate_energy_cost()`: Kiểm tra tính toán năng lượng cho các task khác nhau
- `test_calculate_qos_penalty()`: Kiểm tra logic phạt QoS
- `test_calculate_cost()`: Kiểm tra tổng hợp cost function
- `test_select_best_network()`: Kiểm tra logic lựa chọn mạng

#### `test_simulation.py`
**Coverage**:
- `test_init()`: Kiểm tra khởi tạo simulation engine
- `test_calculate_distance()`: Kiểm tra tính khoảng cách Euclidean
- `test_calculate_qos_by_distance()`: Kiểm tra degradation của QoS theo khoảng cách
- `test_run_simulation_step()`: Kiểm tra logic một bước mô phỏng

#### `test_api.py`
**Coverage**:
- `test_root()`: Kiểm tra endpoint `/`
- `test_status()`: Kiểm tra endpoint `/status`
- `test_simulation_step()`: Kiểm tra endpoint `/simulation/step`
- `test_decision()`: Kiểm tra endpoint `/decision`

### Demo Scripts

#### `demo_main_api.py`
**Mục đích**: Demo các API endpoints chính.

**Sections**:
1. **System Overview**: Gọi `/` và `/status`
2. **Simulation Workflow**: Chạy 8 simulation steps
3. **Decision Making**: Test decision với các scenarios khác nhau
4. **Network Comparison**: So sánh costs của các mạng

**Chạy**: `python demo_main_api.py`

#### `demo_simulation.py`
**Mục đích**: Demo simulation engine trực tiếp (không qua API).

**Scenarios**:
1. Device di chuyển gần Wi-Fi station
2. Device di chuyển gần 5G tower
3. Device ở giữa map (có nhiều networks available)

**Chạy**: `python demo_simulation.py`

#### `demo_system.py`
**Mục đích**: Demo end-to-end workflow.

**Chạy**: `python demo_system.py`

#### `demo_web_ui.py`
**Mục đích**: Mở trình duyệt và navigate đến web UI.

**Chạy**: `python demo_web_ui.py`

---

## 🔧 CONFIGURATION & SETUP

### Environment Setup

#### Conda Environment (`environment.yml`)

```yaml
name: comsys-project
channels:
  - conda-forge
dependencies:
  - python=3.11
  - numpy
  - pandas
  - scipy
  - scikit-learn
  - simpy               # Event-driven simulation
  - matplotlib
  - fastapi
  - uvicorn
  - pydantic
  - rich
  - typer
  - jupyterlab
  - ipykernel
  - pip
  - pip:
      - scikit-optimize
```

**Cài đặt**:
```bash
conda env create -f environment.yml
conda activate comsys-project
```

### VS Code Settings (`.vscode/settings.json`)

```json
{
  "python.defaultInterpreterPath": "C:\\miniconda3\\envs\\comsys-project\\python.exe",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=88"],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "files.exclude": {
    "**/conda-*": true,
    "Tran/AppData/Local/Temp": true
  }
}
```

**Giải thích**:
- Python interpreter: Trỏ đến Conda environment
- Formatter: Black (PEP 8 compliant)
- Linter: Flake8 với max line length = 88
- Testing: Pytest
- Files exclude: Ẩn các thư mục temp của Conda

### Git Ignore (`.gitignore`)

```gitignore
# Conda temp folders
Tran/AppData/Local/Temp/
Tu/
**/conda-*/

# Python caches
__pycache__/
*.pyc
.pytest_cache/

# VS Code
.vscode/

# Node/Frontend
node_modules/
dist/
```

---

## 🚀 CHẠY HỆ THỐNG

### Bước 1: Activate Conda Environment

```bash
conda activate comsys-project
```

### Bước 2: Start FastAPI Server

```bash
# Chạy với auto-reload (dev mode)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc sử dụng script
python -m uvicorn app.main:app --reload
```

**Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
🚀 IoT Network Selection API initialized
📡 Simulation engine ready with 3 network types
```

### Bước 3: Truy cập Web UI

**URL**: http://localhost:8000/ui

**Hoặc**:
- Swagger UI (API docs): http://localhost:8000/docs
- ReDoc (Alternative API docs): http://localhost:8000/redoc

### Bước 4: Test API với Postman

Import collection: `docs/IoT-Network-Selection.postman_collection.json`

**Test sequence**:
1. Health check: `GET /health`
2. System status: `GET /status`
3. Simulation step: `POST /simulation/step`
4. Decision making: `POST /decision`
5. Reset simulation: `POST /simulation/reset?x=100&y=100`

### Bước 5: Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_decision_logic.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v tests/
```

### Bước 6: Run Demo Scripts

```bash
# Demo main API
python demo_main_api.py

# Demo simulation engine
python demo_simulation.py

# Demo system
python demo_system.py

# Demo web UI (opens browser)
python demo_web_ui.py
```

---

## 📊 DỮ LIỆU VÀ THUẬT TOÁN

### MCDM Algorithm Details

#### Cost Function Components

1. **Energy Cost**:
   - Idle energy (mW): Năng lượng tiêu thụ khi mạng idle
   - Transmission energy (mJ/KB): Năng lượng để truyền dữ liệu
   - Wakeup energy (mJ): Năng lượng để khởi động mạng từ sleep

2. **QoS Penalty**:
   - Bandwidth deficit penalty: `(min_required - actual) * 50`
   - Latency excess penalty: `(actual - max_allowed) * 2`
   - Availability penalty: `1000.0` nếu mạng không khả dụng

#### Weight Tuning Rationale

**IDLE_MONITORING** (w_energy=0.8, w_qos=0.2):
- Thiết bị ở chế độ idle, không có tác vụ quan trọng
- Ưu tiên tiết kiệm năng lượng tối đa
- QoS không quan trọng (chỉ cần truyền được sensor data nhỏ)
- → Chọn BLE hoặc Wi-Fi (energy-efficient)

**DATA_BURST_ALERT** (w_energy=0.3, w_qos=0.7):
- Thiết bị cần gửi cảnh báo khẩn cấp
- Ưu tiên độ trễ thấp và bandwidth cao
- Năng lượng là thứ yếu (alert quan trọng hơn)
- → Chọn 5G (low latency, high bandwidth)

**VIDEO_STREAMING** (w_energy=0.4, w_qos=0.6):
- Thiết bị streaming video
- Cân bằng giữa năng lượng và QoS
- Cần bandwidth cao nhưng vẫn quan tâm đến battery life
- → Chọn Wi-Fi hoặc 5G tùy vào vị trí

### QoS Degradation Model

**Công thức tuyến tính**:
```
distance_ratio = distance / max_range

bandwidth(d) = max_bandwidth * (1 - 0.9 * distance_ratio)
latency(d) = min_latency * (1 + 9 * distance_ratio)
```

**Ví dụ với Wi-Fi** (max_range=100m, max_bandwidth=100Mbps, min_latency=5ms):
| Distance | Bandwidth | Latency |
|----------|-----------|---------|
| 0m | 100 Mbps | 5 ms |
| 25m | 77.5 Mbps | 16.25 ms |
| 50m | 55 Mbps | 27.5 ms |
| 75m | 32.5 Mbps | 38.75 ms |
| 100m | 10 Mbps | 50 ms |

**Noise**: ±20% random để mô phỏng biến động thực tế (interference, congestion...).

### Network Characteristics

| Network | Max BW | Min Latency | Max Range | Energy TX | Energy Idle | Energy Wakeup |
|---------|--------|-------------|-----------|-----------|-------------|---------------|
| Wi-Fi | 100 Mbps | 5 ms | 100m | 0.5 mJ/KB | 10 mW | 2 mJ |
| 5G | 200 Mbps | 10 ms | 500m | 1.2 mJ/KB | 15 mW | 5 mJ |
| BLE | 2 Mbps | 20 ms | 50m | 0.1 mJ/KB | 2 mW | 0.5 mJ |

**Insight**:
- BLE: Năng lượng thấp nhất nhưng bandwidth hạn chế, phạm vi nhỏ
- Wi-Fi: Cân bằng tốt, phù hợp cho indoor
- 5G: Bandwidth cao, phạm vi rộng nhưng tốn năng lượng

---

## 🔮 HƯỚNG PHÁT TRIỂN TIẾP THEO

### Phase 1: Data Collection & ML Model (HIỆN TẠI)
- [x] Simulation engine với QoS dynamics
- [x] MCDM algorithm (cost function)
- [x] REST API với FastAPI
- [x] Web UI với map visualization
- [ ] **TODO**: Thu thập dataset (1000+ samples)
- [ ] **TODO**: Train Random Forest Classifier
- [ ] **TODO**: Evaluate model accuracy vs baseline algorithm

### Phase 2: Advanced Features
- [ ] Handoff simulation (chuyển mạng khi di chuyển)
- [ ] Battery level tracking
- [ ] Multiple devices simulation
- [ ] Realistic mobility patterns (random walk → waypoint model)
- [ ] Network congestion simulation

### Phase 3: AI/ML Enhancements
- [ ] Feature engineering (signal strength, velocity, battery...)
- [ ] Hyperparameter tuning (GridSearchCV)
- [ ] Model comparison (Random Forest vs Decision Tree vs SVM)
- [ ] Online learning (update model với data mới)

### Phase 4: Production Readiness
- [ ] Docker containerization
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Authentication & authorization
- [ ] Logging & monitoring (Prometheus + Grafana)
- [ ] Load testing (Locust)
- [ ] API rate limiting

### Phase 5: Research Extensions
- [ ] Reinforcement Learning (Q-learning, DQN)
- [ ] Multi-objective optimization (Pareto frontier)
- [ ] Context-aware prediction (time, location, user behavior)
- [ ] Federated learning (privacy-preserving)

---

## 📚 TÀI LIỆU THAM KHẢO

### Papers & Publications
1. **MCDM for Network Selection**:
   - "Multi-Criteria Decision Making for Heterogeneous Wireless Networks" (IEEE)
   - "Energy-Efficient Network Selection in IoT" (Journal of Network and Computer Applications)

2. **AI/ML in Network Selection**:
   - "Machine Learning for 5G Network Selection" (IEEE Communications Magazine)
   - "Random Forest for QoS Prediction in Wireless Networks" (Computer Networks)

### Libraries & Frameworks
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **SimPy**: https://simpy.readthedocs.io/
- **Scikit-learn**: https://scikit-learn.org/

### Tools
- **Postman**: API testing - https://www.postman.com/
- **Swagger UI**: API documentation - https://swagger.io/tools/swagger-ui/
- **Conda**: Environment management - https://docs.conda.io/

---

## 🤝 HƯỚNG DẪN ĐÓNG GÓP

### Code Style
- **Python**: PEP 8 (enforced by Black formatter)
- **JavaScript**: Standard JS (with Prettier)
- **Comments**: Tiếng Việt cho logic phức tạp, English cho boilerplate

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat(simulation): add random waypoint mobility model
fix(decision): correct QoS penalty calculation for BLE
docs(readme): update installation instructions
```

### Pull Request Checklist
- [ ] Code đã được format (Black, Prettier)
- [ ] Unit tests đã pass (`pytest tests/`)
- [ ] Docstrings đã được cập nhật
- [ ] CHANGELOG.md đã được cập nhật (nếu là breaking change)
- [ ] Demo script đã được test

### Testing Guidelines
- **Unit tests**: Coverage >= 80%
- **Integration tests**: Test API endpoints end-to-end
- **Smoke tests**: Test critical paths trước khi release

---

## ❓ FAQ

### Q1: Tại sao sử dụng MCDM thay vì machine learning ngay từ đầu?
**A**: MCDM (Multi-Criteria Decision Making) cung cấp một baseline algorithm có thể giải thích được (explainable AI). Chúng ta sử dụng MCDM để:
1. Gán nhãn (label) cho dataset
2. So sánh performance của ML model với baseline
3. Đảm bảo ML model học được logic hợp lý

### Q2: Tại sao QoS degradation là tuyến tính?
**A**: Trong thực tế, QoS degradation phức tạp hơn (log-normal fading, shadowing...). Tuy nhiên, với mục đích demo và education, mô hình tuyến tính đủ để minh họa concept. Phase 2 sẽ integrate mô hình path loss phức tạp hơn (Free-space, Two-ray ground reflection...).

### Q3: Làm sao để thêm một loại mạng mới (ví dụ: LoRaWAN)?
**A**: 
1. Thêm config vào `SimulationEngine._init_network_configs()`:
   ```python
   "LoRaWAN": NetworkConfig(name="LoRaWAN", energy_tx=0.05, energy_idle=0.5, energy_wakeup=0.1)
   ```
2. Thêm base stations vào `_init_base_stations()`:
   ```python
   "LoRaWAN": [(300, 300), (700, 700)]
   ```
3. Thêm max specs vào `_calculate_qos_by_distance()`:
   ```python
   "LoRaWAN": {"bandwidth": 0.05, "latency": 500, "max_range": 10000}
   ```
4. Thêm color vào `map-visualization.js`:
   ```javascript
   this.networkColors = {..., 'LoRaWAN': '#00BCD4'};
   ```

### Q4: Tại sao không dùng database?
**A**: Phase hiện tại tập trung vào prototype và demo. Database sẽ được integrate trong Phase 4 (Production Readiness) để:
- Lưu trữ historical simulation data
- Training data cho ML model
- User profiles và settings

### Q5: Làm sao để chạy trên production?
**A**: 
1. Đổi `allow_origins=["*"]` thành domain cụ thể
2. Sử dụng HTTPS (nginx + certbot)
3. Deploy với Gunicorn + Nginx reverse proxy
4. Containerize với Docker
5. Orchestrate với Kubernetes (nếu cần scale)

---

## 📞 LIÊN HỆ & HỖ TRỢ

### Repository
- **GitHub**: [ngaiTu29s1/ComSys-Project](https://github.com/ngaiTu29s1/ComSys-Project)
- **Branch**: `dev` (development), `main` (stable)

### Issues & Bugs
- Sử dụng GitHub Issues với labels: `bug`, `enhancement`, `documentation`, `question`

### Documentation
- **Code Guide**: `docs/CODE_GUIDE.md` (English)
- **Codebase Breakdown**: `docs/CODEBASE_BREAKDOWN_VI.md` (Tiếng Việt - file này)
- **Postman Guide**: `docs/POSTMAN_GUIDE.md`

---

## 📄 CHANGELOG

### [Unreleased]
- Thêm Random Forest ML model
- Dataset collection workflow
- Docker containerization

### [1.0.0] - 2025-12-01
- Initial release với simulation engine
- MCDM algorithm implementation
- FastAPI REST API
- Web UI với map visualization
- Unit tests cho core components
- Demo scripts và documentation

---

## 📝 LICENSE

MIT License - Xem file `LICENSE` để biết chi tiết.

---

**🎓 Lưu ý học thuật**: Đây là dự án nghiên cứu mô phỏng cho mục đích giáo dục. Các thông số và thuật toán được đơn giản hóa để dễ hiểu và demo. Để deploy trong môi trường thực tế, cần nghiên cứu thêm về:
- 3GPP standards (5G NR, LTE)
- IEEE 802.11 standards (Wi-Fi)
- Bluetooth SIG specifications (BLE)
- Path loss models (Okumura-Hata, COST-231...)
- Mobility models (Random waypoint, Gauss-Markov...)

---

**Tài liệu này được tạo tự động từ codebase vào ngày December 1, 2025.**
