"""
Physical wireless propagation models for IoT network simulation.

This module implements scientifically accurate models based on:
- Log-Distance Path Loss Model with Shadowing
- Shannon-Hartley Theorem for throughput
- Sigmoid model for Packet Loss Rate
- Latency model with retransmission overhead
"""

import math
import random
from typing import Dict


class NetworkPhysics:
    """
    Physical wireless propagation model for different network types.
    Based on Log-Distance Path Loss Model and Shannon-Hartley Theorem.
    """
    
    # Physical parameters for each network type
    CONFIGS = {
        "Wi-Fi": {
            "frequency_ghz": 2.4,
            "tx_power_dbm": 20,          # 100mW
            "ref_path_loss_db": 40,      # PL(d0) at 1m
            "path_loss_exponent": 3.5,   # Indoor with walls
            "bandwidth_mhz": 20,
            "noise_floor_dbm": -95,
            "shadowing_sigma": 4.0,
            "max_throughput_mbps": 100,
            "base_latency_ms": 5,
            "snr_threshold_db": 10       # PLR = 50% at this SNR
        },
        "5G": {
            "frequency_ghz": 3.5,
            "tx_power_dbm": 43,          # 20W
            "ref_path_loss_db": 44,
            "path_loss_exponent": 3.0,   # Urban
            "bandwidth_mhz": 100,
            "noise_floor_dbm": -100,
            "shadowing_sigma": 4.0,
            "max_throughput_mbps": 200,
            "base_latency_ms": 10,
            "snr_threshold_db": 5
        },
        "BLE": {
            "frequency_ghz": 2.4,
            "tx_power_dbm": 0,           # 1mW
            "ref_path_loss_db": 40,
            "path_loss_exponent": 2.5,   # Open space
            "bandwidth_mhz": 2,
            "noise_floor_dbm": -90,
            "shadowing_sigma": 2.0,
            "max_throughput_mbps": 2,
            "base_latency_ms": 20,
            "snr_threshold_db": 8
        }
    }
    
    @staticmethod
    def calculate_path_loss(
        distance: float,
        path_loss_exponent: float,
        d0: float = 1.0,
        pl0: float = 40.0,
        sigma: float = 4.0
    ) -> float:
        """
        Calculate Path Loss using Log-Distance Shadowing Model.
        
        PL(d) = PL(d0) + 10*n*log10(d/d0) + X_sigma
        
        Args:
            distance: Distance in meters
            path_loss_exponent: Path loss exponent (n)
            d0: Reference distance (default 1m)
            pl0: Path loss at d0 (dB)
            sigma: Shadowing standard deviation (dB)
            
        Returns:
            Path loss in dB
        """
        # Clamp distance to avoid log(0)
        d = max(distance, 0.1)
        
        # Log-distance path loss
        pl = pl0 + 10 * path_loss_exponent * math.log10(d / d0)
        
        # Add shadowing (Gaussian noise)
        shadowing = random.gauss(0, sigma)
        
        return pl + shadowing
    
    @staticmethod
    def calculate_rssi(network_type: str, distance: float) -> float:
        """
        Calculate RSSI (Received Signal Strength Indicator).
        
        RSSI = P_tx - PL(d)
        
        Args:
            network_type: Network type ("Wi-Fi", "5G", "BLE")
            distance: Distance in meters
            
        Returns:
            RSSI in dBm
        """
        if network_type not in NetworkPhysics.CONFIGS:
            return -999
        
        config = NetworkPhysics.CONFIGS[network_type]
        
        # Calculate path loss
        pl = NetworkPhysics.calculate_path_loss(
            distance=distance,
            path_loss_exponent=config["path_loss_exponent"],
            d0=1.0,
            pl0=config["ref_path_loss_db"],
            sigma=config["shadowing_sigma"]
        )
        
        # RSSI = Tx Power - Path Loss
        rssi = config["tx_power_dbm"] - pl
        
        return rssi
    
    @staticmethod
    def calculate_snr(rssi_dbm: float, noise_floor_dbm: float) -> float:
        """
        Calculate SNR (Signal-to-Noise Ratio).
        
        SNR = RSSI - N0
        
        Args:
            rssi_dbm: RSSI in dBm
            noise_floor_dbm: Noise floor in dBm
            
        Returns:
            SNR in dB
        """
        return rssi_dbm - noise_floor_dbm
    
    @staticmethod
    def calculate_throughput_shannon(
        snr_db: float,
        bandwidth_mhz: float,
        efficiency: float = 0.5
    ) -> float:
        """
        Calculate throughput using Shannon-Hartley Theorem.
        
        R = B * log2(1 + SNR_linear) * η
        
        Args:
            snr_db: SNR in dB
            bandwidth_mhz: Bandwidth in MHz
            efficiency: Spectral efficiency factor (0-1)
            
        Returns:
            Throughput in Mbps
        """
        # Convert SNR from dB to linear
        snr_linear = 10 ** (snr_db / 10.0)
        
        # Bandwidth from MHz to Hz
        bandwidth_hz = bandwidth_mhz * 1e6
        
        # Shannon capacity in bps
        capacity_bps = bandwidth_hz * math.log2(1 + snr_linear) * efficiency
        
        # Convert to Mbps
        capacity_mbps = capacity_bps / 1e6
        
        return max(0.0, capacity_mbps)
    
    @staticmethod
    def calculate_packet_loss_rate(
        snr_db: float,
        snr_threshold_db: float,
        k: float = 0.5
    ) -> float:
        """
        Calculate Packet Loss Rate using Sigmoid Model.
        
        PLR = 1 / (1 + e^(k*(SNR - SNR_threshold)))
        
        Args:
            snr_db: SNR in dB
            snr_threshold_db: SNR threshold (PLR=50%)
            k: Steepness factor
            
        Returns:
            Packet Loss Rate (0.0 - 1.0)
        """
        exponent = k * (snr_db - snr_threshold_db)
        
        # Clamp to avoid overflow
        exponent = max(-20, min(20, exponent))
        
        plr = 1.0 / (1.0 + math.exp(exponent))
        
        return plr
    
    @staticmethod
    def calculate_qos(network_type: str, distance: float) -> Dict[str, float]:
        """
        Calculate complete QoS metrics for a network type at given distance.
        
        Args:
            network_type: Network type ("Wi-Fi", "5G", "BLE")
            distance: Distance from device to base station (meters)
            
        Returns:
            Dict containing:
                - bandwidth: Actual throughput (Mbps)
                - latency: Latency (ms)
                - packet_loss: Packet loss rate (0.0-1.0)
                - rssi: RSSI (dBm)
                - snr: SNR (dB)
                - is_available: Is network available
        """
        if network_type not in NetworkPhysics.CONFIGS:
            return {
                "bandwidth": 0.0,
                "latency": 9999,
                "packet_loss": 1.0,
                "rssi": -999,
                "snr": -999,
                "is_available": False
            }
        
        config = NetworkPhysics.CONFIGS[network_type]
        
        # 1. Calculate RSSI
        rssi = NetworkPhysics.calculate_rssi(network_type, distance)
        
        # 2. Calculate SNR
        snr = NetworkPhysics.calculate_snr(rssi, config["noise_floor_dbm"])
        
        # 3. Check availability (SNR > 0 dB is minimum threshold)
        is_available = snr > 0
        
        if not is_available:
            return {
                "bandwidth": 0.0,
                "latency": 9999,
                "packet_loss": 1.0,
                "rssi": rssi,
                "snr": snr,
                "is_available": False
            }
        
        # 4. Calculate throughput using Shannon (clamped to max throughput)
        throughput = NetworkPhysics.calculate_throughput_shannon(
            snr_db=snr,
            bandwidth_mhz=config["bandwidth_mhz"],
            efficiency=0.5
        )
        bandwidth = min(throughput, config["max_throughput_mbps"])
        
        # 5. Calculate Packet Loss Rate
        plr = NetworkPhysics.calculate_packet_loss_rate(
            snr_db=snr,
            snr_threshold_db=config["snr_threshold_db"],
            k=0.5
        )
        
        # 6. Calculate Latency (base latency + retransmission overhead)
        # Assumption: each 1% PLR adds 10ms latency due to retransmit
        base_latency = config["base_latency_ms"]
        retransmit_overhead = plr * 100 * 10  # PLR 10% -> +100ms
        latency = base_latency + retransmit_overhead
        
        return {
            "bandwidth": round(bandwidth, 2),
            "latency": int(latency),
            "packet_loss": round(plr, 4),
            "rssi": round(rssi, 1),
            "snr": round(snr, 1),
            "is_available": True
        }
