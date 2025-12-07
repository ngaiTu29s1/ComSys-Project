"""
Physical wireless propagation models for IoT network simulation.

Chỉ giữ phần "điều phối"; toàn bộ công thức được tách sang
`app/core/formulas.py` và tham số nằm trong `app/core/constants.py`.
"""

from typing import Dict
from app.core.constants import NetworkPhysicsConfig
from app.core import formulas


class NetworkPhysics:
    """
    Physical wireless propagation model for different network types.
    Based on Log-Distance Path Loss Model and Shannon-Hartley Theorem.
    """
    
    # Physical parameters cho từng mạng (đã chuẩn hóa tại constants.py)
    CONFIGS = {
        "Wi-Fi": NetworkPhysicsConfig.WIFI,
        "5G": NetworkPhysicsConfig.FIVEG,
        "BLE": NetworkPhysicsConfig.BLE,
    }

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
        
        pl = formulas.calculate_path_loss(
            distance=distance,
            path_loss_exponent=config["path_loss_exponent"],
            d0=config["reference_distance_m"],
            pl0=config["ref_path_loss_db"],
            sigma=config["shadowing_sigma_db"],
        )
        return formulas.calculate_rssi(config["tx_power_dbm"], pl)
    
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
        return formulas.calculate_snr(rssi_dbm, noise_floor_dbm)
    
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
        return formulas.calculate_throughput_shannon(
            snr_db=snr_db,
            bandwidth_mhz=bandwidth_mhz,
            efficiency=efficiency,
            max_throughput_mbps=float("inf"),  # clamp bên ngoài
        )
    
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
        return formulas.calculate_packet_loss_rate(snr_db, snr_threshold_db, k)
    
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
        is_available = formulas.is_network_available(snr)
        
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
        bandwidth = formulas.calculate_throughput_shannon(
            snr_db=snr,
            bandwidth_mhz=config["bandwidth_mhz"],
            efficiency=config["spectral_efficiency"],
            max_throughput_mbps=config["max_throughput_mbps"],
        )
        
        # 5. Calculate Packet Loss Rate (steeper curve = more realistic)
        plr = formulas.calculate_packet_loss_rate(
            snr_db=snr,
            snr_threshold_db=config["snr_threshold_db"],
            k=config["plr_sigmoid_k"],
        )
        plr = formulas.clamp_plr_for_high_snr(plr, snr)
        
        # 6. Calculate Latency (base latency + retransmission overhead)
        # Assumption: each 1% PLR adds 10ms latency due to retransmit
        latency = formulas.calculate_latency(
            base_latency_ms=config["base_latency_ms"],
            plr=plr,
            overhead_per_percent_ms=10.0,
        )
        
        return {
            "bandwidth": round(bandwidth, 2),
            "latency": int(latency),
            "packet_loss": round(plr, 4),
            "rssi": round(rssi, 1),
            "snr": round(snr, 1),
            "is_available": True
        }
