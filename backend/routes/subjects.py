from flask import Blueprint, request, jsonify
from models import db, Subject, Book

bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')

@bp.route('', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([subject.to_dict() for subject in subjects])

@bp.route('', methods=['POST'])
def create_subject():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Subject name is required'}), 400
    
    subject = Subject(
        name=data['name'],
        description=data.get('description')
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify(subject.to_dict()), 201

@bp.route('/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify(subject.to_dict())

@bp.route('/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.get_json()
    
    if 'name' in data:
        subject.name = data['name']
    if 'description' in data:
        subject.description = data['description']
    
    db.session.commit()
    return jsonify(subject.to_dict())

@bp.route('/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({'message': 'Subject deleted successfully'})

@bp.route('/<int:subject_id>/books', methods=['GET'])
def get_subject_books(subject_id):
    books = Book.query.filter_by(subject_id=subject_id).all()
    return jsonify([book.to_dict() for book in books])