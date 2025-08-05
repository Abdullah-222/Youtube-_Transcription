# YouTube Video Q&A Backend API

A FastAPI backend that processes YouTube videos and provides AI-powered Q&A capabilities using Pinecone vector database and Google Generative AI.

## 🚀 Features

- **YouTube Video Processing**: Extract transcripts from any YouTube video
- **AI-Powered Q&A**: Ask natural language questions about video content
- **Pinecone Vector Storage**: Cloud-based vector database for scalable storage
- **Google Generative AI**: Advanced embeddings and text generation
- **Fast Queries**: Optimized vector retrieval for quick responses
- **Error Handling**: Comprehensive error recovery and user feedback

## 🏗️ Architecture

### Backend (FastAPI)
- **Python FastAPI** server
- **Google Generative AI** for embeddings and text generation
- **Pinecone** for cloud-based vector storage
- **YouTube Transcript API** for caption extraction

## 📦 Installation

### Prerequisites
- Python 3.8+
- Google API Key for Gemini models
- Pinecone API Key for vector storage

### Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**
```bash
# Create .env file in backend directory
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
echo "PINECONE_API_KEY=your_pinecone_api_key_here" >> .env
echo "PINECONE_ENVIRONMENT=gcp-starter" >> .env
echo "PINECONE_INDEX_NAME=youtube-qa-index" >> .env
```

3. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the API**
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=youtube-qa-index
```

### API Setup

1. **Google API Setup**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add the key to your `.env` file

2. **Pinecone Setup**
   - Go to [Pinecone Console](https://app.pinecone.io/)
   - Create a new API key
   - Note your environment (e.g., `gcp-starter`)
   - Add the key and environment to your `.env` file

## 🎯 Usage

### Step 1: Process a Video
1. Send a POST request to `/ask` with a YouTube URL and question
2. The system will automatically extract the transcript
3. Create vector embeddings and store them in Pinecone
4. Return an AI-generated answer

### Step 2: Ask Questions
1. Use the same endpoint with different questions
2. The system will retrieve relevant context from Pinecone
3. Generate answers using Google's Gemini model

## 🔍 API Endpoints

### Health Check
```http
GET /health
```
Returns system health including Pinecone connection status.

### Ask Question
```http
POST /ask
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=...",
  "question": "What is this video about?"
}
```

### Pinecone Statistics
```http
GET /pinecone-stats
```
Returns Pinecone index statistics including total vectors and namespaces.

### Delete Pinecone Index
```http
DELETE /pinecone-index
```
Deletes the Pinecone index (use with caution).

## 🚀 Performance Optimizations

### Backend
- **Vector Caching**: Each video gets a unique namespace in Pinecone
- **Chunking**: 200-character chunks with 50-character overlap
- **Retrieval**: Top-3 most relevant chunks for context
- **Error Recovery**: Comprehensive error handling

## 📁 Project Structure

```
backend/
├── app/
│   ├── chains/              # AI processing logic
│   │   ├── qa_chain.py     # Main Q&A processing
│   │   └── utils/          # Utility functions
│   ├── models/             # Data schemas
│   ├── pinecone_config.py  # Pinecone configuration
│   └── main.py            # FastAPI application
├── requirements.txt        # Python dependencies
└── .env                  # Environment variables
```

## 🛠️ Development

### Available Scripts

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python test_api.py
python test_comprehensive.py
```

### Testing

**API Tests**
```bash
python test_api.py
```

**Comprehensive Tests**
```bash
python test_comprehensive.py
```

## 🚀 Deployment

### Backend Deployment
- **Railway**: Easy deployment with Python support
- **Heroku**: Traditional Python hosting
- **AWS Lambda**: Serverless deployment
- **Docker**: Containerized deployment

### Environment Variables for Production
Make sure to set all required environment variables in your production environment:
- `GOOGLE_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`
- `PINECONE_INDEX_NAME`

## 🔧 Troubleshooting

### Common Issues

1. **Pinecone Connection Error**
   - Check if Pinecone API key is set correctly
   - Verify environment is correct
   - Ensure index name is unique

2. **Video Processing Fails**
   - Ensure video has captions enabled
   - Check video is publicly accessible
   - Verify YouTube URL format

3. **Slow Response Times**
   - First-time processing takes longer due to vector creation
   - Subsequent queries use cached embeddings
   - Check internet connection for API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Generative AI** for powerful language models
- **YouTube Transcript API** for caption extraction
- **Pinecone** for cloud-based vector storage
- **FastAPI** for the excellent framework 