"""
Centralized Constants Configuration.

File này chứa TẤT CẢ các constants và configurations của hệ thống:
- Network energy parameters
- QoS requirements per task
- MCDM weights
- Network physics parameters

Mục đích: Dễ dàng điều chỉnh parameters mà không cần sửa logic code.
"""

from typing import Dict, Any
from app.models.schemas import TaskState


# ========================================================================
# NETWORK ENERGY CONFIGURATIONS
# ========================================================================

class NetworkEnergyConfig:
    """Power parameters cho mỗi loại mạng (mW)."""
    
    WIFI = {
        "name": "Wi-Fi",
        "power_tx": 100.0,     # mW
        "power_idle": 10.0,    # mW
        "energy_wakeup": 2.0   # mJ - khởi động radio
    }
    
    FIVEG = {
        "name": "5G",
        "power_tx": 300.0,     # mW
        "power_idle": 15.0,    # mW
        "energy_wakeup": 5.0   # mJ
    }
    
    BLE = {
        "name": "BLE",
        "power_tx": 10.0,      # mW
        "power_idle": 2.0,     # mW
        "energy_wakeup": 0.5   # mJ
    }


# ========================================================================
# TASK-SPECIFIC CONFIGURATIONS
# ========================================================================

class TaskDataEstimates:
    """Ước tính kích thước dữ liệu cho mỗi loại tác vụ (KB)."""
    
    IDLE_MONITORING = 1.0       # 1KB - Sensor data nhỏ
    DATA_BURST_ALERT = 50.0     # 50KB - Alert message + metadata
    VIDEO_STREAMING = 1000.0    # 1MB - Video chunk (1 second @ 8 Mbps)


# Trọng số MCDM cho từng loại tác vụ (w_energy + w_qos = 1.0)
TASK_WEIGHTS: Dict[TaskState, Dict[str, float]] = {
    TaskState.IDLE_MONITORING: {
        "w_energy": 0.8,    # Ưu tiên tiết kiệm năng lượng
        "w_qos": 0.2        # QoS không quá quan trọng
    },
    TaskState.DATA_BURST_ALERT: {
        "w_energy": 0.3,    # Năng lượng ít quan trọng hơn
        "w_qos": 0.7        # Ưu tiên độ trễ thấp và bandwidth cao
    },
    TaskState.VIDEO_STREAMING: {
        "w_energy": 0.4,    # Cân bằng năng lượng
        "w_qos": 0.6        # Ưu tiên QoS cho streaming
    }
}

# Yêu cầu QoS tối thiểu cho từng tác vụ
QOS_REQUIREMENTS: Dict[TaskState, Dict[str, Any]] = {
    TaskState.IDLE_MONITORING: {
        "min_bandwidth": 0.1,       # 0.1 Mbps - Đủ cho sensor data
        "max_latency": 1000,        # 1000ms - Không cần real-time
        "must_be_available": True
    },
    TaskState.DATA_BURST_ALERT: {
        "min_bandwidth": 5.0,       # 5 Mbps - Cần bandwidth trung bình
        "max_latency": 100,         # 100ms - Cần độ trễ thấp
        "must_be_available": True
    },
    TaskState.VIDEO_STREAMING: {
        "min_bandwidth": 10.0,      # 10 Mbps - Cần bandwidth cao
        "max_latency": 200,         # 200ms - Cho phép buffer
        "must_be_available": True
    }
}


# ========================================================================
# QOS PENALTY COEFFICIENTS
# ========================================================================

class QoSPenaltyCoefficients:
    """Hệ số phạt cho các vi phạm QoS."""
    
    UNAVAILABLE_PENALTY = 1000.0        # Phạt nặng nếu mạng không khả dụng
    BANDWIDTH_DEFICIT_FACTOR = 50.0     # Hệ số phạt cho thiếu băng thông
    LATENCY_EXCESS_FACTOR = 2.0         # Hệ số phạt cho độ trễ vượt ngưỡng
    SEVERE_VIOLATION_THRESHOLD = 500.0  # Ngưỡng vi phạm nghiêm trọng


# ========================================================================
# NETWORK PHYSICS PARAMETERS
# ========================================================================

class NetworkPhysicsConfig:
    """
    Các tham số vật lý cho từng loại mạng.
    Sử dụng trong mô hình Log-Distance Path Loss và Shannon-Hartley.
    """
    
    WIFI = {
        "tx_power_dbm": 20.0,           # Công suất phát (dBm) - Router chuẩn
        "path_loss_exponent": 3.5,      # Hệ số suy hao (indoor environment)
        "reference_distance_m": 1.0,    # Khoảng cách tham chiếu (m)
        "shadowing_sigma_db": 2.0,      # Độ lệch chuẩn shadowing (dB)
        "noise_floor_dbm": -90.0,       # Nhiễu nền (dBm)
        "bandwidth_mhz": 20.0,          # Băng thông kênh (MHz)
        "spectral_efficiency": 0.7,     # Hiệu suất phổ (η)
        "base_latency_ms": 5.0,         # Độ trễ cơ bản (ms)
        "snr_threshold_db": 10.0,       # Ngưỡng SNR tối thiểu (dB)
        "plr_sigmoid_k": 1.0,           # Hệ số sigmoid cho PLR
        "frequency_ghz": 2.4,           # Tần số sóng mang (GHz)
        "ref_path_loss_db": 40.0,       # PL(d0) tại 1m
        "max_throughput_mbps": 100.0    # Giới hạn throughput
    }
    
    FIVEG = {
        "tx_power_dbm": 43.0,           # Cao hơn (Macro cell base station)
        "path_loss_exponent": 3.0,      # Thấp hơn (outdoor urban)
        "reference_distance_m": 1.0,
        "shadowing_sigma_db": 2.5,      # Nhiễu cao hơn
        "noise_floor_dbm": -95.0,       # Thấp hơn nhờ công nghệ tốt
        "bandwidth_mhz": 100.0,         # Băng thông rộng
        "spectral_efficiency": 0.8,     # Hiệu suất cao nhờ MIMO
        "base_latency_ms": 10.0,        # Độ trễ cơ bản
        "snr_threshold_db": 5.0,        # Ngưỡng thấp nhờ coding tốt
        "plr_sigmoid_k": 1.0,
        "frequency_ghz": 3.5,           # Tần số sóng mang (GHz)
        "ref_path_loss_db": 44.0,       # PL(d0) tại 1m
        "max_throughput_mbps": 200.0    # Giới hạn throughput
    }
    
    BLE = {
        "tx_power_dbm": 0.0,            # Rất thấp (tiết kiệm năng lượng)
        "path_loss_exponent": 3.5,      # Tương tự Wi-Fi (short range)
        "reference_distance_m": 1.0,
        "shadowing_sigma_db": 1.5,      # Ít nhiễu (2.4 GHz ISM band)
        "noise_floor_dbm": -90.0,
        "bandwidth_mhz": 2.0,           # Băng thông rất hẹp
        "spectral_efficiency": 0.5,     # Hiệu suất thấp (simple modulation)
        "base_latency_ms": 20.0,        # Độ trễ cao
        "snr_threshold_db": 8.0,        # Ngưỡng trung bình
        "plr_sigmoid_k": 1.0,
        "frequency_ghz": 2.4,           # Tần số sóng mang (GHz)
        "ref_path_loss_db": 40.0,       # PL(d0) tại 1m
        "max_throughput_mbps": 2.0      # Giới hạn throughput
    }


# ========================================================================
# SIMULATION PARAMETERS
# ========================================================================

class SimulationConfig:
    """Tham số cho simulation engine."""
    
    # Map configuration
    MAP_WIDTH = 1000                    # pixels
    MAP_HEIGHT = 1000                   # pixels
    
    # Device movement
    MOVEMENT_STEP_SIZE = 50             # pixels per step
    RANDOM_WALK_ENABLED = True
    
    # Base station positions
    BASE_STATION_POSITIONS = {
        "Wi-Fi": [
            {"id": "WiFi-1", "pos": (100, 100)},    # Khu dân cư
            {"id": "WiFi-2", "pos": (300, 250)},    # Văn phòng
            {"id": "WiFi-3", "pos": (600, 400)},    # Quán café
            {"id": "WiFi-4", "pos": (800, 750)},    # Trung tâm thương mại
        ],
        "5G": [
            {"id": "5G-1", "pos": (200, 200)},      # Trung tâm thành phố
            {"id": "5G-2", "pos": (500, 300)},      # Khu công nghiệp
            {"id": "5G-3", "pos": (700, 600)},      # Sân bay
            {"id": "5G-4", "pos": (400, 800)},      # Khu vực ngoại ô
        ],
        "BLE": [
            {"id": "BLE-1", "pos": (150, 150)},     # Smart home hub
            {"id": "BLE-2", "pos": (350, 350)},     # Office beacon
            {"id": "BLE-3", "pos": (550, 550)},     # Retail beacon
            {"id": "BLE-4", "pos": (750, 750)},     # Mall beacon
        ]
    }
    
    # Thresholds
    MIN_RSSI_DBM = -90.0                # Ngưỡng RSSI tối thiểu để mạng available
    MIN_SNR_DB = 0.0                    # Ngưỡng SNR tối thiểu
    MAX_DISTANCE_M = 500.0              # Khoảng cách tối đa để detect base station


# ========================================================================
# MACHINE LEARNING PARAMETERS
# ========================================================================

class MLConfig:
    """Cấu hình cho ML model."""
    
    # Random Forest Hyperparameters
    N_ESTIMATORS = 100
    MAX_DEPTH = 15
    RANDOM_STATE = 42
    
    # Feature engineering
    UNAVAILABLE_RSSI = -999.0           # Giá trị mã hóa khi mạng không available
    UNAVAILABLE_SNR = -999.0
    UNAVAILABLE_BANDWIDTH = 0.0
    UNAVAILABLE_LATENCY = 9999.0
    UNAVAILABLE_DISTANCE = 9999.0
    
    # Training
    TEST_SIZE = 0.2
    CROSS_VALIDATION_FOLDS = 5
    
    # Model paths
    MODEL_PATH = "models/rf_network_selector.pkl"
    TRAINING_DATA_PATH = "data/raw/training_data.csv"


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def get_network_energy_config(network_name: str) -> Dict[str, Any]:
    """Lấy energy config cho một mạng cụ thể."""
    configs = {
        "Wi-Fi": NetworkEnergyConfig.WIFI,
        "5G": NetworkEnergyConfig.FIVEG,
        "BLE": NetworkEnergyConfig.BLE
    }
    return configs.get(network_name, NetworkEnergyConfig.WIFI)


def get_network_physics_config(network_name: str) -> Dict[str, Any]:
    """Lấy physics config cho một mạng cụ thể."""
    configs = {
        "Wi-Fi": NetworkPhysicsConfig.WIFI,
        "5G": NetworkPhysicsConfig.FIVEG,
        "BLE": NetworkPhysicsConfig.BLE
    }
    return configs.get(network_name, NetworkPhysicsConfig.WIFI)


def get_task_data_size(task: TaskState) -> float:
    """Lấy ước tính kích thước dữ liệu cho một task (KB)."""
    estimates = {
        TaskState.IDLE_MONITORING: TaskDataEstimates.IDLE_MONITORING,
        TaskState.DATA_BURST_ALERT: TaskDataEstimates.DATA_BURST_ALERT,
        TaskState.VIDEO_STREAMING: TaskDataEstimates.VIDEO_STREAMING
    }
    return estimates.get(task, 10.0)  # Default 10KB
