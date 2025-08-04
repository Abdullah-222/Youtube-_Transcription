import requests
import json

def test_api():
    url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test ask endpoint with YouTube URL
    data = {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "question": "What is this video about?"
    }
    
    try:
        response = requests.post(f"{url}/ask", json=data)
        print(f"Ask endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Ask endpoint failed: {e}")

if __name__ == "__main__":
    test_api() 