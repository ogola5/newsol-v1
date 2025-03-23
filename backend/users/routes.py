from flask import Blueprint, request, jsonify
from models.database import students, teachers, admins
from users.utils import hash_password, verify_password

users_bp = Blueprint("users", __name__)

@users_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user_type = data.get("user_type")

    if user_type not in ["student", "teacher", "admin"]:
        return jsonify({"error": "Invalid user type"}), 400

    full_name = data.get("fullName")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

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

    elif user_type == "admin":
        user_data.update({
            "role": data.get("role", "admin"),
        })
        admins.insert_one(user_data)

    return jsonify({"message": f"{user_type.capitalize()} registered successfully!"}), 201


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user_type = data.get("user_type")

    if not email or not password or user_type not in ["student", "teacher", "admin"]:
        return jsonify({"error": "Invalid credentials"}), 400

    collection = {"student": students, "teacher": teachers, "admin": admins}.get(user_type)

    user = collection.find_one({"email": email})
    if not user or not verify_password(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": f"Welcome, {user_type.capitalize()}!",
        "user": {"fullName": user["fullName"], "email": user["email"]}
    }), 200
