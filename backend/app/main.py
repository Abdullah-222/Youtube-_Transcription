from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schema import QuestionRequest
from app.chains.qa_chain import ask_video_question, clear_conversation_memory, get_conversation_history, get_video_conversation_history, clear_video_memory, get_all_video_memories
from app.chains.utils.transcript_loader import extract_video_id
from app.pinecone_config import get_pinecone_manager
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
    allow_origins=[
        "*"   ],
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
        
        # Check if Pinecone API key is available
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        pinecone_status = "configured" if pinecone_api_key else "missing"
        
        # Check Pinecone connection
        pinecone_health = "unknown"
        if pinecone_api_key:
            try:
                pinecone_manager = get_pinecone_manager()
                index = pinecone_manager.get_index()
                stats = index.describe_index_stats()
                pinecone_health = "connected"
                total_vectors = stats.get('total_vector_count', 0)
            except Exception as e:
                logger.error(f"Pinecone health check failed: {e}")
                pinecone_health = "error"
                total_vectors = 0
        else:
            total_vectors = 0
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "google_api_key": api_key_status,
            "pinecone_api_key": pinecone_status,
            "pinecone_health": pinecone_health,
            "total_vectors": total_vectors,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/pinecone-stats")
async def get_pinecone_stats():
    """Get Pinecone index statistics"""
    try:
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not pinecone_api_key:
            raise HTTPException(status_code=400, detail="Pinecone API key not configured")
        
        pinecone_manager = get_pinecone_manager()
        index = pinecone_manager.get_index()
        stats = index.describe_index_stats()
        
        return {
            "index_name": pinecone_manager.index_name,
            "environment": pinecone_manager.environment,
            "total_vectors": stats.get('total_vector_count', 0),
            "namespaces": stats.get('namespaces', {}),
            "dimension": pinecone_manager.dimension,
            "metric": pinecone_manager.metric
        }
    except Exception as e:
        logger.error(f"Error getting Pinecone stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting Pinecone stats: {str(e)}")

@app.delete("/pinecone-index")
async def delete_pinecone_index():
    """Delete the Pinecone index (use with caution)"""
    try:
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not pinecone_api_key:
            raise HTTPException(status_code=400, detail="Pinecone API key not configured")
        
        pinecone_manager = get_pinecone_manager()
        pinecone_manager.delete_index()
        
        return {
            "message": f"Index {pinecone_manager.index_name} deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error deleting Pinecone index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting Pinecone index: {str(e)}")

@app.get("/conversation-history")
async def get_conversation_history_endpoint():
    """Get the current conversation history"""
    try:
        history = get_conversation_history()
        return {
            "conversation_history": [
                {
                    "type": message.type,
                    "content": message.content,
                    "timestamp": datetime.now().isoformat()
                }
                for message in history
            ],
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting conversation history: {str(e)}")

@app.get("/video-conversation-history/{video_id}")
async def get_video_conversation_history_endpoint(video_id: str):
    """Get conversation history for a specific video"""
    try:
        history = get_video_conversation_history(video_id)
        return {
            "video_id": video_id,
            "conversation_history": [
                {
                    "type": message.type,
                    "content": message.content,
                    "timestamp": datetime.now().isoformat()
                }
                for message in history
            ],
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting video conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting video conversation history: {str(e)}")

@app.get("/video-memories")
async def get_video_memories_endpoint():
    """Get all video memories for debugging"""
    try:
        memories = get_all_video_memories()
        return {
            "video_memories": memories,
            "total_videos": len(memories),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting video memories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting video memories: {str(e)}")

@app.delete("/conversation-history")
async def clear_conversation_history():
    """Clear the conversation history"""
    try:
        clear_conversation_memory()
        return {
            "message": "Conversation history cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing conversation history: {str(e)}")

@app.delete("/video-conversation-history/{video_id}")
async def clear_video_conversation_history(video_id: str):
    """Clear conversation history for a specific video"""
    try:
        clear_video_memory(video_id)
        return {
            "message": f"Conversation history cleared successfully for video: {video_id}",
            "video_id": video_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing video conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing video conversation history: {str(e)}")

@app.get("/debug/video/{video_id}")
async def debug_video_content(video_id: str):
    """Debug endpoint to check video content and vector store"""
    try:
        from app.chains.utils.transcript_loader import get_transcript
        from app.chains.qa_chain import get_namespace_for_video
        from app.pinecone_config import get_pinecone_manager
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_pinecone import Pinecone
        
        # Get transcript
        transcript = get_transcript(video_id)
        transcript_status = "success" if not transcript.startswith("Error:") else "error"
        transcript_length = len(transcript) if transcript_status == "success" else 0
        
        # Check Pinecone
        pinecone_manager = get_pinecone_manager()
        index = pinecone_manager.get_index()
        namespace = get_namespace_for_video(video_id)
        
        # Get index stats
        stats = index.describe_index_stats()
        namespaces = stats.get('namespaces', {})
        namespace_exists = namespace in namespaces
        namespace_vectors = namespaces.get(namespace, {}).get('vector_count', 0) if namespace_exists else 0
        
        # Try to get embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Try to load vector store
        vectorstore = None
        vectorstore_status = "not_found"
        if namespace_exists:
            try:
                vectorstore = Pinecone.from_existing_index(
                    index_name=pinecone_manager.index_name,
                    embedding=embeddings,
                    namespace=namespace
                )
                vectorstore_status = "loaded"
            except Exception as e:
                vectorstore_status = f"error: {str(e)}"
        
        return {
            "video_id": video_id,
            "transcript": {
                "status": transcript_status,
                "length": transcript_length,
                "preview": transcript[:200] + "..." if transcript_length > 200 else transcript
            },
            "pinecone": {
                "namespace": namespace,
                "namespace_exists": namespace_exists,
                "vector_count": namespace_vectors,
                "total_vectors": stats.get('total_vector_count', 0)
            },
            "vectorstore": {
                "status": vectorstore_status
            }
        }
    except Exception as e:
        logger.error(f"Error debugging video content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error debugging video content: {str(e)}")

@app.get("/debug/test-embedding")
async def test_embedding():
    """Test embedding functionality"""
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        test_text = "This is a test embedding"
        
        # Test embedding
        embedding = embeddings.embed_query(test_text)
        embedding_length = len(embedding)
        
        return {
            "status": "success",
            "embedding_length": embedding_length,
            "test_text": test_text
        }
    except Exception as e:
        logger.error(f"Error testing embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing embedding: {str(e)}")

@app.get("/debug/test-transcript/{video_id}")
async def test_transcript(video_id: str):
    """Test transcript retrieval for a specific video"""
    try:
        from app.chains.utils.transcript_loader import get_transcript
        
        transcript = get_transcript(video_id)
        
        return {
            "video_id": video_id,
            "transcript": transcript,
            "length": len(transcript),
            "is_error": transcript.startswith("Error:")
        }
    except Exception as e:
        logger.error(f"Error testing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing transcript: {str(e)}")

@app.post("/extension/analyze")
async def analyze_video_extension(request: QuestionRequest):
    """Extension-specific endpoint for video analysis"""
    try:
        logger.info(f"Extension request received for video URL: {request.video_url}")
        logger.info(f"Extension question: {request.question}")
        
        # Validate YouTube URL
        video_id = extract_video_id(request.video_url)
        if not video_id:
            logger.error(f"Invalid YouTube URL: {request.video_url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        logger.info(f"Extracted video ID: {video_id}")
        
        # Process the video
        answer = ask_video_question(request.video_url, request.question)
        
        logger.info(f"Extension request completed successfully")
        
        return {
            "answer": answer,
            "video_url": request.video_url,
            "video_id": video_id,
            "question": request.question
        }
    except Exception as e:
        logger.error(f"Extension request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/extension/test")
async def test_extension_endpoint():
    """Test endpoint for extension connectivity"""
    return {
        "message": "Extension endpoint is working!",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/context/{video_id}")
async def debug_context_for_video(video_id: str, question: str = "What is this video about?"):
    """Debug endpoint to check what context is being passed to the LLM"""
    try:
        from app.chains.utils.transcript_loader import get_transcript
        from app.chains.qa_chain import get_namespace_for_video, get_memory_for_video
        from app.pinecone_config import get_pinecone_manager
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_pinecone import Pinecone
        
        # Get transcript
        transcript = get_transcript(video_id)
        transcript_status = "success" if not transcript.startswith("Error:") else "error"
        transcript_length = len(transcript) if transcript_status == "success" else 0
        
        # Check Pinecone
        pinecone_manager = get_pinecone_manager()
        index = pinecone_manager.get_index()
        namespace = get_namespace_for_video(video_id)
        
        # Get index stats
        stats = index.describe_index_stats()
        namespaces = stats.get('namespaces', {})
        namespace_exists = namespace in namespaces
        namespace_vectors = namespaces.get(namespace, {}).get('vector_count', 0) if namespace_exists else 0
        
        # Try to get embeddings and vector store
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        vectorstore = None
        vectorstore_status = "not_found"
        retrieved_docs = []
        context_from_vector = ""
        
        if namespace_exists:
            try:
                vectorstore = Pinecone.from_existing_index(
                    index_name=pinecone_manager.index_name,
                    embedding=embeddings,
                    namespace=namespace
                )
                vectorstore_status = "loaded"
                
                # Try to retrieve documents
                retriever = vectorstore.as_retriever(
                    search_kwargs={
                        "k": 8,
                        "namespace": namespace,
                        "score_threshold": 0.3
                    }
                )
                
                docs = retriever.invoke(question)
                retrieved_docs = [doc.page_content for doc in docs]
                context_from_vector = "\n".join(retrieved_docs)
                
            except Exception as e:
                vectorstore_status = f"error: {str(e)}"
        
        # Get memory
        video_memory = get_memory_for_video(video_id)
        chat_history = video_memory.chat_memory.messages
        history_text = ""
        
        if chat_history:
            history_text = "\n\nPrevious conversation context:\n"
            for i, message in enumerate(chat_history[-6:]):
                role = "User" if message.type == "human" else "Assistant"
                history_text += f"{role}: {message.content}\n"
        
        # Simulate the context that would be passed to LLM
        full_context = f"""Video Transcript (Full):
{transcript}

Relevant Content from Vector Search:
{context_from_vector}

{history_text}

User's question: {question}"""
        
        return {
            "video_id": video_id,
            "question": question,
            "transcript": {
                "status": transcript_status,
                "length": transcript_length,
                "preview": transcript[:500] + "..." if transcript_length > 500 else transcript
            },
            "vector_search": {
                "status": vectorstore_status,
                "namespace": namespace,
                "vector_count": namespace_vectors,
                "retrieved_docs_count": len(retrieved_docs),
                "context_length": len(context_from_vector)
            },
            "memory": {
                "messages_count": len(chat_history),
                "history_preview": history_text[:200] + "..." if len(history_text) > 200 else history_text
            },
            "full_context": {
                "total_length": len(full_context),
                "preview": full_context[:1000] + "..." if len(full_context) > 1000 else full_context
            }
        }
    except Exception as e:
        logger.error(f"Error debugging context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error debugging context: {str(e)}")
