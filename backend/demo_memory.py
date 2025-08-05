#!/usr/bin/env python3
"""
Demonstration script showing how buffer memory works in the transcription tool.
This script shows a simple conversation flow with memory retention.
"""

import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_VIDEO = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def demo_memory_workflow():
    """Demonstrate how buffer memory works"""
    print("🎬 Buffer Memory Demonstration")
    print("=" * 50)
    print("This demo shows how the system remembers conversation context.")
    print()
    
    # Clear any existing memory
    print("1️⃣ Clearing existing memory...")
    clear_memory()
    
    # Initial question
    print("\n2️⃣ Asking initial question...")
    question1 = "What is this video about?"
    print(f"   User: {question1}")
    
    response1 = ask_question(TEST_VIDEO, question1)
    print(f"   Assistant: {response1['answer'][:150]}...")
    
    # Follow-up question that should use context
    print("\n3️⃣ Asking follow-up question...")
    question2 = "Can you tell me more about what you just mentioned?"
    print(f"   User: {question2}")
    
    response2 = ask_question(TEST_VIDEO, question2)
    print(f"   Assistant: {response2['answer'][:150]}...")
    
    # Another follow-up
    print("\n4️⃣ Asking another follow-up...")
    question3 = "What were the key points from our discussion?"
    print(f"   User: {question3}")
    
    response3 = ask_question(TEST_VIDEO, question3)
    print(f"   Assistant: {response3['answer'][:150]}...")
    
    # Check conversation history
    print("\n5️⃣ Checking conversation history...")
    history = get_conversation_history()
    print(f"   Total messages in memory: {history['message_count']}")
    
    print("\n✅ Memory demonstration completed!")
    print("\n📝 Key Points:")
    print("- Each question and answer is stored in memory")
    print("- Follow-up questions can reference previous context")
    print("- Memory is video-specific (different videos have separate memories)")
    print("- Memory persists across multiple requests")

def demo_memory_isolation():
    """Demonstrate memory isolation between different videos"""
    print("\n🎬 Memory Isolation Demonstration")
    print("=" * 50)
    print("This demo shows how different videos have separate memories.")
    print()
    
    # Clear memory
    print("1️⃣ Clearing memory...")
    clear_memory()
    
    # Ask question about first video
    print("\n2️⃣ Asking about first video...")
    video1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    question1 = "What is this video about?"
    print(f"   User (Video 1): {question1}")
    
    response1 = ask_question(video1, question1)
    print(f"   Assistant: {response1['answer'][:100]}...")
    
    # Ask question about second video
    print("\n3️⃣ Asking about second video...")
    video2 = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    question2 = "What is this video about?"
    print(f"   User (Video 2): {question2}")
    
    response2 = ask_question(video2, question2)
    print(f"   Assistant: {response2['answer'][:100]}...")
    
    # Ask follow-up about first video
    print("\n4️⃣ Asking follow-up about first video...")
    followup1 = "Can you elaborate on what you mentioned earlier?"
    print(f"   User (Video 1): {followup1}")
    
    response_followup1 = ask_question(video1, followup1)
    print(f"   Assistant: {response_followup1['answer'][:100]}...")
    
    # Check memory for both videos
    print("\n5️⃣ Checking memory isolation...")
    memories = get_video_memories()
    print(f"   Videos with memory: {memories['total_videos']}")
    for video_id, message_count in memories['video_memories'].items():
        print(f"   Video {video_id}: {message_count} messages")
    
    print("\n✅ Memory isolation demonstration completed!")
    print("\n📝 Key Points:")
    print("- Each video has its own separate memory")
    print("- Questions about one video don't affect another video's memory")
    print("- Follow-up questions work correctly for each video")

def ask_question(video_url: str, question: str):
    """Send a question to the API"""
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={
                "video_url": video_url,
                "question": question
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return {"answer": f"Error: {e}"}

def get_conversation_history():
    """Get conversation history"""
    try:
        response = requests.get(f"{BASE_URL}/conversation-history")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return {"message_count": 0}

def get_video_memories():
    """Get all video memories"""
    try:
        response = requests.get(f"{BASE_URL}/video-memories")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return {"video_memories": {}, "total_videos": 0}

def clear_memory():
    """Clear conversation memory"""
    try:
        response = requests.delete(f"{BASE_URL}/conversation-history")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def main():
    """Main demonstration function"""
    print("🚀 Buffer Memory System Demonstration")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return
    
    # Run demonstrations
    demo_memory_workflow()
    demo_memory_isolation()
    
    print("\n🎉 Demonstration completed!")
    print("\n💡 How Buffer Memory Works:")
    print("1. Each question and answer pair is stored in memory")
    print("2. Memory is video-specific (different videos have separate memories)")
    print("3. Follow-up questions can reference previous conversation context")
    print("4. Memory persists across multiple requests until cleared")
    print("5. The AI uses this context to provide more relevant answers")

if __name__ == "__main__":
    main() 