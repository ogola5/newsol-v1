from flask import Blueprint, request, jsonify
from models.embedding import generate_embedding
from models.gemini import generate_response
from pinecone import Pinecone
from config import PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("education-ai")

query_bp = Blueprint("query_bp", __name__)

def query_pinecone(query_text):
    """Query Pinecone for relevant results."""
    # Generate an embedding for the query
    query_embedding = generate_embedding(query_text)

    # Search for the most relevant results in Pinecone
    response = index.query(vector=query_embedding, top_k=5, include_metadata=True)

    # Extract relevant text from the response
    results = [match["metadata"]["text"] for match in response["matches"]]

    return results

@query_bp.route("/", methods=["POST"])
def query_pdf():
    """Handle queries and retrieve relevant chunks from Pinecone."""
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400

    query_text = data["query"]
    results = query_pinecone(query_text)  # Fetch relevant chunks from Pinecone

    return jsonify({"results": results}), 200
