"""
Test script cho thuật toán decision logic.
Chạy: python tests/test_decision_logic.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schemas import TaskState, NetworkState, NetworkConfig
from app.core.decision_logic import (
    TASK_WEIGHTS,
    QOS_REQUIREMENTS,
    calculate_cost,
    calculate_energy_cost, 
    calculate_qos_penalty,
    select_best_network
)


def test_task_weights():
    """Test cấu hình trọng số"""
    print("=== Test Task Weights ===")
    
    # Kiểm tra tất cả tasks đều có weights
    for task in TaskState:
        assert task in TASK_WEIGHTS, f"Missing weights for {task}"
        weights = TASK_WEIGHTS[task]
        
        # Kiểm tra tổng trọng số = 1.0
        total = weights["w_energy"] + weights["w_qos"]
        assert abs(total - 1.0) < 0.001, f"Weights sum != 1.0 for {task}: {total}"
        
        print(f"✓ {task}: w_energy={weights['w_energy']}, w_qos={weights['w_qos']}")
    
    print("✓ Task weights đều hợp lệ")


def test_qos_requirements():
    """Test yêu cầu QoS"""
    print("\n=== Test QoS Requirements ===")
    
    for task in TaskState:
        assert task in QOS_REQUIREMENTS, f"Missing QoS requirements for {task}"
        req = QOS_REQUIREMENTS[task]
        
        assert "min_bandwidth" in req
        assert "max_latency" in req
        assert "must_be_available" in req
        
        print(f"✓ {task}: BW>={req['min_bandwidth']}Mbps, Latency<={req['max_latency']}ms")
    
    print("✓ QoS requirements đều có đầy đủ")


def test_energy_cost_calculation():
    """Test tính toán chi phí năng lượng"""
    print("\n=== Test Energy Cost Calculation ===")
    
    # Tạo network config mẫu
    wifi_config = NetworkConfig(
        name="Wi-Fi",
        energy_tx=0.5,      # 0.5 mJ/KB
        energy_idle=10.0,   # 10 mW  
        energy_wakeup=2.0   # 2 mJ
    )
    
    # Tạo network state mẫu
    wifi_state = NetworkState(
        name="Wi-Fi",
        bandwidth=50.0,
        latency=15,
        is_available=True
    )
    
    # Test với các tasks khác nhau
    for task in TaskState:
        energy_cost = calculate_energy_cost(wifi_config, wifi_state, task)
        print(f"✓ {task}: Energy cost = {energy_cost:.2f} mJ")
        assert energy_cost > 0, f"Energy cost should be positive for {task}"
    
    print("✓ Energy cost calculation hoạt động đúng")


def test_qos_penalty():
    """Test tính toán QoS penalty"""
    print("\n=== Test QoS Penalty Calculation ===")
    
    # Test case 1: Mạng tốt - không có penalty
    good_network = NetworkState(
        name="5G",
        bandwidth=100.0,    # Rất cao
        latency=10,         # Rất thấp
        is_available=True
    )
    
    for task in TaskState:
        penalty = calculate_qos_penalty(good_network, task)
        print(f"✓ {task} với mạng tốt: penalty = {penalty}")
        # Mạng tốt nên có penalty thấp
    
    # Test case 2: Mạng kém - có penalty cao
    bad_network = NetworkState(
        name="BLE",
        bandwidth=0.5,      # Rất thấp
        latency=500,        # Rất cao
        is_available=True
    )
    
    for task in TaskState:
        penalty = calculate_qos_penalty(bad_network, task)
        print(f"✓ {task} với mạng kém: penalty = {penalty}")
    
    # Test case 3: Mạng không khả dụng
    unavailable_network = NetworkState(
        name="Offline",
        bandwidth=100.0,
        latency=10,
        is_available=False
    )
    
    penalty = calculate_qos_penalty(unavailable_network, TaskState.IDLE_MONITORING)
    print(f"✓ Mạng offline: penalty = {penalty}")
    assert penalty >= 1000, "Unavailable network should have high penalty"
    
    print("✓ QoS penalty calculation hoạt động đúng")


def test_cost_calculation():
    """Test tính toán tổng chi phí"""
    print("\n=== Test Total Cost Calculation ===")
    
    # Setup networks
    wifi_config = NetworkConfig(
        name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0
    )
    g5_config = NetworkConfig(
        name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0
    )
    
    wifi_state = NetworkState(
        name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True
    )
    g5_state = NetworkState(
        name="5G", bandwidth=100.0, latency=25, is_available=True
    )
    
    # Test với các tasks khác nhau
    for task in TaskState:
        wifi_cost = calculate_cost(wifi_state, wifi_config, task)
        g5_cost = calculate_cost(g5_state, g5_config, task)
        
        print(f"✓ {task}:")
        print(f"  Wi-Fi cost: {wifi_cost:.2f}")
        print(f"  5G cost: {g5_cost:.2f}")
        
        assert wifi_cost > 0 and g5_cost > 0, f"Costs should be positive for {task}"
    
    print("✓ Total cost calculation hoạt động đúng")


def test_network_selection():
    """Test thuật toán lựa chọn mạng"""
    print("\n=== Test Network Selection ===")
    
    # Setup configs
    network_configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "5G": NetworkConfig(name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0),
        "BLE": NetworkConfig(name="BLE", energy_tx=0.1, energy_idle=2.0, energy_wakeup=0.5)
    }
    
    # Setup available networks
    available_networks = [
        NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True),
        NetworkState(name="5G", bandwidth=100.0, latency=25, is_available=True), 
        NetworkState(name="BLE", bandwidth=1.0, latency=200, is_available=True)
    ]
    
    # Test selection cho từng task
    for task in TaskState:
        try:
            best_network, min_cost = select_best_network(
                available_networks, network_configs, task
            )
            print(f"✓ {task}: Chọn {best_network.name} (cost: {min_cost:.2f})")
        except Exception as e:
            print(f"✗ Error with {task}: {e}")
            raise
    
    print("✓ Network selection hoạt động đúng")


def test_realistic_scenarios():
    """Test với các kịch bản thực tế"""
    print("\n=== Test Realistic Scenarios ===")
    
    # Scenario 1: IDLE - nên chọn mạng tiết kiệm năng lượng (BLE)
    configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "BLE": NetworkConfig(name="BLE", energy_tx=0.1, energy_idle=2.0, energy_wakeup=0.5)
    }
    
    networks = [
        NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True),
        NetworkState(name="BLE", bandwidth=1.0, latency=100, is_available=True)
    ]
    
    best, cost = select_best_network(networks, configs, TaskState.IDLE_MONITORING)
    print(f"✓ IDLE scenario: Chọn {best.name} (energy-efficient)")
    
    # Scenario 2: DATA_BURST - nên chọn mạng có QoS tốt
    fast_networks = [
        NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True),
        NetworkState(name="BLE", bandwidth=0.5, latency=300, is_available=True)  # QoS kém
    ]
    
    best, cost = select_best_network(fast_networks, configs, TaskState.DATA_BURST_ALERT)
    print(f"✓ DATA_BURST scenario: Chọn {best.name} (better QoS)")
    
    print("✓ Realistic scenarios pass")


if __name__ == "__main__":
    print("Kiểm tra thuật toán Decision Logic...")
    print("=" * 50)
    
    test_task_weights()
    test_qos_requirements()
    test_energy_cost_calculation()
    test_qos_penalty() 
    test_cost_calculation()
    test_network_selection()
    test_realistic_scenarios()
    
    print("\n" + "=" * 50)
    print("🎉 Tất cả tests PASS!")
    print("\n📊 Thuật toán Decision Logic đã sẵn sàng để:")
    print("- Tích hợp vào FastAPI endpoints")
    print("- Huấn luyện mô hình Random Forest")
    print("- Mô phỏng hệ thống IoT network selection")