# from models.embedding import generate_embedding
# from pinecone import Pinecone
# from config import PINECONE_API_KEY

# # Initialize Pinecone
# pc = Pinecone(api_key=PINECONE_API_KEY)

# # Define the index name and embedding dimensions
# index_name = "education-ai"
# dimension = 384  # Ensure this matches your embedding model output

# # Check if the index exists
# existing_indexes = [index["name"] for index in pc.list_indexes()]
# if index_name not in existing_indexes:
#     pc.create_index(name=index_name, dimension=dimension, metric="cosine")  # Use cosine similarity

# # Wait for the index to be ready
# index = pc.Index(index_name)

# def store_in_pinecone(chunks, grade, subject):
#     """Stores chunks in Pinecone with embeddings, attaching metadata for grade and subject."""
#     vectors = [
#         (
#             str(i), 
#             generate_embedding(chunk), 
#             {"text": chunk, "grade": grade, "subject": subject}  # Store metadata
#         )
#         for i, chunk in enumerate(chunks)
#     ]
#     index.upsert(vectors)

# def search_pinecone(query, grade=None, subject=None, top_k=3):
#     """Search for relevant content in Pinecone with optional filters."""
#     query_embedding = generate_embedding(query)

#     # Build metadata filter
#     metadata_filter = {}
#     if grade:
#         metadata_filter["grade"] = grade
#     if subject:
#         metadata_filter["subject"] = subject

#     try:
#         results = index.query(
#             vector=query_embedding,
#             top_k=top_k,
#             include_metadata=True,
#             filter=metadata_filter if metadata_filter else None  # Apply filter only if needed
#         )
#     except Exception as e:
#         return {"error": f"Pinecone query failed: {str(e)}"}

#     if "matches" not in results:
#         return []

#     return [match["metadata"]["text"] for match in results["matches"] if "metadata" in match]
from models.embedding import generate_embedding
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name and embedding dimensions
index_name = PINECONE_INDEX_NAME
dimension = 384  # Ensure this matches your embedding model output

# Check if the index exists
existing_indexes = [index["name"] for index in pc.list_indexes()]
if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Adjust if needed
    )

# Wait for the index to be ready
index = pc.Index(index_name)

def store_in_pinecone(chunks, grade, subject, filename):
    """Stores chunks in Pinecone with embeddings, attaching metadata for grade, subject, and filename."""
    vectors = [
        (
            f"{filename}_{i}",  # Unique ID based on filename and index
            generate_embedding(chunk),
            {"text": chunk, "grade": grade, "subject": subject, "filename": filename}  # Store metadata
        )
        for i, chunk in enumerate(chunks)
    ]
    
    try:
        index.upsert(vectors)
        return {"message": f"✅ Successfully stored {len(chunks)} chunks for {filename} in Pinecone."}
    except Exception as e:
        return {"error": f"Failed to store data in Pinecone: {str(e)}"}

def search_pinecone(query, grade=None, subject=None, top_k=3):
    """Search for relevant content in Pinecone with optional filters."""
    query_embedding = generate_embedding(query)

    # Build metadata filter
    metadata_filter = {}
    if grade:
        metadata_filter["grade"] = grade
    if subject:
        metadata_filter["subject"] = subject

    try:
        results = index.query(
            vector=query_embedding, 
            top_k=top_k, 
            include_metadata=True,
            filter=metadata_filter if metadata_filter else None  # Apply filter only if needed
        )
        if "matches" not in results:
            return []
        return [match["metadata"]["text"] for match in results["matches"] if "metadata" in match]
    except Exception as e:
        return {"error": f"Pinecone query failed: {str(e)}"}

def delete_from_pinecone(filename):
    """Deletes all vector data related to a specific file from Pinecone."""
    try:
        query_filter = {"filename": filename}  # Match all records with this filename
        index.delete(filter=query_filter)
        return {"message": f"✅ Successfully deleted all content related to {filename} from Pinecone."}
    except Exception as e:
        return {"error": f"Failed to delete from Pinecone: {str(e)}"}
