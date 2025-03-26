from flask import Blueprint, request, jsonify
from models.embedding import generate_embedding
from models.gemini import generate_response
from pinecone import Pinecone
from config import PINECONE_API_KEY
from users.utils import token_required  # Import authentication decorator

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "education-ai"

# Ensure index exists before querying
existing_indexes = [index["name"] for index in pc.list_indexes()]
if index_name not in existing_indexes:
    raise ValueError(f"Pinecone index '{index_name}' not found. Ensure it is created.")

index = pc.Index(index_name)

query_bp = Blueprint("query_bp", __name__)

def query_pinecone(query_text, grade=None, subject=None, top_k=5):
    """Query Pinecone for relevant results based on query, grade, and subject."""
    query_embedding = generate_embedding(query_text)

    # Build metadata filter
    metadata_filter = {}
    if grade:
        metadata_filter["grade"] = grade
    if subject:
        metadata_filter["subject"] = subject

    # Search Pinecone with filters
    try:
        response = index.query(
            vector=query_embedding, 
            top_k=top_k, 
            include_metadata=True,
            filter=metadata_filter if metadata_filter else None  # Apply filter only if needed
        )
    except Exception as e:
        return {"error": f"Pinecone query failed: {str(e)}"}

    # Extract relevant results
    results = [
        match["metadata"]["text"] for match in response.get("matches", []) if "metadata" in match
    ]

    return results

@query_bp.route("/", methods=["POST"])
@token_required
def query_pdf(user_data):
    """Handle queries and retrieve relevant chunks from Pinecone."""
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "query" not in data:
        return jsonify({"error": "Query field is required"}), 400

    query_text = data["query"]
    grade = data.get("grade")
    subject = data.get("subject")

    try:
        results = query_pinecone(query_text, grade, subject)
        return jsonify({
            "success": True,
            "results": results,
            "user": user_data["email"]  # Return minimal user info
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500