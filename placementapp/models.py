"""Database models for Placement Prep Starter backend using SQLAlchemy ORM."""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and data isolation."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationships
    tasks = db.relationship('Task', back_populates='user', cascade='all, delete-orphan')
    skills = db.relationship('Skill', back_populates='user', cascade='all, delete-orphan')
    test_attempts = db.relationship('TestAttempt', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dict (exclude password)."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Task(db.Model):
    """Task model for weekly tasks."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    week = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # relationship
    user = db.relationship('User', back_populates='tasks')
    
    def to_dict(self):
        """Convert task to dict."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'week': self.week,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Skill(db.Model):
    """Skill tracker model."""
    __tablename__ = 'skills'
    
    SKILL_TYPES = ['Coding Basics', 'Git & GitHub', 'LinkedIn', 'Communication']
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_name = db.Column(db.String(100), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)  # 0-100
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # relationship
    user = db.relationship('User', back_populates='skills')
    
    def to_dict(self):
        """Convert skill to dict."""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'progress_percentage': self.progress_percentage,
            'updated_at': self.updated_at.isoformat()
        }


class MockTest(db.Model):
    """Mock test questions model."""
    __tablename__ = 'mock_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    questions_json = db.Column(db.Text, nullable=False)  # JSON array of questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationship
    attempts = db.relationship('TestAttempt', back_populates='mock_test', cascade='all, delete-orphan')
    
    def get_questions(self):
        """Parse and return questions from JSON."""
        return json.loads(self.questions_json)
    
    def to_dict(self, include_answers=False):
        """Convert mock test to dict."""
        questions = self.get_questions()
        if not include_answers:
            # Remove answers for frontend
            for q in questions:
                q.pop('correct_answer', None)
        return {
            'id': self.id,
            'title': self.title,
            'questions': questions,
            'total_questions': len(questions)
        }


class TestAttempt(db.Model):
    """Test attempt/submission model."""
    __tablename__ = 'test_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_tests.id'), nullable=False, index=True)
    answers_json = db.Column(db.Text, nullable=False)  # JSON of user answers
    score = db.Column(db.Integer)  # points earned
    total_score = db.Column(db.Integer)  # total possible points
    percentage = db.Column(db.Float)  # score percentage (0-100)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationships
    user = db.relationship('User', back_populates='test_attempts')
    mock_test = db.relationship('MockTest', back_populates='attempts')
    
    def get_answers(self):
        """Parse and return answers from JSON."""
        return json.loads(self.answers_json)
    
    def to_dict(self):
        """Convert test attempt to dict."""
        return {
            'id': self.id,
            'mock_test_id': self.mock_test_id,
            'score': self.score,
            'total_score': self.total_score,
            'percentage': self.percentage,
            'submitted_at': self.submitted_at.isoformat()
        }
