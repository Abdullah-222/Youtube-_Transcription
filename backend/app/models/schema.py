from pydantic import BaseModel, validator
import re

class QuestionRequest(BaseModel):
    video_url: str
    question: str
    
    @validator('video_url')
    def validate_video_url(cls, v):
        """Validate and extract video ID from YouTube URL"""
        if not v:
            raise ValueError('Video URL is required')
        
        # YouTube URL patterns
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, v)
            if match:
                return v  # Return the original URL, we'll extract ID in the backend
        
        raise ValueError('Invalid YouTube URL format. Please provide a valid YouTube URL or video ID.')

