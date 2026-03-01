"""Main Flask application for Placement Prep Starter backend.

Professional structure with:
- SQLAlchemy ORM for database management
- JWT authentication
- RESTful API design
- CORS support
- SQLite persistence
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, MockTest
from routes import auth_bp, api_bp
from datetime import timedelta
import os
import json


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Configure Flask app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = 'placement-prep-secret-key-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized - please login'}), 401
    
    # Health check endpoint
    @app.route('/', methods=['GET'])
    def health_check():
        return jsonify({
            'message': 'Placement Prep Starter Backend Running',
            'version': '2.0',
            'features': [
                'User Authentication (JWT)',
                'Task Management',
                'Skill Tracking',
                'Mock Tests',
                'Dashboard Analytics'
            ]
        }), 200
    
    # Database initialization
    with app.app_context():
        db.create_all()
        init_mock_tests()
    
    return app


def init_mock_tests():
    """Initialize mock test data if not already present."""
    if MockTest.query.first():
        return  # Already initialized
    
    # Sample mock test questions
    mock_questions = [
        {
            "id": 1,
            "question": "What does CORS stand for?",
            "options": {
                "a": "Cross-Origin Request Sharing",
                "b": "Cross-Origin Resource Sharing",
                "c": "Cross-Object Request Sync",
                "d": "Cross-Origin Response System"
            },
            "correct_answer": "b"
        },
        {
            "id": 2,
            "question": "Which HTTP method is used to retrieve data?",
            "options": {
                "a": "GET",
                "b": "POST",
                "c": "PUT",
                "d": "DELETE"
            },
            "correct_answer": "a"
        },
        {
            "id": 3,
            "question": "What is JWT used for?",
            "options": {
                "a": "Database querying",
                "b": "Authentication and authorization",
                "c": "File compression",
                "d": "API rate limiting"
            },
            "correct_answer": "b"
        },
        {
            "id": 4,
            "question": "Which of the following is a relational database?",
            "options": {
                "a": "MongoDB",
                "b": "Redis",
                "c": "SQLite",
                "d": "Elasticsearch"
            },
            "correct_answer": "c"
        },
        {
            "id": 5,
            "question": "What does ORM stand for?",
            "options": {
                "a": "Object-Relational Mapping",
                "b": "Object-Request Manager",
                "c": "Online Response Module",
                "d": "Object-Relations Model"
            },
            "correct_answer": "a"
        },
        {
            "id": 6,
            "question": "Which Flask extension is used for database management?",
            "options": {
                "a": "Flask-Database",
                "b": "Flask-SQLAlchemy",
                "c": "Flask-ORM",
                "d": "Flask-SQL"
            },
            "correct_answer": "b"
        },
        {
            "id": 7,
            "question": "What is the correct way to hash a password?",
            "options": {
                "a": "Store it in plain text",
                "b": "Use a hashing algorithm like bcrypt",
                "c": "Use base64 encoding",
                "d": "Use simple encryption"
            },
            "correct_answer": "b"
        },
        {
            "id": 8,
            "question": "Which of these is a Git command?",
            "options": {
                "a": "git commit",
                "b": "git save",
                "c": "git store",
                "d": "git keep"
            },
            "correct_answer": "a"
        },
        {
            "id": 9,
            "question": "What is REST API?",
            "options": {
                "a": "Represented Extensible Simple Type",
                "b": "Representational State Transfer",
                "c": "Response State Transfer",
                "d": "Representation Service Transfer"
            },
            "correct_answer": "b"
        },
        {
            "id": 10,
            "question": "Which status code means 'Created'?",
            "options": {
                "a": "200",
                "b": "201",
                "c": "301",
                "d": "401"
            },
            "correct_answer": "b"
        }
    ]
    
    # Create and save mock test
    mock_test = MockTest(
        title='Placement Prep - Web Development Quiz',
        questions_json=json.dumps(mock_questions)
    )
    db.session.add(mock_test)
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
