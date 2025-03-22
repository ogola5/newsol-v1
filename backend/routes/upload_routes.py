from flask import Blueprint, request, jsonify
import fitz  # PyMuPDF
from models.embedding import generate_embedding
from models.rag import store_in_pinecone

upload_bp = Blueprint("upload_bp", __name__)

def extract_text_from_pdf(file):
    """Extract text from all pages of a PDF file."""
    doc = fitz.open(stream=file.read(), filetype="pdf")  # Read from file stream
    full_text = []

    for page in doc:
        text = page.get_text("text")
        if text.strip():
            full_text.append(text)

    return "\n".join(full_text)

@upload_bp.route("/", methods=["POST"])
def upload_pdf():
    """Handle PDF upload, extract, chunk, embed, and store in Pinecone."""
    print("Received files:", request.files)  # Debugging log

    if "file" not in request.files:
        print("No file key found in request.files")  # Debugging log
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        print("No file selected")  # Debugging log
        return jsonify({"error": "No file selected"}), 400

    print(f"Processing file: {file.filename}")  # Debugging log

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(file)

    # Chunk the text into smaller pieces
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_text(pdf_text)

    # Generate embeddings and store them in Pinecone
    store_in_pinecone(chunks)

    return jsonify({"message": f"Uploaded {len(chunks)} chunks!"}), 200
