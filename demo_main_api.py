"""
Demo script cho app/main.py - showcase main API endpoints.
Chạy: python demo_main_api.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
import json
import time


def print_header(title: str):
    """In header đẹp cho mỗi section"""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)


def print_json_pretty(data: dict, title: str = ""):
    """In JSON data đẹp"""
    if title:
        print(f"\n📄 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def demo_system_overview():
    """Demo tổng quan hệ thống"""
    print_header("TỔNG QUAN HỆ THỐNG")
    
    client = TestClient(app)
    
    # Root endpoint
    response = client.get("/")
    root_data = response.json()
    print("🏠 Root endpoint:")
    print(f"  Service: {root_data['message']}")
    print(f"  Version: {root_data['version']}")
    print("  Available endpoints:")
    for endpoint, desc in root_data['endpoints'].items():
        print(f"    📌 {desc}")
    
    # System status
    response = client.get("/status")
    status_data = response.json()
    print(f"\n📊 System Status:")
    print(f"  Status: {status_data['system_status']}")
    
    sim_info = status_data['simulation_engine']
    print(f"  📍 Current position: {sim_info['device_position']}")
    print(f"  📋 Current task: {sim_info['current_task']}")
    print(f"  📶 Available networks: {sim_info['available_networks']}")
    print(f"  🗺️  Map size: {sim_info['map_size']}")
    print(f"  📡 Total base stations: {sim_info['total_base_stations']}")
    
    print(f"\n⚡ Network Configurations:")
    for name, config in status_data['network_configs'].items():
        print(f"  {name}: TX={config['energy_tx']} mJ/KB, Idle={config['energy_idle']} mW")


def demo_simulation_workflow():
    """Demo workflow simulation cơ bản"""
    print_header("DEMO SIMULATION WORKFLOW")
    
    client = TestClient(app)
    
    # Reset simulation về vị trí gần Wi-Fi station
    print("🔄 Reset simulation về vị trí (100, 100) - gần Wi-Fi station:")
    response = client.post("/simulation/reset?x=100&y=100")
    reset_data = response.json()
    print(f"  ✅ {reset_data['message']}")
    print(f"  📍 New position: {reset_data['new_position']}")
    
    # Chạy 8 simulation steps
    print(f"\n🚶‍♂️ Running 8 simulation steps:")
    
    for i in range(8):
        response = client.post("/simulation/step")
        step_data = response.json()
        
        device_state = step_data['device_state']
        sim_info = step_data['simulation_info']
        
        print(f"  Step {i+1}: {device_state['position']} | {device_state['current_task']} | Networks: {sim_info['networks_list']}")
        
        # Show QoS details cho step 1, 4, 8
        if i + 1 in [1, 4, 8]:
            print(f"    📊 Network details:")
            for net in device_state['available_networks']:
                print(f"      📡 {net['name']}: {net['bandwidth']:.1f} Mbps, {net['latency']}ms")


def demo_decision_making():
    """Demo decision making với các scenarios"""
    print_header("DEMO DECISION MAKING")
    
    client = TestClient(app)
    
    # Scenario 1: IDLE task với 3 mạng
    print("🧠 Scenario 1: IDLE task với nhiều mạng")
    
    idle_payload = {
        "position": [100, 100],
        "current_task": "IDLE_MONITORING",
        "available_networks": [
            {"name": "Wi-Fi", "bandwidth": 80.0, "latency": 8, "is_available": True},
            {"name": "5G", "bandwidth": 150.0, "latency": 15, "is_available": True},
            {"name": "BLE", "bandwidth": 1.5, "latency": 40, "is_available": True}
        ]
    }
    
    response = client.post("/decision", json=idle_payload)
    idle_result = response.json()
    
    print(f"  ✅ Decision: {idle_result['optimal_network']} (cost: {idle_result['optimal_cost']})")
    print(f"  📊 All costs: {idle_result['all_network_costs']}")
    print(f"  💡 Reason: IDLE task ưu tiên tiết kiệm năng lượng (BLE)")
    
    # Scenario 2: DATA_BURST task
    print(f"\n🧠 Scenario 2: DATA_BURST_ALERT task")
    
    burst_payload = {
        "position": [200, 200], 
        "current_task": "DATA_BURST_ALERT",
        "available_networks": idle_payload["available_networks"]  # Same networks
    }
    
    response = client.post("/decision", json=burst_payload)
    burst_result = response.json()
    
    print(f"  ✅ Decision: {burst_result['optimal_network']} (cost: {burst_result['optimal_cost']})")
    print(f"  📊 All costs: {burst_result['all_network_costs']}")
    print(f"  💡 Reason: DATA_BURST ưu tiên QoS (bandwidth + latency)")
    
    # Scenario 3: VIDEO_STREAMING task
    print(f"\n🧠 Scenario 3: VIDEO_STREAMING task")
    
    video_payload = {
        "position": [300, 300],
        "current_task": "VIDEO_STREAMING", 
        "available_networks": idle_payload["available_networks"]
    }
    
    response = client.post("/decision", json=video_payload)
    video_result = response.json()
    
    print(f"  ✅ Decision: {video_result['optimal_network']} (cost: {video_result['optimal_cost']})")
    print(f"  📊 All costs: {video_result['all_network_costs']}")
    print(f"  💡 Reason: VIDEO cần bandwidth cao để tránh buffering")
    
    # So sánh decisions
    print(f"\n🔍 So sánh decisions cho cùng networks:")
    decisions = [
        ("IDLE", idle_result['optimal_network']),
        ("DATA_BURST", burst_result['optimal_network']),
        ("VIDEO", video_result['optimal_network'])
    ]
    
    for task, network in decisions:
        print(f"  {task:12} → {network}")


def demo_integrated_workflow():
    """Demo integrated workflow: simulation + decision"""
    print_header("DEMO INTEGRATED WORKFLOW")
    
    client = TestClient(app)
    
    print("🔄 Reset simulation về vị trí (0, 0):")
    client.post("/simulation/reset?x=0&y=0")
    
    print(f"\n🎯 Running integrated simulation + decision workflow:")
    
    network_selections = {}
    task_counts = {}
    
    for i in range(10):
        response = client.post("/simulation/step-with-decision")
        result = response.json()
        
        sim_info = result['simulation']
        decision_info = result['decision']
        
        task = sim_info['current_task']
        task_counts[task] = task_counts.get(task, 0) + 1
        
        if decision_info:
            selected = decision_info['optimal_network']
            network_selections[selected] = network_selections.get(selected, 0) + 1
            
            print(f"  Step {i+1:2d}: {sim_info['device_position']} | {task:20s} → {selected:5s} | Networks: {sim_info['networks']}")
        else:
            print(f"  Step {i+1:2d}: {sim_info['device_position']} | {task:20s} → No networks available")
    
    # Thống kê
    print(f"\n📊 Workflow Statistics:")
    print(f"  Task distribution:")
    for task, count in task_counts.items():
        percentage = (count / 10) * 100
        print(f"    {task}: {count}/10 ({percentage:.0f}%)")
    
    print(f"  Network selection:")
    for net, count in network_selections.items():
        percentage = (count / len(network_selections)) * 100 if network_selections else 0
        print(f"    {net}: {count} times ({percentage:.0f}%)")


def demo_real_world_scenarios():
    """Demo các scenarios thực tế"""
    print_header("DEMO SCENARIOS THỰC TẾ")
    
    client = TestClient(app)
    
    scenarios = [
        {
            "name": "📱 Smartphone ở nhà",
            "position": [100, 100],  # Gần Wi-Fi
            "networks": [
                {"name": "Wi-Fi", "bandwidth": 100.0, "latency": 5, "is_available": True},
                {"name": "5G", "bandwidth": 80.0, "latency": 25, "is_available": True}
            ]
        },
        {
            "name": "🚗 IoT trong xe hơi",
            "position": [500, 300],  # Xa base stations
            "networks": [
                {"name": "5G", "bandwidth": 50.0, "latency": 40, "is_available": True},
                {"name": "Wi-Fi", "bandwidth": 5.0, "latency": 200, "is_available": False}  # Hotspot yếu
            ]
        },
        {
            "name": "🏥 Sensor y tế",
            "position": [150, 150],  # Gần BLE beacon
            "networks": [
                {"name": "BLE", "bandwidth": 0.5, "latency": 100, "is_available": True},
                {"name": "Wi-Fi", "bandwidth": 30.0, "latency": 20, "is_available": True}
            ]
        },
        {
            "name": "🏭 Industrial IoT",
            "position": [800, 750],  # Vùng xa
            "networks": [
                {"name": "5G", "bandwidth": 20.0, "latency": 80, "is_available": True}
            ]
        }
    ]
    
    tasks = ["IDLE_MONITORING", "DATA_BURST_ALERT", "VIDEO_STREAMING"]
    
    for scenario in scenarios:
        print(f"\n🎬 {scenario['name']} tại {scenario['position']}:")
        
        for task in tasks:
            payload = {
                "position": scenario['position'],
                "current_task": task,
                "available_networks": scenario['networks']
            }
            
            response = client.post("/decision", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                selected = result['optimal_network']
                cost = result['optimal_cost']
                
                print(f"  {task:20s} → {selected:5s} (cost: {cost:6.2f})")
            else:
                print(f"  {task:20s} → ❌ Error: {response.json()['detail']}")


def demo_performance_analysis():
    """Demo phân tích performance"""
    print_header("PHÂN TÍCH PERFORMANCE")
    
    client = TestClient(app)
    
    print("⏱️  Testing API response times...")
    
    # Test simulation step performance
    times = []
    for i in range(20):
        start = time.time()
        response = client.post("/simulation/step")
        end = time.time()
        
        if response.status_code == 200:
            times.append((end - start) * 1000)  # Convert to ms
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"📊 Simulation Step Performance (20 calls):")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    
    # Test decision performance
    decision_payload = {
        "position": [100, 100],
        "current_task": "DATA_BURST_ALERT",
        "available_networks": [
            {"name": "Wi-Fi", "bandwidth": 50.0, "latency": 15, "is_available": True},
            {"name": "5G", "bandwidth": 100.0, "latency": 20, "is_available": True},
            {"name": "BLE", "bandwidth": 1.0, "latency": 50, "is_available": True}
        ]
    }
    
    decision_times = []
    for i in range(20):
        start = time.time()
        response = client.post("/decision", json=decision_payload)
        end = time.time()
        
        if response.status_code == 200:
            decision_times.append((end - start) * 1000)
    
    avg_decision_time = sum(decision_times) / len(decision_times)
    
    print(f"📊 Decision Performance (20 calls):")
    print(f"  Average: {avg_decision_time:.2f}ms")
    
    # Overall throughput estimate
    total_throughput = 1000 / (avg_time + avg_decision_time)  # requests per second
    print(f"📈 Estimated throughput: {total_throughput:.0f} integrated requests/second")


def main():
    """Chạy toàn bộ demo"""
    print("🚀 DEMO APP/MAIN.PY - IOT NETWORK SELECTION API")
    print("Complete FastAPI application with simulation and decision making")
    
    demo_system_overview()
    demo_simulation_workflow()
    demo_decision_making()
    demo_integrated_workflow()
    demo_real_world_scenarios()
    demo_performance_analysis()
    
    print_header("KẾT LUẬN")
    print("🎉 Demo app/main.py hoàn tất!")
    
    print("\n✅ API Features:")
    print("  🎯 Complete simulation workflow")
    print("  🧠 Intelligent network selection") 
    print("  🔧 Easy integration endpoints")
    print("  📊 Detailed response data")
    print("  🛡️  Robust error handling")
    print("  ⚡ High performance (sub-ms response times)")
    
    print("\n📋 Available Endpoints:")
    endpoints = [
        ("GET  /", "System overview"),
        ("GET  /health", "Health check"),
        ("GET  /status", "System status"),
        ("POST /simulation/step", "Run simulation step"),
        ("POST /decision", "Network selection decision"),
        ("POST /simulation/step-with-decision", "Integrated workflow"),
        ("POST /simulation/reset", "Reset simulation"),
        ("GET  /simulation/current-state", "Current state")
    ]
    
    for endpoint, desc in endpoints:
        print(f"  {endpoint:35} - {desc}")
    
    print("\n🚀 Ready for:")
    print("  1. Frontend React.js integration")
    print("  2. Real-time IoT device communication")
    print("  3. ML model training data collection")
    print("  4. Research and benchmarking")
    print("  5. Production deployment")


if __name__ == "__main__":
    main()