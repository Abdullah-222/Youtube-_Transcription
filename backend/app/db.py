from chromadb import EmbeddingFunction
from langchain.vectorstores import Chroma

# Load your Chroma vector DB
db = Chroma(persist_directory="db", embedding_function=EmbeddingFunction)

# View all stored documents
docs = db.get()

print(docs["documents"])     # List of text chunks
print(docs["ids"])           # List of IDs
print(docs["metadatas"])     # List of metadata dicts
print(docs["embeddings"])    # (Optional) List of vectors
