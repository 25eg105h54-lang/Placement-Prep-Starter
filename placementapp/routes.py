"""REST API routes for Placement Prep Starter backend."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Task, Skill, MockTest, TestAttempt
from datetime import datetime
import json

# Create blueprints for different route groups
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
api_bp = Blueprint('api', __name__, url_prefix='/api')


# ==================== AUTH ROUTES ====================

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields: name, email, password'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(name=data['name'], email=data['email'])
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Initialize skills for user
        for skill_name in Skill.SKILL_TYPES:
            skill = Skill(user_id=user.id, skill_name=skill_name, progress_percentage=0.0)
            db.session.add(skill)
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user info."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


# ==================== TASK ROUTES ====================

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_all_tasks():
    """Get all tasks for current user."""
    user_id = int(get_jwt_identity())
    week = request.args.get('week', type=int)
    
    query = Task.query.filter_by(user_id=user_id)
    
    if week:
        query = query.filter_by(week=week)
    
    tasks = query.all()
    return jsonify([task.to_dict() for task in tasks]), 200


@api_bp.route('/tasks/week/<int:week>', methods=['GET'])
@jwt_required()
def get_tasks_by_week(week):
    """Get tasks for a specific week."""
    user_id = int(get_jwt_identity())
    
    if week < 1 or week > 8:
        return jsonify({'error': 'Week must be between 1 and 8'}), 400
    
    tasks = Task.query.filter_by(user_id=user_id, week=week).all()
    return jsonify([task.to_dict() for task in tasks]), 200


@api_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate input
    if not data.get('title') or not data.get('week'):
        return jsonify({'error': 'Missing required fields: title, week'}), 400
    
    if data['week'] < 1 or data['week'] > 8:
        return jsonify({'error': 'Week must be between 1 and 8'}), 400
    
    task = Task(
        user_id=user_id,
        title=data['title'],
        description=data.get('description', ''),
        week=data['week']
    )
    
    try:
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task (mark as complete/incomplete)."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Update fields
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
        if data['completed']:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
    
    try:
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task."""
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== DASHBOARD/PROGRESS ROUTES ====================

@api_bp.route('/dashboard/summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """Get dashboard summary (total tasks, completed, progress)."""
    user_id = int(get_jwt_identity())
    
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).count()
    overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Weekly breakdown
    weekly_progress = {}
    for week in range(1, 9):
        week_total = Task.query.filter_by(user_id=user_id, week=week).count()
        week_completed = Task.query.filter_by(user_id=user_id, week=week, completed=True).count()
        weekly_progress[f'week_{week}'] = {
            'total': week_total,
            'completed': week_completed,
            'percentage': (week_completed / week_total * 100) if week_total > 0 else 0
        }
    
    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overall_progress': round(overall_progress, 2),
        'weekly_progress': weekly_progress
    }), 200


@api_bp.route('/progress/overall', methods=['GET'])
@jwt_required()
def get_overall_progress():
    """Get overall 8-week progress percentage."""
    user_id = int(get_jwt_identity())
    
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).count()
    progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return jsonify({
        'total': total_tasks,
        'completed': completed_tasks,
        'progress': round(progress, 2)
    }), 200


@api_bp.route('/progress/week/<int:week>', methods=['GET'])
@jwt_required()
def get_week_progress(week):
    """Get progress for a specific week."""
    user_id = int(get_jwt_identity())
    
    if week < 1 or week > 8:
        return jsonify({'error': 'Week must be between 1 and 8'}), 400
    
    total = Task.query.filter_by(user_id=user_id, week=week).count()
    completed = Task.query.filter_by(user_id=user_id, week=week, completed=True).count()
    progress = (completed / total * 100) if total > 0 else 0
    
    return jsonify({
        'week': week,
        'total': total,
        'completed': completed,
        'progress': round(progress, 2)
    }), 200


# ==================== SKILL ROUTES ====================

@api_bp.route('/skills', methods=['GET'])
@jwt_required()
def get_skills():
    """Get all skills for current user."""
    user_id = int(get_jwt_identity())
    
    skills = Skill.query.filter_by(user_id=user_id).all()
    
    if not skills:
        # Initialize skills if they don't exist
        for skill_name in Skill.SKILL_TYPES:
            skill = Skill(user_id=user_id, skill_name=skill_name, progress_percentage=0.0)
            db.session.add(skill)
        db.session.commit()
        skills = Skill.query.filter_by(user_id=user_id).all()
    
    return jsonify([skill.to_dict() for skill in skills]), 200


@api_bp.route('/skills/<int:skill_id>', methods=['PUT'])
@jwt_required()
def update_skill(skill_id):
    """Update skill progress."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first()
    
    if not skill:
        return jsonify({'error': 'Skill not found'}), 404
    
    if 'progress_percentage' in data:
        progress = data['progress_percentage']
        if progress < 0 or progress > 100:
            return jsonify({'error': 'Progress must be between 0 and 100'}), 400
        skill.progress_percentage = progress
    
    try:
        db.session.commit()
        return jsonify(skill.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== MOCK TEST ROUTES ====================

@api_bp.route('/mock-test', methods=['GET'])
@jwt_required()
def get_mock_test():
    """Get mock test questions (exclude answers)."""
    mock_test = MockTest.query.first()
    
    if not mock_test:
        return jsonify({'error': 'No mock test available'}), 404
    
    return jsonify(mock_test.to_dict(include_answers=False)), 200


@api_bp.route('/submit-test', methods=['POST'])
@jwt_required()
def submit_test():
    """Submit mock test answers and calculate score."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('mock_test_id') or not data.get('answers'):
        return jsonify({'error': 'Missing mock_test_id or answers'}), 400
    
    mock_test = MockTest.query.get(data['mock_test_id'])
    if not mock_test:
        return jsonify({'error': 'Mock test not found'}), 404
    
    # Get questions and calculate score
    questions = mock_test.get_questions()
    user_answers = data['answers']
    score = 0
    total_score = len(questions)
    
    for i, question in enumerate(questions):
        user_answer = user_answers.get(str(i))
        if user_answer == question.get('correct_answer'):
            score += 1
    
    percentage = (score / total_score * 100) if total_score > 0 else 0
    
    # Save test attempt
    attempt = TestAttempt(
        user_id=user_id,
        mock_test_id=data['mock_test_id'],
        answers_json=json.dumps(user_answers),
        score=score,
        total_score=total_score,
        percentage=round(percentage, 2)
    )
    
    try:
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'message': 'Test submitted successfully',
            'score': score,
            'total_score': total_score,
            'percentage': round(percentage, 2),
            'attempt_id': attempt.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/mock-history', methods=['GET'])
@jwt_required()
def get_mock_history():
    """Get test attempt history for current user."""
    user_id = int(get_jwt_identity())
    
    attempts = TestAttempt.query.filter_by(user_id=user_id).order_by(TestAttempt.submitted_at.desc()).all()
    
    return jsonify([attempt.to_dict() for attempt in attempts]), 200


@api_bp.route('/mock-history/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_test_attempt(attempt_id):
    """Get specific test attempt details."""
    user_id = int(get_jwt_identity())
    
    attempt = TestAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
    
    if not attempt:
        return jsonify({'error': 'Test attempt not found'}), 404
    
    result = attempt.to_dict()
    result['answers'] = attempt.get_answers()
    result['questions'] = attempt.mock_test.get_questions()
    
    return jsonify(result), 200
