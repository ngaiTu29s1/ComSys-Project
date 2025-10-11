# Code Guide for IoT Network Selection System

This document provides a detailed guide to understanding and navigating the codebase of the IoT Network Selection System. It is intended for collaborators and reviewers to quickly grasp the structure, logic, and functionality of the project.

---

## 📂 Project Structure

The project is organized into the following main directories:

```
📦 ComSys-Project/
├── 📁 app/                      ← Main application (FastAPI)
│   ├── 📄 main.py              ← API endpoints
│   ├── 📁 models/              ← Data models
│   │   └── 📄 schemas.py       ← Pydantic models for validation
│   ├── 📁 core/                ← Core logic
│   │   └── 📄 decision_logic.py ← MCDM algorithm implementation
│   └── 📁 services/            ← Simulation engine
│       └── 📄 simulation.py     ← IoT simulation logic
├── 📁 docs/                     ← Documentation
│   ├── 📄 CODE_GUIDE.md        ← This guide
│   ├── 📄 POSTMAN_GUIDE.md     ← Postman API testing guide
│   └── 📄 IoT-Network-Selection.postman_collection.json
├── 📁 web/                      ← Frontend UI
│   ├── 📄 index.html           ← Map visualization UI
│   └── 📄 map-visualization.js ← JavaScript logic for UI
├── 📁 tests/                    ← Unit tests
│   ├── 📄 test_decision_logic.py ← Tests for MCDM algorithm
│   ├── 📄 test_simulation.py    ← Tests for simulation engine
│   └── 📄 test_api.py           ← Tests for API endpoints
├── 📄 README.md                 ← Project overview
├── 🐍 environment.yml           ← Conda environment setup
└── 📄 demo_*.py                 ← Demo scripts
```

---

## 🛠️ Key Components

### 1. **Backend (FastAPI)**

#### `app/main.py`
- **Purpose**: Defines all API endpoints for simulation and decision-making.
- **Endpoints**:
  - `/simulation/step`: Runs a simulation step.
  - `/decision`: Executes the MCDM algorithm to select the best network.
  - `/simulation/reset`: Resets the simulation.
  - `/ui`: Serves the web-based map visualization.
- **Key Functions**:
  - `simulation_step()`: Calls the simulation engine to update device state.
  - `make_decision()`: Implements the MCDM algorithm.

#### `app/models/schemas.py`
- **Purpose**: Defines Pydantic models for data validation.
- **Key Models**:
  - `DeviceState`: Represents the current state of the IoT device.
  - `NetworkState`: Represents the state of a network (e.g., bandwidth, latency).
  - `TaskState`: Enum for IoT device tasks (`IDLE_MONITORING`, `DATA_BURST_ALERT`, `VIDEO_STREAMING`).

#### `app/core/decision_logic.py`
- **Purpose**: Implements the MCDM algorithm.
- **Key Functions**:
  - `calculate_cost()`: Computes the cost for a network based on energy and QoS.
  - `select_best_network()`: Selects the network with the lowest cost.
- **Algorithm**:
  ```python
  Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty
  ```

#### `app/services/simulation.py`
- **Purpose**: Simulates the movement and state of the IoT device.
- **Key Functions**:
  - `run_simulation_step()`: Updates the device's position and available networks.
  - `reset_simulation()`: Resets the simulation to a new position.

---

### 2. **Frontend (Web UI)**

#### `web/index.html`
- **Purpose**: Provides the user interface for map visualization.
- **Key Features**:
  - Displays the IoT device and base stations on a map.
  - Allows users to manually place the device.
  - Provides controls for simulation steps and decision-making.

#### `web/map-visualization.js`
- **Purpose**: Implements the logic for map visualization.
- **Key Functions**:
  - `handleCanvasClick()`: Updates the device's position based on mouse clicks.
  - `setupEventListeners()`: Sets up UI interactions (e.g., buttons, dropdowns).
  - `runSimulationStep()`: Calls the API to run a simulation step.
  - `makeDecision()`: Calls the API to execute the MCDM algorithm.

---

### 3. **Testing**

#### `tests/test_decision_logic.py`
- **Purpose**: Tests the MCDM algorithm.
- **Key Tests**:
  - Validates cost calculation.
  - Ensures correct network selection.

#### `tests/test_simulation.py`
- **Purpose**: Tests the simulation engine.
- **Key Tests**:
  - Validates device movement.
  - Ensures correct network availability.

#### `tests/test_api.py`
- **Purpose**: Tests the API endpoints.
- **Key Tests**:
  - Validates endpoint responses.
  - Ensures data integrity.

---

## 🔍 Debugging Tips

### Backend
- Use `logging` in `app/main.py` to debug API calls.
- Check the FastAPI Swagger UI at `http://localhost:8000/docs`.

### Frontend
- Open the browser console (`F12` > `Console`) to view logs from `map-visualization.js`.
- Ensure the API server is running before interacting with the UI.

### Testing
- Run unit tests using:
  ```bash
  python -m pytest tests/ -v
  ```
- Check test coverage using:
  ```bash
  pytest --cov=app tests/
  ```

---

## 🚀 Workflow

### 1. Simulation
- Use `/simulation/step` to update the device's state.
- View the updated state on the map.

### 2. Decision Making
- Use `/decision` to select the best network.
- View the decision result in the UI.

### 3. Integrated Flow
- Use `/simulation/step-with-decision` for a combined simulation and decision-making step.

---

## 🤝 Collaboration

### Code Review
- Focus on `decision_logic.py` for algorithm correctness.
- Check `simulation.py` for realistic simulation behavior.
- Ensure `schemas.py` has proper validation.

### Adding Features
1. Create a new branch:
   ```bash
   git checkout -b feature/new-feature
   ```
2. Implement changes and write tests.
3. Submit a pull request for review.

---

For any questions, refer to the [README.md](../README.md) for an overview or contact the project maintainer.