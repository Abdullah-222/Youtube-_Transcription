# YouTube Video Q&A Tool

A powerful AI-powered tool that allows users to ask questions about YouTube videos by analyzing their transcripts. Built with Next.js frontend and FastAPI backend.

## 🚀 Features

- **YouTube Video Processing**: Extract transcripts from any YouTube video
- **AI-Powered Q&A**: Ask natural language questions about video content
- **Fast Queries**: Optimized vector storage for quick responses
- **Modern UI**: Clean, responsive interface with real-time status
- **Error Handling**: Comprehensive error recovery and user feedback
- **Caching**: Persistent vector stores for faster subsequent queries

## 🏗️ Architecture

### Frontend (Next.js)
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Real-time status monitoring**
- **Optimized API calls**

### Backend (FastAPI)
- **Python FastAPI** server
- **Google Generative AI** for embeddings and text generation
- **ChromaDB** for vector storage
- **YouTube Transcript API** for caption extraction

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.8+
- Google API Key for Gemini models

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd Transcription_Tool
```

2. **Install dependencies**
```bash
npm run install:all
```

3. **Set up environment variables**
```bash
# Create .env file in backend directory
cd backend
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
```

4. **Start both servers**
```bash
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
GOOGLE_API_KEY=your_google_api_key_here
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Google API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your backend `.env` file

## 🎯 Usage

### Step 1: Process a Video
1. Open the application in your browser
2. Paste a YouTube URL in the input field
3. Click "Process Video" to extract the transcript
4. The system will automatically initialize the video with a basic question

### Step 2: Ask Questions
1. Once the video is processed, the question form appears
2. Type any question about the video content
3. Click "Ask Question" to get an AI-generated answer
4. View the answer with processing time information

## 🔍 API Endpoints

### Health Check
```http
GET /health
```

### Ask Question
```http
POST /ask
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=...",
  "question": "What is this video about?"
}
```

### List Vector Stores
```http
GET /vector-stores
```

## 🚀 Performance Optimizations

### Backend
- **Vector Caching**: Each video gets a unique vector store
- **Chunking**: 200-character chunks with 50-character overlap
- **Retrieval**: Top-3 most relevant chunks for context
- **Error Recovery**: Comprehensive error handling

### Frontend
- **Loading States**: Visual feedback during API calls
- **Error Recovery**: Retry functionality for failed requests
- **Status Monitoring**: Real-time backend connection status
- **Optimized Requests**: Efficient API communication

## 📁 Project Structure

```
Transcription_Tool/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── chains/         # AI processing logic
│   │   ├── models/         # Data schemas
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── vector_stores/      # Cached embeddings
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utility libraries
│   │   └── types/         # TypeScript types
│   └── package.json       # Node.js dependencies
└── package.json           # Root package.json
```

## 🛠️ Development

### Available Scripts

```bash
# Start both frontend and backend
npm run dev

# Start only backend
npm run dev:backend

# Start only frontend
npm run dev:frontend

# Build frontend for production
npm run build

# Install all dependencies
npm run install:all
```

### Testing

**Backend Tests**
```bash
cd backend
python test_api.py
python test_comprehensive.py
```

**Frontend Tests**
```bash
cd frontend
npm run test
```

## 🚀 Deployment

### Backend Deployment
- **Railway**: Easy deployment with Python support
- **Heroku**: Traditional Python hosting
- **AWS Lambda**: Serverless deployment
- **Docker**: Containerized deployment

### Frontend Deployment
- **Vercel**: Recommended for Next.js
- **Netlify**: Alternative hosting
- **AWS Amplify**: AWS integration

## 🔧 Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Check if backend is running on port 8000
   - Verify Google API key is set correctly
   - Check CORS settings

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
- **ChromaDB** for vector storage
- **Next.js** and **FastAPI** for the excellent frameworks 