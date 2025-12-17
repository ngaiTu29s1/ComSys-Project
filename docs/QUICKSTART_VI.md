# 🚀 Hướng Dẫn Chạy Toàn Bộ Hệ Thống (Quick Start)

**Tài liệu này hướng dẫn chi tiết từng bước từ kích hoạt môi trường đến chạy đầy đủ hệ thống.**

---

## 📋 Mục lục

1. [Chuẩn bị môi trường](#chuẩn-bị-môi-trường)
2. [Khởi tạo dữ liệu](#khởi-tạo-dữ-liệu)
3. [Huấn luyện mô hình ML](#huấn-luyện-mô-hình-ml)
4. [Chạy API Backend](#chạy-api-backend)
5. [Chạy Simulation](#chạy-simulation)
6. [Chạy Web UI](#chạy-web-ui)
7. [Tạo biểu đồ chính sách](#tạo-biểu-đồ-chính-sách)
8. [Chạy Kiểm thử](#chạy-kiểm-thử)

---

## 🔧 Chuẩn bị môi trường

### Bước 1: Kích hoạt Conda Environment

```bash
conda env create -f environment.yml
```

**Ý nghĩa:**
- `conda env create`: Lệnh tạo môi trường conda mới
- `-f environment.yml`: Chỉ định file cấu hình (tên môi trường: `comsys-project`)
- **Kết quả:** Tạo môi trường Python 3.11 với tất cả dependencies:
  - NumPy, Pandas, SciPy (xử lý dữ liệu)
  - Scikit-learn (ML models)
  - FastAPI, Uvicorn (Backend API)
  - Matplotlib (Visualizations)
  - PyTest (Testing)

**Thời gian:** ~2-3 phút lần đầu

---

### Bước 2: Kích hoạt Môi trường

**Trên Windows (PowerShell):**
```bash
conda activate comsys-project
```

**Trên Linux/Mac (Bash):**
```bash
conda activate comsys-project
```

**Ý nghĩa:**
- Kích hoạt môi trường Python đã tạo
- Sau câu lệnh này, terminal sẽ hiển thị `(comsys-project)` ở đầu dòng
- Tất cả pip packages chỉ được cài trong môi trường này, không ảnh hưởng toàn cục

**Xác nhận:** Kiểm tra Python đúng:
```bash
python --version
```
Should output: `Python 3.11.x`

---

## 📊 Khởi tạo dữ liệu

### Bước 3: Thu thập dữ liệu huấn luyện

```bash
python scripts/collect_training_data.py
```

**Ý nghĩa:**
- Tạo bộ dữ liệu huấn luyện từ simulation
- Chạy các scenario khác nhau (IDLE, DATA_BURST, VIDEO_STREAMING)
- Ghi nhãn dữ liệu bằng thuật toán MCDM (Multi-Criteria Decision Making)
- **Input:** Không cần (dùng constants từ `app/core/constants.py`)
- **Output:** `data/raw/training_data.csv` (~5000 samples)
- **Thời gian:** ~30-60 giây

**Chi tiết quá trình:**
1. Khởi tạo simulation với 100+ thiết bị IoT ảo
2. Chuyển động thiết bị (hotspot-based positioning)
3. Tính toán chi phí MCDM cho từng trạng thái mạng
4. Chọn mạng tối ưu theo thuật toán gốc
5. Lưu features + labels vào CSV

---

## 🤖 Huấn luyện mô hình ML

### Bước 4: Huấn luyện Random Forest

```bash
python -m app.ml.train_model --data data/raw/training_data.csv --model models/rf_network_selector.pkl
```

**Ý nghĩa từng phần:**
- `python -m app.ml.train_model`: Chạy module `train_model.py` như package Python
  - `-m` = chạy module (thay vì script)
  - Đúng cách để import các module từ `app/` package
  
- `--data data/raw/training_data.csv`: Chỉ định file dữ liệu
  - Input: CSV từ bước 3 (training_data.csv)
  - Cột: `network_type`, `task_state`, `bandwidth`, `latency`, v.v.
  - Labels: `optimal_network` (Wi-Fi, 5G, hay BLE)

- `--model models/rf_network_selector.pkl`: Nơi lưu mô hình
  - Output: `models/rf_network_selector.pkl` (mô hình đã train)
  - Output: `models/rf_network_selector_feature_engineer.pkl` (feature encoder)
  - Output: `confusion_matrix.png` (hiệu suất mô hình)
  - Output: `feature_importance.png` (độ quan trọng của features)

**Thời gian:** ~10-20 giây

**Các bước bên trong:**
1. Load CSV training data
2. Feature engineering (encode task_state, network_type)
3. Train/test split (80/20)
4. Train Random Forest (100 trees)
5. Tính confusion matrix, accuracy
6. Lưu mô hình (pickle format)
7. Vẽ biểu đồ confusion matrix & feature importance

**Verify kết quả:**
```bash
ls -la models/
```
Should show: `rf_network_selector.pkl`, `rf_network_selector_feature_engineer.pkl`

---

## 🌐 Chạy API Backend

### Bước 5: Khởi động Server FastAPI

```bash
python app/main.py
```

**Ý nghĩa:**
- Khởi động server FastAPI trên `http://localhost:8000`
- **Port:** 8000 (mặc định FastAPI)
- **Host:** 127.0.0.1 (localhost)
- **Workers:** 1 (dev mode)
- **Auto-reload:** Có (dev mode)

**Quá trình:**
1. Import FastAPI app từ `app/main.py`
2. Load mô hình ML: `models/rf_network_selector.pkl`
3. Khởi động Uvicorn server
4. Lắng nghe requests trên port 8000

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Endpoints có sẵn:**

| Method | Endpoint | Mục đích |
|--------|----------|---------|
| POST | `/v1/network-selection` | Dự đoán mạng tối ưu |
| POST | `/v1/decision-logic` | Chạy thuật toán MCDM |
| GET | `/health` | Kiểm tra server |

**Ví dụ request:**
```bash
curl -X POST http://localhost:8000/v1/network-selection \
  -H "Content-Type: application/json" \
  -d '{
    "current_task": "VIDEO_STREAMING",
    "available_networks": ["WIFI", "FIVEG"],
    "network_states": [
      {"network": "WIFI", "bandwidth": 85.3, "latency": 15},
      {"network": "FIVEG", "bandwidth": 500, "latency": 20}
    ]
  }'
```

**Để dừng server:** `Ctrl+C` hoặc `Cmd+C`

---

## 🎲 Chạy Simulation

### Bước 6: Chạy Simulation CLI

**Cửa sổ terminal mới** (giữ API đang chạy):

```bash
python demo_simulation.py --duration 3600 --num-devices 10
```

**Ý nghĩa từng phần:**
- `python demo_simulation.py`: Chạy script simulation
- `--duration 3600`: Thời gian simulation = 3600 giây (1 giờ)
  - Càng dài càng nhiều scenarios được test
  - Mặc định: 3600s nếu không chỉ định
  
- `--num-devices 10`: Số thiết bị IoT ảo
  - Mỗi device chuyển động, thay đổi mạng
  - Simulation lặp cho mỗi device
  - Mặc định: 10 devices

**Quá trình simulation:**
1. Khởi tạo 10 thiết bị IoT (mỗi device 1 vị trí)
2. Tạo bản đồ với 3 Wi-Fi hotspots và 1 trạm 5G
3. Vòng lặp simulation (3600 giây):
   - Mỗi 100ms: Cập nhật vị trí device (hotspot-based)
   - Kiểm tra mạng khả dụng (dựa vào tín hiệu & khoảng cách)
   - Chạy thuật toán MCDM → chọn mạng
   - Ghi metrics: energy, latency, QoS
4. Xuất kết quả (terminal hoặc file log)

**Output:**
```
[Device 0] Time: 100s, Task: VIDEO_STREAMING, Network: WIFI, Energy: 21.4 mJ
[Device 1] Time: 200s, Task: IDLE_MONITORING, Network: BLE, Energy: 1.2 mJ
...
[Summary] Total simulations: 1000, Energy saved by AI: 15%
```

**Để dừng:** `Ctrl+C`

---

## 🎨 Tạo biểu đồ chính sách

### Bước 7: Sinh biểu đồ so sánh chiến lược

**Cửa sổ terminal khác:**

```bash
python scripts/generate_policy_charts.py
```

**Ý nghĩa:**
- So sánh 3 chiến lược chọn mạng:
  1. **Max-RSSI:** Chọn mạng có tín hiệu mạnh nhất (đơn giản, tốn năng lượng)
  2. **MCDM AI:** Thuật toán đề xuất (tối ưu hóa năng lượng + QoS)
  3. **Random:** Chọn ngẫu nhiên (baseline)

- Tạo 3 biểu đồ:
  1. `policy_energy.png` - So sánh năng lượng tiêu thụ
     - Trục Y: Năng lượng (mJ)
     - Trục X: Task state (IDLE, DATA_BURST, VIDEO_STREAMING)
     - **Mục đích:** Chứng minh AI tiết kiệm năng lượng

  2. `policy_qos_penalty.png` - So sánh QoS penalty
     - Trục Y: Penalty (0-1, thấp tốt)
     - Trục X: Task state
     - **Mục đích:** Chứng minh AI không hy sinh QoS

  3. `policy_total_cost.png` - So sánh tổng chi phí MCDM
     - Trục Y: Chi phí tổng (năng lượng + QoS penalty)
     - Trục X: Task state
     - **Mục đích:** Chứng minh MCDM tối ưu tổng thể

**Quá trình:**
1. Load constants (network params, QoS requirements)
2. Chạy 1000 scenarios cho mỗi task state
3. Tính metrics cho 3 chiến lược
4. Vẽ biểu đồ bar chart (Matplotlib)
5. Lưu vào `models/` folder

**Output:**
```
✅ Generated: models/policy_energy.png
✅ Generated: models/policy_qos_penalty.png
✅ Generated: models/policy_total_cost.png
```

**Verify:**
```bash
ls -la models/policy_*.png
```

---

## 🧪 Chạy Kiểm thử (Optional)

### Bước 8: Chạy Unit Tests

```bash
pytest tests/ -v --tb=short
```

**Ý nghĩa từng phần:**
- `pytest tests/`: Chạy tất cả tests trong folder `tests/`
- `-v`: Verbose mode (hiển thị tên từng test)
- `--tb=short`: Traceback ngắn (dễ đọc)

**Các test chính:**

| File | Mục đích | Số tests |
|------|---------|----------|
| `test_decision_logic.py` | Kiểm tra tính toán chi phí MCDM | 5 |
| `test_simulation.py` | Kiểm tra simulation vật lý | 4 |
| `test_ml_inference.py` | Kiểm tra dự đoán ML | 3 |
| `test_schemas.py` | Kiểm tra Pydantic schemas | 2 |
| `test_api.py` | Kiểm tra FastAPI endpoints | 4 |

**Output:**
```
test_decision_logic.py::test_energy_calculation PASSED
test_decision_logic.py::test_qos_penalty PASSED
test_simulation.py::test_device_movement PASSED
test_ml_inference.py::test_model_prediction PASSED
... 
======================== 18 passed in 0.45s ========================
```

**Chạy test cụ thể:**
```bash
pytest tests/test_decision_logic.py::test_energy_calculation -v
```

---

## 🔄 Quy trình chạy hoàn chỉnh (từ đầu)

### Scenario 1: Lần đầu chạy (Full Pipeline)

```bash
# Terminal 1: Chuẩn bị môi trường
conda env create -f environment.yml
conda activate comsys-project

# Đợi khoảng 2-3 phút

# Terminal 1: Thu thập dữ liệu & train model
python scripts/collect_training_data.py
# Output: data/raw/training_data.csv (~1-2 phút)

python -m app.ml.train_model --data data/raw/training_data.csv --model models/rf_network_selector.pkl
# Output: models/rf_network_selector.pkl, confusion_matrix.png (~20 giây)

# Terminal 1: Chạy API
python app/main.py
# Output: INFO: Uvicorn running on http://127.0.0.1:8000

# Terminal 2: Mở terminal mới, kích hoạt môi trường
conda activate comsys-project

# Terminal 2: Chạy simulation
python demo_simulation.py --duration 3600 --num-devices 10
# Output: [Device X] Time: Ys, ...

# Terminal 3: Mở terminal mới, kích hoạt môi trường
conda activate comsys-project

# Terminal 3: Tạo biểu đồ
python scripts/generate_policy_charts.py
# Output: Generated 3 charts (policy_energy.png, v.v.)

# Terminal 3: Chạy tests (Optional)
pytest tests/ -v
# Output: 18 passed in 0.45s
```

**Tổng thời gian:** ~5-10 phút

---

### Scenario 2: Lần thứ 2 trở đi (Skip data collection)

```bash
# Terminal 1:
conda activate comsys-project
python app/main.py

# Terminal 2:
conda activate comsys-project
python demo_simulation.py --duration 3600 --num-devices 10

# Terminal 3:
conda activate comsys-project
python scripts/generate_policy_charts.py
```

**Thời gian:** ~1-2 phút

---

## 📈 Chạy dòng lệnh cho phát triển

### Debug mode: Xem chi tiết simulation

```bash
python demo_simulation.py --duration 600 --num-devices 2 --verbose
```

- `--verbose`: In log chi tiết mỗi quyết định mạng
- `--duration 600`: Chỉ 600 giây (10 phút) để debug nhanh

### Xây dựng mô hình từ đầu

```bash
# Xóa mô hình cũ
rm models/rf_network_selector.pkl models/rf_network_selector_feature_engineer.pkl

# Tạo dữ liệu mới
python scripts/collect_training_data.py

# Train lại
python -m app.ml.train_model --data data/raw/training_data.csv --model models/rf_network_selector.pkl
```

### Chạy API với multiple workers (Production)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

- `--workers 4`: Chạy 4 worker processes (xử lý 4 requests đồng thời)
- `--host 0.0.0.0`: Lắng nghe từ mọi IP (không chỉ localhost)

---

## ⚠️ Troubleshooting

### Lỗi: `ModuleNotFoundError: No module named 'app'`

**Nguyên nhân:** Python không tìm thấy package `app/`

**Giải pháp:**
```bash
# Chạy từ folder gốc (CommunicationSystem)
cd c:\Users\Tuan Tu Tran\Documents\code\CommunicationSystem

# Verify folder structure
ls app/
# Should show: __init__.py, main.py, core/, ml/, models/, services/
```

### Lỗi: `FileNotFoundError: data/raw/training_data.csv`

**Nguyên nhân:** Chưa chạy `collect_training_data.py`

**Giải pháp:**
```bash
python scripts/collect_training_data.py
```

### Lỗi: Port 8000 đã bị chiếm dụng

**Nguyên nhân:** API cũ vẫn chạy

**Giải pháp:**
```bash
# Tìm process chạy trên port 8000
lsof -i :8000  # (Mac/Linux)
netstat -ano | findstr :8000  # (Windows)

# Kill process đó
kill -9 <PID>  # (Mac/Linux)
taskkill /PID <PID> /F  # (Windows)

# Hoặc chọn port khác
python app/main.py --port 8001
```

### Lỗi: Memory không đủ khi train model

**Nguyên nhân:** Dữ liệu quá lớn

**Giải pháp:**
```bash
# Giảm số samples
python scripts/collect_training_data.py --max-samples 1000
```

---

## 📞 Xem thêm

- [CODE_GUIDE.md](CODE_GUIDE.md) - Chi tiết kỹ thuật
- [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) - API testing
- [RESEARCH_REPORT.md](RESEARCH_REPORT.md) - Báo cáo nghiên cứu
