from flask import Flask
from routes.upload_routes import upload_bp
from routes.query_routes import query_bp
from flask_cors import CORS
from users.routes import users_bp

app = Flask(__name__)
CORS(app)
# Register Routes
app.register_blueprint(upload_bp, url_prefix="/upload")
app.register_blueprint(query_bp, url_prefix="/query")
app.register_blueprint(users_bp, url_prefix="/users")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
