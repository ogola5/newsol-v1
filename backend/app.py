# from flask import Flask
# from routes.upload_routes import upload_bp
# from routes.query_routes import query_bp
# from flask_cors import CORS
# from users.routes import users_bp

# app = Flask(__name__)
# CORS(app)
# # Register Routes
# app.register_blueprint(upload_bp, url_prefix="/upload")
# app.register_blueprint(query_bp, url_prefix="/query")
# app.register_blueprint(users_bp, url_prefix="/users")

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the SECRET_KEY from .env
SECRET_KEY = os.getenv("SECRET_KEY")

# Check if SECRET_KEY is loaded
if not SECRET_KEY:
    print("❌ SECRET_KEY is NOT loaded! Check your .env file.")
else:
    print("✅ SECRET_KEY is loaded successfully.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set Flask secret key
app.config["SECRET_KEY"] = SECRET_KEY

# Import existing routes
from routes.upload_routes import upload_bp
from routes.query_routes import query_bp
from users.routes import users_bp
from routes.exam_routes import exam_bp  # New Exam Routes
from routes.feedback_routes import feedback_bp  # New Feedback Routes
from routes.admin_routes import admin_bp  # New Admin Routes

# Register Routes
app.register_blueprint(upload_bp, url_prefix="/")
app.register_blueprint(query_bp, url_prefix="/query")
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(exam_bp, url_prefix="/exam")
app.register_blueprint(feedback_bp, url_prefix="/feedback")
app.register_blueprint(admin_bp, url_prefix="/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
