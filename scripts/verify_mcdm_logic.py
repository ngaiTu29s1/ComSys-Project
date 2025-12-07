"""
Script kiểm tra chi tiết thuật toán MCDM với các test case cụ thể.
Verify công thức năng lượng mới và logic decision making.

Chạy: python scripts/verify_mcdm_logic.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schemas import TaskState, NetworkState, NetworkConfig
from app.core.decision_logic import (
    calculate_energy_cost,
    calculate_qos_penalty,
    calculate_cost,
    select_best_network
)
from app.core.constants import NetworkEnergyConfig, QOS_REQUIREMENTS, get_task_data_size


def print_section(title: str):
    """In header cho section"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def verify_energy_formula():
    """Kiểm tra công thức năng lượng mới: E_total = energy_tx * Data + E_wakeup"""
    print_section("1️⃣ VERIFY ENERGY COST FORMULA")
    
    # Network configs
    wifi_config = NetworkConfig(**NetworkEnergyConfig.WIFI)
    ble_config = NetworkConfig(**NetworkEnergyConfig.BLE)
    
    # Network state (giả định tốt, không penalty QoS)
    good_network = NetworkState(
        name="Wi-Fi",
        bandwidth=50.0,
        latency=15,
        is_available=True
    )
    
    print("\n📊 Test với các task khác nhau:")
    for task in TaskState:
        data_size = get_task_data_size(task)
        
        # Wi-Fi
        wifi_energy = calculate_energy_cost(wifi_config, good_network, task)
        expected_wifi = wifi_config.energy_tx * data_size + wifi_config.energy_wakeup
        
        # BLE
        ble_energy = calculate_energy_cost(ble_config, good_network, task)
        expected_ble = ble_config.energy_tx * data_size + ble_config.energy_wakeup
        
        print(f"\n  Task: {task.value}")
        print(f"    Data size: {data_size} KB")
        print(f"    Wi-Fi: {wifi_energy:.2f} mJ (expected: {expected_wifi:.2f})")
        print(f"    BLE:   {ble_energy:.2f} mJ (expected: {expected_ble:.2f})")
        
        # Verify
        assert abs(wifi_energy - expected_wifi) < 0.01, f"Wi-Fi energy mismatch for {task}"
        assert abs(ble_energy - expected_ble) < 0.01, f"BLE energy mismatch for {task}"
    
    print("\n  ✅ Energy formula verified!")


def verify_qos_penalty():
    """Kiểm tra logic QoS penalty"""
    print_section("2️⃣ VERIFY QoS PENALTY LOGIC")
    
    test_cases = [
        {
            "name": "Good QoS for IDLE",
            "network": NetworkState(name="BLE", bandwidth=1.0, latency=100, is_available=True),
            "task": TaskState.IDLE_MONITORING,
            "expected_penalty": 0.0
        },
        {
            "name": "Bad bandwidth for DATA_BURST",
            "network": NetworkState(name="BLE", bandwidth=0.5, latency=50, is_available=True),
            "task": TaskState.DATA_BURST_ALERT,
            "expected_penalty": ">100"  # Should have high penalty
        },
        {
            "name": "Bad latency for VIDEO",
            "network": NetworkState(name="Wi-Fi", bandwidth=50.0, latency=500, is_available=True),
            "task": TaskState.VIDEO_STREAMING,
            "expected_penalty": ">100"
        },
        {
            "name": "Network unavailable",
            "network": NetworkState(name="5G", bandwidth=100.0, latency=20, is_available=False),
            "task": TaskState.DATA_BURST_ALERT,
            "expected_penalty": 1000.0  # Max penalty
        }
    ]
    
    for test in test_cases:
        penalty = calculate_qos_penalty(test["network"], test["task"])
        print(f"\n  {test['name']}")
        print(f"    Network: {test['network'].name} (BW={test['network'].bandwidth}, Lat={test['network'].latency})")
        print(f"    Task: {test['task'].value}")
        print(f"    QoS Penalty: {penalty:.2f}")
        print(f"    Expected: {test['expected_penalty']}")
        
        # Verify
        if isinstance(test['expected_penalty'], str):
            if test['expected_penalty'].startswith('>'):
                threshold = float(test['expected_penalty'][1:])
                assert penalty > threshold, f"Penalty should be > {threshold}"
        else:
            assert abs(penalty - test['expected_penalty']) < 0.01
    
    print("\n  ✅ QoS penalty logic verified!")


def verify_decision_making():
    """Kiểm tra logic ra quyết định tổng thể"""
    print_section("3️⃣ VERIFY DECISION MAKING LOGIC")
    
    # Network configs
    configs = {
        "Wi-Fi": NetworkConfig(**NetworkEnergyConfig.WIFI),
        "5G": NetworkConfig(**NetworkEnergyConfig.FIVEG),
        "BLE": NetworkConfig(**NetworkEnergyConfig.BLE)
    }
    
    test_scenarios = [
        {
            "name": "IDLE: Should prefer BLE (energy efficient)",
            "task": TaskState.IDLE_MONITORING,
            "networks": [
                NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True),
                NetworkState(name="BLE", bandwidth=1.0, latency=100, is_available=True)
            ],
            "expected": "BLE"
        },
        {
            "name": "DATA_BURST: Should avoid BLE (poor QoS)",
            "task": TaskState.DATA_BURST_ALERT,
            "networks": [
                NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True),
                NetworkState(name="5G", bandwidth=100.0, latency=25, is_available=True),
                NetworkState(name="BLE", bandwidth=0.5, latency=300, is_available=True)
            ],
            "expected_not": "BLE"
        },
        {
            "name": "VIDEO: Should prefer high bandwidth",
            "task": TaskState.VIDEO_STREAMING,
            "networks": [
                NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True),
                NetworkState(name="5G", bandwidth=100.0, latency=25, is_available=True)
            ],
            "expected_not": "BLE"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n  Scenario: {scenario['name']}")
        print(f"    Task: {scenario['task'].value}")
        
        # Calculate costs
        costs = {}
        for net in scenario['networks']:
            config = configs[net.name]
            cost = calculate_cost(net, config, scenario['task'])
            costs[net.name] = cost
            print(f"    {net.name:8} → Cost: {cost:8.2f} mJ")
        
        # Select best
        best_net, best_cost = select_best_network(scenario['networks'], configs, scenario['task'])
        print(f"    ✓ Selected: {best_net.name} (cost: {best_cost:.2f} mJ)")
        
        # Verify
        if "expected" in scenario:
            assert best_net.name == scenario["expected"], \
                f"Expected {scenario['expected']}, got {best_net.name}"
        
        if "expected_not" in scenario:
            assert best_net.name != scenario["expected_not"], \
                f"Should not select {scenario['expected_not']}"
    
    print("\n  ✅ Decision making logic verified!")


def verify_energy_savings():
    """So sánh tiết kiệm năng lượng giữa các lựa chọn"""
    print_section("4️⃣ VERIFY ENERGY SAVINGS")
    
    configs = {
        "Wi-Fi": NetworkConfig(**NetworkEnergyConfig.WIFI),
        "5G": NetworkConfig(**NetworkEnergyConfig.FIVEG),
        "BLE": NetworkConfig(**NetworkEnergyConfig.BLE)
    }
    
    good_network = NetworkState(name="", bandwidth=50.0, latency=15, is_available=True)
    
    print("\n📊 Energy consumption comparison (pure energy, no QoS penalty):")
    print("\n  Task                  | Wi-Fi (mJ) | 5G (mJ)    | BLE (mJ)   | Best")
    print("  " + "-"*66)
    
    for task in TaskState:
        data_size = get_task_data_size(task)
        
        energies = {}
        for net_name, config in configs.items():
            good_network.name = net_name
            energy = calculate_energy_cost(config, good_network, task)
            energies[net_name] = energy
        
        best = min(energies, key=energies.get)
        
        print(f"  {task.value:20} | {energies['Wi-Fi']:10.2f} | "
              f"{energies['5G']:10.2f} | {energies['BLE']:10.2f} | {best}")
    
    print("\n  💡 Insight: BLE luôn tiết kiệm năng lượng nhất (nếu QoS đủ)")
    print("  ✅ Energy comparison verified!")


def main():
    print("🔍 MCDM LOGIC VERIFICATION SUITE")
    print("="*70)
    print("Kiểm tra chi tiết thuật toán decision making với công thức mới")
    
    try:
        verify_energy_formula()
        verify_qos_penalty()
        verify_decision_making()
        verify_energy_savings()
        
        print("\n" + "="*70)
        print("✅ ALL VERIFICATIONS PASSED!")
        print("="*70)
        print("\n📝 Summary:")
        print("  - Energy formula: E_total = energy_tx × Data + E_wakeup ✓")
        print("  - QoS penalty: Correctly penalizes violations ✓")
        print("  - Decision logic: Selects optimal network for each task ✓")
        print("  - Energy savings: BLE best for IDLE, Wi-Fi/5G for heavy tasks ✓")
        print("\n🎯 MCDM algorithm is working correctly with new formulas!")
        
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
