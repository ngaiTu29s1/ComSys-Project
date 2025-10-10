# IoT Network Selection System 🚀

Hệ thống lựa chọn mạng tiết kiệm năng lượng dựa trên trạng thái tác vụ cho thiết bị IoT sử dụng thuật toán Multi-Criteria Decision Making (MCDM).

## 📋 Tổng quan

Đây là một hệ thống **MÔ PHỎNG** một thiết bị IoT trong vùng phủ sóng của nhiều mạng (Wi-Fi, 5G, BLE...). Mô hình AI sẽ ra quyết định chọn mạng nào để **TỐI THIỂU HÓA NĂNG LƯỢNG TIÊU THỤ**, dựa trên trạng thái tác vụ hiện tại.

### ⚡ Ý tưởng chính
- **Mô phỏng**: Thiết bị IoT di chuyển trong không gian 1000x1000 với 12 base stations
- **MCDM Algorithm**: `Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty`
- **AI Decision**: Random Forest học từ dữ liệu được gán nhãn bởi thuật toán cơ sở
- **Reactive System**: Quyết định tức thời, không dự báo

### 🎯 Trạng thái tác vụ IoT
- `IDLE_MONITORING`: Giám sát nhàn rỗi (ưu tiên tiết kiệm năng lượng)
- `DATA_BURST_ALERT`: Cảnh báo burst data (cân bằng năng lượng/QoS)
- `VIDEO_STREAMING`: Streaming video (ưu tiên QoS)

## 🛠️ Tech Stack

- **Backend & AI**: Python 3.11+, FastAPI, Scikit-learn, Pandas
- **Data Models**: Pydantic V2 với validation
- **Simulation**: Custom engine với numpy
- **API**: REST API với OpenAPI documentation
- **Environment**: Conda environment management

## 📁 Cấu trúc Project

```
📦 ComSys-Project/
├── 📄 README.md                 ← Tài liệu này
├── 🐍 environment.yml           ← Conda environment
├── 📁 app/                      ← Main application (FastAPI)
│   ├── 📄 main.py              ← API endpoints
│   ├── 📁 models/
│   │   └── 📄 schemas.py       ← Pydantic data models
│   ├── 📁 core/
│   │   └── 📄 decision_logic.py ← MCDM algorithm
│   └── 📁 services/
│       └── 📄 simulation.py     ← Simulation engine
├── 📁 docs/                     ← Documentation & Postman
│   └── 📄 IoT-Network-Selection.postman_collection.json
├── 📁 demo_*.py                 ← Demo scripts
└── 📁 tests/                    ← Unit tests
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Tạo và activate conda environment
conda env create -f environment.yml
conda activate comsys-project

# Hoặc dùng pip
pip install fastapi uvicorn pydantic pandas numpy scikit-learn
```

### 2. Chạy FastAPI Server
```bash
# Development server với auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 4. Demo Scripts
```bash
# Demo thuật toán MCDM cơ bản
python demo_system.py

# Demo simulation engine
python demo_simulation.py

# Demo FastAPI endpoints
python demo_main_api.py
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint với thông tin hệ thống |
| `GET` | `/health` | Health check |
| `GET` | `/status` | Trạng thái tổng quát hệ thống |
| `POST` | `/simulation/step` | Chạy một bước mô phỏng |
| `POST` | `/decision` | Thực hiện quyết định chọn mạng |
| `POST` | `/simulation/step-with-decision` | Tích hợp simulation + decision |
| `POST` | `/simulation/reset` | Reset simulation về vị trí mới |
| `GET` | `/simulation/current-state` | Lấy trạng thái hiện tại |

## 🧪 Testing với Postman

Import collection từ `docs/IoT-Network-Selection.postman_collection.json` để test tất cả endpoints với sample data.

### Workflow Testing
1. **Health Check**: Kiểm tra API hoạt động
2. **Get Status**: Xem trạng thái hệ thống
3. **Simulation Step**: Chạy mô phỏng di chuyển thiết bị
4. **Make Decision**: Test thuật toán MCDM với dữ liệu custom
5. **Integrated Flow**: Test workflow đầy đủ

## 🔬 Core Algorithm - MCDM

### Cost Function
```python
Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty

Where:
- Energy_Cost = energy_tx * data_size + energy_idle * time + energy_wakeup
- QoS_Penalty = penalty if (bandwidth < min_bw OR latency > max_latency)
- Weights vary by TaskState (energy vs QoS priority)
```

### Task Weights
```python
TASK_WEIGHTS = {
    TaskState.IDLE_MONITORING: {"w_energy": 0.8, "w_qos": 0.2},     # Ưu tiên năng lượng
    TaskState.DATA_BURST_ALERT: {"w_energy": 0.6, "w_qos": 0.4},    # Cân bằng
    TaskState.VIDEO_STREAMING: {"w_energy": 0.3, "w_qos": 0.7}      # Ưu tiên QoS
}
```

### QoS Requirements
```python
QOS_REQUIREMENTS = {
    TaskState.IDLE_MONITORING: {"min_bandwidth": 0.1, "max_latency": 1000},
    TaskState.DATA_BURST_ALERT: {"min_bandwidth": 5.0, "max_latency": 100},  
    TaskState.VIDEO_STREAMING: {"min_bandwidth": 25.0, "max_latency": 50}
}
```

## 🎮 Demo Scenarios

### 1. Office Environment
- **Networks**: Wi-Fi, 5G, Ethernet
- **Result**: Wi-Fi cho IDLE, Ethernet cho VIDEO

### 2. Mobile Environment  
- **Networks**: 4G/5G với signal strength thay đổi
- **Result**: Adaptive selection theo chất lượng mạng

### 3. IoT Sensors
- **Networks**: BLE, LoRa (ultra low power)
- **Result**: BLE/LoRa cho IDLE, Wi-Fi cho high QoS tasks

## 📈 Performance Metrics

Từ `demo_main_api.py`:
- **Simulation Step**: ~2.3ms
- **Decision Making**: ~2.5ms  
- **API Throughput**: ~207 requests/second
- **Memory Usage**: < 50MB

## 🔧 Development

### Code Structure
- **Models** (`schemas.py`): Pydantic data validation
- **Core Logic** (`decision_logic.py`): MCDM implementation
- **Services** (`simulation.py`): IoT simulation engine
- **API** (`main.py`): FastAPI endpoints

### Testing
```bash
# Chạy unit tests
python -m pytest tests/ -v

# Test specific module
python tests/test_decision_logic.py
python tests/test_simulation.py
```

### Code Quality
- **Type Hints**: Full type annotation với Python 3.11+
- **Documentation**: Comprehensive docstrings
- **Validation**: Pydantic models với field validation
- **Error Handling**: Proper HTTP exceptions

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use production ASGI server (Gunicorn + Uvicorn workers)
- Add authentication/authorization
- Implement rate limiting
- Add monitoring/logging
- Database integration for persistent storage

## 📚 Research Context

Đây là project nghiên cứu về **Energy-Efficient Network Selection** cho IoT systems, focusing on:

- **Multi-Criteria Decision Making (MCDM)** trong telecommunications
- **Machine Learning** cho network optimization
- **IoT Energy Management** strategies
- **QoS vs Energy Trade-offs** analysis

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Submit Pull Request

## 📄 License

This project is for research and educational purposes.

## 👥 Team

- **Research Focus**: IoT Communication Systems
- **Algorithm**: Multi-Criteria Decision Making (MCDM)
- **Implementation**: Python FastAPI + ML Stack

---

⭐ **Star this repo** if you find it useful for IoT network optimization research!