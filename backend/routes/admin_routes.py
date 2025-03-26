# import jwt
# import datetime
# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# from werkzeug.security import generate_password_hash, check_password_hash
# from config import MONGO_URI

# # Create Blueprint for admin routes
# admin_bp = Blueprint("admin", __name__)

# # Connect to MongoDB
# client = MongoClient(MONGO_URI)
# db = client["education_ai"]
# admins = db["admins"]

# @admin_bp.route("/register", methods=["POST"])
# def register_admin():
#     """Registers a new admin"""
#     try:
#         data = request.get_json()
#         full_name = data.get("fullName")
#         email = data.get("email")
#         password = data.get("password")

#         if not full_name or not email or not password:
#             return jsonify({"error": "Missing required fields"}), 400

#         # Hash the password before saving
#         hashed_password = generate_password_hash(password)

#         # Check if admin already exists
#         if admins.find_one({"email": email}):
#             return jsonify({"error": "Admin already exists"}), 409

#         # Save admin to the database
#         admin_id = admins.insert_one({
#             "fullName": full_name,
#             "email": email,
#             "password": hashed_password
#         }).inserted_id

#         return jsonify({"message": "Admin registered successfully", "admin_id": str(admin_id)}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @admin_bp.route("/login", methods=["POST"])
# def login_admin():
#     try:
#         data = request.get_json()
#         email = data.get("email")
#         password = data.get("password")

#         if not email or not password:
#             return jsonify({"error": "Missing email or password"}), 400

#         admin = admins.find_one({"email": email})
#         if not admin or not check_password_hash(admin["password"], password):
#             return jsonify({"error": "Invalid email or password"}), 401

#         # Generate a JWT token
#         token = jwt.encode(
#             {
#                 "admin_id": str(admin["_id"]),
#                 "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token expires in 2 hours
#             },
#             SECRET_KEY,
#             algorithm="HS256",
#         )

#         return jsonify({"message": "Login successful", "token": token}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

import jwt
import datetime
import os
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from config import MONGO_URI

# Load SECRET_KEY securely
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY is not set. Please check your environment variables!")

# Create Blueprint for admin routes
admin_bp = Blueprint("admin", __name__)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["education_ai"]
admins = db["admins"]

@admin_bp.route("/register", methods=["POST"])
def register_admin():
    """Registers a new admin"""
    try:
        data = request.get_json()
        full_name = data.get("fullName")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        # Hash the password before saving
        hashed_password = generate_password_hash(password)

        # Check if admin already exists
        if admins.find_one({"email": email}):
            return jsonify({"error": "Admin already exists"}), 409

        # Save admin to the database
        admin_id = admins.insert_one({
            "fullName": full_name,
            "email": email,
            "password": hashed_password
        }).inserted_id

        return jsonify({"message": "Admin registered successfully", "admin_id": str(admin_id)}), 201

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@admin_bp.route("/login", methods=["POST"])
def login_admin():
    """Logs in an admin and returns a JWT token"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        admin = admins.find_one({"email": email})
        if not admin or not check_password_hash(admin["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate a JWT token
        token = jwt.encode(
            {
                "admin_id": str(admin["_id"]),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token expires in 2 hours
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        return jsonify({"message": "Login successful", "token": token}), 200

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
