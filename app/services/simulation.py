import random
import math
from typing import Dict, List, Tuple
from app.models.schemas import TaskState, NetworkState, NetworkConfig, DeviceState
from app.services.network_physics import NetworkPhysics


class SimulationEngine:
    """Main simulation engine for IoT Network Selection system.
    
    Simulates an IoT device moving in an environment with multiple base stations,
    with QoS changing based on distance using physics-based wireless propagation models.
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
        # Store stations with IDs
        self.base_stations = {
            "Wi-Fi": [
                {"id": "WiFi-1", "pos": (100, 100)},   # Wi-Fi router 1 - khu dân cư
                {"id": "WiFi-2", "pos": (300, 250)},   # Wi-Fi router 2 - văn phòng  
                {"id": "WiFi-3", "pos": (600, 400)},   # Wi-Fi router 3 - quán café
                {"id": "WiFi-4", "pos": (800, 750)},   # Wi-Fi router 4 - trung tâm thương mại
            ],
            "5G": [
                {"id": "5G-1", "pos": (200, 200)},   # 5G tower 1 - trung tâm thành phố
                {"id": "5G-2", "pos": (500, 300)},   # 5G tower 2 - khu công nghiệp
                {"id": "5G-3", "pos": (700, 600)},   # 5G tower 3 - sân bay
                {"id": "5G-4", "pos": (900, 100)},   # 5G tower 4 - khu vực ngoại ô
            ],
            "BLE": [
                {"id": "BLE-1", "pos": (150, 150)},   # BLE beacon 1 - cửa hàng
                {"id": "BLE-2", "pos": (350, 350)},   # BLE beacon 2 - bảo tàng  
                {"id": "BLE-3", "pos": (550, 550)},   # BLE beacon 3 - bệnh viện
                {"id": "BLE-4", "pos": (750, 750)},   # BLE beacon 4 - nhà ga
            ]
        }
        
        print(f"📡 Đã khởi tạo base stations:")
        for network_type, stations in self.base_stations.items():
            print(f"  {network_type}: {len(stations)} stations")
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Tính khoảng cách Euclidean giữa 2 điểm"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    

    def _find_best_base_station(
        self, 
        device_position: Tuple[int, int], 
        network_type: str
    ) -> Tuple[str | None, Dict[str, float]]:
        """Find the best base station for a network type using physics-based model.
        
        Selects station with best SNR (not necessarily closest due to shadowing).
        
        Returns:
            Tuple (station_id, QoS metrics)
        """
        if network_type not in self.base_stations:
            return None, {
                "bandwidth": 0.0,
                "latency": 9999,
                "packet_loss_rate": 1.0,
                "rssi": -999,
                "snr": -999,
                "is_available": False
            }
        
        stations = self.base_stations[network_type]
        best_station_id = None
        best_qos = None
        best_snr = -999
        
        # Find station with best SNR (not necessarily closest)
        for station in stations:
            station_id = station["id"]
            station_pos = station["pos"]
            distance = self._calculate_distance(device_position, station_pos)
            
            # Calculate QoS using physics-based model
            qos = NetworkPhysics.calculate_qos(network_type, distance)
            
            # Select station with best SNR
            if qos["is_available"] and qos["snr"] > best_snr:
                best_snr = qos["snr"]
                best_station_id = station_id
                best_qos = qos
        
        # If no station is available
        if best_qos is None:
            return None, {
                "bandwidth": 0.0,
                "latency": 9999,
                "packet_loss_rate": 1.0,
                "rssi": -999,
                "snr": -999,
                "is_available": False
            }
        
        return best_station_id, best_qos
    
    def _update_available_networks(self):
        """Update list of available networks for current position using physics model"""
        available_networks = []
        current_pos = self.device_state.position
        
        for network_type in self.network_configs.keys():
            station_id, qos = self._find_best_base_station(current_pos, network_type)
            
            # Only add if network is available (SNR > 0)
            if qos["is_available"]:
                network_state = NetworkState(
                    name=network_type,
                    bandwidth=qos["bandwidth"],
                    latency=qos["latency"],
                    is_available=True,
                    station_id=station_id,
                    rssi=qos.get("rssi"),
                    snr=qos.get("snr"),
                    packet_loss_rate=qos.get("packet_loss_rate")
                )
                available_networks.append(network_state)
        
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
        """Run one simulation step.
        
        Returns:
            Latest DeviceState after this simulation step
        """
        self.simulation_step += 1
        
        new_position = self._move_device()
        new_task = self._generate_random_task()
        
        self.device_state.position = new_position
        self.device_state.current_task = new_task
        
        # Recalculate available networks using physics-based model
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