"""
Engine mô phỏng cho hệ thống IoT Network Selection.

Module này cung cấp lõi mô phỏng để:
- Tạo môi trường mạng động với các base stations
- Di chuyển thiết bị IoT trong không gian 2D
- Tính toán QoS dựa trên khoảng cách thực tế
- Generate scenarios cho việc thu thập dữ liệu và testing
"""

import random
import math
from typing import Dict, List, Tuple
from app.models.schemas import TaskState, NetworkState, NetworkConfig, DeviceState


class SimulationEngine:
    """
    Engine mô phỏng chính cho hệ thống IoT Network Selection.
    
    Mô phỏng một thiết bị IoT di chuyển trong môi trường có nhiều base stations,
    với QoS thay đổi theo khoảng cách và các tác vụ ngẫu nhiên.
    """
    
    def __init__(self, map_size: Tuple[int, int] = (1000, 1000)):
        """
        Khởi tạo simulation engine.
        
        Args:
            map_size: Kích thước bản đồ mô phỏng (width, height)
        """
        self.map_size = map_size
        self.simulation_step = 0
        
        # Khởi tạo cấu hình các loại mạng
        self._init_network_configs()
        
        # Đặt các base stations tại các vị trí cố định
        self._init_base_stations()
        
        # Khởi tạo thiết bị tại vị trí ban đầu với network tạm thời
        temp_network = NetworkState(
            name="Temp", bandwidth=1.0, latency=100, is_available=True
        )
        self.device_state = DeviceState(
            position=(0, 0),
            current_task=TaskState.IDLE_MONITORING,
            available_networks=[temp_network]
        )
        
        # Cập nhật networks khả dụng thực tế cho vị trí ban đầu
        self._update_available_networks()
    
    def _init_network_configs(self):
        """Khởi tạo cấu hình các loại mạng với thông số giả định"""
        self.network_configs = {
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
    
    def _init_base_stations(self):
        """Đặt các base stations tại các vị trí cố định trên bản đồ"""
        self.base_stations = {
            "Wi-Fi": [
                (100, 100),   # Wi-Fi router 1 - khu dân cư
                (300, 250),   # Wi-Fi router 2 - văn phòng  
                (600, 400),   # Wi-Fi router 3 - quán café
                (800, 750),   # Wi-Fi router 4 - trung tâm thương mại
            ],
            "5G": [
                (200, 200),   # 5G tower 1 - trung tâm thành phố
                (500, 300),   # 5G tower 2 - khu công nghiệp
                (700, 600),   # 5G tower 3 - sân bay
                (900, 100),   # 5G tower 4 - khu vực ngoại ô
            ],
            "BLE": [
                (150, 150),   # BLE beacon 1 - cửa hàng
                (350, 350),   # BLE beacon 2 - bảo tàng  
                (550, 550),   # BLE beacon 3 - bệnh viện
                (750, 750),   # BLE beacon 4 - nhà ga
            ]
        }
        
        print(f"📡 Đã khởi tạo base stations:")
        for network_type, stations in self.base_stations.items():
            print(f"  {network_type}: {len(stations)} stations")
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Tính khoảng cách Euclidean giữa 2 điểm"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def _calculate_qos_by_distance(
        self, 
        device_position: Tuple[int, int], 
        base_station_position: Tuple[int, int],
        network_type: str
    ) -> Dict[str, float]:
        """
        Tính toán QoS (bandwidth, latency) dựa trên khoảng cách.
        
        Args:
            device_position: Vị trí thiết bị (x, y)
            base_station_position: Vị trí base station (x, y)  
            network_type: Loại mạng ("Wi-Fi", "5G", "BLE")
            
        Returns:
            Dict chứa bandwidth (Mbps) và latency (ms)
        """
        distance = self._calculate_distance(device_position, base_station_position)
        
        # Thông số tối đa cho từng loại mạng (khi khoảng cách = 0)
        max_specs = {
            "Wi-Fi": {"bandwidth": 100.0, "latency": 5, "max_range": 100},
            "5G": {"bandwidth": 200.0, "latency": 10, "max_range": 500}, 
            "BLE": {"bandwidth": 2.0, "latency": 20, "max_range": 50}
        }
        
        if network_type not in max_specs:
            return {"bandwidth": 0.0, "latency": 9999}
        
        spec = max_specs[network_type]
        max_range = spec["max_range"]
        
        # Nếu quá xa khỏi phạm vi, mạng không khả dụng
        if distance > max_range:
            return {"bandwidth": 0.0, "latency": 9999}
        
        # Công thức tuyến tính: giá trị giảm theo khoảng cách
        # Bandwidth giảm tuyến tính từ max về 10% khi ở biên
        distance_ratio = distance / max_range  # 0.0 -> 1.0
        
        # Bandwidth: từ 100% xuống 10% theo khoảng cách
        bandwidth = spec["bandwidth"] * (1.0 - 0.9 * distance_ratio)
        
        # Latency: từ min tăng lên 10x khi ở biên  
        latency = spec["latency"] * (1.0 + 9.0 * distance_ratio)
        
        # Thêm một chút noise để mô phỏng thực tế
        bandwidth *= (0.8 + 0.4 * random.random())  # ±20% noise
        latency *= (0.8 + 0.4 * random.random())    # ±20% noise
        
        return {
            "bandwidth": max(0.1, bandwidth),  # Tối thiểu 0.1 Mbps
            "latency": max(5, int(latency))    # Tối thiểu 5ms
        }
    
    def _find_best_base_station(
        self, 
        device_position: Tuple[int, int], 
        network_type: str
    ) -> Tuple[Tuple[int, int], Dict[str, float]]:
        """
        Tìm base station tốt nhất (gần nhất) cho một loại mạng.
        
        Returns:
            Tuple (vị trí base station tốt nhất, QoS tương ứng)
        """
        if network_type not in self.base_stations:
            return None, {"bandwidth": 0.0, "latency": 9999}
        
        stations = self.base_stations[network_type]
        best_station = None
        best_qos = None
        min_distance = float('inf')
        
        for station_pos in stations:
            distance = self._calculate_distance(device_position, station_pos)
            if distance < min_distance:
                min_distance = distance
                best_station = station_pos
                best_qos = self._calculate_qos_by_distance(
                    device_position, station_pos, network_type
                )
        
        return best_station, best_qos or {"bandwidth": 0.0, "latency": 9999}
    
    def _update_available_networks(self):
        """Cập nhật danh sách networks khả dụng cho vị trí hiện tại"""
        available_networks = []
        current_pos = self.device_state.position
        
        for network_type in self.network_configs.keys():
            # Tìm base station tốt nhất cho loại mạng này
            best_station, qos = self._find_best_base_station(current_pos, network_type)
            
            # Chỉ thêm vào nếu có signal (bandwidth > 0)
            if qos["bandwidth"] > 0:
                network_state = NetworkState(
                    name=network_type,
                    bandwidth=round(qos["bandwidth"], 1),
                    latency=qos["latency"],
                    is_available=True
                )
                available_networks.append(network_state)
        
        # Cập nhật device state
        self.device_state.available_networks = available_networks
    
    def _generate_random_task(self) -> TaskState:
        """Generate task ngẫu nhiên với xác suất thực tế"""
        # Xác suất cho từng task (tổng = 1.0)
        task_probabilities = {
            TaskState.IDLE_MONITORING: 0.6,    # 60% - thiết bị chủ yếu idle
            TaskState.DATA_BURST_ALERT: 0.3,   # 30% - thỉnh thoảng có alert
            TaskState.VIDEO_STREAMING: 0.1     # 10% - ít khi streaming
        }
        
        rand = random.random()
        cumulative = 0.0
        
        for task, prob in task_probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return task
        
        # Fallback
        return TaskState.IDLE_MONITORING
    
    def _move_device(self, step_size: int = 10) -> Tuple[int, int]:
        """
        Di chuyển thiết bị đến vị trí mới.
        
        Args:
            step_size: Kích thước bước di chuyển
            
        Returns:
            Vị trí mới (x, y)
        """
        current_x, current_y = self.device_state.position
        
        # Di chuyển theo pattern: zig-zag để cover toàn bộ map
        if self.simulation_step < 100:
            # Giai đoạn 1: di chuyển ngang
            new_x = min(current_x + step_size, self.map_size[0] - 1)
            new_y = current_y
        elif self.simulation_step < 200: 
            # Giai đoạn 2: di chuyển dọc
            new_x = current_x
            new_y = min(current_y + step_size, self.map_size[1] - 1)
        else:
            # Giai đoạn 3: di chuyển ngẫu nhiên
            directions = [(-step_size, 0), (step_size, 0), (0, -step_size), (0, step_size)]
            dx, dy = random.choice(directions)
            
            new_x = max(0, min(current_x + dx, self.map_size[0] - 1))
            new_y = max(0, min(current_y + dy, self.map_size[1] - 1))
        
        return (new_x, new_y)
    
    def run_simulation_step(self) -> DeviceState:
        """
        Chạy một bước mô phỏng.
        
        Returns:
            DeviceState mới nhất sau bước mô phỏng này
        """
        self.simulation_step += 1
        
        # 1. Di chuyển thiết bị đến vị trí mới
        new_position = self._move_device()
        
        # 2. Chọn task ngẫu nhiên
        new_task = self._generate_random_task()
        
        # 3. Cập nhật device state
        self.device_state.position = new_position
        self.device_state.current_task = new_task
        
        # 4. Tính toán lại networks khả dụng cho vị trí mới
        self._update_available_networks()
        
        return self.device_state
    
    def run_multiple_steps(self, num_steps: int) -> List[DeviceState]:
        """
        Chạy nhiều bước mô phỏng liên tiếp.
        
        Args:
            num_steps: Số bước cần chạy
            
        Returns:
            List các DeviceState qua từng bước
        """
        results = []
        
        for i in range(num_steps):
            device_state = self.run_simulation_step()
            
            # Deep copy để tránh reference issues
            results.append(DeviceState(
                position=device_state.position,
                current_task=device_state.current_task,
                available_networks=[
                    NetworkState(
                        name=net.name,
                        bandwidth=net.bandwidth,
                        latency=net.latency,
                        is_available=net.is_available
                    ) for net in device_state.available_networks
                ]
            ))
        
        return results
    
    def get_simulation_stats(self) -> Dict:
        """Lấy thống kê về simulation hiện tại"""
        return {
            "simulation_step": self.simulation_step,
            "current_position": self.device_state.position,
            "current_task": self.device_state.current_task.value,
            "available_networks_count": len(self.device_state.available_networks),
            "available_networks": [net.name for net in self.device_state.available_networks],
            "map_size": self.map_size,
            "total_base_stations": sum(len(stations) for stations in self.base_stations.values())
        }
    
    def reset_simulation(self, new_position: Tuple[int, int] = (0, 0)):
        """
        Reset simulation về trạng thái ban đầu.
        
        Args:
            new_position: Vị trí mới để bắt đầu (default: 0,0)
        """
        self.simulation_step = 0
        self.device_state.position = new_position
        self.device_state.current_task = TaskState.IDLE_MONITORING
        self._update_available_networks()
        
        print(f"🔄 Đã reset simulation tại vị trí {new_position}")