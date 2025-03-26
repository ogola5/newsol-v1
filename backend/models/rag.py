# from models.embedding import generate_embedding
# from pinecone import Pinecone, ServerlessSpec
# from config import PINECONE_API_KEY, PINECONE_INDEX_NAME

# # Initialize Pinecone
# pc = Pinecone(api_key=PINECONE_API_KEY)

# # Define the index name and embedding dimensions
# index_name = PINECONE_INDEX_NAME
# dimension = 384  # Ensure this matches your embedding model output

# # Check if the index exists
# existing_indexes = [index["name"] for index in pc.list_indexes()]
# if index_name not in existing_indexes:
#     pc.create_index(
#         name=index_name,
#         dimension=dimension,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Adjust if needed
#     )

# # Wait for the index to be ready
# index = pc.Index(index_name)

# def store_in_pinecone(chunks, grade, subject, filename):
#     """Stores chunks in Pinecone with embeddings, attaching metadata for grade, subject, and filename."""
#     vectors = [
#         (
#             f"{filename}_{i}",  # Unique ID based on filename and index
#             generate_embedding(chunk),
#             {"text": chunk, "grade": grade, "subject": subject, "filename": filename}  # Store metadata
#         )
#         for i, chunk in enumerate(chunks)
#     ]
    
#     try:
#         index.upsert(vectors)
#         return {"message": f"✅ Successfully stored {len(chunks)} chunks for {filename} in Pinecone."}
#     except Exception as e:
#         return {"error": f"Failed to store data in Pinecone: {str(e)}"}

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
#         if "matches" not in results:
#             return []
#         return [match["metadata"]["text"] for match in results["matches"] if "metadata" in match]
#     except Exception as e:
#         return {"error": f"Pinecone query failed: {str(e)}"}

# def delete_from_pinecone(filename):
#     """Deletes all vector data related to a specific file from Pinecone."""
#     try:
#         query_filter = {"filename": filename}  # Match all records with this filename
#         index.delete(filter=query_filter)
#         return {"message": f"✅ Successfully deleted all content related to {filename} from Pinecone."}
#     except Exception as e:
#         return {"error": f"Failed to delete from Pinecone: {str(e)}"}

import logging
from models.embedding import generate_embedding
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    logging.info("✅ Successfully connected to Pinecone.")
except Exception as e:
    logging.error(f"❌ Pinecone initialization failed: {str(e)}")
    pc = None

# Define index parameters
index_name = PINECONE_INDEX_NAME
dimension = 384  # Ensure this matches the embedding model's output dimensions

# Ensure index exists
if pc:
    try:
        existing_indexes = [index["name"] for index in pc.list_indexes()]
        if index_name not in existing_indexes:
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            logging.info(f"✅ Created new Pinecone index: {index_name}")
        index = pc.Index(index_name)
    except Exception as e:
        logging.error(f"❌ Failed to create/access Pinecone index: {str(e)}")
        index = None
else:
    index = None  # Prevent errors if Pinecone initialization failed

def store_in_pinecone(chunks, grade, subject, filename):
    """Stores text chunks in Pinecone with metadata, handling potential failures."""
    if not index:
        return {"error": "Pinecone index is unavailable."}

    if not chunks or not isinstance(chunks, list):
        return {"error": "Invalid chunks data. Must be a non-empty list."}

    try:
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)
            if not embedding:
                logging.warning(f"⚠️ Skipping chunk {i} - failed embedding.")
                continue  # Skip if embedding fails

            vectors.append((
                f"{filename}_{i}",  # Unique identifier
                embedding,
                {"text": chunk, "grade": grade, "subject": subject, "filename": filename}
            ))

        if vectors:
            index.upsert(vectors)
            return {"message": f"✅ Stored {len(vectors)} chunks for {filename} in Pinecone."}
        else:
            return {"error": "Failed to generate embeddings for all chunks."}
    except Exception as e:
        logging.error(f"❌ Error storing data in Pinecone: {str(e)}")
        return {"error": f"Pinecone storage failed: {str(e)}"}

def search_pinecone(query, grade=None, subject=None, top_k=3):
    """Searches Pinecone for relevant content, handling errors and falling back to AI."""
    from models.gemini import generate_response  # ✅ Import here to prevent circular import

    if not index:
        return {"error": "Pinecone index is unavailable."}

    if not query or not isinstance(query, str):
        return {"error": "Invalid query. Must be a non-empty string."}

    try:
        query_embedding = generate_embedding(query)
        if not query_embedding:
            return {"error": "Failed to generate embedding for query."}

        # Build metadata filter
        metadata_filter = {}
        if grade:
            metadata_filter["grade"] = grade
        if subject:
            metadata_filter["subject"] = subject

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=metadata_filter if metadata_filter else None
        )

        retrieved_texts = [
            match["metadata"]["text"]
            for match in results.get("matches", [])
            if "metadata" in match and "text" in match["metadata"]
        ]

        if retrieved_texts:
            return retrieved_texts  # ✅ Return relevant content
        else:
            logging.info("ℹ️ No relevant results found in Pinecone. Falling back to AI response.")
            return [generate_response(query)]  # 🔄 AI fallback if nothing is retrieved

    except Exception as e:
        logging.error(f"❌ Pinecone query failed: {str(e)}")
        return {"error": f"Pinecone search failed: {str(e)}"}

def delete_from_pinecone(filename):
    """Deletes all vector data related to a specific file, handling potential failures."""
    if not index:
        return {"error": "Pinecone index is unavailable."}

    if not filename or not isinstance(filename, str):
        return {"error": "Invalid filename. Must be a non-empty string."}

    try:
        query_filter = {"filename": filename}
        index.delete(filter=query_filter)
        return {"message": f"✅ Successfully deleted all content related to {filename} from Pinecone."}
    except Exception as e:
        logging.error(f"❌ Failed to delete from Pinecone: {str(e)}")
        return {"error": f"Deletion failed: {str(e)}"}
