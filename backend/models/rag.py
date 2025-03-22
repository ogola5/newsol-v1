from models.embedding import generate_embedding
from pinecone import Pinecone
from config import PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name
index_name = "education-ai"

# Check if the index exists, and create it if it doesn't
if index_name not in pc.list_indexes().names():
    pc.create_index(name=index_name, dimension=384)  # Adjust dimension as needed

# Connect to the index
index = pc.Index(index_name)

def store_in_pinecone(chunks):
    """Stores chunks in Pinecone with embeddings."""
    vectors = [(str(i), generate_embedding(chunk), {"text": chunk}) for i, chunk in enumerate(chunks)]
    index.upsert(vectors)

def search_pinecone(query):
    """Search for relevant content in Pinecone."""
    query_embedding = generate_embedding(query)
    results = index.query(vector=query_embedding, top_k=3, include_metadata=True)

    return [match["metadata"]["text"] for match in results["matches"]]