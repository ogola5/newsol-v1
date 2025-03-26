from flask import Blueprint, request, jsonify
from models.database import students, teachers, parents
from users.utils import hash_password, verify_password, generate_token
from users.sessions import add_session
users_bp = Blueprint("users", __name__)
from flask_cors import CORS  # Import CORS

CORS(users_bp)  # Apply CORS to this blueprint
@users_bp.route("/register", methods=["OPTIONS", "POST"])
def register():
    """Register users: students, teachers, parents."""
    if request.method == "OPTIONS":
        return '', 200  # Handle preflight request

    data = request.get_json()
    print("📩 Received Data:", data)  # Debugging line to log incoming request

    if not data:
        return jsonify({"error": "No data received"}), 400

    user_type = data.get("user_type")

    if user_type not in ["student", "teacher", "parent"]:
        return jsonify({"error": "Invalid user type"}), 400

    full_name = data.get("fullName")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Hash password and insert into DB
    hashed_password = hash_password(password)
    user_data = {
        "fullName": full_name,
        "email": email,
        "password": hashed_password,
    }

    if user_type == "student":
        user_data.update({
            "dateOfBirth": data.get("dateOfBirth"),
            "parentEmail": data.get("parentEmail"),
            "gradeLevel": data.get("gradeLevel"),
        })
        students.insert_one(user_data)

    elif user_type == "teacher":
        user_data.update({
            "qualifications": data.get("qualifications"),
            "subjects": data.get("subjects"),
        })
        teachers.insert_one(user_data)

    elif user_type == "parent":
        parents.insert_one(user_data)

    return jsonify({"message": f"{user_type.capitalize()} registered successfully!"}), 201

@users_bp.route("/login", methods=["POST"])
def login():
    """Login users and return a JWT token."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user_type = data.get("user_type")

    if not email or not password or user_type not in ["student", "teacher", "parent"]:
        return jsonify({"error": "Invalid credentials"}), 400

    collection = {"student": students, "teacher": teachers, "parent": parents}.get(user_type)
    user = collection.find_one({"email": email})

    if not user or not verify_password(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate token and track session
    token = generate_token(user["email"], user_type)
    add_session(user["email"], token)

    return jsonify({
        "message": f"Welcome, {user_type.capitalize()}!",
        "token": token,
        "user": {"fullName": user["fullName"], "email": user["email"]}
    }), 200