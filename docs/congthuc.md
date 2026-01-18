# 📡 IoT Network Selection - Mathematical Formulas

> **Cập nhật**: December 7, 2025  
> **Branch**: fix/Etx-formula

This document defines the mathematical models and parameters for:
1. **Energy Cost Calculation** (Simplified formula)
2. **QoS Penalty Calculation** (MCDM weights)
3. **Wireless Channel Physics** (Path loss, SNR, throughput)

## 1. Energy Cost Formula (Simplified)

### A. Energy Transmission Cost
**Previous (complex)**: `E_total = (energy_tx × T_tx) + (energy_idle × T_idle) + E_wakeup`

**Current (simplified)**:
$$E_{total} = (E_{tx} \times DataSize) + E_{wakeup}$$

Where:
- $E_{tx}$: Transmission energy per KB (mJ/KB) - **includes RF power + circuit overhead**
- $DataSize$: Estimated data size for task (KB)
- $E_{wakeup}$: One-time radio wake-up energy (mJ)

**Rationale**:
- $E_{tx}$ is normalized per KB → no need to multiply by $T_{tx}$
- Idle energy removed (negligible for short transmission bursts)
- Simpler model → easier to interpret and scale

**Implementation**: `app/core/decision_logic.py::calculate_energy_cost()`

### B. Task Data Size Estimates

| Task | Data Size | Location |
|------|-----------|----------|
| IDLE_MONITORING | 1.0 KB | `constants.py::TaskDataEstimates` |
| DATA_BURST_ALERT | 50.0 KB | |
| VIDEO_STREAMING | 1000.0 KB | |

---

## 2. QoS Penalty Formula (MCDM)

### A. Cost Function
$$Cost_{total} = w_{energy} \times E_{cost} + w_{qos} \times Penalty_{QoS}$$

Where:
- $w_{energy}$: Energy weight (task-dependent)
- $w_{qos}$: QoS weight (task-dependent)
- $w_{energy} + w_{qos} = 1.0$

### B. Task Weights

| Task | w_energy | w_qos | Priority |
|------|----------|-------|----------|
| IDLE_MONITORING | 0.8 | 0.2 | Energy first |
| DATA_BURST_ALERT | 0.3 | 0.7 | QoS first (low latency) |
| VIDEO_STREAMING | 0.4 | 0.6 | Balanced |

**Location**: `app/core/constants.py::TASK_WEIGHTS`

### C. QoS Penalty Calculation

$$Penalty_{QoS} = \begin{cases}
1000 & \text{if network unavailable} \\
\sum(\text{bandwidth deficit} \times 50) + \sum(\text{latency excess} \times 2) & \text{otherwise}
\end{cases}$$

**QoS Requirements**:

| Task | Min Bandwidth | Max Latency |
|------|---------------|-------------|
| IDLE | 0.1 Mbps | 1000 ms |
| DATA_BURST | 5.0 Mbps | 100 ms |
| VIDEO | 10.0 Mbps | 200 ms |

**Location**: `app/core/constants.py::QOS_REQUIREMENTS`

**Implementation**: `app/core/decision_logic.py::calculate_qos_penalty()`

---

## 3. Wireless Channel Physics

### A. Path Loss Model (Log-Distance Shadowing)
We use the standard Log-Distance Path Loss model to calculate signal attenuation.

$$PL(d) = PL(d_0) + 10 \cdot n \cdot \log_{10}\left(\frac{d}{d_0}\right) + X_\sigma$$

Where:
- $d$: Distance between device and Access Point (meters).
- $d_0$: Reference distance (standard = 1.0 meter).
- $PL(d_0)$: Path loss at reference distance (dB).
- $n$: Path Loss Exponent (Environmental factor).
- $X_\sigma$: Shadowing factor, a random variable following Gaussian distribution $N(0, \sigma^2)$.

### B. RSSI & SNR Calculation
Received Signal Strength Indicator (RSSI) and Signal-to-Noise Ratio (SNR).

$$RSSI [dBm] = P_{tx} - PL(d)$$
$$SNR [dB] = RSSI - N_0$$

Where:
- $P_{tx}$: Transmission Power (dBm).
- $N_0$: Noise Floor (dBm).

### C. Throughput Calculation (Shannon-Hartley)
Theoretical maximum data rate based on SNR.

$$R = B \cdot \log_2(1 + 10^{\frac{SNR}{10}}) \cdot \eta$$

Where:
- $R$: Throughput (bps).
- $B$: Channel Bandwidth (Hz).
- $\eta$: Spectral Efficiency Factor (0 < $\eta$ < 1, typically 0.5 for realistic overhead).

### D. Packet Loss Rate (Sigmoid Model)
Approximation of Packet Error Rate based on SNR.

$$PLR = \frac{1}{1 + e^{k \cdot (SNR - SNR_{threshold})}}$$

Where:
- $k$: Slope factor (steepness of the curve).
- $SNR_{threshold}$: The SNR value where PLR is 50%.

---

### Physics Parameters

| Parameter | Wi-Fi (802.11n) | 5G (Sub-6GHz) | BLE (Bluetooth 5) |
|-----------|-----------------|---------------|-------------------|
| **Frequency** | 2.4 GHz | 3.5 GHz | 2.4 GHz |
| **Tx Power** | 20 dBm | 43 dBm | 0 dBm |
| **Path Loss Exp (n)** | 3.5 | 3.0 | 4.0 |
| **Ref Path Loss** | 40 dB | 44 dB | 40 dB |
| **Bandwidth** | 20 MHz | 100 MHz | 2 MHz |
| **Noise Floor** | -90 dBm | -95 dBm | -85 dBm |
| **Base Latency** | 5 ms | 10 ms | 20 ms |
| **Max Throughput** | 100 Mbps | 200 Mbps | 2 Mbps |

**Location**: `app/core/constants.py::NetworkPhysicsConfig`

---

## 6. Usage Examples

### Calculate Energy Cost
```python
from app.core.decision_logic import calculate_energy_cost
from app.models.schemas import TaskState, NetworkConfig

wifi_config = NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0)
network_state = NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True)

energy = calculate_energy_cost(wifi_config, network_state, TaskState.DATA_BURST_ALERT)
# Output: 27.0 mJ (0.5 × 50 KB + 2.0 mJ)
```

### Calculate QoS Penalty
```python
from app.core.decision_logic import calculate_qos_penalty

bad_network = NetworkState(name="BLE", bandwidth=0.5, latency=300, is_available=True)
penalty = calculate_qos_penalty(bad_network, TaskState.DATA_BURST_ALERT)
# Output: 625.0 (high penalty due to insufficient bandwidth + high latency)
```

### Select Best Network
```python
from app.core.decision_logic import select_best_network

available_networks = [wifi_state, fiveg_state, ble_state]
best_network, cost = select_best_network(available_networks, network_configs, TaskState.IDLE_MONITORING)
# Output: BLE (lowest energy cost for IDLE task)
```

---

## 7. Validation & Testing

### Verification Scripts

1. **`scripts/verify_mcdm_logic.py`**: Verify MCDM algorithm correctness
   - Energy formula validation
   - QoS penalty logic
   - Decision making for each task
   - Energy savings comparison

2. **`scripts/run_all_tests.py`**: Run full test suite
   - Unit tests (decision logic, simulation, schemas)
   - ML inference tests
   - Environment smoke tests

### Expected Results

- **Energy formula**: Exact match with `energy_tx × Data + E_wakeup`
- **QoS penalty**: Correct thresholds and penalty factors
- **Decision logic**: BLE for IDLE, Wi-Fi/5G for heavy tasks
- **ML accuracy**: ~99.9% (CV + test + unseen data)

---

## 8. References

**Implementation Files**:
- `app/core/constants.py`: All constants
- `app/core/formulas.py`: Math formulas
- `app/core/decision_logic.py`: MCDM algorithm
- `app/services/network_physics.py`: QoS coordinator
- `app/services/simulation.py`: Simulation engine

**Documentation**:
- `docs/CODEBASE_BREAKDOWN_VI.md`: Architecture details
- `docs/CODE_GUIDE.md`: Code guide (English)
- `docs/POSTMAN_GUIDE.md`: API testing guide

---

## 4. Implementation Architecture

### File Organization

```
app/
├── core/
│   ├── constants.py          # ⭐ ALL constants (energy, QoS, physics)
│   ├── formulas.py           # ⭐ Reusable math formulas
│   └── decision_logic.py     # MCDM algorithm
│
└── services/
    ├── network_physics.py    # Coordinator: calls formulas + constants
    └── simulation.py         # Simulation engine
```

### Key Design Principles

1. **Centralized Constants** (`app/core/constants.py`):
   - `NetworkEnergyConfig`: Energy params for Wi-Fi/5G/BLE
   - `NetworkPhysicsConfig`: Physics params (tx_power, path_loss_exponent...)
   - `TASK_WEIGHTS`: MCDM weights per task
   - `QOS_REQUIREMENTS`: QoS thresholds per task
   - `MLConfig`: ML unavailable markers + hyperparams

2. **Separated Formulas** (`app/core/formulas.py`):
   - `calculate_path_loss()`: Log-distance shadowing
   - `calculate_rssi()`: RSSI = Tx - PL
   - `calculate_snr()`: SNR = RSSI - N0
   - `calculate_throughput_shannon()`: Shannon-Hartley
   - `calculate_packet_loss_rate()`: Sigmoid PLR
   - `calculate_latency()`: Base + retransmit overhead

3. **Clean Separation**:
   - **Config** (constants.py) ≠ **Formulas** (formulas.py) ≠ **Logic** (decision_logic.py)
   - Easy to modify parameters without touching code
   - Easy to extend with new network types or tasks

---

## 5. Network Parameters (Updated)

### Energy Parameters

| Parameter | Wi-Fi | 5G | BLE |
|-----------|-------|-----|-----|
| **energy_tx** (mJ/KB) | 0.5 | 1.2 | 0.1 |
| **energy_idle** (mW) | 10.0 | 15.0 | 2.0 |
| **energy_wakeup** (mJ) | 2.0 | 5.0 | 0.5 |

**Location**: `app/core/constants.py::NetworkEnergyConfig`

### Physics Parameters