# Transcription Tool Backend

This is the backend for the Transcription Tool that allows you to ask questions about YouTube videos using AI-powered embeddings and retrieval.

## Features

- ✅ YouTube transcript extraction
- ✅ Automatic video ID extraction from YouTube URLs
- ✅ AI-powered embeddings using Google Gemini
- ✅ Persistent vector storage with ChromaDB
- ✅ Question-answering with context retrieval
- ✅ Caching for improved performance
- ✅ Comprehensive error handling
- ✅ Health monitoring endpoints

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file in the backend directory with:
```
GOOGLE_API_KEY=your_google_api_key_here
```

3. Get a Google API Key:
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create a new API key
- Add it to your `.env` file

## Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Check API health and configuration
- Returns: `{"status": "healthy", "timestamp": "...", "api_key": "configured", "version": "1.0.0"}`

### Root Endpoint
- `GET /` - Get API information
- Returns: `{"message": "Transcription Tool API", "version": "1.0.0"}`

### Vector Stores
- `GET /vector-stores` - List all stored vector embeddings
- Returns: `{"vector_stores": [...], "count": 0}`

### Ask Questions
- `POST /ask` - Ask a question about a YouTube video
- Body: `{"video_url": "youtube_url", "question": "your question"}`
- Returns: `{"answer": "AI generated answer", "video_url": "...", "question": "...", "processing_time": 2.5}`

## Supported YouTube URL Formats

The API automatically extracts video IDs from these URL formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`
- Direct video ID (11 characters)

## Testing

### 1. Using the Test Script
Run the comprehensive test script:
```bash
python test_comprehensive.py
```

This will test:
- Health check endpoint
- Root endpoint
- Vector stores listing
- Invalid video URL handling
- Valid video URL processing
- Embedding caching
- Error handling
- Different URL formats

### 2. Using Postman
1. Import the `Transcription_Tool_API.postman_collection.json` file into Postman
2. Make sure your server is running on `http://localhost:8000`
3. Run the collection tests in order

### 3. Manual Testing with curl

Health Check:
```bash
curl -X GET "http://localhost:8000/health"
```

Ask a Question:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "question": "What is this video about?"}'
```

List Vector Stores:
```bash
curl -X GET "http://localhost:8000/vector-stores"
```

## Embeddings Storage

The system now properly stores embeddings:

1. **Persistent Storage**: Vector embeddings are stored in `./vector_stores/` directory
2. **Video-specific**: Each video gets its own vector store folder
3. **Caching**: Subsequent requests for the same video use cached embeddings
4. **Performance**: Cached requests are significantly faster

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY environment variable is not set"**
   - Check your `.env` file exists and contains the API key
   - Restart the server after adding the `.env` file

2. **"Error retrieving transcript"**
   - Verify the YouTube URL is correct
   - Check if the video has captions enabled
   - Ensure the video is publicly accessible

3. **"Error creating vector store"**
   - Check your internet connection
   - Verify your Google API key is valid
   - Check if you have write permissions in the backend directory

4. **"Invalid YouTube URL format"**
   - Make sure you're using a supported URL format
   - The API supports youtube.com, youtu.be, and direct video IDs

5. **Slow response times**
   - First request for a video will be slower (creating embeddings)
   - Subsequent requests should be faster (using cached embeddings)

### Performance Tips

1. **Use valid YouTube URLs**: Full URLs or short URLs work
2. **Check video availability**: Ensure videos have captions enabled
3. **Monitor vector stores**: Use `/vector-stores` endpoint to see stored embeddings
4. **Restart server**: If you change environment variables, restart the server

## File Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   └── schema.py        # Pydantic models with URL validation
│   └── chains/
│       ├── qa_chain.py      # Main QA logic with URL processing
│       └── utils/
│           └── transcript_loader.py  # YouTube transcript extraction
├── vector_stores/           # Persistent embeddings storage
├── test_comprehensive.py    # Comprehensive test script
├── test_api.py             # Basic test script
├── requirements.txt         # Python dependencies
└── README.md              # This file
```

## Example Usage

```python
import requests

# Ask a question about a YouTube video using URL
response = requests.post("http://localhost:8000/ask", json={
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "question": "What is the main topic of this video?"
})

print(response.json())
# Output: {"answer": "...", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "question": "...", "processing_time": 2.5}
```

## URL Examples

The API supports these YouTube URL formats:

```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

```json
{
  "video_url": "https://youtu.be/dQw4w9WgXcQ"
}
```

```json
{
  "video_url": "dQw4w9WgXcQ"
}
``` 