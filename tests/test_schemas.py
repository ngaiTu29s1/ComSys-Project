"""
Script test đơn giản để kiểm tra các Pydantic models.
Chạy: python tests/test_schemas.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import TaskState, NetworkConfig, NetworkState, DeviceState


def test_task_state():
    """Test TaskState enum"""
    print("=== Test TaskState ===")
    
    # Test các giá trị enum
    assert TaskState.IDLE_MONITORING == "IDLE_MONITORING"
    assert TaskState.DATA_BURST_ALERT == "DATA_BURST_ALERT" 
    assert TaskState.VIDEO_STREAMING == "VIDEO_STREAMING"
    
    print("✓ TaskState enum hoạt động đúng")


def test_network_config():
    """Test NetworkConfig model"""
    print("\n=== Test NetworkConfig ===")
    
    # Tạo config cho Wi-Fi
    wifi_config = NetworkConfig(
        name="Wi-Fi",
        power_tx=100.0,
        power_idle=10.0,
        energy_wakeup=2.0
    )
    
    print(f"Wi-Fi config: {wifi_config}")
    assert wifi_config.name == "Wi-Fi"
    assert wifi_config.power_tx == 100.0
    
    # Tạo config cho 5G
    g5_config = NetworkConfig(
        name="5G",
        power_tx=300.0,
        power_idle=15.0,
        energy_wakeup=5.0
    )
    
    print(f"5G config: {g5_config}")
    print("✓ NetworkConfig model hoạt động đúng")


def test_network_state():
    """Test NetworkState model"""
    print("\n=== Test NetworkState ===")
    
    wifi_state = NetworkState(
        name="Wi-Fi",
        bandwidth=50.0,
        latency=10,
        is_available=True
    )
    
    g5_state = NetworkState(
        name="5G", 
        bandwidth=100.0,
        latency=20,
        is_available=True
    )
    
    print(f"Wi-Fi state: {wifi_state}")
    print(f"5G state: {g5_state}")
    print("✓ NetworkState model hoạt động đúng")


def test_device_state():
    """Test DeviceState model"""
    print("\n=== Test DeviceState ===")
    
    # Tạo danh sách mạng khả dụng
    available_networks = [
        NetworkState(name="Wi-Fi", bandwidth=50.0, latency=10, is_available=True),
        NetworkState(name="5G", bandwidth=100.0, latency=20, is_available=True),
        NetworkState(name="BLE", bandwidth=1.0, latency=100, is_available=False)
    ]
    
    # Tạo device state
    device = DeviceState(
        position=(100, 200),
        current_task=TaskState.IDLE_MONITORING,
        available_networks=available_networks
    )
    
    print(f"Device state: {device}")
    print(f"Position: {device.position}")
    print(f"Current task: {device.current_task}")
    print(f"Available networks: {len(device.available_networks)} networks")
    
    # Test với task khác
    streaming_device = DeviceState(
        position=(300, 400),
        current_task=TaskState.VIDEO_STREAMING,
        available_networks=available_networks[:2]  # Chỉ lấy Wi-Fi và 5G
    )
    
    print(f"Streaming device task: {streaming_device.current_task}")
    print("✓ DeviceState model hoạt động đúng")


def test_json_serialization():
    """Test JSON serialization/deserialization"""
    print("\n=== Test JSON Serialization ===")
    
    # Tạo device state
    device = DeviceState(
        position=(50, 75),
        current_task=TaskState.DATA_BURST_ALERT,
        available_networks=[
            NetworkState(name="Wi-Fi", bandwidth=25.0, latency=15, is_available=True)
        ]
    )
    
    # Serialize to JSON
    json_data = device.model_dump_json()
    print(f"JSON: {json_data}")
    
    # Deserialize from JSON
    device_from_json = DeviceState.model_validate_json(json_data)
    print(f"From JSON: {device_from_json}")
    
    assert device.position == device_from_json.position
    assert device.current_task == device_from_json.current_task
    
    print("✓ JSON serialization hoạt động đúng")


if __name__ == "__main__":
    print("Kiểm tra các Pydantic models cho hệ thống mô phỏng...")
    
    test_task_state()
    test_network_config()
    test_network_state()
    test_device_state()
    test_json_serialization()
    
    print("\n🎉 Tất cả tests đều PASS!")
    print("\nCác models đã sẵn sàng sử dụng trong:")
    print("- API endpoints (FastAPI)")
    print("- Thuật toán MCDM")
    print("- Mô hình ML (Random Forest)")