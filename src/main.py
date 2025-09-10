import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.soil import soil_bp
from src.routes.disease import disease_bp
from src.routes.weather import weather_bp
from src.routes.community import community_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, origins=['*'])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(soil_bp, url_prefix='/api')
app.register_blueprint(disease_bp, url_prefix='/api')
app.register_blueprint(weather_bp, url_prefix='/api')
app.register_blueprint(community_bp, url_prefix='/api')

# Database configuration
database_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
os.makedirs(database_dir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(database_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "✅ Krishi AI Backend is running!"
@app.route('/', defaults={'path': ''})

@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'message': 'Agriculture API is running',
        'version': '1.0.0'
    }

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint"""
    docs = {
        'title': 'Agriculture Platform API',
        'version': '1.0.0',
        'description': 'Comprehensive API for agriculture platform with ML integration',
        'endpoints': {
            'User Management': {
                'GET /api/users': 'Get all users',
                'POST /api/users': 'Create new user',
                'GET /api/users/<id>': 'Get user by ID',
                'PUT /api/users/<id>': 'Update user',
                'DELETE /api/users/<id>': 'Delete user'
            },
            'Soil Analysis': {
                'POST /api/soil/analyze': 'Analyze soil sample',
                'GET /api/soil/history/<user_id>': 'Get soil analysis history',
                'GET /api/soil/<analysis_id>': 'Get specific soil analysis'
            },
            'Crop Recommendations': {
                'POST /api/crops/recommend': 'Get crop recommendations',
            },
            'Disease Detection': {
                'POST /api/disease/detect': 'Detect crop disease',
                'POST /api/disease/upload': 'Upload image for analysis',
                'GET /api/disease/history/<user_id>': 'Get disease detection history'
            },
            'Weather': {
                'GET /api/weather/current/<location>': 'Get current weather',
                'GET /api/weather/forecast/<location>': 'Get weather forecast',
                'GET /api/weather/alerts/<location>': 'Get weather alerts',
                'GET /api/weather/history/<location>': 'Get weather history'
            },
            'Community': {
                'GET /api/community/posts': 'Get community posts',
                'POST /api/community/posts': 'Create new post',
                'GET /api/community/posts/<id>': 'Get specific post',
                'POST /api/community/posts/<id>/comments': 'Add comment',
                'POST /api/community/posts/<id>/like': 'Like post',
                'GET /api/community/search': 'Search posts',
                'GET /api/community/trending': 'Get trending posts'
            }
        }
    }
    return docs
#
#if __name__ == '__main__':
  #  app.run(host='0.0.0.0', port=5001, debug=True) 

# import os

# if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


