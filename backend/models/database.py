from pymongo import MongoClient
from config import MONGO_URI

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["education_ai"]

# Collections
students = db["students"]
teachers = db["teachers"]
parents = db["parents"]
admins = db["admins"]
pdf_uploads = db["pdf_uploads"]
history = db["history"]
feedback = db["feedback"]  # ✅ New Collection for AI Refinement

# 📝 Register Users
def register_user(user_type, user_data):
    """
    Registers a new user (student, teacher, parent, or admin).
    :param user_type: "student", "teacher", "parent", or "admin"
    :param user_data: Dictionary containing user details
    """
    collections = {
        "student": students,
        "teacher": teachers,
        "parent": parents,
        "admin": admins
    }
    if user_type in collections:
        collections[user_type].insert_one(user_data)
    else:
        raise ValueError("Invalid user type")

# 📂 Store PDF Metadata (Admins Upload)
def save_pdf_metadata(admin_id, filename, grade, subject, chunk_count):
    """
    Stores metadata about an uploaded PDF, linking it to an admin.
    :param admin_id: The ID of the admin uploading the PDF
    :param filename: Name of the uploaded file
    :param grade: Grade level associated with the document
    :param subject: Subject of the document
    :param chunk_count: Number of text chunks stored in Pinecone
    """
    pdf_uploads.insert_one({
        "admin_id": admin_id,
        "filename": filename,
        "grade": grade,
        "subject": subject,
        "chunk_count": chunk_count,
        "status": "active"  # Can later be updated to "archived" or "updated"
    })

# 📌 Store Teacher Feedback on AI Content
def store_teacher_feedback(teacher_id, query, ai_response, correct_response, rating):
    """
    Stores feedback from teachers about AI-generated content.
    :param teacher_id: ID of the teacher providing feedback
    :param query: The original question asked
    :param ai_response: The AI's generated response
    :param correct_response: The teacher's suggested correct response
    :param rating: A score (1-5) indicating AI accuracy
    """
    feedback.insert_one({
        "teacher_id": teacher_id,
        "query": query,
        "ai_response": ai_response,
        "correct_response": correct_response,
        "rating": rating
    })

# 🏡 Store Parental Insights on Student Learning
def store_parent_feedback(parent_id, student_id, observation, recommendation):
    """
    Stores insights from parents about their child's learning needs.
    :param parent_id: The ID of the parent giving feedback
    :param student_id: The child's ID
    :param observation: Notes on child behavior or struggles
    :param recommendation: Parent’s suggestion for improving learning
    """
    feedback.insert_one({
        "parent_id": parent_id,
        "student_id": student_id,
        "observation": observation,
        "recommendation": recommendation
    })

# 🔍 Log Student Queries & AI Responses
def save_user_query(user_id, query, response, pinecone_matches):
    """
    Logs a user's query, AI response, and Pinecone search results.
    :param user_id: The user making the query
    :param query: The user's search text
    :param response: AI-generated response
    :param pinecone_matches: Relevant text chunks retrieved from Pinecone
    """
    history.insert_one({
        "user_id": user_id,
        "query": query,
        "response": response,
        "pinecone_matches": pinecone_matches
    })
