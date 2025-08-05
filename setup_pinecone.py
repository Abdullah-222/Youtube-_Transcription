#!/usr/bin/env python3
"""
Pinecone Setup Script for YouTube Video Q&A Tool

This script helps you set up Pinecone for the migration from ChromaDB.
"""

import os
import sys
import requests
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        'GOOGLE_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT',
        'PINECONE_INDEX_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease add these to your backend/.env file")
        return False
    
    print("✅ All environment variables are set")
    return True

def test_pinecone_connection():
    """Test Pinecone connection"""
    try:
        import pinecone
        from app.pinecone_config import get_pinecone_manager
        
        print("🔗 Testing Pinecone connection...")
        pinecone_manager = get_pinecone_manager()
        index = pinecone_manager.create_index_if_not_exists()
        
        # Test basic operations
        stats = index.describe_index_stats()
        print(f"✅ Pinecone connection successful!")
        print(f"   Index: {pinecone_manager.index_name}")
        print(f"   Environment: {pinecone_manager.environment}")
        print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

def test_backend_health():
    """Test backend health endpoint"""
    try:
        print("🏥 Testing backend health...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Google API: {data.get('google_api_key', 'unknown')}")
            print(f"   Pinecone API: {data.get('pinecone_api_key', 'unknown')}")
            print(f"   Pinecone Health: {data.get('pinecone_health', 'unknown')}")
            print(f"   Total Vectors: {data.get('total_vectors', 0)}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start the server first:")
        print("   cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_video_processing():
    """Test video processing with a sample video"""
    try:
        print("🎥 Testing video processing...")
        
        # Use a simple test video
        test_data = {
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "question": "What is this video about?"
        }
        
        response = requests.post(
            "http://localhost:8000/ask",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Video processing successful!")
            print(f"   Processing time: {data.get('processing_time', 0):.2f} seconds")
            print(f"   Answer length: {len(data.get('answer', ''))} characters")
            return True
        else:
            print(f"❌ Video processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Video processing error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Pinecone Migration Setup")
    print("=" * 40)
    
    # Step 1: Check environment
    print("\n1. Checking environment variables...")
    if not check_environment():
        return False
    
    # Step 2: Test Pinecone connection
    print("\n2. Testing Pinecone connection...")
    if not test_pinecone_connection():
        return False
    
    # Step 3: Test backend health
    print("\n3. Testing backend health...")
    if not test_backend_health():
        return False
    
    # Step 4: Test video processing
    print("\n4. Testing video processing...")
    if not test_video_processing():
        return False
    
    print("\n🎉 Setup complete! Your migration to Pinecone is successful!")
    print("\nNext steps:")
    print("1. Start your frontend: npm run dev:frontend")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Test with different YouTube videos")
    print("4. Monitor Pinecone usage in the console")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 