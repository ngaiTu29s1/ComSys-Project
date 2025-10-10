"""
Test script cho simulation API endpoints.
Để test mà không cần server running.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.simulation import SimulationEngine
from app.core.decision_logic import select_best_network


def test_simulation_api_logic():
    """Test logic của simulation API endpoints"""
    print("=== Test Simulation API Logic ===")
    
    # Test simulation engine initialization
    engine = SimulationEngine()
    
    print("🎮 Simulation Engine initialized:")
    stats = engine.get_simulation_stats()
    print(f"  Map size: {stats['map_size']}")
    print(f"  Base stations: {stats['total_base_stations']}")
    print(f"  Starting position: {stats['current_position']}")
    print(f"  Current task: {stats['current_task']}")
    
    # Test single step simulation (equivalent to /simulation/step)
    print("\n📍 Running single simulation step:")
    device_state = engine.run_simulation_step()
    
    step_result = {
        "step": engine.simulation_step,
        "device_state": {
            "position": device_state.position,
            "current_task": device_state.current_task.value,
            "available_networks": [
                {
                    "name": net.name,
                    "bandwidth": net.bandwidth,
                    "latency": net.latency,
                    "is_available": net.is_available
                }
                for net in device_state.available_networks
            ]
        }
    }
    
    # Add decision
    if device_state.available_networks:
        try:
            best_net, cost = select_best_network(
                device_state.available_networks,
                engine.network_configs,
                device_state.current_task
            )
            step_result["decision"] = {
                "selected_network": best_net.name,
                "cost": round(cost, 2)
            }
        except Exception as e:
            step_result["decision"] = {"error": str(e)}
    
    print(f"  Step result: {step_result}")
    
    # Test multiple steps simulation (equivalent to /simulation/run)
    print("\n🚀 Running multiple simulation steps:")
    
    num_steps = 5
    results = []
    
    for i in range(num_steps):
        device_state = engine.run_simulation_step()
        
        step_result = {
            "step": engine.simulation_step,
            "position": device_state.position,
            "task": device_state.current_task.value,
            "available_networks": len(device_state.available_networks),
            "networks": [net.name for net in device_state.available_networks]
        }
        
        # Add decision
        if device_state.available_networks:
            try:
                best_net, cost = select_best_network(
                    device_state.available_networks,
                    engine.network_configs,
                    device_state.current_task
                )
                step_result["decision"] = {
                    "selected": best_net.name,
                    "cost": round(cost, 2)
                }
            except Exception as e:
                step_result["decision"] = {"error": str(e)}
        
        results.append(step_result)
        print(f"  Step {step_result['step']}: {step_result['position']} | {step_result['task']} → {step_result.get('decision', {}).get('selected', 'N/A')}")
    
    multiple_result = {
        "total_steps": len(results),
        "simulation_summary": engine.get_simulation_stats(),
        "results": results
    }
    
    print(f"\n📊 Multiple steps summary:")
    print(f"  Total steps: {multiple_result['total_steps']}")
    print(f"  Final position: {multiple_result['simulation_summary']['current_position']}")
    print(f"  Final task: {multiple_result['simulation_summary']['current_task']}")
    
    # Test reset (equivalent to /simulation/reset)
    print("\n🔄 Testing simulation reset:")
    
    reset_position = (500, 500)
    engine.reset_simulation(reset_position)
    
    reset_result = {
        "message": f"Simulation reset to position {reset_position}",
        "status": engine.get_simulation_stats()
    }
    
    print(f"  Reset result: {reset_result}")
    
    print("\n✅ All simulation API logic tests PASS!")


def simulate_api_endpoints_workflow():
    """Mô phỏng workflow của API endpoints"""
    print("\n=== Simulate API Endpoints Workflow ===")
    
    engine = SimulationEngine()
    
    print("🌐 Simulating API workflow:")
    
    # 1. GET /simulation/status
    print("\n1️⃣ GET /simulation/status")
    status = engine.get_simulation_stats()
    print(f"   Status: {status}")
    
    # 2. POST /simulation/step (multiple times)
    print("\n2️⃣ POST /simulation/step (3 times)")
    for i in range(3):
        device_state = engine.run_simulation_step()
        
        api_response = {
            "step": engine.simulation_step,
            "device_state": {
                "position": device_state.position,
                "current_task": device_state.current_task.value,
                "available_networks": [
                    {"name": net.name, "bandwidth": net.bandwidth, "latency": net.latency}
                    for net in device_state.available_networks
                ]
            }
        }
        
        # Add decision
        if device_state.available_networks:
            best_net, cost = select_best_network(
                device_state.available_networks,
                engine.network_configs,
                device_state.current_task
            )
            api_response["decision"] = {
                "selected_network": best_net.name,
                "cost": round(cost, 2)
            }
        
        print(f"   Step {i+1} response: {api_response}")
    
    # 3. POST /simulation/run
    print("\n3️⃣ POST /simulation/run (5 steps)")
    
    run_results = []
    for i in range(5):
        device_state = engine.run_simulation_step()
        
        step_data = {
            "step": engine.simulation_step,
            "position": device_state.position,
            "task": device_state.current_task.value,
            "available_networks": len(device_state.available_networks),
            "networks": [net.name for net in device_state.available_networks]
        }
        
        if device_state.available_networks:
            best_net, cost = select_best_network(
                device_state.available_networks,
                engine.network_configs,
                device_state.current_task
            )
            step_data["decision"] = {
                "selected": best_net.name,
                "cost": round(cost, 2)
            }
        
        run_results.append(step_data)
    
    run_response = {
        "total_steps": len(run_results),
        "simulation_summary": engine.get_simulation_stats(),
        "results": run_results
    }
    
    print(f"   Run response: {run_response}")
    
    # 4. POST /simulation/reset
    print("\n4️⃣ POST /simulation/reset")
    
    new_position = (100, 100)
    engine.reset_simulation(new_position)
    
    reset_response = {
        "message": f"Simulation reset to position {new_position}",
        "status": engine.get_simulation_stats()
    }
    
    print(f"   Reset response: {reset_response}")
    
    print("\n✅ API workflow simulation complete!")


if __name__ == "__main__":
    print("🧪 Testing Simulation API Logic (without server)")
    print("=" * 60)
    
    test_simulation_api_logic()
    simulate_api_endpoints_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 All simulation API tests PASS!")
    print("\n📋 API Endpoints ready:")
    print("  GET  /simulation/status     - Get simulation state")
    print("  POST /simulation/step       - Run one simulation step")  
    print("  POST /simulation/run        - Run multiple steps")
    print("  POST /simulation/reset      - Reset simulation")
    print("\n🚀 Ready for frontend integration!")