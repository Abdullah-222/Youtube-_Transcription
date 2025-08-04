from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schema import QuestionRequest
from app.chains.qa_chain import ask_video_question
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Transcription Tool API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Transcription Tool API", "version": "1.0.0"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        logger.info(f"Received question request for video URL: {request.video_url}")
        start_time = datetime.now()
        
        answer = ask_video_question(request.video_url, request.question)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Question processed in {processing_time:.2f} seconds")
        
        return {
            "answer": answer,
            "video_url": request.video_url,
            "question": request.question,
            "processing_time": processing_time
        }
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if Google API key is available
        api_key = os.getenv('GOOGLE_API_KEY')
        api_key_status = "configured" if api_key else "missing"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "api_key": api_key_status,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/vector-stores")
async def list_vector_stores():
    """List all stored vector stores"""
    try:
        import os
        vector_stores_dir = "./vector_stores"
        
        if not os.path.exists(vector_stores_dir):
            return {"vector_stores": [], "message": "No vector stores directory found"}
        
        stores = []
        for item in os.listdir(vector_stores_dir):
            item_path = os.path.join(vector_stores_dir, item)
            if os.path.isdir(item_path):
                stores.append({
                    "id": item,
                    "path": item_path,
                    "created": datetime.fromtimestamp(os.path.getctime(item_path)).isoformat()
                })
        
        return {
            "vector_stores": stores,
            "count": len(stores)
        }
    except Exception as e:
        logger.error(f"Error listing vector stores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing vector stores: {str(e)}")
