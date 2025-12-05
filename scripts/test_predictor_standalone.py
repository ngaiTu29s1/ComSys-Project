"""
Standalone test script để kiểm tra MLPredictor logic.

Kiểm tra:
- Singleton pattern hoạt động
- Feature extraction đúng 18 features
- Prediction logic hoạt động
- Model path handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.predictor import MLPredictor
from app.models.schemas import DeviceState, TaskState, NetworkState
from app.services.simulation import SimulationEngine


def create_dummy_device_state():
    """Tạo dummy DeviceState với đầy đủ thông tin"""
    
    # Tạo 3 mạng khả dụng với QoS ngẫu nhiên
    wifi_network = NetworkState(
        name="Wi-Fi",
        bandwidth=85.3,
        latency=12,
        is_available=True,
        station_id="WiFi-1",
        rssi=-68.4,
        snr=26.6,
        packet_loss_rate=0.02
    )
    
    fiveg_network = NetworkState(
        name="5G",
        bandwidth=120.5,
        latency=8,
        is_available=True,
        station_id="5G-1",
        rssi=-72.1,
        snr=22.9,
        packet_loss_rate=0.01
    )
    
    ble_network = NetworkState(
        name="BLE",
        bandwidth=2.0,
        latency=150,
        is_available=True,
        station_id="BLE-1",
        rssi=-85.0,
        snr=10.0,
        packet_loss_rate=0.05
    )
    
    # Tạo DeviceState
    device_state = DeviceState(
        position=(150, 200),  # Device ở vị trí (150, 200)
        current_task=TaskState.IDLE_MONITORING,
        available_networks=[wifi_network, fiveg_network, ble_network]
    )
    
    return device_state


def test_feature_extraction_size(predictor, device_state, engine):
    """Kiểm tra số lượng features = 18"""
    print("\n" + "="*60)
    print("🔍 TEST: Feature Extraction")
    print("="*60)
    
    features_dict = predictor._extract_features(device_state, engine)
    
    print(f"\n📊 Number of features: {len(features_dict)}")
    print(f"✅ Expected: 18 features")
    
    if len(features_dict) == 18:
        print("✅ PASS: Feature count correct!")
    else:
        print(f"❌ FAIL: Expected 18 features, got {len(features_dict)}")
    
    print(f"\n📋 Feature names:")
    for i, (key, value) in enumerate(features_dict.items(), 1):
        print(f"   {i:2d}. {key:20s} = {value}")
    
    return features_dict


def test_singleton_pattern():
    """Kiểm tra Singleton pattern"""
    print("\n" + "="*60)
    print("🔍 TEST: Singleton Pattern")
    print("="*60)
    
    predictor1 = MLPredictor.get_instance()
    predictor2 = MLPredictor.get_instance()
    
    if predictor1 is predictor2:
        print("✅ PASS: Singleton pattern works! (same instance)")
    else:
        print("❌ FAIL: Different instances created!")
    
    print(f"   Instance 1 ID: {id(predictor1)}")
    print(f"   Instance 2 ID: {id(predictor2)}")


def test_model_availability(predictor):
    """Kiểm tra model có load được không"""
    print("\n" + "="*60)
    print("🔍 TEST: Model Availability")
    print("="*60)
    
    if predictor.is_available:
        print("✅ PASS: ML model loaded successfully!")
        print(f"   Model type: {type(predictor._model).__name__}")
        print(f"   Feature engineer loaded: {predictor._feature_engineer is not None}")
    else:
        print("⚠️  WARNING: ML model not available (will fallback to MCDM)")
        print("   To fix: python scripts/train_model.py")


def test_prediction(predictor, device_state, engine):
    """Kiểm tra prediction logic"""
    print("\n" + "="*60)
    print("🔍 TEST: Prediction Logic")
    print("="*60)
    
    if not predictor.is_available:
        print("⚠️  Skipping prediction test (model not available)")
        return
    
    print(f"\n📍 Device position: {device_state.position}")
    print(f"📋 Current task: {device_state.current_task.value}")
    print(f"📡 Available networks: {[n.name for n in device_state.available_networks]}")
    
    # Predict
    best_network, confidence = predictor.predict(
        device_state,
        device_state.available_networks,
        engine
    )
    
    if best_network is not None:
        print(f"\n✅ Prediction successful!")
        print(f"   Selected network: {best_network.name}")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Station ID: {best_network.station_id}")
        print(f"   Bandwidth: {best_network.bandwidth:.1f} Mbps")
        print(f"   Latency: {best_network.latency} ms")
    else:
        print(f"\n❌ Prediction failed (returned None)")


def test_prediction_with_probabilities(predictor, device_state, engine):
    """Kiểm tra prediction với probabilities"""
    print("\n" + "="*60)
    print("🔍 TEST: Prediction with Probabilities")
    print("="*60)
    
    if not predictor.is_available:
        print("⚠️  Skipping test (model not available)")
        return
    
    result = predictor.predict_with_probabilities(
        device_state,
        device_state.available_networks,
        engine
    )
    
    if result:
        print(f"\n✅ Prediction successful!")
        print(f"   Predicted: {result['prediction']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"\n📊 Probability distribution:")
        for network, prob in result['probabilities'].items():
            bar = "█" * int(prob * 50)
            print(f"   {network:6s}: {prob:6.2%} {bar}")
    else:
        print(f"\n❌ Prediction failed (returned None)")


def main():
    """Main test runner"""
    print("="*60)
    print("🧪 MLPredictor Standalone Test")
    print("="*60)
    
    # Test 1: Singleton Pattern
    test_singleton_pattern()
    
    # Initialize predictor (singleton)
    predictor = MLPredictor.get_instance()
    
    # Test 2: Model Availability
    test_model_availability(predictor)
    
    # Initialize simulation engine (for distance calculation)
    engine = SimulationEngine()
    
    # Create dummy device state
    device_state = create_dummy_device_state()
    
    # Test 3: Feature Extraction
    features = test_feature_extraction_size(predictor, device_state, engine)
    
    # Test 4: Prediction
    test_prediction(predictor, device_state, engine)
    
    # Test 5: Prediction with Probabilities
    test_prediction_with_probabilities(predictor, device_state, engine)
    
    # Summary
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()
