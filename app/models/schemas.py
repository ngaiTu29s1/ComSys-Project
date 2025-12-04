from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel, Field


class TaskState(str, Enum):
    IDLE_MONITORING = "IDLE_MONITORING"
    DATA_BURST_ALERT = "DATA_BURST_ALERT"      
    VIDEO_STREAMING = "VIDEO_STREAMING"        


class NetworkConfig(BaseModel):
    name: str = Field(..., description="Network name (e.g., 'Wi-Fi', '5G', 'BLE')")
    energy_tx: float = Field(..., gt=0, description="Transmission energy (mJ/KB)")
    energy_idle: float = Field(..., gt=0, description="Idle energy (mW)")
    energy_wakeup: float = Field(..., ge=0, description="Wakeup energy (mJ)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Wi-Fi",
                    "energy_tx": 0.5,
                    "energy_idle": 10.0,
                    "energy_wakeup": 2.0
                }
            ]
        }
    }


class NetworkState(BaseModel):
    name: str = Field(..., description="Network name")
    bandwidth: float = Field(..., gt=0, description="Available bandwidth (Mbps)")
    latency: int = Field(..., gt=0, description="Latency (ms)")
    is_available: bool = Field(..., description="Network availability status")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "5G",
                    "bandwidth": 100.0,
                    "latency": 20,
                    "is_available": True
                }
            ]
        }
    }


class DeviceState(BaseModel):
    """
    Current state of the IoT device in the simulation system.
    Includes position, current task, and list of available networks.
    """
    position: Tuple[int, int] = Field(..., description="Device coordinates (x, y)")
    current_task: TaskState = Field(..., description="Current task state")
    available_networks: List[NetworkState] = Field(
        ..., 
        min_items=0, 
        description="List of available networks at current position"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "position": [100, 200],
                    "current_task": "IDLE_MONITORING",
                    "available_networks": [
                        {
                            "name": "Wi-Fi",
                            "bandwidth": 50.0,
                            "latency": 10,
                            "is_available": True
                        },
                        {
                            "name": "5G",
                            "bandwidth": 100.0,
                            "latency": 20,
                            "is_available": True
                        }
                    ]
                }
            ]
        }
    }