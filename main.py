import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta

# Import database and models
from src.models.user import db, User
from src.models.inventory import InventoryItem
from src.models.job import Job
from src.models.assignment import InventoryAssignment
from src.models.media import Media

# Import all routes
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.inventory import inventory_bp
from src.routes.jobs import jobs_bp
from src.routes.reports import reports_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))


# Configuration
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['JWT_CSRF_CHECK_FORM'] = False
app.config['JWT_CSRF_IN_COOKIES'] = False
app.config['JWT_ALGORITHM'] = 'HS256'

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize JWT
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(inventory_bp, url_prefix='/api')
app.register_blueprint(jobs_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if it doesn't exist
    admin_user = db.session.query(User).filter_by(username='admin').first()
    if not admin_user:
        admin = User(
            username='admin',
            email='admin@icebreaking.com',
            role='admin',
            first_name='System',
            last_name='Administrator'
        )
        admin.set_password('admin123')  # Change this in production
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin/admin123")

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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'error': 'Token has expired'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'error': 'Invalid token'}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'error': 'Authorization token is required'}, 401

# Routes to serve React frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_frontend_routes(path):
    # Serve static files if they exist
    if path.startswith('assets/'):
        return app.send_static_file(path)
    # Otherwise serve the React app for client-side routing
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
