from app.chains.utils.transcript_loader import get_transcript, extract_video_id
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Global variable to store vector stores
vector_stores = {}

def get_vector_store_path(video_id: str) -> str:
    """Generate a unique path for storing vector embeddings for a video"""
    # Create a hash of the video_id for safe file naming
    video_hash = hashlib.md5(video_id.encode()).hexdigest()
    return f"./vector_stores/{video_hash}"

def ask_video_question(video_url: str, question: str) -> str:
    try:
        # Check if Google API key is set
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "I'm currently unable to process video analysis. Please contact the system administrator."
        
        # Extract video ID from URL
        video_id = extract_video_id(video_url)
        if not video_id:
            return "I couldn't recognize that as a valid YouTube URL. Please provide a complete YouTube video link."
        
        print(f"Extracted video ID: {video_id} from URL: {video_url}")
        
        # Get transcript
        try:
            text = get_transcript(video_id)
            #print(f"Transcript: {text}")
            if not text or text.startswith("Error:"):
                return "I'm unable to access the content from this video. This might be due to the video being private, unavailable, or not having captions enabled."
        except Exception as e:
            return "I'm having trouble accessing this video's content. Please make sure the video is public and has captions available."
        
        # Create vector store path
        vector_store_path = get_vector_store_path(video_id)
        
        # Check if vector store already exists for this video
        if os.path.exists(vector_store_path):
            print(f"Loading existing vector store for video: {video_id}")
            try:
                vectorstore = Chroma(
                    persist_directory=vector_store_path,
                    embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                )
            except Exception as e:
                print(f"Error loading existing vector store: {e}")
                # If loading fails, recreate it
                vectorstore = None
        else:
            vectorstore = None
        
        # If no existing vector store, create new one
        if vectorstore is None:
            print(f"Creating new vector store for video: {video_id}")
            # Split text into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
            docs = splitter.create_documents([text])
            
            # Create and persist vector store
            try:
                vectorstore = Chroma.from_documents(
                    documents=docs,
                    embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
                    persist_directory=vector_store_path
                )
                # Chroma automatically persists when persist_directory is specified
                print(f"Vector store created and persisted for video: {video_id}")
            except Exception as e:
                return "I'm having trouble processing this video. Please try again or contact support if the issue persists."
        
        # Create retriever
        try:
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        except Exception as e:
            return "I'm having trouble analyzing this video. Please try again or contact support if the issue persists."
        
        # Create QA chain using a simpler approach
        try:
            # Get relevant documents using invoke instead of get_relevant_documents
            docs = retriever.invoke(question)
            print(docs)
            # Create context from documents
            context = "\n".join([doc.page_content for doc in docs])
            print(context)
            
            # Create the LLM
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.1
            )
            
            # Create the prompt
            prompt = f"""You are an expert video analyst. Based on the following content from a YouTube video, provide a comprehensive and detailed answer to the user's question. 

Content from the video:
{context}

User's question: {question}

Instructions:
- Provide a thorough, well-structured response that directly addresses the question
- Include relevant details and insights from the video content
- Write in a natural, conversational tone as if you're explaining the video to someone
- Don't mention that you're working with transcripts or video content - just provide the information naturally
- If the content doesn't contain enough information to answer the question fully, acknowledge this but provide what you can from the available content
- Make your response informative and engaging

Answer:"""
            
            # Get the response
            response = llm.invoke(prompt)
            
            # Extract the answer
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            return "I'm having trouble generating a response for this question. Please try rephrasing your question or try again later."
            
    except Exception as e:
        return "I encountered an unexpected issue while processing your request. Please try again or contact support if the problem persists."
