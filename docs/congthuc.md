# 📡 Realistic Wireless Channel Model Specification

This document defines the mathematical models and parameters for simulating network Quality of Service (QoS) based on physics, replacing the simple linear degradation model.

## 1. Mathematical Formulas

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

## 2. Network Parameters Configuration

Use these standard values for the simulation `CONFIGS`.

| Parameter | Wi-Fi (802.11n) | 5G (Sub-6GHz) | BLE (Bluetooth 5) |
| :--- | :--- | :--- | :--- |
| **Frequency** | 2.4 GHz | 3.5 GHz | 2.4 GHz |
| **Tx Power ($P_{tx}$)** | 20 dBm (100mW) | 43 dBm (20W) | 0 dBm (1mW) |
| **Ref. Path Loss ($PL(d_0)$)** | 40 dB | 44 dB | 40 dB |
| **Path Loss Exp ($n$)** | 3.5 (Indoor/Walls) | 3.0 (Urban) | 2.5 (Open space) |
| **Bandwidth ($B$)** | 20 MHz | 100 MHz | 2 MHz |
| **Noise Floor ($N_0$)** | -95 dBm | -100 dBm | -90 dBm |
| **Shadowing ($\sigma$)** | 4.0 dB | 4.0 dB | 2.0 dB |
| **Max Throughput** | 100 Mbps | 200 Mbps | 2 Mbps |

---

## 3. Implementation Logic (Python Class)

Create a class `NetworkPhysics` with the following static methods:

1.  **`calculate_path_loss(distance, n, d0, pl0, sigma)`**:
    - Returns path loss in dB.
    - Handle `distance <= 0` cases (clamp to 0.1m).

2.  **`calculate_rssi(network_type, distance)`**:
    - Look up params from CONFIGS.
    - Return RSSI value.

3.  **`calculate_qos(network_type, distance)`**:
    - Calculate SNR.
    - Calculate Throughput using Shannon formula (clamped to Max Throughput).
    - Calculate Packet Loss using Sigmoid function (Logic: High SNR -> Low PLR).
    - Calculate Latency:
        - Base Latency: Wi-Fi=5ms, 5G=10ms, BLE=20ms.
        - Latency increases as Packet Loss increases (due to retransmissions).
    - Determine `is_available`: True if $SNR > 0$.