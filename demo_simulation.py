"""
Demo Simulation Engine - showcasing dynamic IoT network selection.

Chạy: python demo_simulation.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from app.services.simulation import SimulationEngine
from app.core.decision_logic import select_best_network
from app.models.schemas import TaskState


def print_header(title: str):
    """In header đẹp cho mỗi section"""
    print("\n" + "=" * 70)
    print(f"🎮 {title}")
    print("=" * 70)


def demo_basic_simulation():
    """Demo cơ bản về simulation engine"""
    print_header("DEMO CƠ BẢN - SIMULATION ENGINE")
    
    # Khởi tạo simulation
    engine = SimulationEngine()
    
    print("🗺️  Khởi tạo môi trường mô phỏng:")
    stats = engine.get_simulation_stats()
    print(f"  📏 Map size: {stats['map_size']}")
    print(f"  📡 Total base stations: {stats['total_base_stations']}")
    print(f"  📍 Starting position: {stats['current_position']}")
    
    print(f"\n📋 Base stations layout:")
    for network_type, stations in engine.base_stations.items():
        print(f"  📡 {network_type}: {stations}")
    
    print(f"\n🔋 Network configurations:")
    for name, config in engine.network_configs.items():
        print(f"  ⚡ {name}: TX={config.energy_tx} mJ/KB, Idle={config.energy_idle} mW")


def demo_movement_simulation():
    """Demo thiết bị di chuyển và network availability thay đổi"""
    print_header("DEMO DI CHUYỂN THIẾT BỊ")
    
    engine = SimulationEngine()
    
    print("🚶‍♂️ Thiết bị di chuyển qua 15 vị trí:")
    
    for i in range(15):
        device_state = engine.run_simulation_step()
        
        print(f"\n📍 Step {i+1}: Position {device_state.position}")
        print(f"  📋 Task: {device_state.current_task.value}")
        print(f"  📶 Available networks ({len(device_state.available_networks)}):")
        
        for net in device_state.available_networks:
            print(f"    📡 {net.name}: {net.bandwidth:.1f} Mbps, {net.latency}ms")
        
        if not device_state.available_networks:
            print("    ⚠️  No networks available!")


def demo_decision_making_during_movement():
    """Demo việc ra quyết định trong quá trình di chuyển"""
    print_header("DEMO RA QUYẾT ĐỊNH TRONG CHUYỂN ĐỘNG")
    
    engine = SimulationEngine()
    
    print("🧠 Thiết bị tự động ra quyết định lựa chọn mạng:")
    
    decision_history = []
    
    for i in range(20):
        device_state = engine.run_simulation_step()
        
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
                    "alternatives": len(device_state.available_networks)
                }
                
                decision_history.append(decision)
                
                print(f"Step {i+1:2d}: {device_state.position} | {device_state.current_task.value:20s} → {best_net.name:5s} (cost: {cost:6.2f}) | {len(device_state.available_networks)} options")
                
            except Exception as e:
                print(f"Step {i+1:2d}: ❌ Decision error: {e}")
        else:
            print(f"Step {i+1:2d}: ⚠️  No networks at {device_state.position}")
    
    # Phân tích decisions
    print(f"\n📊 Phân tích quyết định:")
    
    # Network selection frequency
    network_counts = {}
    task_network_mapping = {}
    
    for decision in decision_history:
        net = decision["selected"]
        task = decision["task"]
        
        network_counts[net] = network_counts.get(net, 0) + 1
        
        if task not in task_network_mapping:
            task_network_mapping[task] = {}
        task_network_mapping[task][net] = task_network_mapping[task].get(net, 0) + 1
    
    print(f"  📡 Network usage:")
    for net, count in network_counts.items():
        percentage = (count / len(decision_history)) * 100
        print(f"    {net}: {count}/{len(decision_history)} ({percentage:.0f}%)")
    
    print(f"  🎯 Task-Network mapping:")
    for task, networks in task_network_mapping.items():
        print(f"    {task}:")
        for net, count in networks.items():
            print(f"      → {net}: {count} times")


def demo_data_collection_scenario():
    """Demo thu thập dữ liệu cho machine learning"""
    print_header("DEMO THU THẬP DỮ LIỆU CHO ML")
    
    engine = SimulationEngine()
    
    print("📊 Collecting training data for Random Forest model...")
    
    training_data = []
    
    # Thu thập 50 data points
    for i in range(50):
        device_state = engine.run_simulation_step()
        
        if device_state.available_networks:
            # Tính toán cost cho tất cả networks
            for net in device_state.available_networks:
                if net.name in engine.network_configs:
                    config = engine.network_configs[net.name]
                    
                    # Tạo feature vector
                    features = {
                        "device_x": device_state.position[0],
                        "device_y": device_state.position[1], 
                        "task": device_state.current_task.value,
                        "network": net.name,
                        "bandwidth": net.bandwidth,
                        "latency": net.latency,
                        "energy_tx": config.energy_tx,
                        "energy_idle": config.energy_idle,
                        "energy_wakeup": config.energy_wakeup
                    }
                    
                    # Label: tính cost bằng thuật toán rule-based
                    try:
                        from app.core.decision_logic import calculate_cost
                        cost = calculate_cost(net, config, device_state.current_task)
                        features["target_cost"] = round(cost, 2)
                        
                        training_data.append(features)
                    except Exception as e:
                        continue
        
        if (i + 1) % 10 == 0:
            print(f"  Collected {len(training_data)} samples after {i+1} steps")
    
    print(f"\n📈 Training data summary:")
    print(f"  Total samples: {len(training_data)}")
    
    # Phân tích data distribution
    task_dist = {}
    network_dist = {}
    
    for sample in training_data:
        task = sample["task"]
        network = sample["network"]
        
        task_dist[task] = task_dist.get(task, 0) + 1
        network_dist[network] = network_dist.get(network, 0) + 1
    
    print(f"  Task distribution:")
    for task, count in task_dist.items():
        print(f"    {task}: {count} samples")
    
    print(f"  Network distribution:")
    for net, count in network_dist.items():
        print(f"    {net}: {count} samples")
    
    # Show mẫu dữ liệu
    print(f"\n🔍 Sample data points:")
    for i in range(min(5, len(training_data))):
        sample = training_data[i]
        print(f"  Sample {i+1}:")
        print(f"    Position: ({sample['device_x']}, {sample['device_y']})")
        print(f"    Task: {sample['task']}")
        print(f"    Network: {sample['network']} | BW: {sample['bandwidth']} Mbps | Latency: {sample['latency']}ms")
        print(f"    Target cost: {sample['target_cost']}")


def demo_performance_benchmark():
    """Demo benchmark hiệu suất simulation"""
    print_header("BENCHMARK HIỆU SUẤT")
    
    print("⚡ Testing simulation performance...")
    
    # Test tốc độ simulation
    engine = SimulationEngine()
    
    start_time = time.time()
    results = engine.run_multiple_steps(100)
    end_time = time.time()
    
    duration = end_time - start_time
    steps_per_second = 100 / duration
    
    print(f"📊 Performance metrics:")
    print(f"  Steps simulated: 100")
    print(f"  Time taken: {duration:.3f} seconds")
    print(f"  Speed: {steps_per_second:.1f} steps/second")
    
    # Test memory usage (approximate)
    import sys
    data_size = sys.getsizeof(results) + sum(sys.getsizeof(r) for r in results)
    print(f"  Memory usage: ~{data_size / 1024:.1f} KB for 100 steps")
    
    # Test decision making speed
    start_time = time.time()
    decisions_made = 0
    
    for state in results:
        if state.available_networks:
            try:
                select_best_network(
                    state.available_networks,
                    engine.network_configs,
                    state.current_task
                )
                decisions_made += 1
            except:
                continue
    
    end_time = time.time()
    decision_duration = end_time - start_time
    decisions_per_second = decisions_made / decision_duration if decision_duration > 0 else 0
    
    print(f"  Decisions made: {decisions_made}/100")
    print(f"  Decision speed: {decisions_per_second:.1f} decisions/second")


def demo_different_scenarios():
    """Demo các kịch bản khác nhau"""
    print_header("DEMO CÁC KỊCH BẢN KHÁC NHAU")
    
    scenarios = [
        {"name": "Urban Dense", "map_size": (500, 500)},
        {"name": "Rural Sparse", "map_size": (2000, 2000)}, 
        {"name": "Campus", "map_size": (800, 800)}
    ]
    
    for scenario in scenarios:
        print(f"\n🏙️ Scenario: {scenario['name']} - Map {scenario['map_size']}")
        
        engine = SimulationEngine(map_size=scenario['map_size'])
        
        # Chạy ngắn để so sánh
        results = engine.run_multiple_steps(10)
        
        # Thống kê networks
        network_availability = {}
        
        for state in results:
            for net in state.available_networks:
                network_availability[net.name] = network_availability.get(net.name, 0) + 1
        
        total_steps = len(results)
        print(f"  Network availability over {total_steps} steps:")
        
        for net, count in network_availability.items():
            availability_rate = (count / total_steps) * 100
            print(f"    📡 {net}: {availability_rate:.0f}% availability")


def main():
    """Chạy toàn bộ demo simulation"""
    print("🎮 DEMO SIMULATION ENGINE - IOT NETWORK SELECTION")
    print("Dynamic simulation with realistic network conditions")
    
    demo_basic_simulation()
    demo_movement_simulation() 
    demo_decision_making_during_movement()
    demo_data_collection_scenario()
    demo_performance_benchmark()
    demo_different_scenarios()
    
    print_header("KẾT LUẬN")
    print("🎉 Demo simulation hoàn tất!")
    
    print("\n✅ Simulation Engine capabilities:")
    print("  🗺️  Realistic environment với base stations")
    print("  🚶‍♂️ Device movement với QoS thay đổi theo khoảng cách")
    print("  🧠 Tích hợp với decision logic algorithm")
    print("  📊 Thu thập dữ liệu training cho ML")
    print("  ⚡ Performance tốt cho real-time simulation")
    print("  🎯 Support nhiều scenarios khác nhau")
    
    print("\n📈 Ứng dụng thực tế:")
    print("  1. Training Random Forest model")
    print("  2. Benchmark các thuật toán network selection")
    print("  3. Demo real-time cho khách hàng") 
    print("  4. Research & development IoT protocols")
    print("  5. Tối ưu hóa network deployment")


if __name__ == "__main__":
    main()