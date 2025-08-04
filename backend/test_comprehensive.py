import requests
import json
import time
import os
from datetime import datetime

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("=== Transcription Tool API Comprehensive Test ===\n")
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test 2: Root endpoint
    print("\n2. Testing Root Endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        if response.status_code == 200:
            print("   ✅ Root endpoint working")
        else:
            print("   ❌ Root endpoint failed")
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
    
    # Test 3: Vector Stores List (before any requests)
    print("\n3. Testing Vector Stores List (before requests)...")
    try:
        response = requests.get(f"{base_url}/vector-stores")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        if response.status_code == 200:
            print("   ✅ Vector stores endpoint working")
        else:
            print("   ❌ Vector stores endpoint failed")
    except Exception as e:
        print(f"   ❌ Vector stores endpoint failed: {e}")
    
    # Test 4: Invalid video URL test
    print("\n4. Testing Invalid Video URL...")
    invalid_data = {
        "video_url": "https://invalid-url.com",
        "question": "What is this video about?"
    }
    try:
        response = requests.post(f"{base_url}/ask", json=invalid_data)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        if "Error" in result.get("answer", ""):
            print("   ✅ Invalid video URL handled correctly")
        else:
            print("   ❌ Invalid video URL not handled properly")
    except Exception as e:
        print(f"   ❌ Invalid video URL test failed: {e}")
    
    # Test 5: Valid video URL test (using a known video with transcript)
    print("\n5. Testing Valid Video URL...")
    # Using a popular video that should have transcripts
    valid_data = {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - should have transcript
        "question": "What is the main topic of this video?"
    }
    try:
        print("   Sending request...")
        start_time = time.time()
        response = requests.post(f"{base_url}/ask", json=valid_data)
        end_time = time.time()
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Processing time: {result.get('processing_time', 'N/A')} seconds")
        print(f"   Response length: {len(str(result))} characters")
        
        if response.status_code == 200 and "answer" in result:
            print("   ✅ Valid video URL processed successfully")
            if "Error" not in result["answer"]:
                print("   ✅ Answer generated successfully")
            else:
                print(f"   ⚠️  Answer contains error: {result['answer']}")
        else:
            print("   ❌ Valid video URL test failed")
    except Exception as e:
        print(f"   ❌ Valid video URL test failed: {e}")
    
    # Test 6: Vector Stores List (after requests)
    print("\n6. Testing Vector Stores List (after requests)...")
    try:
        response = requests.get(f"{base_url}/vector-stores")
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Vector stores count: {result.get('count', 0)}")
        print(f"   Response: {result}")
        if response.status_code == 200:
            print("   ✅ Vector stores endpoint working after requests")
        else:
            print("   ❌ Vector stores endpoint failed")
    except Exception as e:
        print(f"   ❌ Vector stores endpoint failed: {e}")
    
    # Test 7: Same video URL test (should use cached embeddings)
    print("\n7. Testing Same Video URL (should use cached embeddings)...")
    try:
        print("   Sending request for same video...")
        start_time = time.time()
        response = requests.post(f"{base_url}/ask", json=valid_data)
        end_time = time.time()
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Processing time: {result.get('processing_time', 'N/A')} seconds")
        
        if response.status_code == 200:
            print("   ✅ Same video URL processed successfully")
            # Second request should be faster due to cached embeddings
            if result.get('processing_time', 0) < 5:  # Should be faster
                print("   ✅ Cached embeddings working (faster response)")
            else:
                print("   ⚠️  Response time suggests no caching")
        else:
            print("   ❌ Same video URL test failed")
    except Exception as e:
        print(f"   ❌ Same video URL test failed: {e}")
    
    # Test 8: Different video URL test
    print("\n8. Testing Different Video URL...")
    different_data = {
        "video_url": "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
        "question": "What is the main message of this video?"
    }
    try:
        print("   Sending request for different video...")
        start_time = time.time()
        response = requests.post(f"{base_url}/ask", json=different_data)
        end_time = time.time()
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Processing time: {result.get('processing_time', 'N/A')} seconds")
        
        if response.status_code == 200:
            print("   ✅ Different video URL processed successfully")
        else:
            print("   ❌ Different video URL test failed")
    except Exception as e:
        print(f"   ❌ Different video URL test failed: {e}")
    
    print("\n=== Test Summary ===")
    print("Check the console output above for detailed results.")
    print("If you see ✅ marks, those tests passed.")
    print("If you see ❌ marks, those tests failed.")
    print("If you see ⚠️ marks, those tests had warnings.")

if __name__ == "__main__":
    test_api() 