"""
DataCollector - Thu thập training data từ simulation engine.

Usage:
    collector = DataCollector(simulation_engine, network_configs)
    collector.collect(num_samples=1000)
    collector.save_dataset("data/raw/training_data.csv")
"""

from typing import List, Dict
import pandas as pd
import os
from app.models.schemas import DeviceState, NetworkState, TaskState
from app.core.decision_logic import calculate_cost, select_best_network


class DataCollector:
    """
    Thu thập và lưu trữ training data cho ML model.
    
    Data format:
    - Features: position_x, position_y, task_type, 
                wifi_rssi, wifi_snr, wifi_bandwidth, wifi_latency, wifi_distance,
                5g_rssi, 5g_snr, 5g_bandwidth, 5g_latency, 5g_distance,
                ble_rssi, ble_snr, ble_bandwidth, ble_latency, ble_distance
    - Label: optimal_network (0=Wi-Fi, 1=5G, 2=BLE)
    """
    
    def __init__(self, simulation_engine, network_configs):
        """
        Args:
            simulation_engine: Instance của SimulationEngine
            network_configs: Dict of NetworkConfig
        """
        self.simulation_engine = simulation_engine
        self.network_configs = network_configs
        self.samples: List[Dict] = []
    
    def collect(self, num_samples: int = 1000):
        """
        Thu thập training samples từ simulation.
        
        Args:
            num_samples: Số lượng samples cần thu thập
        """
        print(f"🚀 Collecting {num_samples} training samples...")
        
        for i in range(num_samples):
            # Run simulation step
            device_state = self.simulation_engine.run_simulation_step()
            
            # Nếu không có mạng khả dụng, skip
            if len(device_state.available_networks) == 0:
                continue
            
            # Sử dụng MCDM để tìm optimal network (label)
            try:
                optimal_network, optimal_cost = select_best_network(
                    device_state.available_networks,
                    self.network_configs,
                    device_state.current_task
                )
                
                # Extract features
                sample = self._extract_features(device_state, optimal_network)
                self.samples.append(sample)
                
                if (i + 1) % 100 == 0:
                    print(f"  ✅ Collected {i + 1}/{num_samples} samples")
                    
            except Exception as e:
                print(f"  ⚠️ Error at step {i}: {e}")
                continue
        
        print(f"✅ Collection complete: {len(self.samples)} valid samples")
    
    def _extract_features(self, device_state: DeviceState, optimal_network: NetworkState) -> Dict:
        """
        Trích xuất features từ device state.
        
        Args:
            device_state: Current device state
            optimal_network: Network được chọn bởi MCDM
            
        Returns:
            Dict chứa features và label
        """
        features = {
            'position_x': device_state.position[0],
            'position_y': device_state.position[1],
            'task_type': self._encode_task(device_state.current_task),
        }
        
        # Initialize all network features with default values (không available)
        for net_type in ['Wi-Fi', '5G', 'BLE']:
            prefix = net_type.lower().replace('-', '')
            features[f'{prefix}_rssi'] = -999.0
            features[f'{prefix}_snr'] = -999.0
            features[f'{prefix}_bandwidth'] = 0.0
            features[f'{prefix}_latency'] = 9999
            features[f'{prefix}_distance'] = 9999.0
        
        # Fill in actual values for available networks
        for network in device_state.available_networks:
            prefix = network.name.lower().replace('-', '')
            features[f'{prefix}_rssi'] = network.rssi if network.rssi else -999.0
            features[f'{prefix}_snr'] = network.snr if network.snr else -999.0
            features[f'{prefix}_bandwidth'] = network.bandwidth
            features[f'{prefix}_latency'] = network.latency
            
            # Calculate distance to station
            if network.station_id:
                distance = self._calculate_distance_to_station(
                    device_state.position,
                    network.name,
                    network.station_id
                )
                features[f'{prefix}_distance'] = distance
        
        # Label: optimal network type
        features['optimal_network'] = self._encode_network(optimal_network.name)
        
        return features
    
    def _calculate_distance_to_station(self, device_pos, network_type, station_id):
        """Tính khoảng cách từ device đến station"""
        import math
        
        stations = self.simulation_engine.base_stations.get(network_type, [])
        for station in stations:
            if station['id'] == station_id:
                dx = device_pos[0] - station['pos'][0]
                dy = device_pos[1] - station['pos'][1]
                return math.sqrt(dx * dx + dy * dy)
        
        return 9999.0  # Fallback
    
    def _encode_task(self, task: TaskState) -> int:
        """Encode task type sang integer"""
        mapping = {
            TaskState.IDLE_MONITORING: 0,
            TaskState.DATA_BURST_ALERT: 1,
            TaskState.VIDEO_STREAMING: 2
        }
        return mapping.get(task, 0)
    
    def _encode_network(self, network_name: str) -> int:
        """Encode network name sang integer"""
        mapping = {
            'Wi-Fi': 0,
            '5G': 1,
            'BLE': 2
        }
        return mapping.get(network_name, 0)
    
    def save_dataset(self, filepath: str):
        """
        Lưu dataset ra CSV file.
        
        Args:
            filepath: Đường dẫn file output
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df = pd.DataFrame(self.samples)
        df.to_csv(filepath, index=False)
        print(f"💾 Dataset saved to {filepath}")
        print(f"📊 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        Trả về pandas DataFrame của collected data.
        
        Returns:
            DataFrame với features và labels
        """
        return pd.DataFrame(self.samples)
