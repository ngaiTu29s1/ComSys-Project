from fastapi import FastAPI, HTTPException
from typing import Dict, List
from pydantic import BaseModel
from app.models.schemas import TaskState, NetworkState, NetworkConfig, DeviceState
from app.core.decision_logic import select_best_network, calculate_cost
from app.services.simulation import SimulationEngine

app = FastAPI(
    title="IoT Network Selection API", 
    version="0.2.0",
    description="API cho hệ thống mô phỏng lựa chọn mạng tiết kiệm năng lượng cho thiết bị IoT"
)

# Cấu hình mặc định các loại mạng (có thể load từ file config)
DEFAULT_NETWORK_CONFIGS: Dict[str, NetworkConfig] = {
    "Wi-Fi": NetworkConfig(
        name="Wi-Fi",
        energy_tx=0.5,      # mJ/KB
        energy_idle=10.0,   # mW
        energy_wakeup=2.0   # mJ
    ),
    "5G": NetworkConfig(
        name="5G", 
        energy_tx=1.2,      # mJ/KB
        energy_idle=15.0,   # mW
        energy_wakeup=5.0   # mJ
    ),
    "BLE": NetworkConfig(
        name="BLE",
        energy_tx=0.1,      # mJ/KB
        energy_idle=2.0,    # mW
        energy_wakeup=0.5   # mJ
    )
}

# Global simulation engine instance
simulation_engine = SimulationEngine()


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "version": "0.2.0"}


@app.get("/network-configs")
def get_network_configs() -> Dict[str, NetworkConfig]:
    """Lấy danh sách cấu hình các loại mạng"""
    return DEFAULT_NETWORK_CONFIGS


@app.post("/decide")
def decide_network(device_state: DeviceState) -> dict:
    """
    API chính để lựa chọn mạng tối ưu cho thiết bị IoT.
    
    Sử dụng thuật toán MCDM với hàm chi phí:
    Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty
    """
    try:
        # Lựa chọn mạng tối ưu
        best_network, min_cost = select_best_network(
            available_networks=device_state.available_networks,
            network_configs=DEFAULT_NETWORK_CONFIGS,
            task=device_state.current_task
        )
        
        # Tính chi phí cho tất cả các mạng để so sánh
        all_costs = {}
        for network in device_state.available_networks:
            if network.name in DEFAULT_NETWORK_CONFIGS:
                cost = calculate_cost(
                    network, 
                    DEFAULT_NETWORK_CONFIGS[network.name], 
                    device_state.current_task
                )
                all_costs[network.name] = round(cost, 2)
        
        return {
            "device_position": device_state.position,
            "current_task": device_state.current_task.value,
            "selected_network": best_network.name,
            "selected_cost": round(min_cost, 2),
            "all_costs": all_costs,
            "available_networks": len(device_state.available_networks),
            "algorithm": "MCDM_Energy_QoS"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


class CostCalculationRequest(BaseModel):
    """Request model cho cost calculation endpoint"""
    network_state: NetworkState
    task: TaskState
    network_name: str = None


@app.post("/calculate-cost")
def calculate_network_cost(request: CostCalculationRequest) -> dict:
    """
    Tính chi phí cho một mạng cụ thể và tác vụ.
    Hữu ích để debug hoặc phân tích chi tiết.
    """
    try:
        # Sử dụng network_name từ request hoặc từ network_state
        config_name = request.network_name or request.network_state.name
        
        if config_name not in DEFAULT_NETWORK_CONFIGS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown network type: {config_name}"
            )
        
        config = DEFAULT_NETWORK_CONFIGS[config_name]
        total_cost = calculate_cost(request.network_state, config, request.task)
        
        # Import các hàm con để tính chi tiết
        from app.core.decision_logic import calculate_energy_cost, calculate_qos_penalty
        
        energy_cost = calculate_energy_cost(config, request.network_state, request.task)
        qos_penalty = calculate_qos_penalty(request.network_state, request.task)
        
        return {
            "network": request.network_state.name,
            "task": request.task.value,
            "total_cost": round(total_cost, 2),
            "energy_cost": round(energy_cost, 2),
            "qos_penalty": round(qos_penalty, 2),
            "network_config": config.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/simulation/status")
def get_simulation_status():
    """Lấy trạng thái hiện tại của simulation engine"""
    return simulation_engine.get_simulation_stats()


@app.post("/simulation/step")
def run_simulation_step():
    """Chạy một bước mô phỏng và trả về device state mới"""
    try:
        device_state = simulation_engine.run_simulation_step()
        
        # Thực hiện network selection cho state mới
        decision_result = None
        if device_state.available_networks:
            try:
                best_net, cost = select_best_network(
                    device_state.available_networks,
                    simulation_engine.network_configs,
                    device_state.current_task
                )
                decision_result = {
                    "selected_network": best_net.name,
                    "cost": round(cost, 2)
                }
            except Exception as e:
                decision_result = {"error": str(e)}
        
        return {
            "step": simulation_engine.simulation_step,
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
            },
            "decision": decision_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SimulationRequest(BaseModel):
    """Request model cho multiple simulation steps"""
    num_steps: int = 10
    include_decisions: bool = True


@app.post("/simulation/run")
def run_simulation(request: SimulationRequest):
    """Chạy nhiều bước simulation"""
    try:
        if request.num_steps <= 0 or request.num_steps > 1000:
            raise HTTPException(
                status_code=400, 
                detail="num_steps must be between 1 and 1000"
            )
        
        results = []
        
        for i in range(request.num_steps):
            device_state = simulation_engine.run_simulation_step()
            
            step_result = {
                "step": simulation_engine.simulation_step,
                "position": device_state.position,
                "task": device_state.current_task.value,
                "available_networks": len(device_state.available_networks),
                "networks": [net.name for net in device_state.available_networks]
            }
            
            # Thêm decision nếu được yêu cầu
            if request.include_decisions and device_state.available_networks:
                try:
                    best_net, cost = select_best_network(
                        device_state.available_networks,
                        simulation_engine.network_configs,
                        device_state.current_task
                    )
                    step_result["decision"] = {
                        "selected": best_net.name,
                        "cost": round(cost, 2)
                    }
                except Exception as e:
                    step_result["decision"] = {"error": str(e)}
            
            results.append(step_result)
        
        return {
            "total_steps": len(results),
            "simulation_summary": simulation_engine.get_simulation_stats(),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulation/reset")
def reset_simulation(position: tuple = (0, 0)):
    """Reset simulation về trạng thái ban đầu"""
    try:
        simulation_engine.reset_simulation(position)
        return {
            "message": f"Simulation reset to position {position}",
            "status": simulation_engine.get_simulation_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))