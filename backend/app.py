from flask import Flask
from routes.query_routes import query_bp,upload_bp

app = Flask(__name__)

# Register Routes
app.register_blueprint(query_bp)
app.register_blueprint(upload_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
