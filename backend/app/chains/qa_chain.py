from app.chains.utils.transcript_loader import get_transcript, extract_video_id
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from app.pinecone_config import get_pinecone_manager
import os
from dotenv import load_dotenv
import hashlib
import logging
import time
import re

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global variable to store vector stores
vector_stores = {}

# Global memory for conversation context - improved implementation
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="question",
    output_key="answer"
)

# Dictionary to store video-specific memories
video_memories = {}

def get_namespace_for_video(video_id: str) -> str:
    """Generate a unique namespace for storing vector embeddings for a video"""
    # Create a hash of the video_id for safe namespace naming
    video_hash = hashlib.md5(video_id.encode()).hexdigest()
    return f"video_{video_hash}"

def get_memory_for_video(video_id: str) -> ConversationBufferMemory:
    """Get or create memory for a specific video"""
    if video_id not in video_memories:
        video_memories[video_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="question",
            output_key="answer"
        )
    return video_memories[video_id]

def ask_video_question(video_url: str, question: str) -> str:
    try:
        # Check if Google API key is set
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "I'm currently unable to process video analysis. Please contact the system administrator."
        
        # Check if Pinecone API key is set
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not pinecone_api_key:
            return "I'm currently unable to process video analysis. Pinecone configuration is missing. Please contact the system administrator."
        
        # Extract video ID from URL
        video_id = extract_video_id(video_url)
        if not video_id:
            return "I couldn't recognize that as a valid YouTube URL. Please provide a complete YouTube video link."
        
        logger.info(f"Extracted video ID: {video_id} from URL: {video_url}")
        
        # Get video-specific memory
        video_memory = get_memory_for_video(video_id)
        
        # Get transcript
        try:
            text = get_transcript(video_id)
            if not text or text.startswith("Error:"):
                return "I'm unable to access the content from this video. This might be due to the video being private, unavailable, or not having captions enabled."
        except Exception as e:
            return "I'm having trouble accessing this video's content. Please make sure the video is public and has captions available."
        
        # Get Pinecone manager and ensure index exists
        try:
            pinecone_manager = get_pinecone_manager()
            index = pinecone_manager.create_index_if_not_exists()
        except Exception as e:
            logger.error(f"Pinecone initialization error: {e}")
            return "I'm having trouble initializing the vector database. Please try again or contact support if the issue persists."
        
        # Create namespace for this video
        namespace = get_namespace_for_video(video_id)
        
        # Initialize embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Check if vector store already exists for this video
        try:
            # Check if documents exist in the namespace
            index_stats = index.describe_index_stats()
            existing_namespaces = index_stats.get('namespaces', {})
            
            if namespace in existing_namespaces:
                logger.info(f"Loading existing vector store for video: {video_id}")
                vectorstore = Pinecone.from_existing_index(
                    index_name=pinecone_manager.index_name,
                    embedding=embeddings,
                    namespace=namespace
                )
            else:
                logger.info(f"Creating new vector store for video: {video_id}")
                # Split text into chunks optimized for semantic search
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=800,  # Optimized for better semantic matching
                    chunk_overlap=150,  # Balanced overlap for context preservation
                    length_function=len,
                    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
                )
                docs = splitter.create_documents([text])
                
                # Log the number of chunks created
                logger.info(f"Created {len(docs)} text chunks for video: {video_id}")
                
                # Validate that we have documents to store
                if not docs:
                    logger.error(f"No documents created for video: {video_id}")
                    return "I'm having trouble processing this video. No content was extracted."
                
                # Log first few chunks for debugging
                for i, doc in enumerate(docs[:3]):
                    logger.info(f"Chunk {i+1}: {doc.page_content[:100]}...")
                
                # Create and store vectors in Pinecone
                try:
                    vectorstore = Pinecone.from_documents(
                        documents=docs,
                        embedding=embeddings,
                        index_name=pinecone_manager.index_name,
                        namespace=namespace
                    )
                    logger.info(f"Vector store created and stored in Pinecone for video: {video_id}")
                    
                    # Verify that vectors were actually stored
                    time.sleep(2)  # Give Pinecone time to index
                    updated_stats = index.describe_index_stats()
                    updated_namespaces = updated_stats.get('namespaces', {})
                    if namespace in updated_namespaces:
                        stored_vectors = updated_namespaces[namespace].get('vector_count', 0)
                        logger.info(f"Verified {stored_vectors} vectors stored for video: {video_id}")
                    else:
                        logger.warning(f"No vectors found in namespace after creation for video: {video_id}")
                        
                except Exception as e:
                    logger.error(f"Error creating vector store: {e}")
                    # Continue with fallback approach
                    vectorstore = None
                
        except Exception as e:
            logger.error(f"Error with vector store operations: {e}")
            return "I'm having trouble processing this video. Please try again or contact support if the issue persists."
        
        # Create retriever
        try:
            if vectorstore:
                retriever = vectorstore.as_retriever(
                    search_kwargs={
                        "k": 12,  # Increased to get more relevant documents
                        "namespace": namespace,
                        "score_threshold": 0.2  # Lowered to get more results while maintaining relevance
                    }
                )
            else:
                logger.warning("Vector store creation failed, will use transcript directly")
                retriever = None
        except Exception as e:
            logger.error(f"Error creating retriever: {e}")
            retriever = None
        
        # Create QA chain using a simpler approach with improved memory
        try:
            # Get relevant documents using invoke instead of get_relevant_documents
            if retriever:
                docs = retriever.invoke(question)
                logger.info(f"Retrieved {len(docs)} relevant documents")
                
                # Create context from documents
                context = "\n".join([doc.page_content for doc in docs])
                
                # If no relevant documents found, try multiple fallback strategies
                if not context.strip():
                    logger.warning("No relevant documents found, trying fallback strategies")
                    
                    # Strategy 1: Try with a more general query
                    try:
                        general_docs = retriever.invoke("video content overview")
                        if general_docs:
                            context = "\n".join([doc.page_content for doc in general_docs[:3]])
                            logger.info(f"Retrieved {len(general_docs)} general documents as fallback")
                        else:
                            # Strategy 2: Try to get any documents from namespace
                            try:
                                # Get all documents from the namespace (if possible)
                                all_docs = retriever.invoke("")
                                if all_docs:
                                    context = "\n".join([doc.page_content for doc in all_docs[:5]])
                                    logger.info(f"Retrieved {len(all_docs)} documents as final fallback")
                                else:
                                    # Strategy 3: Use limited transcript sections
                                    logger.info("Using limited transcript sections as final fallback")
                                    transcript_text = get_transcript(video_id)
                                    if transcript_text and not transcript_text.startswith("Error:"):
                                        # Use first 1500 characters of transcript (reduced from 2000)
                                        context = transcript_text[:1500] + "..."
                                        logger.info("Using limited transcript sections (1500 chars)")
                                    else:
                                        context = "No specific content found for this question."
                            except Exception as e:
                                logger.error(f"Error getting all documents: {e}")
                                # Final fallback: use limited transcript
                                transcript_text = get_transcript(video_id)
                                if transcript_text and not transcript_text.startswith("Error:"):
                                    context = transcript_text[:1500] + "..."
                                    logger.info("Using limited transcript as final fallback (1500 chars)")
                                else:
                                    context = "No specific content found for this question."
                    except Exception as e:
                        logger.error(f"Error getting fallback documents: {e}")
                        # Final fallback: use limited transcript
                        transcript_text = get_transcript(video_id)
                        if transcript_text and not transcript_text.startswith("Error:"):
                            context = transcript_text[:1500] + "..."
                            logger.info("Using limited transcript as final fallback (1500 chars)")
                        else:
                            context = "No specific content found for this question."
            else:
                # No retriever available, use limited transcript directly
                logger.info("No retriever available, using limited transcript directly")
                transcript_text = get_transcript(video_id)
                if transcript_text and not transcript_text.startswith("Error:"):
                    context = transcript_text[:1500] + "..."
                    logger.info("Using limited transcript (1500 chars)")
                else:
                    context = "No specific content found for this question."
            
            # Get conversation history from video-specific memory
            chat_history = video_memory.chat_memory.messages
            
            # Create the LLM
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.1
            )
            
            # Create the prompt with improved conversation history handling
            history_text = ""
            if chat_history:
                history_text = "\n\nPrevious conversation context:\n"
                # Include more context (last 6 messages instead of 4)
                for i, message in enumerate(chat_history[-6:]):
                    role = "User" if message.type == "human" else "Assistant"
                    history_text += f"{role}: {message.content}\n"
                
                history_text += "\nBased on the conversation above and the video content below, please answer the current question."
            
            # Log context usage for monitoring
            log_context_usage(context, question, video_id)
            
            # Improved prompt that focuses on relevant content
            prompt = f"""You are an expert video analyst. Based on the following relevant content from a YouTube video, provide a comprehensive and detailed answer to the user's question. 

Relevant content from the video:
{context}

{history_text}

User's question: {question}

Instructions:
- Provide a thorough, well-structured response that directly addresses the question
- Include relevant details and insights from the provided video content
- Write in a natural, conversational tone as if you're explaining the video to someone
- Don't mention that you're working with transcripts or video content - just provide the information naturally
- If the content doesn't contain enough information to answer the question fully, acknowledge this but provide what you can from the available content
- Make your response informative and engaging
- Consider the conversation history to provide contextually relevant answers
- If the user asks follow-up questions, reference previous parts of the conversation when relevant
- Focus on the most relevant information from the provided content
- If you need more specific information, suggest asking a more targeted question
- Always try to provide a helpful response based on the available content

Answer:"""
            
            # Get the response
            response = llm.invoke(prompt)
            
            # Extract the answer
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
            
            # Save to video-specific memory
            video_memory.save_context(
                {"question": question},
                {"answer": answer}
            )
            
            # Also save to global memory for backward compatibility
            conversation_memory.save_context(
                {"question": question},
                {"answer": answer}
            )
            
            return answer
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm having trouble generating a response for this question. Please try rephrasing your question or try again later."
            
    except Exception as e:
        logger.error(f"Unexpected error in ask_video_question: {e}")
        return "I encountered an unexpected issue while processing your request. Please try again or contact support if the problem persists."

def clear_conversation_memory():
    """Clear the conversation memory"""
    global conversation_memory, video_memories
    conversation_memory.clear()
    video_memories.clear()
    logger.info("All conversation memories cleared")

def clear_video_memory(video_id: str = None):
    """Clear memory for a specific video or all videos"""
    global video_memories
    if video_id:
        if video_id in video_memories:
            video_memories[video_id].clear()
            logger.info(f"Memory cleared for video: {video_id}")
    else:
        video_memories.clear()
        logger.info("All video memories cleared")

def get_conversation_history():
    """Get the current conversation history from global memory"""
    return conversation_memory.chat_memory.messages

def get_video_conversation_history(video_id: str):
    """Get conversation history for a specific video"""
    video_memory = get_memory_for_video(video_id)
    return video_memory.chat_memory.messages

def get_all_video_memories():
    """Get all video memories for debugging"""
    return {video_id: len(memory.chat_memory.messages) for video_id, memory in video_memories.items()}

def estimate_tokens(text: str) -> int:
    """Estimate token count for monitoring costs"""
    # Rough estimation: 1 token ≈ 4 characters for English text
    return len(text) // 4

def log_context_usage(context: str, question: str, video_id: str):
    """Log context usage for monitoring and optimization"""
    context_tokens = estimate_tokens(context)
    question_tokens = estimate_tokens(question)
    total_tokens = context_tokens + question_tokens
    
    logger.info(f"Context usage for video {video_id}: {context_tokens} tokens (context) + {question_tokens} tokens (question) = {total_tokens} total tokens")
    
    # Log context length for optimization
    if context_tokens > 4000:
        logger.warning(f"Large context detected for video {video_id}: {context_tokens} tokens")
    elif context_tokens < 100:
        logger.info(f"Small context for video {video_id}: {context_tokens} tokens")
