from flask import Blueprint, request, jsonify
from models.embedding import generate_embedding
from models.gemini import generate_response
from pinecone import Pinecone

from config import PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("education-ai")

query_bp = Blueprint("query_bp", __name__)

@query_bp.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data["text"]

    # Generate embedding for the query
    query_embedding = generate_embedding(query_text)

    # Search in Pinecone
    results = index.query(vector=query_embedding, top_k=3, include_metadata=True)

    if not results["matches"]:
        return jsonify({"response": "No relevant information found."})

    # Extract the most relevant document
    relevant_texts = [match["metadata"]["text"] for match in results["matches"]]

    # Generate AI response (Modify this according to your LLM model)
    ai_response = generate_response(relevant_texts)

    return jsonify({"response": ai_response, "source_documents": relevant_texts})


upload_bp = Blueprint("upload_bp", __name__)

@upload_bp.route("/upload", methods=["POST"])
def upload():
    data = request.json
    document_text = data.get("text")  # Get the document text
    document_id = data.get("id")  # Unique identifier for the document

    if not document_text or not document_id:
        return jsonify({"error": "Document text and ID are required"}), 400

    # Generate embeddings for the document
    document_embedding = generate_embedding(document_text)

    # Store in Pinecone
    index.upsert([(document_id, document_embedding, {"text": document_text})])

    return jsonify({"message": "Document uploaded successfully"})