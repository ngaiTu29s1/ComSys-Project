"""
ML Predictor - Inference logic với trained Random Forest model.

Usage:
    predictor = MLPredictor("models/rf_network_selector.pkl")
    best_network, confidence = predictor.predict(device_state, available_networks)
"""

import joblib
from typing import List, Tuple, Dict
import numpy as np
import pandas as pd
from app.models.schemas import DeviceState, NetworkState, TaskState
from .feature_engineering import FeatureEngineer


class MLPredictor:
    """
    ML-based network selection predictor.
    """
    
    def __init__(self, model_path: str):
        """
        Load trained model và feature engineer.
        
        Args:
            model_path: Path to .pkl model file
        """
        print(f"📂 Loading ML model from {model_path}...")
        self.model = joblib.load(model_path)
        
        # Load feature engineer
        fe_path = model_path.replace('.pkl', '_feature_engineer.pkl')
        self.feature_engineer = FeatureEngineer.load(fe_path)
        
        self.network_labels = {0: 'Wi-Fi', 1: '5G', 2: 'BLE'}
        print(f"✅ ML model loaded successfully")
    
    def predict(
        self, 
        device_state: DeviceState,
        available_networks: List[NetworkState],
        simulation_engine=None
    ) -> Tuple[NetworkState, float]:
        """
        Predict best network sử dụng ML model.
        
        Args:
            device_state: Current device state
            available_networks: List of available networks
            simulation_engine: SimulationEngine instance (để tính distance)
            
        Returns:
            Tuple (best_network, confidence_score)
        """
        if not available_networks:
            raise ValueError("No networks available")
        
        # Extract features
        features_dict = self._extract_features(device_state, simulation_engine)
        
        # Convert to DataFrame
        features_df = pd.DataFrame([features_dict])
        
        # Transform features
        X = self.feature_engineer.transform(features_df)
        
        # Predict
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Get predicted network name
        predicted_network_name = self.network_labels[prediction]
        confidence = probabilities[prediction]
        
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
    
    def predict_with_probabilities(
        self,
        device_state: DeviceState,
        available_networks: List[NetworkState],
        simulation_engine=None
    ) -> Dict:
        """
        Predict với probability distribution cho từng network.
        
        Returns:
            Dict {
                'prediction': network_name,
                'confidence': float,
                'probabilities': {network: prob}
            }
        """
        features_dict = self._extract_features(device_state, simulation_engine)
        features_df = pd.DataFrame([features_dict])
        X = self.feature_engineer.transform(features_df)
        
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        return {
            'prediction': self.network_labels[prediction],
            'confidence': float(probabilities[prediction]),
            'probabilities': {
                self.network_labels[i]: float(prob) 
                for i, prob in enumerate(probabilities)
            }
        }
    
    def _extract_features(self, device_state: DeviceState, simulation_engine) -> Dict:
        """
        Trích xuất features từ device state.
        
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
        
        # Initialize all network features
        for net_type in ['Wi-Fi', '5G', 'BLE']:
            prefix = net_type.lower().replace('-', '')
            features[f'{prefix}_rssi'] = -999.0
            features[f'{prefix}_snr'] = -999.0
            features[f'{prefix}_bandwidth'] = 0.0
            features[f'{prefix}_latency'] = 9999
            features[f'{prefix}_distance'] = 9999.0
        
        # Fill actual values
        for network in device_state.available_networks:
            prefix = network.name.lower().replace('-', '')
            features[f'{prefix}_rssi'] = network.rssi if network.rssi else -999.0
            features[f'{prefix}_snr'] = network.snr if network.snr else -999.0
            features[f'{prefix}_bandwidth'] = network.bandwidth
            features[f'{prefix}_latency'] = network.latency
            
            # Calculate distance
            if simulation_engine and network.station_id:
                distance = self._calculate_distance_to_station(
                    device_state.position,
                    network.name,
                    network.station_id,
                    simulation_engine
                )
                features[f'{prefix}_distance'] = distance
        
        return features
    
    def _calculate_distance_to_station(self, device_pos, network_type, station_id, simulation_engine):
        """Tính khoảng cách từ device đến station"""
        import math
        
        stations = simulation_engine.base_stations.get(network_type, [])
        for station in stations:
            if station['id'] == station_id:
                dx = device_pos[0] - station['pos'][0]
                dy = device_pos[1] - station['pos'][1]
                return math.sqrt(dx * dx + dy * dy)
        
        return 9999.0
    
    def _encode_task(self, task: TaskState) -> int:
        """Encode task type"""
        mapping = {
            TaskState.IDLE_MONITORING: 0,
            TaskState.DATA_BURST_ALERT: 1,
            TaskState.VIDEO_STREAMING: 2
        }
        return mapping.get(task, 0)
