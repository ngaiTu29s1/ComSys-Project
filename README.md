# 🚀 IoT Network Selection System
**Intelligent Network Selection for Multi-Homed IoT Devices using Machine Learning**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![ML Accuracy](https://img.shields.io/badge/ML%20Accuracy-99.5%25-brightgreen.svg)](docs/RESEARCH_REPORT.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Mô hình Lựa chọn Mạng Tiết kiệm Năng lượng dựa trên Trạng thái Tác vụ cho Thiết bị IoT** - Một hệ thống mô phỏng giáo dục kết hợp **vật lý viễn thông** và **học máy** để giải quyết bài toán tối ưu hóa mạng không đồng nhất (Heterogeneous Networks).

---

## 📋 Tổng quan

Hệ thống này **MÔ PHỎNG** một thiết bị IoT di động hoạt động trong môi trường mạng đa kết nối (Wi-Fi, 5G, BLE), sử dụng **mô hình vật lý chính xác** để tính toán QoS và ra quyết định lựa chọn mạng **TỨC THỜI** (reactive) nhằm **TỐI THIỂU HÓA NĂNG LƯỢNG** trong khi vẫn đảm bảo chất lượng dịch vụ.

### 🎯 Mục tiêu
- **Mô phỏng chính xác:** Sử dụng mô hình Log-Distance Path Loss + Shannon-Hartley để tính toán QoS thực tế
- **Tối ưu năng lượng:** Tiết kiệm ~40% năng lượng so với thuật toán Max-RSSI truyền thống
- **Ra quyết định thông minh:** Kết hợp MCDM (Multi-Criteria Decision Making) và Random Forest (99.5% accuracy)
- **Nhận biết ngữ cảnh:** Thích ứng trọng số dựa trên trạng thái tác vụ hiện tại

### ⚡ Đặc điểm nổi bật

#### **1. Mô hình Vật lý Chính xác**
```python
# Log-Distance Path Loss với Shadowing
PL(d) = PL(d₀) + 10·n·log₁₀(d/d₀) + Xσ

# Shannon-Hartley Capacity
R = B·log₂(1 + 10^(SNR/10))·η

# Packet Loss Rate (Sigmoid Model)
PLR = 1 / (1 + exp(k·(SNR - SNRthreshold)))
```

#### **2. Ba Trạng thái Tác vụ (Context-Aware)**
| Trạng thái | w_energy | w_qos | Yêu cầu | Ứng dụng |
|-----------|----------|--------|---------|----------|
| `IDLE_MONITORING` | 0.8 | 0.2 | 0.1 Mbps, 1000ms | Sensor định kỳ |
| `DATA_BURST_ALERT` | 0.3 | 0.7 | 5 Mbps, 100ms | Alert khẩn cấp |
| `VIDEO_STREAMING` | 0.4 | 0.6 | 10 Mbps, 200ms | Video real-time |

#### **3. Kiến trúc Lai ghép (Hybrid Architecture)**
```
┌──────────────┐     Labels      ┌──────────────┐
│ MCDM Baseline│ ──────────────> │   Training   │
│  (Expert)    │                 │     Data     │
└──────────────┘                 └──────┬───────┘
                                        │
                                        ▼
                                 ┌──────────────┐
                                 │ Random Forest│
                                 │  (99.5% acc) │
                                 └──────────────┘
```

#### **4. Cấu hình Mạng Mặc định**
| Network Type | Energy TX | Energy Idle | Base Latency | Bandwidth | TX Power |
|--------------|-----------|-------------|--------------|-----------|----------|
| **Wi-Fi**    | 0.5 mJ/KB | 10.0 mW     | 5 ms         | 20 MHz    | 20 dBm   |
| **5G**       | 1.2 mJ/KB | 15.0 mW     | 10 ms        | 100 MHz   | 43 dBm   |
| **BLE**      | 0.1 mJ/KB | 2.0 mW      | 20 ms        | 2 MHz     | 0 dBm    |

---

## 🛠️ Tech Stack

### Backend & ML
- **Python 3.11+** - Language core
- **FastAPI** - REST API framework
- **Pydantic** - Data validation
- **Scikit-learn** - Random Forest model
- **Pandas/NumPy** - Data processing
- **Joblib** - Model serialization

### Frontend
- **HTML5 Canvas** - Map visualization
- **Chart.js** - Real-time charts
- **Vanilla JavaScript** - No framework bloat

### DevOps
- **Conda** - Environment management
- **Pytest** - Unit testing
- **Uvicorn** - ASGI server

---

## 📁 Cấu trúc Dự án

```
📦 CommunicationSystem/
│
├── 📄 README.md                     ← Bạn đang ở đây
├── 📄 environment.yml               ← Conda environment dependencies
│
├── 📁 app/                          ← Backend Python Application
│   ├── 📄 main.py                   ← FastAPI server chính (592 lines)
│   │
│   ├── 📁 models/                   ← Pydantic Data Models
│   │   └── 📄 schemas.py            ← DeviceState, NetworkState, TaskState
│   │
│   ├── 📁 core/                     ← Core Business Logic
│   │   └── 📄 decision_logic.py     ← MCDM cost calculation baseline
│   │
│   ├── 📁 services/                 ← Backend Services
│   │   ├── 📄 simulation.py         ← Simulation engine (12 base stations)
│   │   └── 📄 network_physics.py    ← Physics-based QoS calculation
│   │
│   └── 📁 ml/                       ← Machine Learning Module
│       ├── 📄 train_model.py        ← Random Forest training logic
│       ├── 📄 predictor.py          ← ML inference (singleton pattern)
│       ├── 📄 data_collector.py     ← Training data extraction
│       └── 📄 feature_engineering.py ← Feature preprocessing
│
├── 📁 web/                          ← Frontend UI
│   ├── 📄 index.html                ← Dark-themed map visualization
│   └── 📄 map-visualization.js      ← Canvas rendering + Chart.js
│
├── 📁 docs/                         ← Documentation Hub
│   ├── 📄 CODE_GUIDE.md             ← Chi tiết cấu trúc code (2141 lines)
│   ├── 📄 RESEARCH_REPORT.md        ← Báo cáo khoa học (toán học)
│   ├── 📄 POSTMAN_GUIDE.md          ← Hướng dẫn test API
│   └── 📄 IoT-Network-Selection.postman_collection.json
│
├── 📁 data/                         ← Training & Results
│   ├── 📁 raw/
│   │   └── 📄 training_data.csv     ← Labeled dataset (MCDM output)
│   └── 📁 processed/
│
├── 📁 models/                       ← Trained Models
│   └── 📄 rf_network_selector.pkl   ← Random Forest (99.5% accuracy)
│
├── 📁 scripts/                      ← Utility Scripts
│   ├── 📄 collect_training_data.py  ← Generate training data
│   ├── 📄 train_model.py            ← Train Random Forest
│   └── 📄 test_predictor_standalone.py
│
├── 📁 tests/                        ← Unit Tests (Pytest)
│   ├── 📄 test_api.py
│   ├── 📄 test_decision_logic.py
│   └── 📄 test_ml_inference.py
│
└── 📁 demo_*.py                     ← Demo Scripts
    ├── 📄 demo_main_api.py          ← API endpoints demo
    ├── 📄 demo_simulation.py        ← Simulation engine demo
    ├── 📄 demo_system.py            ← MCDM algorithm demo
    └── 📄 demo_web_ui.py            ← Launch web UI
```

---

## 🚀 Quick Start

### 1️⃣ Cài đặt Môi trường

```bash
# Clone repository
git clone https://github.com/ngaiTu29s1/ComSys-Project.git
cd CommunicationSystem

# Tạo Conda environment
conda env create -f environment.yml

# Kích hoạt environment
conda activate comsys-project
```

### 2️⃣ Train Model (Tùy chọn)

```bash
# Tạo training data từ simulation
python scripts/collect_training_data.py

# Train Random Forest model
python scripts/train_model.py

# ✅ Model được lưu tại: models/rf_network_selector.pkl
```

### 3️⃣ Chạy API Server

```bash
# Khởi động FastAPI server
uvicorn app.main:app --reload --port 8000

# 🌐 API Docs: http://localhost:8000/docs
# 🗺️ Web UI: http://localhost:8000/ui
```

### 4️⃣ Test hệ thống

```bash
# Chạy unit tests
pytest tests/ -v

# Test API endpoint
python demo_main_api.py

# Chạy simulation demo
python demo_simulation.py
```

---

## 🎮 Cách sử dụng

### API Endpoints Chính

#### **1. Simulation Step** - Chạy một bước mô phỏng
```http
POST http://localhost:8000/simulation/step
Content-Type: application/json

{
  "task": "IDLE_MONITORING",
  "move_device": true,
  "selected_network": "WiFi-1"
}
```

**Response:**
```json
{
  "simulation_step": 42,
  "device_state": {
    "position": [345.2, 678.9],
    "current_task": "IDLE_MONITORING",
    "available_networks": [
      {
        "name": "Wi-Fi",
        "station_id": "WiFi-1",
        "rssi": -55.3,
        "snr": 25.7,
        "bandwidth": 18.5,
        "latency": 8.2,
        "packet_loss_rate": 0.002,
        "is_available": true
      }
    ]
  }
}
```

#### **2. MCDM Decision** - Lựa chọn mạng bằng thuật toán baseline
```http
POST http://localhost:8000/decision
```

**Response:**
```json
{
  "selected_network": "WiFi-1",
  "cost": 12.45,
  "all_network_costs": {
    "WiFi-1": 12.45,
    "5G-2": 28.90,
    "BLE-3": 15.67
  }
}
```

#### **3. ML Prediction** - Lựa chọn mạng bằng Random Forest
```http
POST http://localhost:8000/decision/ml
```

**Response:**
```json
{
  "selected_network": "WiFi-1",
  "confidence": 0.956,
  "probabilities": {
    "Wi-Fi": 0.956,
    "5G": 0.032,
    "BLE": 0.012
  },
  "all_network_costs": {
    "WiFi-1": 12.45,
    "5G-2": 28.90,
    "BLE-3": 15.67
  }
}
```

### Web UI Features

- 🗺️ **Map Visualization:** Hiển thị vị trí device + 12 base stations
- 📊 **Real-time Charts:** Energy consumption, QoS metrics theo thời gian
- 🔄 **Mode Switching:** Toggle giữa MCDM và ML mode
- 📈 **Metrics Table:** RSSI, SNR, Bandwidth, Latency, PLR, Cost
- 🎯 **Confidence Display:** Confidence % cho AI predictions

---

## 📊 Feature Vector & Labels

### Input Features (18 chiều)
```python
[
  # Device Context (3 features)
  device_pos_x,      # Tọa độ X thiết bị
  device_pos_y,      # Tọa độ Y thiết bị
  task_encoded,      # 0=IDLE, 1=ALERT, 2=VIDEO
  
  # Wi-Fi Metrics (5 features)
  wifi_rssi, wifi_snr, wifi_bandwidth, wifi_latency, wifi_distance,
  
  # 5G Metrics (5 features)
  5g_rssi, 5g_snr, 5g_bandwidth, 5g_latency, 5g_distance,
  
  # BLE Metrics (5 features)
  ble_rssi, ble_snr, ble_bandwidth, ble_latency, ble_distance
]

# Mạng không khả dụng: RSSI=-999, SNR=-999, BW=0, Lat=9999, Dist=9999
```

### Output Labels (3 classes)
```python
{
  0: 'Wi-Fi',  # Labeled by MCDM baseline
  1: '5G',
  2: 'BLE'
}
```

---

## 🔬 Kết quả Nghiên cứu

### Model Performance
- **Accuracy:** 99.5% trên test set
- **Feature Importance:** `Task Type` (38%) > `Distance` (24%) > `SNR` (18%)
- **Training Time:** ~2 seconds trên 10,000 samples
- **Inference Time:** <1ms per prediction

### Energy Savings
- **vs Max-RSSI:** ~40% tiết kiệm năng lượng
- **vs Random:** ~65% tiết kiệm năng lượng
- **QoS Violation Rate:** <1% (tương đương Max-RSSI)

> Xem chi tiết trong [`docs/RESEARCH_REPORT.md`](docs/RESEARCH_REPORT.md)

---

## 📚 Tài liệu Chi tiết

| Document | Description |
|----------|-------------|
| [`CODE_GUIDE.md`](docs/CODE_GUIDE.md) | Giải thích chi tiết từng module (2141 lines) |
| [`RESEARCH_REPORT.md`](docs/RESEARCH_REPORT.md) | Báo cáo khoa học với công thức toán học |
| [`POSTMAN_GUIDE.md`](docs/POSTMAN_GUIDE.md) | Hướng dẫn test API với Postman |
| `congthuc.md` | Chi tiết các công thức vật lý |
| `CODEBASE_BREAKDOWN_VI.md` | Tổng quan codebase (Vietnamese) |

---

## 🧪 Testing

```bash
# Chạy tất cả tests
pytest tests/ -v

# Test một module cụ thể
pytest tests/test_decision_logic.py -v

# Test với coverage report
pytest tests/ --cov=app --cov-report=html
```

**Test Coverage:**
- ✅ Decision Logic: 95%
- ✅ Network Physics: 92%
- ✅ ML Inference: 88%
- ✅ API Endpoints: 85%

---

## 🎓 Ứng dụng Giáo dục

Hệ thống này được thiết kế cho mục đích **GIÁO DỤC** và phù hợp với:

- **Sinh viên Viễn thông:** Hiểu mô hình kênh truyền, QoS metrics, handover
- **Sinh viên AI/ML:** Học supervised learning, feature engineering, model deployment
- **Sinh viên Backend:** Nghiên cứu FastAPI, REST API design, async programming
- **Nghiên cứu IoT:** Benchmark cho thuật toán network selection mới

### Hạn chế và Giả định
⚠️ **Đây là HỆ THỐNG MÔ PHỎNG**, không phải production system:
- Giả định thiết bị **LUÔN** trong vùng phủ sóng ít nhất 1 mạng
- Không xử lý "ngắt session" hay "packet retransmission" chi tiết
- Energy model đơn giản hóa (TX energy không phụ thuộc khoảng cách)
- Tập trung vào **MỘT THIẾT BỊ** duy nhất

---

## 🤝 Contributing

Contributions are welcome! Đặc biệt các cải tiến về:
- 🔋 Mô hình năng lượng chi tiết hơn (distance-dependent TX energy)
- 🌐 Handover scenarios (session continuity)
- 📡 Thêm loại mạng mới (LoRa, LTE-M, NB-IoT)
- 🧠 Thuật toán ML nâng cao (Deep RL, Transfer Learning)

```bash
# Fork repository -> Create branch -> Commit -> Push -> Pull Request
git checkout -b feature/your-feature-name
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Author:** Tuan Tu Tran 
**Email:** [trantuantu2004@gmail.com]  
**GitHub:** [@ngaiTu29s1](https://github.com/ngaiTu29s1)

---

## 🙏 Acknowledgments

Công trình này sử dụng các tài liệu tham khảo:
- **T. S. Rappaport** - *Wireless Communications: Principles and Practice* (Path Loss Model)
- **C. E. Shannon** - *A Mathematical Theory of Communication* (Shannon-Hartley)
- **K. Piamrat et al.** - *QoE-aware Vertical Handover* (Energy Model)

---

⭐ **Nếu dự án này hữu ích cho nghiên cứu của bạn, hãy star repo để ủng hộ!** ⭐