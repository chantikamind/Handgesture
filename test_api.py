#!/usr/bin/env python
"""Test script for Hand Gesture Recognition API"""

import requests
import json
import numpy as np

API_URL = "http://localhost:5000"

def test_get_gesture():
    """Test getting current gesture status"""
    print("[TEST] Getting current gesture status...")
    response = requests.get(f"{API_URL}/api/gesture")
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Status: {data.get('gesture')}")
        print(f"  [OK] Confidence: {data.get('confidence')}")
        print(f"  [OK] Categories: {data.get('categories')}")
        print(f"  [OK] Features length: {len(data.get('features', [])) if data.get('features') else 'None'}")
        return True
    else:
        print(f"  [ERROR] Status code: {response.status_code}")
        return False

def test_save_gesture():
    """Test saving a gesture"""
    print("\n[TEST] Testing save gesture endpoint...")
    
    # Create a dummy feature vector
    dummy_features = list(np.random.rand(42))  # 42D feature vector
    
    payload = {
        'gesture_name': 'test_gesture',
        'features': dummy_features
    }
    
    print(f"  [INFO] Sending payload with gesture_name='test_gesture'")
    print(f"  [INFO] Feature vector length: {len(dummy_features)}")
    
    response = requests.post(
        f"{API_URL}/api/save_gesture",
        json=payload
    )
    
    print(f"  [INFO] Response status: {response.status_code}")
    print(f"  [INFO] Response: {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Message: {data.get('message')}")
        print(f"  [OK] Gesture ID: {data.get('gesture_id')}")
        print(f"  [OK] Total categories: {data.get('total_categories')}")
        return True
    else:
        print(f"  [ERROR] Failed to save gesture")
        try:
            error_data = response.json()
            print(f"  [ERROR] Details: {error_data}")
        except:
            print(f"  [ERROR] Response: {response.text}")
        return False

def test_list_gestures():
    """Test listing all saved gestures"""
    print("\n[TEST] Listing all saved gestures...")
    response = requests.get(f"{API_URL}/api/gestures/list")
    if response.status_code == 200:
        data = response.json()
        gestures = data.get('gestures', [])
        print(f"  [OK] Found {len(gestures)} gestures")
        for g in gestures:
            print(f"      - ID {g['id']}: {g['name']}")
        return True
    else:
        print(f"  [ERROR] Status code: {response.status_code}")
        return False

def test_save_model():
    """Test saving the model"""
    print("\n[TEST] Testing save model endpoint...")
    response = requests.post(f"{API_URL}/api/save_model")
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Message: {data.get('message')}")
        return True
    else:
        print(f"  [ERROR] Status code: {response.status_code}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  HAND GESTURE RECOGNITION - API TEST")
    print("="*60 + "\n")
    
    # Run tests
    test_get_gesture()
    test_save_gesture()
    test_list_gestures()
    test_save_model()
    
    print("\n" + "="*60)
    print("  TESTS COMPLETED")
    print("="*60 + "\n")
