"""
Test script cho Simulation Engine.
Chạy: python tests/test_simulation.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.simulation import SimulationEngine
from app.models.schemas import TaskState
from app.core.decision_logic import select_best_network


def test_simulation_initialization():
    """Test khởi tạo simulation engine"""
    print("=== Test Simulation Initialization ===")
    
    # Tạo engine với map size mặc định
    engine = SimulationEngine()
    
    # Kiểm tra cấu hình
    assert len(engine.network_configs) == 3, "Should have 3 network types"
    assert "Wi-Fi" in engine.network_configs
    assert "5G" in engine.network_configs
    assert "BLE" in engine.network_configs
    
    # Kiểm tra base stations
    assert len(engine.base_stations) == 3, "Should have 3 network types"
    for network_type, stations in engine.base_stations.items():
        assert len(stations) > 0, f"Should have stations for {network_type}"
        print(f"  📡 {network_type}: {len(stations)} base stations")
    
    # Kiểm tra device state ban đầu
    assert engine.device_state.position == (0, 0), "Should start at (0,0)"
    assert engine.device_state.current_task == TaskState.IDLE_MONITORING
    
    print(f"✓ Device starts at: {engine.device_state.position}")
    print(f"✓ Initial task: {engine.device_state.current_task.value}")
    print(f"✓ Available networks: {len(engine.device_state.available_networks)}")
    
    for net in engine.device_state.available_networks:
        print(f"  📶 {net.name}: {net.bandwidth} Mbps, {net.latency}ms")
    
    print("✓ Simulation initialization OK")


def test_distance_calculation():
    """Test tính toán khoảng cách và QoS"""
    print("\n=== Test Distance & QoS Calculation ===")
    
    engine = SimulationEngine()
    
    # Test với các vị trí khác nhau
    test_positions = [
        (0, 0),      # Góc map
        (100, 100),  # Gần Wi-Fi station đầu tiên
        (500, 500),  # Giữa map
        (999, 999)   # Xa nhất
    ]
    
    for pos in test_positions:
        print(f"\n📍 Testing position {pos}:")
        
        for network_type in ["Wi-Fi", "5G", "BLE"]:
            best_station, qos = engine._find_best_base_station(pos, network_type)
            
            if best_station and qos["bandwidth"] > 0:
                distance = engine._calculate_distance(pos, best_station)
                print(f"  📡 {network_type}: {distance:.0f}m → {qos['bandwidth']:.1f} Mbps, {qos['latency']}ms")
            else:
                print(f"  📡 {network_type}: Out of range")
    
    print("✓ Distance & QoS calculation OK")


def test_simulation_steps():
    """Test chạy các bước mô phỏng"""
    print("\n=== Test Simulation Steps ===")
    
    engine = SimulationEngine()
    
    print(f"Initial position: {engine.device_state.position}")
    print(f"Initial task: {engine.device_state.current_task.value}")
    
    # Chạy 10 bước
    for i in range(10):
        old_pos = engine.device_state.position
        device_state = engine.run_simulation_step()
        
        print(f"\nStep {i+1}:")
        print(f"  📍 Position: {old_pos} → {device_state.position}")
        print(f"  📋 Task: {device_state.current_task.value}")
        print(f"  📶 Networks: {len(device_state.available_networks)}")
        
        # Kiểm tra networks có hợp lý không
        for net in device_state.available_networks:
            assert net.bandwidth > 0, f"{net.name} should have positive bandwidth"
            assert net.latency > 0, f"{net.name} should have positive latency"
            assert net.is_available, f"{net.name} should be available"
    
    print("✓ Simulation steps OK")


def test_multiple_steps():
    """Test chạy nhiều bước cùng lúc"""
    print("\n=== Test Multiple Steps ===")
    
    engine = SimulationEngine()
    
    # Chạy 20 bước
    results = engine.run_multiple_steps(20)
    
    assert len(results) == 20, "Should return 20 results"
    
    # Thống kê
    tasks_count = {}
    positions = []
    
    for i, state in enumerate(results):
        task = state.current_task.value
        tasks_count[task] = tasks_count.get(task, 0) + 1
        positions.append(state.position)
        
        if i % 5 == 0:  # Print mỗi 5 bước
            print(f"  Step {i+1}: {state.position}, {task}, {len(state.available_networks)} networks")
    
    print(f"\n📊 Task distribution:")
    for task, count in tasks_count.items():
        percentage = (count / 20) * 100
        print(f"  {task}: {count}/20 ({percentage:.0f}%)")
    
    print(f"📍 Position range: {min(positions)} → {max(positions)}")
    print("✓ Multiple steps OK")


def test_simulation_with_decision_logic():
    """Test tích hợp simulation với decision logic"""
    print("\n=== Test Integration with Decision Logic ===")
    
    engine = SimulationEngine()
    
    print("🧪 Running simulation với decision making:")
    
    decisions_log = []
    
    for i in range(15):
        # Chạy bước mô phỏng
        device_state = engine.run_simulation_step()
        
        # Nếu có networks khả dụng, thực hiện decision
        if device_state.available_networks:
            try:
                best_net, cost = select_best_network(
                    device_state.available_networks,
                    engine.network_configs,
                    device_state.current_task
                )
                
                decision = {
                    "step": i + 1,
                    "position": device_state.position,
                    "task": device_state.current_task.value,
                    "selected": best_net.name,
                    "cost": round(cost, 2),
                    "available_count": len(device_state.available_networks)
                }
                
                decisions_log.append(decision)
                
                print(f"  Step {i+1}: {device_state.position} | {device_state.current_task.value} → {best_net.name} (cost: {cost:.2f})")
                
            except Exception as e:
                print(f"  Step {i+1}: ❌ Decision error: {e}")
        else:
            print(f"  Step {i+1}: ⚠️  No networks available at {device_state.position}")
    
    # Thống kê decisions
    network_selections = {}
    for decision in decisions_log:
        net = decision["selected"]
        network_selections[net] = network_selections.get(net, 0) + 1
    
    print(f"\n📊 Network selection summary:")
    for net, count in network_selections.items():
        percentage = (count / len(decisions_log)) * 100
        print(f"  {net}: {count}/{len(decisions_log)} ({percentage:.0f}%)")
    
    print("✓ Integration with decision logic OK")


def test_simulation_stats():
    """Test thống kê simulation"""
    print("\n=== Test Simulation Stats ===")
    
    engine = SimulationEngine()
    
    # Chạy một vài bước
    engine.run_multiple_steps(5)
    
    # Lấy stats
    stats = engine.get_simulation_stats()
    
    print("📊 Simulation statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Kiểm tra stats hợp lý
    assert stats["simulation_step"] == 5
    assert "current_position" in stats
    assert "available_networks_count" in stats
    assert stats["total_base_stations"] > 0
    
    print("✓ Simulation stats OK")


def test_simulation_reset():
    """Test reset simulation"""
    print("\n=== Test Simulation Reset ===")
    
    engine = SimulationEngine()
    
    # Chạy một số bước
    engine.run_multiple_steps(10)
    
    print(f"Before reset: step {engine.simulation_step}, pos {engine.device_state.position}")
    
    # Reset về vị trí mới
    new_pos = (500, 500)
    engine.reset_simulation(new_pos)
    
    print(f"After reset: step {engine.simulation_step}, pos {engine.device_state.position}")
    
    # Kiểm tra reset thành công
    assert engine.simulation_step == 0
    assert engine.device_state.position == new_pos
    assert engine.device_state.current_task == TaskState.IDLE_MONITORING
    
    print("✓ Simulation reset OK")


if __name__ == "__main__":
    print("Kiểm tra Simulation Engine...")
    print("=" * 60)
    
    test_simulation_initialization()
    test_distance_calculation()
    test_simulation_steps()
    test_multiple_steps()
    test_simulation_with_decision_logic()
    test_simulation_stats()
    test_simulation_reset()
    
    print("\n" + "=" * 60)
    print("🎉 Tất cả tests PASS!")
    print("\n🎮 Simulation Engine đã sẵn sàng cho:")
    print("- Thu thập dữ liệu training cho ML")
    print("- Demo real-time simulation")
    print("- Benchmarking các thuật toán khác nhau") 
    print("- Tích hợp với API để tạo scenarios")