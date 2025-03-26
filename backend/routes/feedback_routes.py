from flask import Blueprint, request, jsonify
from models.database import store_feedback

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """Store feedback from users"""
    data = request.json
    userType, rating, comment = data["userType"], data["rating"], data["comment"]

    store_feedback(userType, rating, comment)
    return jsonify({"message": "Feedback submitted successfully"}), 201
