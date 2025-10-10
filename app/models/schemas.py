"""
Pydantic models cho hệ thống mô phỏng lựa chọn mạng tiết kiệm năng lượng.

Các models này định nghĩa cấu trúc dữ liệu cho:
- Trạng thái tác vụ của thiết bị IoT
- Cấu hình và trạng thái mạng
- Thông tin thiết bị trong hệ thống mô phỏng
"""

from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel, Field


class TaskState(str, Enum):
    """
    Enum định nghĩa các trạng thái tác vụ của thiết bị IoT.
    Mỗi trạng thái có đặc điểm năng lượng và QoS khác nhau.
    """
    IDLE_MONITORING = "IDLE_MONITORING"        # Giám sát nhàn rỗi
    DATA_BURST_ALERT = "DATA_BURST_ALERT"      # Cảnh báo với burst data
    VIDEO_STREAMING = "VIDEO_STREAMING"        # Streaming video


class NetworkConfig(BaseModel):
    """
    Cấu hình tĩnh của một mạng trong hệ thống.
    Chứa các thông số năng lượng cơ bản để tính toán cost function.
    """
    name: str = Field(..., description="Tên mạng (ví dụ: 'Wi-Fi', '5G', 'BLE')")
    energy_tx: float = Field(..., gt=0, description="Năng lượng truyền (mJ/KB)")
    energy_idle: float = Field(..., gt=0, description="Năng lượng chờ (mW)")
    energy_wakeup: float = Field(..., ge=0, description="Năng lượng khởi động (mJ)")

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
    """
    Trạng thái động của một mạng tại thời điểm hiện tại.
    Bao gồm các thông số QoS và khả năng kết nối.
    """
    name: str = Field(..., description="Tên mạng")
    bandwidth: float = Field(..., gt=0, description="Băng thông khả dụng (Mbps)")
    latency: int = Field(..., gt=0, description="Độ trễ (ms)")
    is_available: bool = Field(..., description="Trạng thái khả dụng của mạng")

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
    Trạng thái hiện tại của thiết bị IoT trong hệ thống mô phỏng.
    Bao gồm vị trí, tác vụ hiện tại và danh sách mạng khả dụng.
    """
    position: Tuple[int, int] = Field(..., description="Tọa độ thiết bị (x, y)")
    current_task: TaskState = Field(..., description="Trạng thái tác vụ hiện tại")
    available_networks: List[NetworkState] = Field(
        ..., 
        min_items=0, 
        description="Danh sách các mạng khả dụng tại vị trí hiện tại"
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