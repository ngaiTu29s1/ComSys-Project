# 📘 Complete Code Guide - IoT Network Selection System

> **Dành cho:** Developers, Researchers, Contributors
> 
> **Mục đích:** Giải thích chi tiết kiến trúc, công thức, API, và ML pipeline
> 
> **Tech Stack:** Python 3.11 | FastAPI | Random Forest (99.9% accuracy) | Physics-based QoS
> 
> **Cập nhật:** December 17, 2025 (Power-based Energy + Hotspot Positioning + Energy Tie-breaker)
> 
> **Liên quan:** [`congthuc.md`](congthuc.md) cho chi tiết toán học

---

## 🚀 MAJOR UPDATES (December 17, 2025)

### ⚡ Energy Formula Refinement: Power-Based Time Calculation

**Before (Per-KB model):**
```
E_total = (energy_tx × DataSize_KB) + E_wakeup
```

**After (Power × Time model):**
```
E_total = (power_tx + power_idle) × (DataSize_MB / Bandwidth_Mbps) + E_wakeup
         = Power_mW × TX_Time_s + E_wakeup (mJ)
```

**Key Changes:**
- Renamed: `energy_tx` (mJ/KB) → `power_tx` (mW)
- Renamed: `energy_idle` (mJ/KB) → `power_idle` (mW)
- Formula: Explicit **time-based calculation** reflects real physics
- Unit clarity: `mW == mJ/s` (power is energy per second)

**Network Parameters (in constants.py):**

| Network | power_tx (mW) | power_idle (mW) | energy_wakeup (mJ) |
|---------|--------------|-----------------|-------------------|
| Wi-Fi   | 100.0        | 10.0            | 2.0               |
| 5G      | 300.0        | 15.0            | 5.0               |
| BLE     | 10.0         | 2.0             | 0.5               |

**Example Calculation (VIDEO_STREAMING: 15 MB @ Wi-Fi):**
```
1. throughput = 85.3 Mbps (from QoS)
2. time_tx = 15 MB / 85.3 Mbps = 0.176 s
3. power_total = 100 + 10 = 110 mW
4. energy_tx = 110 mW × 0.176 s = 19.4 mJ
5. total_energy = 19.4 + 2.0 = 21.4 mJ ✅
```

**Impact:** Accurate energy modeling, reflects physical device power profiles

---

### 📍 Realistic Multi-Homed Device Positioning

**New hotspot-based generation in `simulation.py`:**
```python
def _generate_hotspot_position(self):
    """70% near Wi-Fi, 30% random anywhere"""
```

**Logic:**
- **70% of steps:** Device stays near Wi-Fi station (5-40m radius)
  - Creates **multi-homed zones** where both Wi-Fi + 5G available
  - Enables dilemma scenarios: low-power Wi-Fi vs high-power 5G
  
- **30% of steps:** Device moves randomly across map
  - 5G-only zones where Wi-Fi unavailable
  - Tests algorithm's ability to handle network constraints

**Impact:** Charts now show **meaningful energy delta** (AI < Max-RSSI)
- **Max-RSSI:** Always chooses 5G in hotspots (higher power waste)
- **Proposed (MCDM/AI):** Chooses Wi-Fi in hotspots (energy saved)
- **Random:** Scattered between the two

---

### ⚖️ Decision Logic: Energy Tie-Breaker for MCDM

**Updated `select_best_network()` in decision_logic.py:**

```python
epsilon = 1e-9
if cost < min_cost or (abs(cost - min_cost) < epsilon and energy < min_energy):
    min_cost = cost
    min_energy = energy
    best_network = network
```

**Logic:**
1. **Primary:** Choose network with minimum total cost
2. **Tie-breaker:** When costs nearly equal (within ε), prefer lower energy
3. **Floating-point safety:** `abs(cost - min_cost) < epsilon` instead of `==`

**When does tie-breaking occur?**
- Multiple networks meet QoS requirement equally well
- Both have similar total cost (within floating-point tolerance)
- → Prefer the one consuming less energy (more sustainable)

**Impact:** More consistent decisions + stable policy charts

---

### 🎯 QoS Requirements Tightening

**Updated minimums in constants.py (QOS_REQUIREMENTS):**

| Task | min_bandwidth | max_latency | reasoning |
|------|---------------|------------|-----------|
| IDLE_MONITORING | 0.1 Mbps | 1000 ms | Sensor data is small |
| DATA_BURST_ALERT | 5.0 Mbps | 100 ms | Alert needs low latency |
| VIDEO_STREAMING | **36.0 Mbps** ⬆️ | 200 ms | Eliminates weak networks |

**Note:** VIDEO_STREAMING raised from generic to **36 Mbps**
- Prevents fallback to poor networks
- Forces WiFi/5G selection (BLE max ≤ 2 Mbps)
- Realistic video quality threshold

---

### ✅ ML & Training Pipeline Updates

**Training model with CLI:**
```bash
python -m app.ml.train_model --data data/raw/training_data.csv \
                             --model models/rf_network_selector.pkl
```

**Auto-save features:**
- Generates `confusion_matrix.png` → Model validation
- Generates `feature_importance.png` → Insight into decision factors

**Policy comparison charts:**
```bash
python scripts/generate_policy_charts.py
```

**Outputs:**
- `policy_energy.png` → Energy comparison
- `policy_qos_penalty.png` → QoS compliance
- `policy_total_cost.png` → Overall efficiency

**Expected result:** AI algorithm ≈ or better than Max-RSSI in energy

---

### 🏗️ Architecture Refactor: Constants & Formulas Separation

**New Structure:**
```
app/core/
├── constants.py       # ⭐ ALL parameters (energy, QoS, physics, ML)
├── formulas.py        # ⭐ Reusable math functions (pure functions)
└── decision_logic.py  # MCDM algorithm (uses constants + formulas)
```

**Key Principles:**
1. **Single Source of Truth:** All constants in `constants.py`
2. **Pure Functions:** All formulas in `formulas.py` (no side effects)
3. **Clear Separation:** Config ≠ Formulas ≠ Logic
4. **Easy Extension:** Add new network type → update `constants.py` only

**Benefits:**
- No hardcoded values scattered in code
- Easy to modify parameters without touching logic
- Reusable formulas across modules
- Testable pure functions

---

### 📊 ML Pipeline Improvements

**Training Data:**
- **36,000 samples** (3× increase from 12k)
- **Grid-based sampling** (50m intervals) → better coverage
- **Balanced task distribution** (33% each task) → no bias
- **Comprehensive metrics** (18 features including RSSI, SNR, PLR)

**Model Performance:**
- **Test accuracy:** 99.89% (CV: 99.90% ±0.08%)
- **Unseen data:** 100% (verified no overfitting)
- **Training time:** ~30 seconds (100 trees, depth 15)
- **Inference:** <50ms per prediction

**Validation:**
- 5-fold cross-validation
- Unseen data test (1000 fresh samples)
- MCDM baseline comparison
- Feature importance analysis

---

## 🎯 BẮT ĐẦU TỪ ĐÂU?

### Lộ Trình Đọc Code Theo Thứ Tự

**For Beginners (Follow this order):**
1. [`app/core/constants.py`](#1-appcoreconstantspy) - Understand all system parameters
2. [`app/core/formulas.py`](#2-appcoreformulaspy) - Understand physics formulas
3. [`app/models/schemas.py`](#3-appmodelsschemaspy) - Understand data structures
4. [`app/services/network_physics.py`](#4-appservicesnetwork_physicspy) - Understand QoS coordinator
5. [`app/services/simulation.py`](#5-appservicessimulationpy) - Understand simulation engine
6. [`app/core/decision_logic.py`](#6-appcoredesicion_logicpy) - Understand MCDM algorithm
7. [`app/ml/`](#7-appml-machine-learning) - Understand ML pipeline
8. [`app/main.py`](#8-appmainpy-api-server) - Understand API endpoints

**For Specific Tasks:**
- **Modify energy params?** → Edit `constants.py::NetworkEnergyConfig`
- **Modify QoS requirements?** → Edit `constants.py::QOS_REQUIREMENTS`
- **Add new network type?** → Add to `constants.py` + update `decision_logic.py`
- **Understand QoS calculation?** → Read `formulas.py` + `network_physics.py`
- **Train new model?** → Run `scripts/collect_training_data.py` → `scripts/train_model.py`
- **Test API?** → Read `main.py` + use Postman collection

---

## 📂 CẤU TRÚC DỰ ÁN

```
📦 CommunicationSystem/
│
├── 📁 app/                          # Backend Python
│   ├── 📄 __init__.py              # Package initialization
│   ├── 📄 main.py                  # ⭐ API Server chính (FastAPI)
│   │
│   ├── 📁 models/                   # Định nghĩa cấu trúc dữ liệu
│   │   ├── 📄 __init__.py
│   │   └── 📄 schemas.py           # ⭐ Pydantic models (DeviceState, NetworkState...)
│   │
│   ├── 📁 core/                     # Logic nghiệp vụ cốt lõi
│   │   ├── 📄 __init__.py
│   │   ├── 📄 constants.py         # ⭐ Tất cả tham số (energy, QoS, physics, ML)
│   │   ├── 📄 formulas.py          # ⭐ Công thức vật lý/QoS (pure functions)
│   │   └── 📄 decision_logic.py    # ⭐ Thuật toán MCDM (dùng constants + formulas)
│   │
│   ├── 📁 ml/                       # ⭐ Machine Learning module
│   │   ├── 📄 __init__.py
│   │   ├── 📄 data_collector.py    # ⭐ Thu thập training data
│   │   ├── 📄 feature_engineering.py # Feature processing
│   │   ├── 📄 train_model.py       # ⭐ Model training logic
│   │   └── 📄 predictor.py         # ⭐ ML inference
│   │
│   └── 📁 services/                 # Các service hỗ trợ
│       ├── 📄 __init__.py
│       ├── 📄 network_physics.py   # ⭐ Mô hình vật lý sóng vô tuyến
│       └── 📄 simulation.py        # ⭐ Engine mô phỏng IoT device
│
├── 📁 web/                          # Frontend (HTML/JavaScript)
│   ├── 📄 index.html               # ⭐ Giao diện map visualization
│   ├── 📄 map-visualization.js     # ⭐ Logic JavaScript cho UI
│   └── 📄 README.md
│
├── 📁 docs/                         # Tài liệu
│   ├── 📄 CODE_GUIDE.md            # ⭐ File này
│   ├── 📄 CODEBASE_BREAKDOWN_VI.md # Phân tích codebase tiếng Việt
│   ├── 📄 congthuc.md              # Công thức toán học
│   └── 📄 POSTMAN_GUIDE.md         # Hướng dẫn test API
│
├── 📁 tests/                        # Unit tests
│   ├── 📄 test_decision_logic.py   # Test thuật toán MCDM
│   ├── 📄 test_simulation.py       # Test engine mô phỏng
│   ├── 📄 test_api.py              # Test API endpoints
│   ├── 📄 test_ml_inference.py     # ⭐ Test ML predictor
│   └── 📄 smoke_env.py             # Kiểm tra môi trường
│
├── 📁 scripts/                      # ⭐ Training scripts
│   ├── 📄 collect_training_data.py # ⭐ Thu thập dataset
│   ├── 📄 train_model.py           # ⭐ Train Random Forest
│   └── 📄 clean-conda-temp.ps1     # Utility: dọn Conda temp
│
├── 📁 data/                         # ⭐ Datasets (gitignored)
│   ├── 📁 raw/                     # Raw CSV từ simulation
│   └── 📁 processed/               # Cleaned data
│
├── 📁 models/                       # ⭐ Trained models (gitignored)
│   └── 📄 rf_network_selector.pkl  # Random Forest model
│
├── 📁 notebooks/                    # Jupyter notebooks (optional)
│
├── 📄 demo_*.py                     # Demo scripts
├── 📄 environment.yml               # Conda environment setup
├── 📄 README.md                     # Tổng quan dự án
└── 📄 .gitignore                    # Git ignore rules
```

---

## 📘 CHI TIẾT TỪNG FILE

### 1. `app/models/schemas.py`

**Mục đích:** Định nghĩa cấu trúc dữ liệu cho toàn bộ hệ thống sử dụng Pydantic.

#### 🔹 Class `TaskState` (Enum)
```python
class TaskState(str, Enum):
    IDLE_MONITORING = "IDLE_MONITORING"
    DATA_BURST_ALERT = "DATA_BURST_ALERT"
    VIDEO_STREAMING = "VIDEO_STREAMING"
```

**Chức năng:** Định nghĩa các trạng thái tác vụ của thiết bị IoT.

**Giải thích:**
- `IDLE_MONITORING`: Thiết bị đang ở chế độ chờ, chỉ gửi dữ liệu cảm biến nhỏ
- `DATA_BURST_ALERT`: Thiết bị cần gửi cảnh báo khẩn cấp (burst data)
- `VIDEO_STREAMING`: Thiết bị đang stream video

**Ý nghĩa trong thuật toán:**
- Mỗi task có yêu cầu năng lượng và QoS khác nhau
- `IDLE_MONITORING` → ưu tiên tiết kiệm năng lượng
- `DATA_BURST_ALERT` → ưu tiên độ trễ thấp
- `VIDEO_STREAMING` → cân bằng giữa năng lượng và QoS

#### 🔹 Class `NetworkConfig` (BaseModel)
```python
class NetworkConfig(BaseModel):
    name: str
    power_tx: float       # Công suất truyền (mW)
    power_idle: float     # Công suất chờ (mW == mJ/s)
    energy_wakeup: float  # Năng lượng khởi động (mJ)
```

**Chức năng:** Lưu trữ thông số năng lượng **cố định** của một loại mạng.

**Ví dụ thực tế (từ constants.py):**
```python
# Wi-Fi
{
    "name": "Wi-Fi",
    "power_tx": 100.0,      # mW - Công suất truyền
    "power_idle": 10.0,     # mW - Công suất chờ
    "energy_wakeup": 2.0    # mJ - Khởi động radio
}

# 5G
{
    "name": "5G",
    "power_tx": 300.0,      # mW - Cao hơn Wi-Fi
    "power_idle": 15.0,     # mW
    "energy_wakeup": 5.0    # mJ
}

# BLE
{
    "name": "BLE",
    "power_tx": 10.0,       # mW - Tiết kiệm nhất
    "power_idle": 2.0,      # mW
    "energy_wakeup": 0.5    # mJ
}
```

**Dùng để làm gì?**
- Tính toán chi phí năng lượng trong thuật toán MCDM
- So sánh hiệu suất năng lượng giữa các mạng
- Cơ sở cho định luật `Energy = (power_tx + power_idle) × time_tx + energy_wakeup`

#### 🔹 Class `NetworkState` (BaseModel)
```python
class NetworkState(BaseModel):
    name: str                          # Loại mạng (Wi-Fi/5G/BLE)
    bandwidth: float                   # Băng thông (Mbps)
    latency: int                       # Độ trễ (ms)
    is_available: bool                 # Mạng có khả dụng không
    station_id: str | None             # ID của base station (NEW!)
    rssi: float | None                 # RSSI (dBm) - từ physics model
    snr: float | None                  # SNR (dB) - từ physics model
    packet_loss_rate: float | None     # PLR (0-1) - từ physics model
```

**Chức năng:** Lưu trữ trạng thái **động** của mạng tại thời điểm hiện tại.

**Giải thích:**
- `bandwidth`: Tốc độ truyền dữ liệu thực tế (thay đổi theo khoảng cách)
- `latency`: Thời gian delay (ms)
- `is_available`: `True` nếu SNR > 0 dB, `False` nếu không có tín hiệu
- `station_id`: **ID cụ thể** của trạm đang phục vụ (ví dụ: "WiFi-2", "5G-3")
- `rssi`: Cường độ tín hiệu thu được (dBm) - càng cao càng tốt
- `snr`: Tỷ lệ tín hiệu/nhiễu (dB) - quyết định chất lượng kết nối
- `packet_loss_rate`: Tỷ lệ mất gói (0.0 = không mất, 1.0 = mất 100%)

**Ví dụ thực tế:**
```python
wifi_state = NetworkState(
    name="Wi-Fi",
    bandwidth=85.3,            # 85.3 Mbps từ Shannon-Hartley
    latency=12,                # 12ms (base + retransmission overhead)
    is_available=True,         # SNR > 0
    station_id="WiFi-2",       # Đang kết nối với router #2
    rssi=-68.4,                # -68.4 dBm (tín hiệu mạnh)
    snr=26.6,                  # 26.6 dB (chất lượng tốt)
    packet_loss_rate=0.02      # 2% mất gói
)
```

**Ý nghĩa quan trọng:**
- **station_id** giúp phân biệt các trạm cùng loại (có 4 trạm Wi-Fi, 4 trạm 5G, 4 trạm BLE)
- **rssi, snr, packet_loss_rate** là metrics từ **physics model** - không phải giá trị giả định!

#### 🔹 Class `DeviceState` (BaseModel)
```python
class DeviceState(BaseModel):
    position: Tuple[int, int]              # Tọa độ (x, y)
    current_task: TaskState                # Tác vụ hiện tại
    available_networks: List[NetworkState] # Các mạng khả dụng
```

**Chức năng:** Đại diện cho trạng thái hiện tại của thiết bị IoT.

**Ví dụ:**
```python
device = DeviceState(
    position=(150, 200),           # Thiết bị ở tọa độ (150, 200)
    current_task=TaskState.IDLE_MONITORING,
    available_networks=[wifi_state, ble_state]  # Có 2 mạng khả dụng
)
```

**Dùng để làm gì?**
- Truyền dữ liệu giữa các API endpoints
- Lưu trữ snapshot của simulation tại mỗi bước

---

### 2. `app/services/network_physics.py`

**Mục đích:** Coordinator tính QoS bằng cách **dùng constants + formulas**.

#### 🔹 Vai trò
- Lấy tham số vật lý từ `app/core/constants.py::NetworkPhysicsConfig`
- Gọi các hàm thuần từ `app/core/formulas.py` để tính RSSI, SNR, throughput, PLR, latency
- Trả về QoS metrics + cờ `is_available`

#### 🔹 Luồng tính QoS (`calculate_qos`)
1) Path loss → RSSI → SNR (từ formulas)
2) Check availability: `SNR > 0 dB`
3) Throughput: Shannon-Hartley, clamp `max_throughput_mbps`
4) Packet loss: Sigmoid PLR + clamp high-SNR
5) Latency: `base_latency_ms + PLR * 100 * overhead_per_percent`

**Outputs:** `bandwidth`, `latency`, `packet_loss`, `rssi`, `snr`, `is_available`

**Lưu ý:** Không còn logic trùng lặp trong `network_physics.py`; mọi công thức nằm ở `formulas.py`, tham số ở `constants.py`.

---

### 3. `app/services/simulation.py`

**Mục đích:** Mô phỏng thiết bị IoT di chuyển trong môi trường có nhiều base stations.

#### 🔹 Class `SimulationEngine`

**Tổng quan:** Engine chính để chạy mô phỏng.
#### 📍 Hàm `_init_base_stations()`

```python
def _init_base_stations(self):
    """Đặt các base stations tại các vị trí cố định với ID riêng."""
    self.base_stations = {
        "Wi-Fi": [
            {"id": "WiFi-1", "pos": (100, 100)},
            {"id": "WiFi-2", "pos": (300, 250)},
            {"id": "WiFi-3", "pos": (600, 400)},
            {"id": "WiFi-4", "pos": (800, 750)}
        ],
        "5G": [
            {"id": "5G-1", "pos": (200, 200)},
            {"id": "5G-2", "pos": (500, 300)},
            {"id": "5G-3", "pos": (700, 600)},
            {"id": "5G-4", "pos": (900, 100)}
        ],
        "BLE": [
            {"id": "BLE-1", "pos": (150, 150)},
            {"id": "BLE-2", "pos": (350, 350)},
            {"id": "BLE-3", "pos": (550, 550)},
            {"id": "BLE-4", "pos": (750, 750)}
        ]
    }
```

**Chức năng:** Tạo map với **12 base stations có ID riêng biệt**.

**Layout:**
- **4 Wi-Fi routers:** WiFi-1 đến WiFi-4
- **4 5G towers:** 5G-1 đến 5G-4
#### 📍 Hàm `_find_best_base_station()`

```python
def _find_best_base_station(self, device_position, network_type):
    """Tìm base station tốt nhất cho một loại mạng.
    
    Returns:
        Tuple (station_id, qos_metrics)
    """
```

**Chức năng:** Với một loại mạng (Wi-Fi/5G/BLE), tìm station nào cho SNR tốt nhất.

**Logic:**
1. Lặp qua tất cả stations của loại mạng đó
2. Với mỗi station:
   - Lấy `station_id` và `station_pos`
   - Tính khoảng cách từ device
   - Dùng `NetworkPhysics.calculate_qos()` để tính QoS đầy đủ
3. Chọn station có **SNR cao nhất** (không phải gần nhất!)
4. **Return station_id** thay vì position

**Tại sao chọn theo SNR chứ không phải khoảng cách?**
- Do có **shadowing** (vật cản ngẫu nhiên)
- Station gần nhất có thể bị che khuất → SNR thấp
- Station xa hơn nhưng không bị che → SNR cao hơn

**Ví dụ:**
```python
# Device ở (150, 200)
station_id, qos = engine._find_best_base_station((150, 200), "Wi-Fi")
# → station_id = "WiFi-1"
# → qos = {
#     "bandwidth": 85.3,
#     "latency": 12,
#     "rssi": -68.4,
#     "snr": 26.6,
#     "packet_loss_rate": 0.02,
#     "is_available": True
# }
```

**Thay đổi quan trọng:**
- **Trước:** Return `(station_position, qos)`
- **Sau:** Return `(station_id, qos)` → Frontend biết đúng trạm nào đang phục vụ! _find_best_base_station(self, device_position, network_type):
    """Tìm base station tốt nhất cho một loại mạng."""
```

**Chức năng:** Với một loại mạng (Wi-Fi/5G/BLE), tìm station nào cho SNR tốt nhất.

**Logic:**
#### 📍 Hàm `_update_available_networks()`

```python
def _update_available_networks(self):
    """Cập nhật danh sách networks khả dụng cho vị trí hiện tại."""
```

**Chức năng:** Tìm TẤT CẢ các mạng khả dụng tại vị trí device với **đầy đủ metrics**.

**Logic:**
1. Lặp qua 3 loại mạng: Wi-Fi, 5G, BLE
2. Với mỗi loại, gọi `_find_best_base_station()` → nhận `(station_id, qos)`
3. Nếu `is_available = True` → tạo `NetworkState` với:
   - `name`: Loại mạng
   - `bandwidth`, `latency`: Từ QoS
   - **`station_id`**: ID của trạm đang phục vụ
   - **`rssi`, `snr`, `packet_loss_rate`**: Metrics từ physics model
4. Cập nhật `device_state.available_networks`

**Kết quả đầy đủ:**
```python
# Tại vị trí (150, 200), device có thể thấy:
available_networks = [
    NetworkState(
        name="Wi-Fi",
        bandwidth=85.3,
        latency=12,
        is_available=True,
        station_id="WiFi-1",        # Đang kết nối WiFi-1
        rssi=-68.4,
        snr=26.6,
        packet_loss_rate=0.02
    ),
    NetworkState(
        name="5G",
        bandwidth=120.5,
        latency=15,
        is_available=True,
        station_id="5G-2",          # Đang kết nối 5G-2
        rssi=-75.2,
        snr=24.8,
        packet_loss_rate=0.03
    ),
    # BLE không có (quá xa, SNR < 0)
]
```

**Ý nghĩa:**
- API response giờ có **đầy đủ thông tin vật lý**
- Frontend có thể hiển thị metrics chi tiết
- Sẵn sàng làm **features cho ML model**!

**Chức năng:** Tìm TẤT CẢ các mạng khả dụng tại vị trí device.

**Logic:**
1. Lặp qua 3 loại mạng: Wi-Fi, 5G, BLE
2. Với mỗi loại, gọi `_find_best_base_station()`
3. Nếu `is_available = True` → thêm vào list
4. Cập nhật `device_state.available_networks`

**Kết quả:**
```python
# Tại vị trí (150, 200), device có thể thấy:
available_networks = [
    NetworkState(name="Wi-Fi", bandwidth=85.3, latency=8, ...),
    NetworkState(name="5G", bandwidth=120.5, latency=15, ...),
    # BLE không có (quá xa, SNR < 0)
]
```

#### 📍 Hàm `_move_device()`

```python
def _move_device(self, step_size=10):
    """Di chuyển thiết bị đến vị trí mới."""
```

**Chức năng:** Di chuyển device theo pattern để cover toàn bộ map.

**Pattern di chuyển:**
- **Step 0-99:** Di chuyển ngang (→) để scan từ trái sang phải
- **Step 100-199:** Di chuyển dọc (↓) để scan từ trên xuống dưới
- **Step 200+:** Di chuyển ngẫu nhiên (↑↓←→)

**Ý nghĩa:** Pattern này giúp device khám phá đều khắp map.

#### 📍 Hàm `run_simulation_step()` - **HÀM CHÍNH**

```python
def run_simulation_step(self):
    """Chạy một bước mô phỏng."""
```

**Chức năng:** Thực hiện MỘT bước trong simulation.

**Các bước:**
1. `simulation_step += 1`: Tăng counter
2. `_move_device()`: Di chuyển device
3. `_generate_random_task()`: Random task mới (60% idle, 30% alert, 10% video)
4. Cập nhật `device_state.position` và `current_task`
5. `_update_available_networks()`: Tính lại mạng khả dụng cho vị trí mới
6. Return `device_state` mới

**Ví dụ sử dụng:**
```python
engine = SimulationEngine()

# Chạy 1 bước
new_state = engine.run_simulation_step()
print(f"Device moved to: {new_state.position}")
print(f"Available networks: {[n.name for n in new_state.available_networks]}")
```

#### 📍 Hàm `get_simulation_stats()`

```python
def get_simulation_stats(self):
    """Lấy thống kê về simulation hiện tại."""
```

**Chức năng:** Trả về snapshot của trạng thái hiện tại.

**Output:**
```python
{
    "simulation_step": 42,
    "current_position": (150, 200),
    "current_task": "IDLE_MONITORING",
    "available_networks_count": 2,
    "available_networks": ["Wi-Fi", "5G"],
    "map_size": (1000, 1000),
    "total_base_stations": 12
}
```

---

### 4. `app/core/decision_logic.py`

**Mục đích:** Implement thuật toán MCDM để chọn mạng tối ưu.

#### 📍 `TASK_WEIGHTS` Dictionary

```python
TASK_WEIGHTS = {
    TaskState.IDLE_MONITORING: {
        "w_energy": 0.8,  # 80% quan tâm năng lượng
        "w_qos": 0.2      # 20% quan tâm QoS
    },
    TaskState.DATA_BURST_ALERT: {
        "w_energy": 0.3,
        "w_qos": 0.7      # 70% quan tâm QoS (độ trễ thấp)
    },
    TaskState.VIDEO_STREAMING: {
        "w_energy": 0.4,
        "w_qos": 0.6
    }
}
```

**Chức năng:** Định nghĩa trọng số ưu tiên cho từng task.

**Giải thích:**
- `IDLE_MONITORING`: Thiết bị idle → ưu tiên tiết kiệm pin (80% energy, 20% QoS)
- `DATA_BURST_ALERT`: Cảnh báo khẩn cấp → ưu tiên gửi nhanh (30% energy, 70% QoS)
- `VIDEO_STREAMING`: Streaming → cần cân bằng (40% energy, 60% QoS)

#### 📍 `QOS_REQUIREMENTS` Dictionary

```python
QOS_REQUIREMENTS = {
    TaskState.IDLE_MONITORING: {
        "min_bandwidth": 0.1,       # Chỉ cần 0.1 Mbps
        "max_latency": 1000,        # Có thể chậm 1 giây
        "must_be_available": True
    },
    TaskState.DATA_BURST_ALERT: {
        "min_bandwidth": 5.0,       # Cần 5 Mbps
        "max_latency": 100,         # Phải < 100ms
        "must_be_available": True
    },
    TaskState.VIDEO_STREAMING: {
        "min_bandwidth": 36.0,      # ⬆️ Cao: loại trừ mạng yếu (BLE max 2Mbps)
        "max_latency": 200,         # 200ms (cho phép buffer)
        "must_be_available": True
    }
}
```

**Chức năng:** Yêu cầu QoS tối thiểu cho từng task.

**Giải thích:**
- **VIDEO_STREAMING ngưỡng cao (36 Mbps):** 
  - BLE không thể đáp ứng (max 2 Mbps) → automatically excluded
  - Wi-Fi/5G thường đủ → algorithm chọn dựa trên energy + QoS trade-off
  - Tạo điều kiện cho "dilemma scenarios": Wi-Fi (low power) vs 5G (high power)

#### 📍 Hàm `calculate_energy_cost()`

```python
def calculate_energy_cost(network_config, network_state, task):
    """Tính chi phí năng lượng (đơn giản hóa)."""
```

**Công thức (hiện tại):**
```
E_total = (energy_tx × DataSize) + energy_wakeup
```

**Giải thích:**
- `energy_tx` (mJ/KB) đã bao gồm RF + circuit overhead → không cần nhân thời gian
- Bỏ `energy_idle` khỏi công thức (không đáng kể với burst ngắn)
- Giữ `energy_wakeup` để phản ánh chi phí bật radio

**Ước tính DataSize (từ `TaskDataEstimates`):**
- IDLE_MONITORING: 1 KB
- DATA_BURST_ALERT: 50 KB
- VIDEO_STREAMING: 1000 KB

**Ví dụ:**
```python
# Wi-Fi, VIDEO_STREAMING
energy = calculate_energy_cost(wifi_config, wifi_state, TaskState.VIDEO_STREAMING)
# = 0.5 mJ/KB * 1000 KB + 2.0 mJ = 502.0 mJ
```

#### 📍 Hàm `calculate_qos_penalty()`

```python
def calculate_qos_penalty(network_state, task):
    """Tính phí phạt QoS."""
```

**Chức năng:** Phạt nếu mạng không đáp ứng yêu cầu QoS.

**Logic phạt:**
1. Nếu `is_available = False` → phạt 1000 (rất nặng)
2. Nếu bandwidth < min_bandwidth → phạt `(thiếu) * 50`
3. Nếu latency > max_latency → phạt `(vượt) * 2`
4. Nếu tổng phạt > 500 → trả về 1000 (vi phạm nghiêm trọng)

**Ví dụ:**
```python
# Task DATA_BURST_ALERT cần min_bandwidth=5.0, max_latency=100
# Mạng BLE có bandwidth=2.0, latency=150

penalty = calculate_qos_penalty(ble_state, TaskState.DATA_BURST_ALERT)
# Bandwidth: thiếu 3.0 Mbps → phạt 3.0 * 50 = 150
# Latency: vượt 50ms → phạt 50 * 2 = 100
# Tổng: 150 + 100 = 250
```

#### 📍 Hàm `calculate_cost()` - **HÀM CHÍNH**

```python
def calculate_cost(network_state, network_config, task):
    """Tính tổng chi phí theo MCDM.
    
    Công thức: Total_Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty
    """
```

**Chức năng:** Tính **tổng chi phí** để lựa chọn mạng.

**Ví dụ đầy đủ:**
```python
# Task: DATA_BURST_ALERT (w_energy=0.3, w_qos=0.7)
# Wi-Fi: energy_cost=62, qos_penalty=0 (đáp ứng đủ QoS)
# BLE: energy_cost=22, qos_penalty=250 (không đủ QoS)

cost_wifi = 0.3 * 62 + 0.7 * 0 = 18.6
cost_ble = 0.3 * 22 + 0.7 * 250 = 181.6

→ Chọn Wi-Fi (chi phí thấp hơn)
```

#### 📍 Hàm `select_best_network()` - **HÀM CHÍNH**

```python
def select_best_network(available_networks, network_configs, task):
    """Lựa chọn mạng tối ưu."""
```

**Chức năng:** Chọn mạng có **cost thấp nhất**.

**Logic:**
1. Lặp qua tất cả `available_networks`
2. Tính `cost` cho từng mạng
3. Chọn mạng có `min_cost`
4. Return `(best_network, min_cost)`

**Ví dụ:**
```python
# Device có 2 mạng: Wi-Fi và 5G
# Task: VIDEO_STREAMING

best_network, cost = select_best_network(
    available_networks=[wifi_state, fiveg_state],
    network_configs=configs,
    task=TaskState.VIDEO_STREAMING
)

# Output: (wifi_state, 45.2)
# → Chọn Wi-Fi vì cost = 45.2 < 5G cost = 58.7
```

---

### 5. `app/main.py`

**Mục đích:** FastAPI server với các REST API endpoints.

#### 📍 Khởi tạo App

```python
app = FastAPI(
    title="IoT Network Selection System",
    version="1.0.0"
)

# CORS middleware để web UI có thể gọi API
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Mount static files (web UI)
app.mount("/static", StaticFiles(directory="web"), name="static")

# Khởi tạo simulation engine (singleton)
simulation_engine = SimulationEngine()
```

#### 📍 `GET /` - Root Endpoint

```python
@app.get("/")
def root():
    """Thông tin tổng quan về API."""
```

**Chức năng:** Hiển thị danh sách endpoints có sẵn.

**Response:**
```json
{
  "message": "IoT Network Selection System API",
  "version": "1.0.0",
  "endpoints": {
    "simulation": "/simulation/step - Run simulation step",
    "decision": "/decision - Make network selection decision",
    ...
  }
}
```

#### 📍 `GET /status` - System Status

```python
@app.get("/status")
def get_system_status():
    """Lấy trạng thái hiện tại của hệ thống."""
```

**Chức năng:** Trả về snapshot của simulation và network configs.

**Response:**
```json
{
  "system_status": "operational",
  "simulation_engine": {
    "current_step": 42,
    "device_position": [150, 200],
    "current_task": "IDLE_MONITORING",
    "available_networks": ["Wi-Fi", "5G"]
  },
  "network_configs": {
    "Wi-Fi": {"energy_tx": 0.5, ...}
  }
}
```

#### 📍 `POST /simulation/step` - Run Simulation

```python
@app.post("/simulation/step")
def simulation_step():
    """Chạy một bước mô phỏng."""
```

**Chức năng:** Gọi `simulation_engine.run_simulation_step()` và format response.

**Request:** Không cần body

**Response:**
```json
{
  "step_number": 43,
  "device_state": {
    "position": [160, 200],
    "current_task": "DATA_BURST_ALERT",
    "available_networks": [
      {
        "name": "Wi-Fi",
        "bandwidth": 85.3,
        "latency": 12,
        "is_available": true
      }
    ]
  },
  "simulation_info": {
    "networks_count": 2,
    "networks_list": ["Wi-Fi", "5G"]
  }
}
```

#### 📍 `POST /decision` - MCDM Decision

```python
@app.post("/decision")
def make_decision(device_state: DeviceState):
    """Ra quyết định lựa chọn mạng bằng MCDM algorithm."""
```

**Chức năng:** Tính cost cho TẤT CẢ networks và chọn network có cost thấp nhất.

**Request Body:**
```json
{
  "position": [150, 200],
  "current_task": "DATA_BURST_ALERT",
  "available_networks": [
    {
      "name": "Wi-Fi",
      "station_id": "WiFi-4",
      "bandwidth": 85.3,
      "latency": 12,
      "is_available": true,
      "rssi": -68.4,
      "snr": 26.6,
      "packet_loss_rate": 0.02
    },
    {
      "name": "5G",
      "station_id": "5G-3",
      "bandwidth": 95.2,
      "latency": 18,
      "is_available": true,
      "rssi": -72.1,
      "snr": 22.8,
      "packet_loss_rate": 0.05
    }
  ]
}
```

**Response:**
```json
{
  "optimal_network": "Wi-Fi",
  "optimal_cost": 12.45,
  "all_network_costs": {
    "WiFi-4": 12.45,
    "5G-3": 18.92
  },
  "device_info": {
    "position": [150, 200],
    "current_task": "DATA_BURST_ALERT"
  },
  "cost_analysis": {
    "WiFi-4": {
      "total_cost": 12.45,
      "network_info": {...},
      "config_info": {...}
    },
    "5G-3": {...}
  }
}
```

**Logic:**
1. Lặp qua `available_networks`
2. Với mỗi network, tính: `Cost = w_energy * E_total + w_qos * P_qos`
3. Chọn network có min cost
4. Return optimal_network + all_network_costs (để frontend so sánh)

**Key Updates:**
- ✅ `all_network_costs` dùng `station_id` làm key (không phải network type)
- ✅ `station_id` cho phép phân biệt giữa các stations cùng loại mạng

---

#### 📍 `POST /decision/ml` - ML Decision (NEW!)

```python
@app.post("/decision/ml")
def make_decision_ml(device_state: DeviceState):
    """Ra quyết định bằng ML (Random Forest) với fallback về MCDM."""
```

**Chức năng:** Dự đoán mạng bằng ML model, automatically calculate cost cho tất cả networks.

**Request Body:** Giống `/decision`

**Response:**
```json
{
  "selected_network": "5G",
  "station_id": "5G-3",
  "method": "ML",
  "confidence": 0.96,
  "cost": 18.92,
  "all_network_costs": {
    "WiFi-4": 12.45,
    "5G-3": 18.92
  },
  "device_info": {
    "position": [150, 200],
    "current_task": "DATA_BURST_ALERT"
  },
  "network_details": {
    "name": "5G",
    "bandwidth": 95.2,
    "latency": 18,
    "snr": 22.8,
    "rssi": -72.1
  }
}
```

**Logic:**
1. Dùng `ml_predictor.predict()` để lấy predicted network + confidence
2. Trích xuất `station_id` của predicted network
3. **Tính MCDM cost cho TẤT CẢ networks** (giống `/decision`)
4. Lấy cost của selected network
5. Return `method="ML"` + confidence + cost + all_network_costs

**Fallback Mechanism:**
- Nếu ML model không khả dụng → `method="MCDM_Fallback"`, `confidence=1.0`
- Nếu predicted network không có trong available_networks → fallback đến MCDM

**Key Difference vs `/decision`:**
- `/decision`: Pure MCDM, `method="MCDM"`
- `/decision/ml`: ML-based, `method="ML"` hoặc `method="MCDM_Fallback"`
- Cả hai return `all_network_costs` để frontend có tất cả options
### 6. `web/map-visualization.js`

**Mục đích:** JavaScript logic cho giao diện map visualization với Canvas API.

#### 🔹 Class `MapVisualization`

**Tổng quan:** Quản lý toàn bộ UI và tương tác với API.

#### 📍 `constructor()`

```javascript
constructor() {
    this.canvas = document.getElementById('mapCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.apiBaseUrl = 'http://localhost:8000';
    
    // Map configuration
    this.mapSize = { width: 1000, height: 1000 };  // Map coordinates
    this.canvasSize = {
        width: this.canvas.width,    // 800px (from HTML)
        height: this.canvas.height   // 600px (from HTML)
    };
    this.scale = {
        x: 0.8,  // canvas_width / map_width = 800/1000
        y: 0.6   // canvas_height / map_height = 600/1000
    };
    
    // State
    this.devicePosition = { x: 0, y: 0 };
    this.currentTask = 'IDLE_MONITORING';
    this.availableNetworks = [];
    this.baseStations = [];
    this.decisionResult = null;
    this.connectedStation = null;  // NEW: Track connected station
    
    // Network colors
    this.networkColors = {
        'Wi-Fi': '#2196F3',   // Blue
        '5G': '#9C27B0',      // Purple
        'BLE': '#FF9800'      // Orange
    };
}
```

**Chức năng:** Khởi tạo các biến state và config.

**Coordinate System:**
- **Map coords:** (0,0) đến (1000,1000) - logic coordinates
- **Canvas coords:** (0,0) đến (800,600) - pixel coordinates
- **Scale factors:** x=0.8, y=0.6 để chuyển đổi map → canvas

**State Management:**
- `devicePosition`: Vị trí thiết bị trên map
- `availableNetworks`: Danh sách mạng khả dụng (từ API)
- `decisionResult`: Kết quả chọn mạng (null khi chưa decide)
- `connectedStation`: Station đang kết nối (để highlight)
    "network_count": 2
  }
}
```

#### 📍 `GET /ui` - Web UI

```python
@app.get("/ui")
def web_ui():
    """Serve web UI HTML file."""
```

**Chức năng:** Trả về file `web/index.html`.

#### 📍 `POST /simulation/reset` - Reset Simulation

```python
@app.post("/simulation/reset")
def reset_simulation(x: int = 0, y: int = 0):
    """Reset simulation về vị trí mới."""
```

**Chức năng:** Gọi `simulation_engine.reset_simulation()`.

---

### 6. `web/map-visualization.js`

**Mục đích:** JavaScript logic cho giao diện map visualization.

#### 🔹 Class `MapVisualization`

**Tổng quan:** Quản lý toàn bộ UI và tương tác với API.

#### 📍 `constructor()`

```javascript
constructor() {
    this.canvas = document.getElementById('mapCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.apiBaseUrl = 'http://localhost:8000';
    this.devicePosition = { x: 0, y: 0 };
    this.availableNetworks = [];
    this.baseStations = [];
    // ...
}
```

**Chức năng:** Khởi tạo các biến state và config.

#### 📍 `init()`

```javascript
init() {
    this.setupEventListeners();
    this.checkApiStatus();
    this.initializeBaseStations();
    this.draw();
    this.startAutoRunTimer();
}
```

**Chức năng:** Setup toàn bộ UI khi trang load.

#### 📍 `setupEventListeners()`

```javascript
setupEventListeners() {
    document.getElementById('stepBtn').addEventListener('click', () => {
        this.runSimulationStep();
    });
    
    document.getElementById('decisionBtn').addEventListener('click', () => {
        this.makeDecision();
#### 📍 `draw()` - **HÀM CHÍNH**

```javascript
draw() {
    this.ctx.clearRect(0, 0, this.canvasSize.width, this.canvasSize.height);
    
    // 1. Vẽ grid lines
    this.drawGrid();
    
    // 2. Vẽ coverage areas (từng trạm riêng biệt)
    this.drawCoverageAreas();
    
    // 3. Vẽ base stations với station IDs
    this.drawBaseStations();
    
    // 4. Vẽ device với task indicator
    this.drawDevice();
    
    // 5. Vẽ network connections (nếu có decision)
    this.drawNetworkConnections();
}
```

**Chức năng:** Vẽ toàn bộ map lên canvas.

**Các layer vẽ theo thứ tự (z-index):**
1. **Grid lines** (nền) - Hệ tọa độ 100m intervals
2. **Coverage areas** (vùng phủ) - **12 circles riêng biệt** (mỗi trạm 1 circle)
3. **Base stations** (trạm) - Hình tròn với antenna icon + **Station ID label**
4. **Device** (thiết bị) - Hình tròn đỏ + task badge + position label
5. **Network connections** (kết nối) - Line + **info box với metrics**

**Cải tiến so với version cũ:**
- ✅ Vẽ **12 coverage circles** thay vì 3 (mỗi trạm riêng)
- ✅ Hiển thị **Station ID** (WiFi-1, 5G-2...) thay vì chỉ loại mạng
- ✅ Info box hiển thị **đầy đủ metrics:** BW, Latency, RSSI, SNR, PLR
- ✅ Highlight trạm đang kết nối với **dashed ring** cập nhật UI.

#### 📍 `handleCanvasClick()` - **HÀM QUAN TRỌNG**

```javascript
handleCanvasClick(event) {
    const rect = this.canvas.getBoundingClientRect();
    
    // Step 1: Get click position relative to canvas DISPLAYED bounds
    const clickX = event.clientX - rect.left;
    const clickY = event.clientY - rect.top;
    
    // Step 2: Scale from DISPLAYED size to CANVAS INTERNAL size
    const displayToCanvasScaleX = this.canvas.width / rect.width;
    const displayToCanvasScaleY = this.canvas.height / rect.height;
    
    const canvasX = clickX * displayToCanvasScaleX;
    const canvasY = clickY * displayToCanvasScaleY;
    
    // Step 3: Convert canvas pixels to map coordinates
    const mapX = canvasX / this.scale.x;
    const mapY = canvasY / this.scale.y;
    
    // Step 4: Round and clamp to map bounds
    const clampedX = Math.max(0, Math.min(1000, Math.round(mapX)));
    const clampedY = Math.max(0, Math.min(1000, Math.round(mapY)));
    
    // Update device position
    this.devicePosition = { x: clampedX, y: clampedY };
    
    // CLEAR decision result when manually placing device
    this.decisionResult = null;
    this.connectedStation = null;
    
    // Recalculate available networks for new position
    this.updateNetworksForPosition();
    this.draw();
    this.updateUI();
}
```

**Chức năng:** Cho phép user click vào canvas để đặt device position.

**Coordinate Transformation Pipeline:**
1. **Browser coords** (event.clientX/Y) → Click position in browser window
2. **Canvas display coords** (clickX/Y) → Position relative to canvas element
3. **Canvas internal coords** (canvasX/Y) → Account for CSS scaling
4. **Map coords** (mapX/Y) → Final logic coordinates (0-1000)

**Logic quan trọng:**
- **Clear decision result:** Khi click, bỏ decision cũ (chỉ hiện stats khi ấn Decision)
- **updateNetworksForPosition():** Tính lại available networks cho vị trí mới
- **Client-side calculation:** UI tính gần đúng, backend có physics chính xác

**Tại sao phức tạp?**
- Canvas có thể bị scale bởi CSS/flexbox
- Phải convert đúng: browser → display → canvas → map
```javascript
draw() {
    this.ctx.clearRect(0, 0, this.canvasSize.width, this.canvasSize.height);
    
    // 1. Vẽ grid lines
    this.drawGrid();
    
    // 2. Vẽ coverage circles
    this.baseStations.forEach(station => {
        this.drawCoverageCircle(station);
    });
    
    // 3. Vẽ base stations
    this.baseStations.forEach(station => {
        this.drawBaseStation(station);
    });
    
    // 4. Vẽ device
    this.drawDevice();
    
    // 5. Vẽ connection lines
    this.drawConnections();
}
```

**Chức năng:** Vẽ toàn bộ map lên canvas.

**Các layer vẽ theo thứ tự:**
1. Grid (nền)
2. Coverage circles (vùng phủ sóng)
3. Base stations (hình vuông màu)
4. Device (hình tròn)
5. Connection lines (từ device đến stations)

#### 📍 `handleCanvasClick()` - **HÀM QUAN TRỌNG**

```javascript
handleCanvasClick(e) {
    const rect = this.canvas.getBoundingClientRect();
    const canvasX = e.clientX - rect.left;
    const canvasY = e.clientY - rect.top;
    
    // Chuyển đổi canvas coords → map coords
    const mapX = Math.round(canvasX / this.scale.x);
    const mapY = Math.round(canvasY / this.scale.y);
    
    // Clamp trong bounds
    this.devicePosition.x = Math.max(0, Math.min(1000, mapX));
    this.devicePosition.y = Math.max(0, Math.min(1000, mapY));
    
    // Cập nhật networks cho vị trí mới
    this.updateNetworksForPosition();
    this.draw();
}
```

**Chức năng:** Cho phép user click vào canvas để đặt device position.

**Logic:**
1. Lấy tọa độ click (pixel coordinates)
2. Chuyển đổi sang map coordinates (0-1000)
3. Clamp trong bounds
4. Cập nhật `devicePosition`
5. Tính lại networks khả dụng
6. Vẽ lại map

---

### 7. `app/ml/` - Machine Learning Module

**Mục đích:** Cung cấp ML-based network selection thay thế cho MCDM baseline.

---

#### 📁 `app/ml/__init__.py`

**Chức năng:** Export các classes chính để dễ import.

```python
from .data_collector import DataCollector
from .predictor import MLPredictor

__all__ = ["DataCollector", "MLPredictor"]
```

---

#### 📁 `app/ml/data_collector.py`

**Mục đích:** Thu thập training data từ simulation engine với MCDM labels.

#### 🔹 Class `DataCollector`

**Workflow:**
1. Chạy simulation nhiều lần
2. Mỗi bước: lấy `device_state`
3. Dùng MCDM để tìm optimal network → **gán nhãn**
4. Trích xuất 18 features + 1 label
5. Lưu vào CSV

#### 📍 Method `collect(num_samples)`

**Chức năng:** Thu thập N samples từ simulation.

**Logic:**
```python
for i in range(num_samples):
    device_state = engine.run_simulation_step()
    
    # MCDM làm "giáo viên" gán nhãn
    optimal_network, cost = select_best_network(
        device_state.available_networks,
        network_configs,
        device_state.current_task
    )
    
    # Extract 18 features
    features = self._extract_features(device_state, optimal_network)
    self.samples.append(features)
```

#### 📍 Method `_extract_features()`

**18 Features được trích xuất:**

1. **Device context (3 features):**
   - `position_x`, `position_y`: Tọa độ thiết bị
   - `task_type`: 0=IDLE, 1=ALERT, 2=VIDEO

2. **Wi-Fi metrics (5 features):**
   - `wifi_rssi`, `wifi_snr`, `wifi_bandwidth`, `wifi_latency`, `wifi_distance`

3. **5G metrics (5 features):**
   - `5g_rssi`, `5g_snr`, `5g_bandwidth`, `5g_latency`, `5g_distance`

4. **BLE metrics (5 features):**
   - `ble_rssi`, `ble_snr`, `ble_bandwidth`, `ble_latency`, `ble_distance`

**Default values khi network không available:**
- `rssi = -999.0` (tín hiệu không có)
- `snr = -999.0`
- `bandwidth = 0.0`
- `latency = 9999` (vô cùng lớn)
- `distance = 9999.0`

**Label:**
- `optimal_network`: 0=Wi-Fi, 1=5G, 2=BLE (từ MCDM)

---

#### 📁 `app/ml/feature_engineering.py`

**Mục đích:** Preprocessing và transformation cho features.

#### 🔹 Class `FeatureEngineer`

**Chức năng:**
- `fit_transform()`: Fit scaler trên training data
- `transform()`: Transform test data hoặc inference data
- `save()/load()`: Lưu/load fitted scaler

**Note:** Hiện tại không dùng scaling vì Random Forest không cần normalize.

---

#### 📁 `app/ml/train_model.py`

**Mục đích:** Training logic cho Random Forest model.

#### 🔹 Class `ModelTrainer`

**Hyperparameters:**
```python
RandomForestClassifier(
    n_estimators=100,    # 100 trees
    max_depth=15,        # Tránh overfitting
    random_state=42,     # Reproducibility
    n_jobs=-1            # Use all CPU cores
)
```

#### 📍 Method `load_data(filepath)`

**Logic:**
1. Load CSV dataset
2. Feature engineering (fit_transform)
3. Train/test split (80/20)
4. Stratify by label (giữ tỷ lệ class)

#### 📍 Method `train()`

**Steps:**
1. Fit model trên training set
2. Tính training accuracy
3. 5-fold cross-validation
4. In CV scores

**Kết quả thực tế:**
```
Training accuracy: 100.0%
CV mean: 98.12% (+/- 1.77%)
```

#### 📍 Method `evaluate()`

**Metrics:**
- Test accuracy: **99.5%**
- Confusion matrix
- Classification report (precision/recall/f1 cho 3 classes)
- Feature importance

**Top features quan trọng:**
1. `task_type` (17.96%)
2. `wifi_distance` (11.56%)
3. `wifi_bandwidth` (11.30%)

---

#### 📁 `app/ml/predictor.py`

**Mục đích:** Inference logic - sử dụng trained model để predict.

#### 🔹 Class `MLPredictor`

**Initialization:**
```python
predictor = MLPredictor("models/rf_network_selector.pkl")
# Tự động load cả feature_engineer
```

#### 📍 Method `predict(device_state, available_networks, engine)` - **MAIN METHOD**

**Chức năng:** Dự đoán mạng tối ưu bằng ML model.

**Workflow:**
1. **Extract 18 features** từ device_state, available_networks
2. **Standardize features** (StandardScaler transform)
3. **Model predict** → class label (0=Wi-Fi, 1=5G, 2=BLE)
4. **Get confidence** → `model.predict_proba()` → max probability
5. **Map result** → NetworkState object của predicted network
6. **Return tuple**: `(best_network_state, confidence_score)`

**Key Detail - Confidence Calculation:**
```python
# Dùng predict_proba để lấy xác suất
probabilities = model.predict_proba(X)[0]  # e.g., [0.96, 0.03, 0.01]
prediction = model.predict(X)[0]           # e.g., 0 (Wi-Fi)
confidence = float(probabilities[prediction])  # e.g., 0.96
```

**Ví dụ đầy đủ:**
```python
device_state = DeviceState(
    position=(150, 200),
    current_task=TaskState.VIDEO_STREAMING,
    available_networks=[wifi_state, fiveg_state]
)

best_network, confidence = predictor.predict(
    device_state, 
    device_state.available_networks,
    engine
)

# Output:
# best_network = wifi_state (NetworkState object)
# confidence = 0.96 (96% chắc chắn)
```

**Output Format:**
- `best_network`: NetworkState object (có tất cả QoS metrics)
- `confidence`: float trong range [0.0, 1.0]

**Sai Số:**
- Nếu model không khả dụng → `return (None, 0.0)`
- Nếu device không có networks → `return (None, 0.0)`

#### 📍 Method `predict_with_probabilities()`

**Return đầy đủ hơn:**
```python
{
    "prediction": "Wi-Fi",
    "confidence": 0.96,
    "probabilities": {
        "Wi-Fi": 0.96,
        "5G": 0.03,
        "BLE": 0.01
    }
}
```

**Use case:** Hiển thị probability distribution trên UI.

---

### 8. `scripts/` - Training Scripts

**Mục đích:** CLI scripts để train và collect data.

---

#### 📁 `scripts/collect_training_data.py`

**Chức năng:** Collect training dataset từ simulation.

**Usage:**
```bash
python scripts/collect_training_data.py --samples 1000 --output data/raw/training_data.csv
```

**Arguments:**
- `--samples`: Số lượng samples (default: 1000)
- `--output`: Output file path (default: data/raw/training_data.csv)

**Workflow:**
1. Initialize `SimulationEngine`
2. Initialize `DataCollector`
3. Loop 1000 lần:
   - Chạy simulation step
   - MCDM gán label
   - Collect features
4. Save to CSV

**Output file format:**
```csv
position_x,position_y,task_type,wifi_rssi,wifi_snr,...,optimal_network
150,200,1,-68.4,26.6,...,0
325,480,2,-75.2,19.8,...,1
...
```

---

#### 📁 `scripts/train_model.py`

**Chức năng:** Train Random Forest model từ CSV.

**Usage:**
```bash
python scripts/train_model.py \
  --data data/raw/training_data.csv \
  --output models/rf_network_selector.pkl \
  --n-estimators 100 \
  --max-depth 15
```

**Arguments:**
- `--data`: Path to training CSV
- `--output`: Model output path
- `--n-estimators`: Số trees (default: 100)
- `--max-depth`: Max depth (default: 15)

**Workflow:**
1. Load CSV dataset
2. Feature engineering + split train/test
3. Train Random Forest
4. 5-fold cross-validation
5. Evaluate on test set
6. Save model + feature_engineer

**Output files:**
- `models/rf_network_selector.pkl` - Model chính
- `models/rf_network_selector_feature_engineer.pkl` - Scaler/encoder

**Console output:**
```
============================================================
🚀 IoT Network Selection - Model Training
============================================================
📊 Data: data/raw/training_data.csv
💾 Output: models/rf_network_selector.pkl
🌲 n_estimators: 100
📏 max_depth: 15

📂 Loading data...
📊 Dataset shape: (1000, 19)
✅ Train set: (800, 18)
✅ Test set: (200, 18)

🚀 Training Random Forest model...
✅ Training accuracy: 1.0000
🔄 Running 5-fold cross-validation...
✅ CV mean: 0.9812 (+/- 0.0177)

📊 Evaluating on test set...
✅ Test accuracy: 0.9950

📋 Classification Report:
              precision    recall  f1-score   support
       Wi-Fi       0.93      1.00      0.96        13
          5G       1.00      0.99      1.00       166
         BLE       1.00      1.00      1.00        21

🎯 Top 10 Feature Importances:
       feature  importance
     task_type    0.179608
 wifi_distance    0.115602
wifi_bandwidth    0.113009

💾 Model saved to models/rf_network_selector.pkl
============================================================
✅ Model training complete!
============================================================
```

---

## 🔄 LUỒNG HOẠT ĐỘNG (CẬP NHẬT VỚI ML)

### Workflow 1: Chạy Simulation Thủ Công

```
User click button "Step"
    ↓
[Web UI] map-visualization.js: runSimulationStep()
    ↓
[API] POST /simulation/step
    ↓
[Backend] simulation_engine.run_simulation_step()
    ↓
    1. simulation_step += 1
    2. _move_device() → vị trí mới
    3. _generate_random_task() → task mới
    4. _update_available_networks():
       - Với mỗi loại mạng (Wi-Fi, 5G, BLE):
         - _find_best_base_station():
           - Lặp qua các stations
           - NetworkPhysics.calculate_qos(distance)
           - Chọn station có SNR tốt nhất
           - Return (station_id, qos_metrics)  ← NEW!
       - Tạo NetworkState với:
         - bandwidth, latency
         - station_id (WiFi-2, 5G-3...)  ← NEW!
         - rssi, snr, packet_loss_rate  ← NEW!
       - Thêm vào available_networks nếu is_available=True
    5. Return DeviceState mới
    ↓
[API] Format response JSON với đầy đủ metrics
    ↓
[Web UI] Nhận data, cập nhật:
    - devicePosition
    - currentTask
    - availableNetworks (giờ có station_id + physics metrics)
    ↓
[Web UI] Gọi draw() để vẽ lại map
    ↓
User thấy:
    - Device đã di chuyển
    - Available networks cập nhật
    - Mỗi network hiện station ID + distance
```

### Workflow 2: Ra Quyết Định Chọn Mạng

```
User click button "Make Decision"
    ↓
[Web UI] map-visualization.js: makeDecision()
    ↓
[API] POST /decision
    Body: {position, current_task, available_networks}
    ↓
[Backend] app/main.py: make_decision()
    ↓
[Core Logic] decision_logic.select_best_network()
    ↓
    Với mỗi available network:
        1. Lấy network_config (energy params)
        2. calculate_energy_cost():
           - Ước tính data_size theo task
           - energy = idle + transmission + wakeup
        3. calculate_qos_penalty():
           - Kiểm tra bandwidth >= min_bandwidth?
           - Kiểm tra latency <= max_latency?
           - Tính penalty
        4. calculate_cost():
           - cost = w_energy * energy + w_qos * penalty
    ↓
    Chọn network có cost thấp nhất
    ↓
[Backend] Return {selected_network, cost, all_costs, ...}
    ↓
[Web UI] Cập nhật decisionResult và vẽ lại:
    - Tìm closest station của network type được chọn
    - Lưu vào connectedStation
    - drawNetworkConnections():
      - Vẽ line từ device → station
      - Highlight station với dashed ring
      - Vẽ info box ở giữa với:
        ✓ Station ID (header: "📡 5G-2")
        ✓ Bandwidth: 120.5 Mbps
        ✓ Latency: 15 ms
        ✓ RSSI: -75.2 dBm
        ✓ SNR: 24.8 dB
        ✓ PLR: 3.0%
        ✓ Distance: 125m
        ✓ Cost: 45.23
    ↓
User thấy:
    - Network được chọn
    - ĐẦY ĐỦ metrics từ physics model
    - Trạm cụ thể đang phục vụ
```

### Workflow 3: Click Vào Map Để Đặt Device

```
User click vào canvas tại pixel (x_pixel, y_pixel)
    ↓
[Web UI] handleCanvasClick(event)
    ↓
    1. Lấy tọa độ click relative to canvas
    2. Convert: browser → display → canvas → map coords
    3. Clamp: x_map ∈ [0, 1000], y_map ∈ [0, 1000]
    4. Cập nhật devicePosition
    5. CLEAR decisionResult (stats biến mất!)  ← NEW!
    6. CLEAR connectedStation  ← NEW!
    ↓
[Web UI] updateNetworksForPosition()
    ↓
    Client-side approximation (không gọi API):
    Với mỗi base station trong 12 stations:
        - Tính distance
        - Kiểm tra in range? (Wi-Fi: 200m, 5G: 400m, BLE: 100m)
        - Nếu YES → Approximate QoS:
          - bandwidth ≈ max_bw * (1 - distance/max_range)
          - latency ≈ 10 + distance/10
        - Thêm vào availableNetworks với station_id
    ↓
    Kết quả: availableNetworks = [
        {name: "5G", station_id: "5G-1", bandwidth: 95.2, latency: 14, distance: 85},
        {name: "5G", station_id: "5G-2", bandwidth: 88.1, latency: 16, distance: 110},
        {name: "Wi-Fi", station_id: "WiFi-3", bandwidth: 72.5, latency: 12, distance: 120},
        ...
    ]
    ↓
[Web UI] updateNetworksList()
    ↓
    Hiển thị TỪNG STATION riêng biệt:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    📶 Available Networks (3)
    
    [5G] 5G-1
         95.2 Mbps • 14ms • 85m
    
    [5G] 5G-2
         88.1 Mbps • 16ms • 110m
    
    [Wi-Fi] WiFi-3
         72.5 Mbps • 12ms • 120m
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
[Web UI] draw() → Vẽ lại map (không có decision line)
    ↓
User thấy:
    - Device đã nhảy đến vị trí click
    - Available networks cập nhật
    - KHÔNG còn stats box (đã clear)
    - Mỗi station hiện riêng với distance
```

### Workflow 4: Auto-Run Mode

```
User click toggle "Auto Run"
    ↓
[Web UI] toggleAutoRun()
    ↓
    Nếu đang tắt → bật:
        - isAutoRunning = true
        - autoRunTimer = setInterval(() => {
            runSimulationStep();
          }, 1000);  // Chạy mỗi 1 giây
    
    Nếu đang bật → tắt:
        - isAutoRunning = false
        - clearInterval(autoRunTimer)
    ↓
Khi bật:
    Mỗi 1 giây tự động:
    - Gọi runSimulationStep()
    - Device di chuyển
    - Available networks cập nhật
    - UI render lại
    ↓
User thấy device tự động di chuyển trên map
```

---

## 🧪 TESTING

### Chạy Unit Tests

```bash
# Chạy tất cả tests
pytest tests/ -v

# Chạy test một file cụ thể
pytest tests/test_decision_logic.py -v

# Chạy với coverage
pytest --cov=app tests/

# Chạy test một hàm cụ thể
pytest tests/test_decision_logic.py::test_calculate_cost -v
```

### Demo Scripts

```bash
# Demo simulation engine
python demo_simulation.py

# Demo main API
python demo_main_api.py

# Demo web UI (mở browser)
python demo_web_ui.py
```

---

## 🚀 CHẠY HỆ THỐNG

### Bước 1: Activate Environment

```bash
conda activate comsys-project
```

### Bước 2: Start API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 3: Mở Web UI

Truy cập: http://localhost:8000/ui

### Bước 4: Thử Nghiệm

1. **Test Simulation:**
   - Click nút "Step" để chạy 1 bước
   - Xem device di chuyển trên map
   - Xem available networks thay đổi

2. **Test Decision:**
   - Chọn task từ dropdown
   - Click "Decision" để chọn mạng
   - Xem kết quả trong status bar

3. **Test Manual Placement:**
   - Click vào map
   - Device nhảy đến vị trí click
   - Networks cập nhật theo vị trí mới

---

## 📚 TÀI LIỆU THAM KHẢO

- **Chi tiết công thức toán học:** Xem `docs/congthuc.md`
- **Phân tích codebase đầy đủ:** Xem `docs/CODEBASE_BREAKDOWN_VI.md`
- **Hướng dẫn API với Postman:** Xem `docs/POSTMAN_GUIDE.md`

---

## ❓ CÂU HỎI THƯỜNG GẶP

### Q1: Tại sao dùng mô hình vật lý phức tạp?
**A:** Để simulation sát với thực tế. Mô hình tuyến tính (giảm 10%) không có cơ sở khoa học. Mô hình Log-Distance Path Loss + Shannon Theorem phản ánh đúng bản chất sóng vô tuyến.

### Q2: NetworkPhysics vs decision_logic khác gì?
**A:** 
- **NetworkPhysics:** Tính QoS dựa trên **vật lý** (RSSI, SNR, throughput)
- **decision_logic:** Tính cost dựa trên **nghiệp vụ** (năng lượng, yêu cầu task)

### Q3: Tại sao cần station_id?
**A:**
- Có **12 trạm** (4 Wi-Fi, 4 5G, 4 BLE), không phải 3 mạng
- Trước: UI chỉ hiện "Wi-Fi available" → không biết trạm nào
- Sau: UI hiện "WiFi-2 available" → biết chính xác
- **Quan trọng cho ML:** Features phải distinguish giữa các stations

### Q4: Làm sao thêm loại mạng mới (ví dụ LoRaWAN)?
**A:**
1. Thêm config vào `NetworkPhysics.CONFIGS`
2. Thêm config vào `SimulationEngine._init_network_configs()`
3. Thêm base stations vào `_init_base_stations()` với IDs
4. Thêm màu vào `map-visualization.js` → `networkColors`

### Q5: Tôi muốn thay đổi trọng số trong MCDM?
**A:** Sửa `decision_logic.py` → `TASK_WEIGHTS`. Ví dụ muốn VIDEO_STREAMING ưu tiên năng lượng hơn:
```python
TaskState.VIDEO_STREAMING: {
    "w_energy": 0.7,  # Tăng từ 0.4 → 0.7
    "w_qos": 0.3      # Giảm từ 0.6 → 0.3
}
```

### Q6: Làm sao debug khi API lỗi?
**A:**
1. Kiểm tra terminal chạy uvicorn → có lỗi Python không?
2. Mở browser console (F12) → có lỗi JavaScript không?
3. Mở Swagger UI: http://localhost:8000/docs → test API trực tiếp
4. Dùng `print()` hoặc `logging` trong code Python

### Q7: Client-side approximation vs Backend physics khác gì?
**A:**
- **Client-side** (`updateNetworksForPosition()`):
  - Tính gần đúng khi click vào map
  - Không có shadowing, không có noise
  - Chỉ dùng để **preview nhanh**
- **Backend** (`NetworkPhysics.calculate_qos()`):
  - Tính CHÍNH XÁC với đầy đủ công thức
  - Có random shadowing, noise floor
  - Dùng cho **simulation step** và **decision making**

### Q8: Tại sao click vào map không gọi API?
**A:**
- Performance: Gọi API mỗi click = slow
- UX: User muốn move nhanh
- Giải pháp: Client approximation + backend verify khi step/decision

### Q9: Available networks list hiện 3 mạng "5G" là sao?
**A:** 
- **Đúng rồi!** Nếu device ở giữa 3 trạm 5G, cả 3 đều available
- Mỗi trạm có ID riêng: 5G-1, 5G-2, 5G-3
- Decision algorithm sẽ chọn 1 trong 3 dựa trên cost

### Q10: MVP này đã đủ để tích hợp ML chưa?
**A:** **ĐỦ RỒI!** ✅
- ✅ Physics-based QoS: RSSI, SNR, BW, Latency, PLR
- ✅ MCDM baseline: Có labels từ cost function
- ✅ Station IDs: Features distinguishable
- ✅ Simulation engine: Có thể generate 1000+ samples
- ✅ API ready: Endpoints cho training data collection

**Chỉ cần thêm:**
- DataCollector module (1 file)
- Training script (1 file)
- ML inference endpoint (1 file)

---

## 🚀 ROADMAP TÍCH HỢP ML (Coming Soon)

### Phase 1: Data Collection (1-2 ngày)
```python
# app/services/data_collector.py
class DataCollector:
    def collect_sample(device_state, decision_result):
        """Thu thập features + label"""
        
    def save_dataset(filename="training_data.csv"):
        """Export dataset cho training"""
```

**Features sẽ thu thập:**
- Position (x, y)
- Task type (encoded)
- Network metrics: rssi, snr, bandwidth, latency, plr
- Distance to stations
- Energy costs
- **Label:** optimal_network (từ MCDM)

### Phase 2: Model Training (1 ngày)
```python
# app/ml/train_model.py
from sklearn.ensemble import RandomForestClassifier

def train_rf_model(data_path):
    # Load dataset
    # Feature engineering
    # Train/test split
    # Train Random Forest
    # Save model: models/rf_network_selector.pkl
```

### Phase 3: Inference Integration (1 ngày)
```python
# app/core/ml_decision.py
class MLDecisionMaker:
    def predict(device_state, available_networks):
        """Dự đoán network bằng ML model"""
```

**New API endpoint:**
```
POST /decision/ml  ← ML-based decision
POST /decision     ← MCDM baseline (giữ lại để so sánh)
```

### Phase 4: A/B Comparison
```python
@app.post("/decision/compare")
def compare_algorithms():
    """So sánh MCDM vs ML"""
    return {
        "mcdm": {...},
        "ml": {...},
        "winner": "ml",
        "energy_saved": "12%"
    }
```

**Metrics so sánh:**
- Energy consumption
- QoS satisfaction
- Decision latency
- Accuracy

---

**📌 Note:** Hệ thống hiện có **2 decision modes:**
1. **MCDM Baseline** - Rule-based, explainable
2. **ML (Random Forest)** - Data-driven, 99.5% accuracy

Cả hai đều có thể sử dụng song song để so sánh performance!