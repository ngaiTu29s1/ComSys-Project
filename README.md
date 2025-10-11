# IoT Network Selection System 🚀

This project simulates an IoT device operating within the coverage of multiple networks (Wi-Fi, 5G, BLE, etc.). The system uses a Multi-Criteria Decision Making (MCDM) algorithm to select the most energy-efficient network based on the current task state.

---

## 📋 Overview

The system is designed to:
- **Simulate**: An IoT device moving in a 1000x1000 space with 12 base stations.
- **Optimize**: Minimize energy consumption while maintaining Quality of Service (QoS).
- **React**: Make real-time decisions without forecasting.

### Key Features
- **Task States**:
  - `IDLE_MONITORING`: Prioritizes energy saving.
  - `DATA_BURST_ALERT`: Balances energy and QoS.
  - `VIDEO_STREAMING`: Prioritizes QoS.
- **MCDM Algorithm**:
  ```
  Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty
  ```
- **AI Integration**: Random Forest model trained on labeled data from the MCDM algorithm.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI.
- **AI/ML**: Scikit-learn, Pandas.
- **Simulation**: Custom engine using NumPy.
- **Frontend**: HTML, JavaScript (Canvas API, Chart.js).
- **Environment**: Conda for dependency management.

---

## 📁 Project Structure

```
📦 ComSys-Project/
├── 📄 README.md                 ← Project overview
├── 🐍 environment.yml           ← Conda environment setup
├── 📁 app/                      ← Backend application (FastAPI)
│   ├── 📄 main.py              ← API endpoints
│   ├── 📁 models/              ← Data models
│   ├── 📁 core/                ← Core logic (MCDM algorithm)
│   └── 📁 services/            ← Simulation engine
├── 📁 docs/                     ← Documentation
│   ├── 📄 CODE_GUIDE.md        ← Code structure and details
│   ├── 📄 POSTMAN_GUIDE.md     ← Postman API testing guide
│   └── 📄 IoT-Network-Selection.postman_collection.json
├── 📁 web/                      ← Frontend UI
│   ├── 📄 index.html           ← Map visualization UI
│   └── 📄 map-visualization.js ← JavaScript logic for UI
├── 📁 tests/                    ← Unit tests
├── 📄 demo_*.py                 ← Demo scripts
```

---

## 📚 Documentation

- **Code Guide**: [docs/CODE_GUIDE.md](docs/CODE_GUIDE.md).
- **Postman Guide**: [docs/POSTMAN_GUIDE.md](docs/POSTMAN_GUIDE.md).
- **API Collection**: Import `docs/IoT-Network-Selection.postman_collection.json` into Postman for API testing.

---

⭐ **Star this repo** if you find it useful for IoT network optimization research!