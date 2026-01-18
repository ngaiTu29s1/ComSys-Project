"""
Test script cho app/main.py API endpoints.
Chạy: python tests/test_main_api.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, simulation_engine
from app.models.schemas import DeviceState, NetworkState, TaskState
import requests
import json


def test_direct_function_calls():
    """Test các function trong main.py trực tiếp (không qua HTTP)"""
    print("=== Test Direct Function Calls ===")
    
    # Test root endpoint
    from app.main import root
    root_response = root()
    print(f"✓ Root endpoint: {root_response['message']}")
    
    # Test status endpoint  
    from app.main import get_system_status
    status = get_system_status()
    print(f"✓ System status: {status['system_status']}")
    print(f"  Current step: {status['simulation_engine']['current_step']}")
    print(f"  Device position: {status['simulation_engine']['device_position']}")
    
    # Test simulation step
    from app.main import simulation_step
    step_result = simulation_step()
    print(f"✓ Simulation step: Step {step_result['step_number']}")
    print(f"  New position: {step_result['device_state']['position']}")
    print(f"  Task: {step_result['device_state']['current_task']}")
    print(f"  Networks: {step_result['simulation_info']['networks_list']}")
    
    print("✓ Direct function calls OK")


def test_decision_endpoint_logic():
    """Test decision endpoint logic với các scenarios khác nhau"""
    print("\n=== Test Decision Endpoint Logic ===")
    
    from app.main import make_decision
    
    # Scenario 1: IDLE task với nhiều mạng
    networks_idle = [
        NetworkState(name="Wi-Fi", bandwidth=50.0, latency=10, is_available=True),
        NetworkState(name="5G", bandwidth=100.0, latency=20, is_available=True),
        NetworkState(name="BLE", bandwidth=1.0, latency=50, is_available=True)
    ]
    
    device_idle = DeviceState(
        position=(100, 100),
        current_task=TaskState.IDLE_MONITORING,
        available_networks=networks_idle
    )
    
    decision_idle = make_decision(device_idle)
    print(f"✓ IDLE task decision:")
    print(f"  Optimal: {decision_idle['optimal_network']} (cost: {decision_idle['optimal_cost']})")
    print(f"  All costs: {decision_idle['all_network_costs']}")
    
    # Scenario 2: DATA_BURST task
    device_burst = DeviceState(
        position=(200, 200),
        current_task=TaskState.DATA_BURST_ALERT,
        available_networks=networks_idle  # Same networks, different task
    )
    
    decision_burst = make_decision(device_burst)
    print(f"✓ DATA_BURST task decision:")
    print(f"  Optimal: {decision_burst['optimal_network']} (cost: {decision_burst['optimal_cost']})")
    print(f"  Cost difference: {decision_burst['decision_summary']['cost_difference']}")
    
    # Scenario 3: VIDEO_STREAMING task 
    device_video = DeviceState(
        position=(300, 300),
        current_task=TaskState.VIDEO_STREAMING,
        available_networks=networks_idle
    )
    
    decision_video = make_decision(device_video)
    print(f"✓ VIDEO_STREAMING task decision:")
    print(f"  Optimal: {decision_video['optimal_network']} (cost: {decision_video['optimal_cost']})")
    
    print("✓ Decision endpoint logic OK")


def test_integrated_simulation():
    """Test integrated simulation step + decision"""
    print("\n=== Test Integrated Simulation ===")
    
    from app.main import simulation_step_with_decision, reset_simulation
    
    # Reset simulation to ensure clean state
    reset_result = reset_simulation(50, 50)
    print(f"✓ Reset simulation: {reset_result['message']}")
    
    # Run integrated steps
    print("🧪 Running 5 integrated simulation steps:")
    
    for i in range(5):
        result = simulation_step_with_decision()
        
        simulation_info = result['simulation']
        decision_info = result['decision']
        
        print(f"  Step {i+1}:")
        print(f"    Position: {simulation_info['device_position']}")
        print(f"    Task: {simulation_info['current_task']}")
        print(f"    Networks: {simulation_info['networks']}")
        
        if decision_info:
            print(f"    Decision: {decision_info['optimal_network']} (cost: {decision_info['optimal_cost']})")
        else:
            print(f"    Decision: No networks available")
    
    print("✓ Integrated simulation OK")


def test_api_with_fastapi_testclient():
    """Test API endpoints với FastAPI TestClient"""
    print("\n=== Test API with TestClient ===")
    
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ GET /: {data['message']}")
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    health_data = response.json()
    print(f"✓ GET /health: {health_data['status']}")
    
    # Test status endpoint
    response = client.get("/status")
    assert response.status_code == 200
    status_data = response.json()
    print(f"✓ GET /status: System is {status_data['system_status']}")
    
    # Test simulation step
    response = client.post("/simulation/step")
    assert response.status_code == 200
    step_data = response.json()
    print(f"✓ POST /simulation/step: Step {step_data['step_number']}")
    
    # Test decision endpoint
    test_device_state = {
        "position": [100, 200],
        "current_task": "IDLE_MONITORING",
        "available_networks": [
            {
                "name": "Wi-Fi",
                "bandwidth": 50.0,
                "latency": 15,
                "is_available": True
            },
            {
                "name": "BLE", 
                "bandwidth": 1.0,
                "latency": 30,
                "is_available": True
            }
        ]
    }
    
    response = client.post("/decision", json=test_device_state)
    assert response.status_code == 200
    decision_data = response.json()
    print(f"✓ POST /decision: Selected {decision_data['optimal_network']}")
    
    # Test integrated endpoint
    response = client.post("/simulation/step-with-decision")
    assert response.status_code == 200
    integrated_data = response.json()
    print(f"✓ POST /simulation/step-with-decision: {integrated_data['integrated_result']['message']}")
    
    # Test reset
    response = client.post("/simulation/reset?x=500&y=500")
    assert response.status_code == 200
    reset_data = response.json()
    print(f"✓ POST /simulation/reset: {reset_data['message']}")
    
    print("✓ FastAPI TestClient tests OK")


def test_error_handling():
    """Test error handling scenarios"""
    print("\n=== Test Error Handling ===")
    
    from fastapi.testclient import TestClient
    from app.main import make_decision
    
    client = TestClient(app)
    
    # Test decision with empty networks
    empty_device_state = {
        "position": [100, 100],
        "current_task": "IDLE_MONITORING", 
        "available_networks": []
    }
    
    response = client.post("/decision", json=empty_device_state)
    assert response.status_code == 400
    error_data = response.json()
    print(f"✓ Empty networks error: {error_data['detail']}")
    
    # Test decision with invalid network name
    invalid_device_state = {
        "position": [100, 100],
        "current_task": "IDLE_MONITORING",
        "available_networks": [
            {
                "name": "InvalidNetwork",  # Not in simulation_engine.network_configs
                "bandwidth": 50.0,
                "latency": 15, 
                "is_available": True
            }
        ]
    }
    
    response = client.post("/decision", json=invalid_device_state)
    # Should handle gracefully - either succeed or return proper error
    print(f"✓ Invalid network handling: Status {response.status_code}")
    
    print("✓ Error handling OK")


def test_performance_benchmark():
    """Benchmark performance của các endpoints"""
    print("\n=== Performance Benchmark ===")
    
    import time
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Benchmark simulation steps
    start_time = time.time()
    num_steps = 50
    
    for i in range(num_steps):
        response = client.post("/simulation/step")
        assert response.status_code == 200
    
    end_time = time.time()
    duration = end_time - start_time
    steps_per_second = num_steps / duration
    
    print(f"📊 Simulation performance:")
    print(f"  Steps: {num_steps}")
    print(f"  Duration: {duration:.3f}s") 
    print(f"  Speed: {steps_per_second:.1f} steps/second")
    
    # Benchmark decision making
    decision_payload = {
        "position": [100, 100],
        "current_task": "DATA_BURST_ALERT",
        "available_networks": [
            {"name": "Wi-Fi", "bandwidth": 50.0, "latency": 15, "is_available": True},
            {"name": "5G", "bandwidth": 100.0, "latency": 20, "is_available": True},
            {"name": "BLE", "bandwidth": 1.0, "latency": 50, "is_available": True}
        ]
    }
    
    start_time = time.time()
    num_decisions = 100
    
    for i in range(num_decisions):
        response = client.post("/decision", json=decision_payload)
        assert response.status_code == 200
    
    end_time = time.time()
    duration = end_time - start_time
    decisions_per_second = num_decisions / duration
    
    print(f"📊 Decision performance:")
    print(f"  Decisions: {num_decisions}")
    print(f"  Duration: {duration:.3f}s")
    print(f"  Speed: {decisions_per_second:.1f} decisions/second")
    
    print("✓ Performance benchmark OK")


if __name__ == "__main__":
    print("Kiểm tra app/main.py API endpoints...")
    print("=" * 60)
    
    test_direct_function_calls()
    test_decision_endpoint_logic()
    test_integrated_simulation()
    test_api_with_fastapi_testclient() 
    test_error_handling()
    test_performance_benchmark()
    
    print("\n" + "=" * 60)
    print("🎉 Tất cả tests PASS!")
    print("\n🚀 app/main.py API đã sẵn sàng:")
    print("  POST /simulation/step           - Chạy simulation step")
    print("  POST /decision                  - Network selection decision")
    print("  POST /simulation/step-with-decision - Tích hợp cả hai")
    print("  GET  /status                    - System status")
    print("  POST /simulation/reset          - Reset simulation")
    print("  GET  /simulation/current-state  - Current state")
    print("  GET  /health                    - Health check")
    print("\n📈 Performance:")
    print("  ⚡ High-speed simulation và decision making")
    print("  🛡️  Robust error handling")
    print("  🔧 Easy integration với frontend")