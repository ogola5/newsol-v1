from flask import Blueprint, request, jsonify
import fitz  # PyMuPDF
from models.embedding import generate_embedding
from models.rag import store_in_pinecone, delete_from_pinecone
from models.database import save_pdf_metadata, store_teacher_feedback, store_parent_feedback, save_user_query, pdf_uploads


upload_bp = Blueprint("upload_bp", __name__)

# 📝 Extract text from PDF
def extract_text_from_pdf(file):
    """Extract text from all pages of a PDF file."""
    doc = fitz.open(stream=file.read(), filetype="pdf")  # Read from file stream
    full_text = [page.get_text("text") for page in doc if page.get_text("text").strip()]
    return "\n".join(full_text)

# 📂 Upload a new PDF (Admins only)
@upload_bp.route("/upload", methods=["POST"])
def upload_pdf():
    """Handle PDF upload, extract, chunk, embed, and store in Pinecone."""
    if "file" not in request.files or "admin_id" not in request.form:
        return jsonify({"error": "Missing file or admin_id"}), 400

    file = request.files["file"]
    admin_id = request.form["admin_id"]
    grade = request.form.get("grade", "unknown")
    subject = request.form.get("subject", "general")

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    pdf_text = extract_text_from_pdf(file)

    # Chunk the text
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_text(pdf_text)

    # Store in Pinecone
    store_in_pinecone(chunks)

    # Store metadata in MongoDB
    save_pdf_metadata(admin_id, file.filename, grade, subject, len(chunks))

    return jsonify({"message": f"Uploaded {len(chunks)} chunks!"}), 200

# 🗑️ Delete a PDF (Admins only)
@upload_bp.route("/delete/<filename>", methods=["DELETE"])
def delete_pdf(filename):
    """Deletes a PDF's metadata & removes associated chunks from Pinecone."""
    deleted_file = pdf_uploads.find_one_and_delete({"filename": filename})
    
    if deleted_file:
        delete_from_pinecone(filename)
        return jsonify({"message": f"Deleted {filename} from system."}), 200
    
    return jsonify({"error": "File not found"}), 404

# ✏️ Update PDF metadata (Admins only)
@upload_bp.route("/update/<filename>", methods=["PUT"])
def update_pdf(filename):
    """Updates metadata for an existing PDF."""
    update_data = request.json
    updated_file = pdf_uploads.find_one_and_update(
        {"filename": filename},
        {"$set": update_data},
        return_document=True
    )

    if updated_file:
        return jsonify({"message": f"Updated {filename}", "new_data": update_data}), 200
    
    return jsonify({"error": "File not found"}), 404

# 📌 Submit teacher feedback on AI response
@upload_bp.route("/feedback/teacher", methods=["POST"])
def teacher_feedback():
    """Allows teachers to provide feedback on AI-generated responses."""
    data = request.json
    required_keys = ["teacher_id", "query", "ai_response", "correct_response", "rating"]

    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing required fields"}), 400

    store_teacher_feedback(
        data["teacher_id"], data["query"], data["ai_response"],
        data["correct_response"], data["rating"]
    )

    return jsonify({"message": "Feedback recorded successfully!"}), 200

# 🏡 Submit parental feedback on student learning
@upload_bp.route("/feedback/parent", methods=["POST"])
def parent_feedback():
    """Allows parents to submit insights on their child's learning."""
    data = request.json
    required_keys = ["parent_id", "student_id", "observation", "recommendation"]

    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing required fields"}), 400

    store_parent_feedback(
        data["parent_id"], data["student_id"], data["observation"], data["recommendation"]
    )

    return jsonify({"message": "Parental feedback recorded!"}), 200

# 🔍 Log student queries & AI responses
@upload_bp.route("/query", methods=["POST"])
def log_query():
    """Logs student queries & AI responses."""
    data = request.json
    required_keys = ["user_id", "query", "response", "pinecone_matches"]

    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing required fields"}), 400

    save_user_query(data["user_id"], data["query"], data["response"], data["pinecone_matches"])

    return jsonify({"message": "Query logged successfully!"}), 200
