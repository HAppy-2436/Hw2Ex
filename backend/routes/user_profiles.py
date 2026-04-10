from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, UserProfile

bp = Blueprint('user_profiles', __name__, url_prefix='/api/user')


def get_or_create_profile():
    """获取或创建用户画像（目前使用默认用户ID=1）"""
    user_id = request.headers.get('X-User-ID', 1, type=int)
    profile = UserProfile.query.filter_by(id=user_id).first()
    if not profile:
        profile = UserProfile(id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile


@bp.route('/profile', methods=['GET'])
def get_profile():
    """
    获取用户画像
    
    Returns: {
        "profile": UserProfile
    }
    """
    try:
        profile = get_or_create_profile()
        return jsonify({'profile': profile.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
def update_profile():
    """
    更新用户画像（完整更新）
    
    Body: {
        "name": str,
        "grade": str,
        "major": str,
        "enrollment_year": int,
        "learning_background": object,
        "subject_preferences": object,
        "learning_habits": object
    }
    
    Returns: {
        "profile": UserProfile
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        profile = get_or_create_profile()
        
        # 更新字段
        if 'name' in data:
            profile.name = data['name']
        if 'grade' in data:
            profile.grade = data['grade']
        if 'major' in data:
            profile.major = data['major']
        if 'enrollment_year' in data:
            profile.enrollment_year = data['enrollment_year']
        if 'learning_background' in data:
            profile.learning_background = data['learning_background']
        if 'subject_preferences' in data:
            profile.subject_preferences = data['subject_preferences']
        if 'learning_habits' in data:
            profile.learning_habits = data['learning_habits']
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'profile': profile.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/profile/weak-points', methods=['PATCH'])
def update_weak_points():
    """
    更新薄弱点
    
    Body: {
        "weak_points": [
            {
                "node_id": int,
                "topic": str,
                "difficulty": int,  # 1-5
                "last_reviewed": str,  # ISO date
                "review_count": int
            }
        ]
    }
    
    Returns: {
        "profile": UserProfile
    }
    """
    try:
        data = request.get_json()
        if not data or 'weak_points' not in data:
            return jsonify({'error': 'weak_points 是必填参数'}), 400

        profile = get_or_create_profile()
        profile.persistent_weak_points = data['weak_points']
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'profile': profile.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/profile/session', methods=['PATCH'])
def update_learning_session():
    """
    更新当前学习上下文
    
    Body: {
        "current_learning_session": {
            "node_id": int,
            "topic": str,
            "sub_topics": [],
            "progress": int,  # 0-100
            "start_time": str  # ISO date
        }
    }
    
    Returns: {
        "profile": UserProfile
    }
    """
    try:
        data = request.get_json()
        if not data or 'current_learning_session' not in data:
            return jsonify({'error': 'current_learning_session 是必填参数'}), 400

        profile = get_or_create_profile()
        profile.current_learning_session = data['current_learning_session']
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'profile': profile.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
