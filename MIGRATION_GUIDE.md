# Migration Guide: ChromaDB to Pinecone

This guide explains the migration from ChromaDB to Pinecone in your YouTube Video Q&A Tool.

## 🔄 What Changed

### Before (ChromaDB)
- **Local Storage**: Vector embeddings stored in local `./vector_stores/` directory
- **File-based**: Each video had its own folder with ChromaDB files
- **Limited Scalability**: Bound by local storage and processing power
- **Simple Setup**: Only required Google API key

### After (Pinecone)
- **Cloud Storage**: Vector embeddings stored in Pinecone cloud database
- **Namespace-based**: Each video gets a unique namespace in Pinecone
- **Scalable**: Cloud-based storage with high availability
- **Enhanced Setup**: Requires both Google API key and Pinecone API key

## 🚀 Benefits of Migration

1. **Scalability**: No longer limited by local storage
2. **Reliability**: Cloud-based storage with high availability
3. **Performance**: Faster queries with optimized cloud infrastructure
4. **Collaboration**: Multiple instances can share the same vector database
5. **Backup**: Automatic cloud backups and redundancy

## 📋 Migration Steps

### Step 1: Get Pinecone API Key

1. Go to [Pinecone Console](https://app.pinecone.io/)
2. Create a new account or sign in
3. Create a new API key
4. Note your environment (e.g., `gcp-starter`, `us-west1-gcp`)

### Step 2: Update Environment Variables

Add these to your `backend/.env` file:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=youtube-qa-index
```

### Step 3: Install New Dependencies

The requirements have been updated. Run:

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Clean Up Old Files (Optional)

If you want to clean up the old ChromaDB files:

```bash
# Remove old vector stores directory
rm -rf backend/vector_stores/
```

## 🔧 Configuration Details

### Pinecone Configuration

The new `pinecone_config.py` file handles:

- **Index Management**: Creates and manages Pinecone indexes
- **Namespace Strategy**: Each video gets a unique namespace
- **Error Handling**: Comprehensive error recovery
- **Health Monitoring**: Connection status and statistics

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Your Pinecone API key | `sk-...` |
| `PINECONE_ENVIRONMENT` | Your Pinecone environment | `gcp-starter` |
| `PINECONE_INDEX_NAME` | Name for your index | `youtube-qa-index` |

## 🔍 New API Endpoints

### Health Check (Enhanced)
```http
GET /health
```
Now includes Pinecone connection status and vector count.

### Pinecone Statistics
```http
GET /pinecone-stats
```
Returns detailed Pinecone index statistics.

### Delete Index (Admin)
```http
DELETE /pinecone-index
```
Deletes the Pinecone index (use with caution).

## 🏗️ Architecture Changes

### Vector Storage Strategy

**Before (ChromaDB):**
```
./vector_stores/
├── video_hash_1/
│   ├── chroma.sqlite3
│   └── embeddings/
└── video_hash_2/
    ├── chroma.sqlite3
    └── embeddings/
```

**After (Pinecone):**
```
Pinecone Index: youtube-qa-index
├── Namespace: video_hash_1
│   └── Vector embeddings
├── Namespace: video_hash_2
│   └── Vector embeddings
└── Namespace: video_hash_3
    └── Vector embeddings
```

### Code Changes

1. **QA Chain**: Updated to use Pinecone instead of ChromaDB
2. **Configuration**: New Pinecone manager class
3. **API Endpoints**: Enhanced health checks and statistics
4. **Error Handling**: Improved error messages for Pinecone issues

## 🧪 Testing the Migration

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Should show Pinecone as "connected".

### 2. Process a Video
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "question": "What is this video about?"}'
```

### 3. Check Pinecone Stats
```bash
curl http://localhost:8000/pinecone-stats
```

## 🔧 Troubleshooting

### Common Issues

1. **"PINECONE_API_KEY environment variable is required"**
   - Check your `.env` file has the correct API key
   - Restart the server after adding the key

2. **"Failed to initialize Pinecone"**
   - Verify your API key is correct
   - Check your environment setting
   - Ensure you have internet connection

3. **"Index not found"**
   - The system will automatically create the index
   - Check if you have permissions to create indexes

4. **"Namespace not found"**
   - This is normal for new videos
   - The system will create the namespace automatically

### Performance Notes

- **First Request**: May take longer as it creates the index
- **Subsequent Requests**: Should be faster with cached embeddings
- **Cloud Latency**: Slight increase due to cloud API calls
- **Scalability**: Much better for multiple users

## 📊 Monitoring

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "google_api_key": "configured",
  "pinecone_api_key": "configured",
  "pinecone_health": "connected",
  "total_vectors": 150,
  "version": "1.0.0"
}
```

### Pinecone Statistics
```json
{
  "index_name": "youtube-qa-index",
  "environment": "gcp-starter",
  "total_vectors": 150,
  "namespaces": {
    "video_hash_1": {"vector_count": 50},
    "video_hash_2": {"vector_count": 100}
  },
  "dimension": 768,
  "metric": "cosine"
}
```

## 🚀 Next Steps

1. **Test thoroughly** with different YouTube videos
2. **Monitor performance** and adjust chunk sizes if needed
3. **Set up monitoring** for Pinecone usage
4. **Consider backup strategies** for your Pinecone data
5. **Optimize costs** by monitoring vector usage

## 📞 Support

If you encounter issues:

1. Check the health endpoint for detailed status
2. Verify all environment variables are set
3. Test with a simple YouTube video first
4. Check Pinecone console for index status
5. Review server logs for detailed error messages

## 🎉 Migration Complete!

Your application is now using Pinecone for scalable, cloud-based vector storage. Enjoy the improved performance and scalability! 