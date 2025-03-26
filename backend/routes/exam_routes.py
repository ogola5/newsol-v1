from flask import Blueprint, request, jsonify
from models.gemini import generate_exam
from models.database import store_exam

exam_bp = Blueprint("exam", __name__)

@exam_bp.route("/generate-exam", methods=["POST"])
def generate_exam_route():
    """Generate an exam based on user input"""
    data = request.json
    subject, difficulty, num_questions = (
        data["subject"], data["difficulty"], data["numQuestions"]
    )

    try:
        questions = generate_exam(subject, difficulty, num_questions)
        store_exam(subject, difficulty, questions)
        return jsonify({"exam": questions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
