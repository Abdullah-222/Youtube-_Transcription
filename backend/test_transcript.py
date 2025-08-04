#!/usr/bin/env python3

from app.chains.utils.transcript_loader import get_transcript, extract_video_id

def test_transcript():
    video_url = "https://youtu.be/-w53i6Ae-YM?si=0iibFAZzvPW4XXRu"
    video_id = extract_video_id(video_url)
    print(f"Extracted video ID: {video_id}")
    
    transcript = get_transcript(video_id)
    print(f"Transcript result: {transcript[:200]}...")
    
    if transcript.startswith("Error"):
        print("❌ Transcript retrieval failed")
        return False
    else:
        print("✅ Transcript retrieval successful")
        return True

if __name__ == "__main__":
    test_transcript() 