"""
Reusable mathematical formulas for network physics and QoS calculations.

Tách riêng công thức khỏi config để các module khác import dùng lại.
"""

import math
import random
from typing import Dict


def calculate_path_loss(
    distance: float,
    path_loss_exponent: float,
    d0: float,
    pl0: float,
    sigma: float,
) -> float:
    """Log-Distance Path Loss with Shadowing (Rappaport)."""
    d = max(distance, 0.1)
    pl = pl0 + 10 * path_loss_exponent * math.log10(d / d0)
    shadowing = random.gauss(0, sigma)
    return pl + shadowing


def calculate_rssi(tx_power_dbm: float, path_loss_db: float) -> float:
    """RSSI = P_tx - PL(d)."""
    return tx_power_dbm - path_loss_db


def calculate_snr(rssi_dbm: float, noise_floor_dbm: float) -> float:
    """SNR = RSSI - N0."""
    return rssi_dbm - noise_floor_dbm


def calculate_throughput_shannon(
    snr_db: float,
    bandwidth_mhz: float,
    efficiency: float,
    max_throughput_mbps: float,
) -> float:
    """Shannon-Hartley throughput (clamped to max_throughput)."""
    snr_linear = 10 ** (snr_db / 10.0)
    bandwidth_hz = bandwidth_mhz * 1e6
    capacity_bps = bandwidth_hz * math.log2(1 + snr_linear) * efficiency
    capacity_mbps = capacity_bps / 1e6
    return max(0.0, min(capacity_mbps, max_throughput_mbps))


def calculate_packet_loss_rate(snr_db: float, snr_threshold_db: float, k: float) -> float:
    """Sigmoid PLR model."""
    exponent = k * (snr_db - snr_threshold_db)
    exponent = max(-20, min(20, exponent))
    return 1.0 / (1.0 + math.exp(exponent))


def clamp_plr_for_high_snr(plr: float, snr_db: float) -> float:
    """Hard caps cho SNR cao để tránh PLR ~ 0 tuyệt đối."""
    if snr_db > 30:
        return min(plr, 0.001)
    if snr_db > 20:
        return min(plr, 0.01)
    return plr


def calculate_latency(base_latency_ms: float, plr: float, overhead_per_percent_ms: float = 10.0) -> float:
    """Latency = base_latency + retransmit overhead (ms)."""
    retransmit_overhead = plr * 100.0 * overhead_per_percent_ms
    return base_latency_ms + retransmit_overhead


def is_network_available(snr_db: float, threshold_db: float = 0.0) -> bool:
    """Network available nếu SNR > threshold_db (mặc định 0 dB)."""
    return snr_db > threshold_db
