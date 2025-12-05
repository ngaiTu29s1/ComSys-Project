"""
Script kiểm thử API endpoint /decision/ml

Script này gửi request đến API endpoint /decision/ml để kiểm tra:
1. ML prediction có hoạt động đúng không
2. Fallback về MCDM có hoạt động không (khi ML unavailable)
3. Format response có đúng không (selected_network, station_id, method, confidence)
4. Station ID selection logic có hoạt động không

Usage:
    python scripts/verify_api_ml.py
    
Requirements:
    - API server phải đang chạy (uvicorn app.main:app --reload)
    - ML model phải được train trước (models/network_selector_rf.pkl)
"""

import requests
import json
from typing import Dict, Any


# API Configuration
API_BASE_URL = "http://localhost:8000"
ML_DECISION_ENDPOINT = f"{API_BASE_URL}/decision/ml"
MCDM_DECISION_ENDPOINT = f"{API_BASE_URL}/decision"


def create_test_payload() -> Dict[str, Any]:
    """
    Tạo test payload cho API request.
    
    Payload mô phỏng thiết bị ở vị trí [150, 200] 
    với task IDLE_MONITORING và 3 mạng khả dụng.
    
    Returns:
        Dict chứa DeviceState data
    """
    payload = {
        "position": [150, 200],
        "current_task": "IDLE_MONITORING",
        "available_networks": [
            {
                "name": "WiFi",
                "bandwidth": 50.0,
                "latency": 20.0,
                "is_available": True,
                "station_id": "WiFi-2",
                "snr": 25.5,
                "rssi": -45.0,
                "packet_loss_rate": 0.01
            },
            {
                "name": "5G",
                "bandwidth": 200.0,
                "latency": 5.0,
                "is_available": True,
                "station_id": "5G-3",
                "snr": 30.2,
                "rssi": -55.0,
                "packet_loss_rate": 0.005
            },
            {
                "name": "BLE",
                "bandwidth": 1.0,
                "latency": 50.0,
                "is_available": True,
                "station_id": "BLE-1",
                "snr": 20.8,
                "rssi": -60.0,
                "packet_loss_rate": 0.02
            }
        ]
    }
    return payload


def test_ml_decision_endpoint():
    """
    Test ML decision endpoint /decision/ml
    
    Kiểm tra:
    - Response status code
    - Response format (selected_network, station_id, method, confidence)
    - Method có phải ML hay MCDM_Fallback
    - Station ID có đúng format không
    """
    print("\n" + "="*70)
    print("🧪 TESTING ML DECISION ENDPOINT: /decision/ml")
    print("="*70)
    
    payload = create_test_payload()
    
    print("\n📤 Sending request...")
    print(f"   URL: {ML_DECISION_ENDPOINT}")
    print(f"   Payload:")
    print(f"     Position: {payload['position']}")
    print(f"     Task: {payload['current_task']}")
    print(f"     Networks: {[n['name'] for n in payload['available_networks']]}")
    
    try:
        response = requests.post(
            ML_DECISION_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response received:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ SUCCESS - Response Data:")
            print(f"   Selected Network: {data.get('selected_network')}")
            print(f"   Station ID: {data.get('station_id')}")
            print(f"   Method: {data.get('method')}")
            print(f"   Confidence: {data.get('confidence'):.2%}")
            
            # Validate response format
            required_fields = ['selected_network', 'station_id', 'method', 'confidence']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"\n⚠️  WARNING: Missing required fields: {missing_fields}")
            else:
                print(f"\n✅ All required fields present")
            
            # Check method type
            if data.get('method') == 'ML':
                print(f"   🤖 ML Model used successfully")
            elif data.get('method') == 'MCDM_Fallback':
                print(f"   ⚠️  Fallback to MCDM (ML unavailable or failed)")
            
            # Validate station_id format
            station_id = data.get('station_id', '')
            if station_id and '-' in station_id and station_id.split('-')[0] == data.get('selected_network'):
                print(f"   ✅ Station ID format valid: {station_id}")
            elif station_id is None:
                print(f"   ❌ Station ID is None")
                return False
            else:
                print(f"   ⚠️  Station ID format unexpected: {station_id}")
            
            # Print full response for debugging
            print(f"\n📋 Full Response:")
            print(json.dumps(data, indent=2))
            
            return True
            
        else:
            print(f"\n❌ FAILED - Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR")
        print(f"   Cannot connect to API at {API_BASE_URL}")
        print(f"   Make sure API server is running:")
        print(f"   → uvicorn app.main:app --reload")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def test_mcdm_decision_endpoint():
    """
    Test MCDM decision endpoint /decision for comparison
    """
    print("\n" + "="*70)
    print("🧪 TESTING MCDM DECISION ENDPOINT (for comparison): /decision")
    print("="*70)
    
    payload = create_test_payload()
    
    print("\n📤 Sending request...")
    print(f"   URL: {MCDM_DECISION_ENDPOINT}")
    
    try:
        response = requests.post(
            MCDM_DECISION_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response received:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ SUCCESS - MCDM Decision:")
            print(f"   Optimal Network: {data.get('optimal_network')}")
            print(f"   Optimal Cost: {data.get('optimal_cost')}")
            print(f"   Algorithm: {data.get('decision_summary', {}).get('algorithm')}")
            
            return True
            
        else:
            print(f"\n❌ FAILED - Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def main():
    """
    Main test runner
    """
    print("\n" + "="*70)
    print("🚀 API ML VERIFICATION SCRIPT")
    print("="*70)
    print("\nThis script tests the ML decision endpoint")
    print("and compares it with the MCDM baseline.")
    
    # Test ML endpoint
    ml_success = test_ml_decision_endpoint()
    
    # Test MCDM endpoint for comparison
    mcdm_success = test_mcdm_decision_endpoint()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"   ML Endpoint (/decision/ml): {'✅ PASSED' if ml_success else '❌ FAILED'}")
    print(f"   MCDM Endpoint (/decision): {'✅ PASSED' if mcdm_success else '❌ FAILED'}")
    
    if ml_success and mcdm_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check API server and ML model.")
        return 1


if __name__ == "__main__":
    exit(main())
