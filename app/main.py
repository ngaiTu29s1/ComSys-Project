"""
Main FastAPI application cho hệ thống IoT Network Selection.

File này chứa các endpoint chính để:
- Chạy simulation steps
- Thực hiện network decision making
- Tích hợp giữa simulation engine và decision logic
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
import os
from app.models.schemas import DeviceState, NetworkState, TaskState
from app.core.decision_logic import calculate_cost, select_best_network
from app.services.simulation import SimulationEngine

# Khởi tạo FastAPI app
app = FastAPI(
    title="IoT Network Selection System",
    version="1.0.0", 
    description="API for IoT device network selection using MCDM algorithm and simulation"
)

# Add CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for web UI
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_dir):
    app.mount("/static", StaticFiles(directory=web_dir), name="static")

# Khởi tạo instance của SimulationEngine
simulation_engine = SimulationEngine()

print("🚀 IoT Network Selection API initialized")
print(f"📡 Simulation engine ready with {len(simulation_engine.network_configs)} network types")


@app.get("/")
def root():
    """Root endpoint với thông tin hệ thống"""
    return {
        "message": "IoT Network Selection System API",
        "version": "1.0.0",
        "endpoints": {
            "simulation": "/simulation/step - Run simulation step",
            "decision": "/decision - Make network selection decision", 
            "status": "/status - Get system status",
            "web_ui": "/ui - Access web-based map visualization"
        }
    }


@app.get("/ui")
def web_ui():
    """Serve the web UI for map visualization"""
    web_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "index.html")
    if os.path.exists(web_file):
        return FileResponse(web_file)
    else:
        raise HTTPException(status_code=404, detail="Web UI not found")


@app.get("/map")
def map_data():
    """Get map data for visualization including base stations and current device state"""
    stats = simulation_engine.get_simulation_stats()
    
    # Get base stations data from simulation engine
    base_stations = []
    
    # Wi-Fi stations
    for i in range(4):
        base_stations.append({
            "id": f"wifi_{i}",
            "type": "Wi-Fi",
            "position": simulation_engine.base_stations["Wi-Fi"][i],
            "color": "#2196F3"
        })
    
    # 5G stations  
    for i in range(4):
        base_stations.append({
            "id": f"5g_{i}",
            "type": "5G", 
            "position": simulation_engine.base_stations["5G"][i],
            "color": "#9C27B0"
        })
        
    # BLE stations
    for i in range(4):
        base_stations.append({
            "id": f"ble_{i}",
            "type": "BLE",
            "position": simulation_engine.base_stations["BLE"][i], 
            "color": "#FF9800"
        })
    
    return {
        "map_size": stats["map_size"],
        "base_stations": base_stations,
        "device_state": {
            "position": stats["current_position"],
            "current_task": stats["current_task"],
            "available_networks": stats["available_networks"]
        },
        "simulation_step": stats["simulation_step"]
    }
    """Root endpoint với thông tin hệ thống"""
    return {
        "message": "IoT Network Selection System API",
        "version": "1.0.0",
        "endpoints": {
            "simulation": "/simulation/step - Run simulation step",
            "decision": "/decision - Make network selection decision", 
            "status": "/status - Get system status"
        }
    }


@app.get("/status")
def get_system_status():
    """Lấy trạng thái tổng quát của hệ thống"""
    simulation_stats = simulation_engine.get_simulation_stats()
    
    return {
        "system_status": "operational",
        "simulation_engine": {
            "current_step": simulation_stats["simulation_step"],
            "device_position": simulation_stats["current_position"],
            "current_task": simulation_stats["current_task"],
            "available_networks": simulation_stats["available_networks"],
            "map_size": simulation_stats["map_size"],
            "total_base_stations": simulation_stats["total_base_stations"]
        },
        "network_configs": {
            name: {
                "energy_tx": config.energy_tx,
                "energy_idle": config.energy_idle,
                "energy_wakeup": config.energy_wakeup
            }
            for name, config in simulation_engine.network_configs.items()
        }
    }


@app.post("/simulation/step")
def simulation_step() -> Dict:
    """
    Endpoint để chạy một bước mô phỏng.
    
    Gọi phương thức run_simulation_step() của SimulationEngine 
    và trả về DeviceState mới cùng với thống kê.
    
    Returns:
        Dict chứa DeviceState mới và thông tin bước mô phỏng
    """
    try:
        # Chạy một bước mô phỏng
        new_device_state = simulation_engine.run_simulation_step()
        
        # Chuẩn bị response data
        response_data = {
            "step_number": simulation_engine.simulation_step,
            "device_state": {
                "position": new_device_state.position,
                "current_task": new_device_state.current_task.value,
                "available_networks": [
                    {
                        "name": network.name,
                        "bandwidth": network.bandwidth,
                        "latency": network.latency,
                        "is_available": network.is_available
                    }
                    for network in new_device_state.available_networks
                ]
            },
            "simulation_info": {
                "networks_count": len(new_device_state.available_networks),
                "networks_list": [net.name for net in new_device_state.available_networks]
            }
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Simulation step failed: {str(e)}"
        )


@app.post("/decision")
def make_decision(device_state: DeviceState) -> Dict:
    """
    Endpoint để thực hiện quyết định lựa chọn mạng.
    
    Nhận vào một DeviceState, tính chi phí cho tất cả mạng khả dụng
    và trả về mạng có chi phí thấp nhất.
    
    Args:
        device_state: Trạng thái thiết bị với danh sách mạng khả dụng
        
    Returns:
        Dict chứa tên mạng tối ưu và thông tin chi tiết
    """
    try:
        # Kiểm tra có mạng khả dụng không
        if not device_state.available_networks:
            raise HTTPException(
                status_code=400,
                detail="No available networks in device state"
            )
        
        # Dictionary để lưu chi phí của từng mạng
        network_costs = {}
        cost_details = {}
        
        # Lặp qua danh sách available_networks
        for network in device_state.available_networks:
            network_name = network.name
            
            # Kiểm tra network config có tồn tại không
            if network_name not in simulation_engine.network_configs:
                print(f"⚠️  Warning: No config found for network {network_name}, skipping...")
                continue
            
            # Lấy network config
            network_config = simulation_engine.network_configs[network_name]
            
            # Tính chi phí cho mạng này
            cost = calculate_cost(
                network_state=network,
                network_config=network_config,
                task=device_state.current_task
            )
            
            network_costs[network_name] = cost
            
            # Lưu chi tiết cho debugging
            cost_details[network_name] = {
                "total_cost": round(cost, 2),
                "network_info": {
                    "bandwidth": network.bandwidth,
                    "latency": network.latency,
                    "is_available": network.is_available
                },
                "config_info": {
                    "energy_tx": network_config.energy_tx,
                    "energy_idle": network_config.energy_idle,
                    "energy_wakeup": network_config.energy_wakeup
                }
            }
        
        # Kiểm tra có mạng nào được tính toán không
        if not network_costs:
            raise HTTPException(
                status_code=400,
                detail="No valid networks found for cost calculation"
            )
        
        # Tìm mạng có chi phí thấp nhất
        optimal_network = min(network_costs, key=network_costs.get)
        optimal_cost = network_costs[optimal_network]
        
        # Chuẩn bị response
        response_data = {
            "optimal_network": optimal_network,
            "optimal_cost": round(optimal_cost, 2),
            "device_info": {
                "position": device_state.position,
                "current_task": device_state.current_task.value
            },
            "all_network_costs": {
                name: round(cost, 2) 
                for name, cost in network_costs.items()
            },
            "cost_analysis": cost_details,
            "decision_summary": {
                "total_networks_evaluated": len(network_costs),
                "cost_difference": round(
                    max(network_costs.values()) - min(network_costs.values()), 2
                ) if len(network_costs) > 1 else 0,
                "algorithm": "MCDM_Energy_QoS"
            }
        }
        
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Decision making failed: {str(e)}"
        )


@app.post("/simulation/step-with-decision")
def simulation_step_with_decision() -> Dict:
    """
    Endpoint tích hợp: chạy simulation step + decision making trong một call.
    
    Tiện lợi cho việc demo và testing.
    
    Returns:
        Dict chứa kết quả simulation và decision
    """
    try:
        # Chạy simulation step
        new_device_state = simulation_engine.run_simulation_step()
        
        # Thực hiện decision nếu có mạng khả dụng
        decision_result = None
        if new_device_state.available_networks:
            # Gọi nội bộ hàm decision
            decision_result = make_decision(new_device_state)
        
        # Kết hợp kết quả
        response_data = {
            "step_number": simulation_engine.simulation_step,
            "simulation": {
                "device_position": new_device_state.position,
                "current_task": new_device_state.current_task.value,
                "available_networks_count": len(new_device_state.available_networks),
                "networks": [net.name for net in new_device_state.available_networks]
            },
            "decision": decision_result,
            "integrated_result": {
                "success": decision_result is not None,
                "message": "Network selected successfully" if decision_result else "No networks available"
            }
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Integrated simulation failed: {str(e)}"
        )


@app.post("/simulation/reset")  
def reset_simulation(x: int = 0, y: int = 0) -> Dict:
    """
    Reset simulation về vị trí mới.
    
    Args:
        x: Tọa độ x mới (default: 0)
        y: Tọa độ y mới (default: 0)
        
    Returns:
        Dict với trạng thái sau khi reset
    """
    try:
        new_position = (x, y)
        simulation_engine.reset_simulation(new_position)
        
        return {
            "message": f"Simulation reset successfully",
            "new_position": new_position,
            "system_status": simulation_engine.get_simulation_stats()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reset simulation failed: {str(e)}"
        )


@app.get("/simulation/current-state")
def get_current_simulation_state() -> Dict:
    """
    Lấy trạng thái hiện tại của simulation mà không chạy step mới.
    
    Returns:
        Dict với trạng thái hiện tại
    """
    try:
        current_state = simulation_engine.device_state
        stats = simulation_engine.get_simulation_stats()
        
        return {
            "current_device_state": {
                "position": current_state.position,
                "current_task": current_state.current_task.value,
                "available_networks": [
                    {
                        "name": net.name,
                        "bandwidth": net.bandwidth,
                        "latency": net.latency,
                        "is_available": net.is_available
                    }
                    for net in current_state.available_networks
                ]
            },
            "simulation_stats": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get current state: {str(e)}"
        )


# Health check endpoint
@app.get("/health")
def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "service": "IoT Network Selection API",
        "version": "1.0.0"
    }