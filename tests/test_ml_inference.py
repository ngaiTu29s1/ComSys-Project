"""
Test ML inference logic.

Chạy: pytest tests/test_ml_inference.py -v
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.ml.predictor import MLPredictor
from app.ml.data_collector import DataCollector
from app.models.schemas import DeviceState, NetworkState, TaskState
from app.services.simulation import SimulationEngine


def test_data_collector_initialization():
    """Test khởi tạo DataCollector"""
    engine = SimulationEngine()
    collector = DataCollector(engine, engine.network_configs)
    
    assert collector is not None
    assert len(collector.samples) == 0


def test_data_collection_basic():
    """Test thu thập data cơ bản"""
    engine = SimulationEngine()
    collector = DataCollector(engine, engine.network_configs)
    
    # Collect small sample
    collector.collect(num_samples=10)
    
    assert len(collector.samples) > 0
    assert 'position_x' in collector.samples[0]
    assert 'optimal_network' in collector.samples[0]


def test_feature_extraction():
    """Test trích xuất features"""
    engine = SimulationEngine()
    collector = DataCollector(engine, engine.network_configs)
    
    # Run one step
    device_state = engine.run_simulation_step()
    
    if len(device_state.available_networks) > 0:
        features = collector._extract_features(
            device_state,
            device_state.available_networks[0]
        )
        
        assert 'position_x' in features
        assert 'position_y' in features
        assert 'task_type' in features
        assert 'optimal_network' in features


# Test ML predictor chỉ chạy nếu đã có trained model
@pytest.mark.skipif(
    not os.path.exists("models/rf_network_selector.pkl"),
    reason="No trained model found"
)
def test_ml_predictor_initialization():
    """Test khởi tạo MLPredictor"""
    predictor = MLPredictor("models/rf_network_selector.pkl")
    assert predictor.model is not None


@pytest.mark.skipif(
    not os.path.exists("models/rf_network_selector.pkl"),
    reason="No trained model found"
)
def test_ml_prediction():
    """Test ML prediction logic"""
    engine = SimulationEngine()
    predictor = MLPredictor("models/rf_network_selector.pkl")
    
    # Run simulation
    device_state = engine.run_simulation_step()
    
    if len(device_state.available_networks) > 0:
        best_network, confidence = predictor.predict(
            device_state,
            device_state.available_networks,
            engine
        )
        
        assert best_network is not None
        assert 0.0 <= confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
