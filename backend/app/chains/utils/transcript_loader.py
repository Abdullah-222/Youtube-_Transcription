from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import re

def validate_video_id(video_id: str) -> bool:
    """Validate if the video ID format is correct"""
    # YouTube video IDs are typically 11 characters long
    if not video_id or len(video_id) != 11:
        return False
    
    # YouTube video IDs contain only alphanumeric characters, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return False
    
    return True

def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as is if it's already an ID"""
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return url_or_id

# def get_transcript(video_id: str) -> str:
#     """Get transcript for a YouTube video with improved error handling"""
#     try:
#         # Clean and validate video ID
#         clean_video_id = extract_video_id(video_id.strip())
        
#         if not validate_video_id(clean_video_id):
#             return "Error: Invalid YouTube video ID format. Please provide a valid 11-character video ID."
        
#         # Create YouTubeTranscriptApi instance
#         transcript_api = YouTubeTranscriptApi()
        
#         # Get transcript using the correct method
#         transcript = transcript_api.fetch(clean_video_id)
        
        
#         if not transcript:
#             return "Error: No transcript available for this video."
        
#         # Handle the new transcript format
#         if hasattr(transcript, 'snippets'):
#             # New format: transcript has snippets attribute
#             full_text = " ".join([snippet.text for snippet in transcript.snippets])
#         elif hasattr(transcript, '__iter__'):
#             # Old format: transcript is iterable
#             full_text = " ".join([t["text"] for t in transcript])
#         else:
#             # Fallback: try to convert to string
#             full_text = str(transcript)
        
#         if not full_text.strip():
#             return "Error: Transcript is empty for this video."
        
#         return full_text
        
#     except TranscriptsDisabled:
#         return "Error: Transcripts are disabled for this video."
#     except NoTranscriptFound:
#         return "Error: No transcript found for this video. The video may not have captions enabled."
#     except VideoUnavailable:
#         return "Error: Video is unavailable or private. Please check if the video exists and is publicly accessible."
#     except Exception as e:
#         return f"Error retrieving transcript: {str(e)}"


def get_transcript(video_id: str) -> str:
    """Get transcript for a YouTube video with improved error handling"""
    try:
        # Clean and validate video ID
        clean_video_id = extract_video_id(video_id.strip())
        
        if not validate_video_id(clean_video_id):
            return "Error: Invalid YouTube video ID format. Please provide a valid 11-character video ID."
        
        # Create YouTubeTranscriptApi instance and get transcript using the correct method
        api = YouTubeTranscriptApi()
        transcript = api.fetch(clean_video_id)
        
        if not transcript:
            return "Error: No transcript available for this video."
        
        # Extract text from transcript - handle new API format
        full_text = ""
        for snippet in transcript:
            if hasattr(snippet, 'text'):
                full_text += snippet.text + " "
            elif hasattr(snippet, '__getitem__') and 'text' in snippet:
                full_text += snippet['text'] + " "
            else:
                # Fallback: convert to string
                full_text += str(snippet) + " "
        
        if not full_text.strip():
            return "Error: Transcript is empty for this video."
        
        return full_text.strip()
        
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "Error: No transcript found for this video. The video may not have captions enabled."
    except VideoUnavailable:
        return "Error: Video is unavailable or private. Please check if the video exists and is publicly accessible."
    except Exception as e:
        return f"Error retrieving transcript: {str(e)}"
