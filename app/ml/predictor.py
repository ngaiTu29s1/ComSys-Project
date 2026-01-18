"""
ML Predictor - Inference logic với trained Random Forest model.

Singleton pattern để load model 1 lần duy nhất.
Robust path handling với pathlib.

Usage:
    predictor = MLPredictor.get_instance()
    best_network, confidence = predictor.predict(device_state, available_networks)
"""

import joblib
from typing import List, Tuple, Dict, Optional
import numpy as np
import pandas as pd
from pathlib import Path
import warnings
import math

from app.models.schemas import DeviceState, NetworkState, TaskState
from app.core.constants import MLConfig
from .feature_engineering import FeatureEngineer


class MLPredictor:
    """
    ML-based network selection predictor với Singleton Pattern.
    
    Singleton ensures model is loaded only once during app lifetime.
    """
    
    _instance = None
    _model = None
    _feature_engineer = None
    _is_initialized = False
    _network_labels = {0: 'Wi-Fi', 1: '5G', 2: 'BLE'}
    
    # Base station positions (same as in SimulationEngine)
    _base_stations = {
        "Wi-Fi": [
            {"id": "WiFi-1", "pos": (100, 100)},
            {"id": "WiFi-2", "pos": (300, 250)},
            {"id": "WiFi-3", "pos": (600, 400)},
            {"id": "WiFi-4", "pos": (800, 750)},
        ],
        "5G": [
            {"id": "5G-1", "pos": (200, 200)},
            {"id": "5G-2", "pos": (500, 300)},
            {"id": "5G-3", "pos": (700, 600)},
            {"id": "5G-4", "pos": (900, 100)},
        ],
        "BLE": [
            {"id": "BLE-1", "pos": (150, 150)},
            {"id": "BLE-2", "pos": (350, 350)},
            {"id": "BLE-3", "pos": (550, 550)},
            {"id": "BLE-4", "pos": (750, 750)},
        ]
    }
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(MLPredictor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize predictor. Load model from relative path.
        Only runs once due to Singleton pattern.
        """
        if MLPredictor._is_initialized:
            return
        
        # Định nghĩa đường dẫn tương đối từ file hiện tại
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        model_path = project_root / "models" / "rf_network_selector.pkl"
        fe_path = project_root / "models" / "rf_network_selector_feature_engineer.pkl"
        
        try:
            # Load model
            if model_path.exists():
                print(f"📂 Loading ML model from {model_path}...")
                MLPredictor._model = joblib.load(str(model_path))
                
                # Load feature engineer
                if fe_path.exists():
                    MLPredictor._feature_engineer = FeatureEngineer.load(str(fe_path))
                    print(f"✅ ML model loaded successfully")
                else:
                    warnings.warn(f"⚠️  Feature engineer not found: {fe_path}")
                    MLPredictor._model = None
            else:
                warnings.warn(
                    f"⚠️  ML model not found: {model_path}\n"
                    f"   System will fallback to MCDM algorithm.\n"
                    f"   To train model: python scripts/train_model.py"
                )
                MLPredictor._model = None
                
        except Exception as e:
            warnings.warn(f"⚠️  Failed to load ML model: {e}\n   Fallback to MCDM algorithm.")
            MLPredictor._model = None
        
        MLPredictor._is_initialized = True
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def is_available(self) -> bool:
        """Check if ML model is loaded and ready"""
        return MLPredictor._model is not None
    
    def predict(
        self, 
        device_state: DeviceState,
        available_networks: List[NetworkState],
        simulation_engine=None
    ) -> Tuple[Optional[NetworkState], float]:
        """
        Predict best network sử dụng ML model.
        
        Args:
            device_state: Current device state
            available_networks: List of available networks
            simulation_engine: SimulationEngine instance (optional, để tính distance)
            
        Returns:
            Tuple (best_network, confidence_score) hoặc (None, 0.0) nếu model không có
        """
        # Fallback nếu model không load được
        if not self.is_available:
            return None, 0.0
        
        if not available_networks:
            return None, 0.0
        
        try:
            # Extract features
            features_dict = self._extract_features(device_state, simulation_engine)
            
            # Convert to DataFrame
            features_df = pd.DataFrame([features_dict])
            
            # Transform features
            X = MLPredictor._feature_engineer.transform(features_df)
            
            # Predict
            prediction = MLPredictor._model.predict(X)[0]
            probabilities = MLPredictor._model.predict_proba(X)[0]
            
            # Get predicted network name
            predicted_network_name = MLPredictor._network_labels[prediction]
            confidence = float(probabilities[prediction])
            
            # Find best network in available networks
            best_network = None
            for network in available_networks:
                if network.name == predicted_network_name:
                    best_network = network
                    break
            
            # Fallback: nếu không có mạng được predict, chọn mạng đầu tiên
            if best_network is None:
                best_network = available_networks[0]
                confidence = 0.0
            
            return best_network, confidence
            
        except Exception as e:
            warnings.warn(f"⚠️  ML prediction failed: {e}")
            return None, 0.0
    
    
    def predict_with_probabilities(
        self,
        device_state: DeviceState,
        available_networks: List[NetworkState],
        simulation_engine=None
    ) -> Optional[Dict]:
        """
        Predict với probability distribution cho từng network.
        
        Returns:
            Dict {
                'prediction': network_name,
                'confidence': float,
                'probabilities': {network: prob}
            } hoặc None nếu model không có
        """
        if not self.is_available:
            return None
        
        try:
            features_dict = self._extract_features(device_state, simulation_engine)
            features_df = pd.DataFrame([features_dict])
            X = MLPredictor._feature_engineer.transform(features_df)
            
            prediction = MLPredictor._model.predict(X)[0]
            probabilities = MLPredictor._model.predict_proba(X)[0]
            
            return {
                'prediction': MLPredictor._network_labels[prediction],
                'confidence': float(probabilities[prediction]),
                'probabilities': {
                    MLPredictor._network_labels[i]: float(prob) 
                    for i, prob in enumerate(probabilities)
                }
            }
        except Exception as e:
            warnings.warn(f"⚠️  ML prediction failed: {e}")
            return None
    
    def _extract_features(self, device_state: DeviceState, simulation_engine) -> Dict:
        """
        Trích xuất features từ device state.
        
        CRITICAL: Feature order MUST match training order:
        - position_x, position_y, task_type
        - wifi_rssi, wifi_snr, wifi_bandwidth, wifi_latency, wifi_distance
        - 5g_rssi, 5g_snr, 5g_bandwidth, 5g_latency, 5g_distance
        - ble_rssi, ble_snr, ble_bandwidth, ble_latency, ble_distance
        
        Args:
            device_state: Current DeviceState
            simulation_engine: SimulationEngine (để tính distance)
            
        Returns:
            Dict chứa features
        """
        features = {
            'position_x': device_state.position[0],
            'position_y': device_state.position[1],
            'task_type': self._encode_task(device_state.current_task),
        }
        
        # Initialize all network features với default values (not available)
        for net_type in ['Wi-Fi', '5G', 'BLE']:
            prefix = net_type.lower().replace('-', '')
            features[f'{prefix}_rssi'] = MLConfig.UNAVAILABLE_RSSI
            features[f'{prefix}_snr'] = MLConfig.UNAVAILABLE_SNR
            features[f'{prefix}_bandwidth'] = MLConfig.UNAVAILABLE_BANDWIDTH
            features[f'{prefix}_latency'] = MLConfig.UNAVAILABLE_LATENCY
            features[f'{prefix}_distance'] = MLConfig.UNAVAILABLE_DISTANCE
        
        # Fill actual values cho available networks
        for network in device_state.available_networks:
            prefix = network.name.lower().replace('-', '')
            features[f'{prefix}_rssi'] = network.rssi if network.rssi else MLConfig.UNAVAILABLE_RSSI
            features[f'{prefix}_snr'] = network.snr if network.snr else MLConfig.UNAVAILABLE_SNR
            features[f'{prefix}_bandwidth'] = network.bandwidth
            features[f'{prefix}_latency'] = network.latency
            
            # Calculate distance to station
            if network.station_id:
                distance = self._calculate_distance_to_station(
                    device_state.position,
                    network.name,
                    network.station_id,
                    simulation_engine
                )
                features[f'{prefix}_distance'] = distance
        
        return features
    
    def _calculate_distance_to_station(
        self, 
        device_pos: Tuple[int, int], 
        network_type: str, 
        station_id: str,
        simulation_engine
    ) -> float:
        """
        Tính khoảng cách từ device đến station.
        
        Args:
            device_pos: Vị trí device (x, y)
            network_type: Loại mạng (Wi-Fi/5G/BLE)
            station_id: ID của station
            simulation_engine: SimulationEngine instance (ưu tiên)
            
        Returns:
            Distance in meters (hoặc 9999.0 nếu không tìm thấy)
        """
        # Ưu tiên dùng simulation_engine nếu có
        if simulation_engine is not None:
            stations = simulation_engine.base_stations.get(network_type, [])
            for station in stations:
                if station['id'] == station_id:
                    dx = device_pos[0] - station['pos'][0]
                    dy = device_pos[1] - station['pos'][1]
                    return math.sqrt(dx * dx + dy * dy)
        
        # Fallback: dùng hardcoded positions
        stations = MLPredictor._base_stations.get(network_type, [])
        for station in stations:
            if station['id'] == station_id:
                dx = device_pos[0] - station['pos'][0]
                dy = device_pos[1] - station['pos'][1]
                return math.sqrt(dx * dx + dy * dy)
        
        return 9999.0  # Station not found
    
    def _encode_task(self, task: TaskState) -> int:
        """
        Encode task type sang integer.
        
        CRITICAL: Must match training encoding!
        """
        mapping = {
            TaskState.IDLE_MONITORING: 0,
            TaskState.DATA_BURST_ALERT: 1,
            TaskState.VIDEO_STREAMING: 2
        }
        return mapping.get(task, 0)
