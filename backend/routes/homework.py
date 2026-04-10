from flask import Blueprint, request, jsonify
import pandas as pd
from io import StringIO
from datetime import datetime
from models import db, Homework, Book, KnowledgeNode

bp = Blueprint('homework', __name__, url_prefix='/api/homework')

VALID_STATUSES = ['new', 'learning', 'reviewed', 'mastered']
VALID_MASTERY_LEVELS = range(0, 6)  # 0-5


@bp.route('', methods=['GET'])
def get_homework():
    """获取所有作业，支持过滤
    Query params: node_id, status, subject_id
    """
    node_id = request.args.get('node_id')
    status = request.args.get('status')
    subject_id = request.args.get('subject_id')
    
    query = Homework.query
    
    if node_id:
        query = query.filter_by(primary_node_id=node_id)
    if status:
        if status not in VALID_STATUSES:
            return jsonify({'error': f'status must be one of: {", ".join(VALID_STATUSES)}'}), 400
        query = query.filter_by(status=status)
    if subject_id:
        # Join through book to filter by subject
        query = query.join(Book).filter(Book.subject_id == subject_id)
    
    homework = query.all()
    return jsonify([h.to_dict() for h in homework])


@bp.route('', methods=['POST'])
def create_homework():
    """创建新作业
    Required: content
    Optional: book_id, title, node_id, answer, status, mastery_level
    """
    data = request.get_json()
    
    if 'content' not in data:
        return jsonify({'error': 'content is required'}), 400
    
    homework = Homework(
        book_id=data.get('book_id'),
        primary_node_id=data.get('node_id'),
        title=data.get('title'),
        content=data['content'],
        answer=data.get('answer'),
        secondary_nodes=data.get('secondary_nodes', []),
        status=data.get('status', 'new'),
        mastery_level=data.get('mastery_level', 0)
    )
    
    db.session.add(homework)
    db.session.commit()
    
    return jsonify(homework.to_dict()), 201


@bp.route('/batch', methods=['POST'])
def batch_create_homework():
    """批量创建作业（从CSV/Excel文件）"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    book_id = request.form.get('book_id')
    
    if not book_id:
        return jsonify({'error': 'book_id is required'}), 400
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(file.read().decode('utf-8')))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'File must be CSV or Excel format'}), 400
        
        required_columns = ['content']
        for col in required_columns:
            if col not in df.columns:
                return jsonify({'error': f'CSV must contain "{col}" column'}), 400
        
        created_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                homework = Homework(
                    book_id=book_id,
                    title=str(row.get('title', '')),
                    content=str(row['content']),
                    answer=str(row.get('answer', '')),
                    status='new'
                )
                
                db.session.add(homework)
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully created {created_count} homework items',
            'created_count': created_count,
            'errors': errors if errors else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500


@bp.route('/<int:homework_id>', methods=['GET'])
def get_homework_item(homework_id):
    """获取作业详情"""
    homework = Homework.query.get_or_404(homework_id)
    return jsonify(homework.to_dict())


@bp.route('/<int:homework_id>', methods=['PUT'])
def update_homework_item(homework_id):
    """更新作业信息"""
    homework = Homework.query.get_or_404(homework_id)
    data = request.get_json()
    
    if 'title' in data:
        homework.title = data['title']
    if 'content' in data:
        homework.content = data['content']
    if 'answer' in data:
        homework.answer = data['answer']
    if 'node_id' in data:
        homework.primary_node_id = data['node_id']
    if 'secondary_nodes' in data:
        homework.secondary_nodes = data['secondary_nodes']
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return jsonify({'error': f'status must be one of: {", ".join(VALID_STATUSES)}'}), 400
        homework.status = data['status']
    if 'mastery_level' in data:
        if data['mastery_level'] not in VALID_MASTERY_LEVELS:
            return jsonify({'error': 'mastery_level must be between 0 and 5'}), 400
        homework.mastery_level = data['mastery_level']
    
    db.session.commit()
    return jsonify(homework.to_dict())


@bp.route('/<int:homework_id>', methods=['DELETE'])
def delete_homework_item(homework_id):
    """删除作业"""
    homework = Homework.query.get_or_404(homework_id)
    
    db.session.delete(homework)
    db.session.commit()
    
    return jsonify({'message': 'Homework deleted successfully'})


@bp.route('/<int:homework_id>/status', methods=['PATCH'])
def update_status(homework_id):
    """更新作业状态
    状态流转: new → learning → reviewed → mastered
    """
    homework = Homework.query.get_or_404(homework_id)
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'error': 'status is required'}), 400
    
    new_status = data['status']
    if new_status not in VALID_STATUSES:
        return jsonify({'error': f'status must be one of: {", ".join(VALID_STATUSES)}'}), 400
    
    # Validate status transition
    status_order = {'new': 0, 'learning': 1, 'reviewed': 2, 'mastered': 3}
    current_order = status_order.get(homework.status, 0)
    new_order = status_order.get(new_status, 0)
    
    # Allow forward progression or same status (for re-review)
    if new_order < current_order and new_status != homework.status:
        return jsonify({'error': f'Invalid status transition from "{homework.status}" to "{new_status}"'}), 400
    
    homework.status = new_status
    db.session.commit()
    
    return jsonify(homework.to_dict())


@bp.route('/<int:homework_id>/mastery', methods=['PATCH'])
def update_mastery(homework_id):
    """更新掌握程度
    mastery_level: 0-5 (0=陌生, 5=熟悉)
    """
    homework = Homework.query.get_or_404(homework_id)
    data = request.get_json()
    
    if 'mastery_level' not in data:
        return jsonify({'error': 'mastery_level is required'}), 400
    
    mastery_level = data['mastery_level']
    if mastery_level not in VALID_MASTERY_LEVELS:
        return jsonify({'error': 'mastery_level must be between 0 and 5'}), 400
    
    homework.mastery_level = mastery_level
    db.session.commit()
    
    return jsonify(homework.to_dict())


@bp.route('/<int:homework_id>/link-node', methods=['POST'])
def link_node(homework_id):
    """关联作业到知识点
    Body: {node_id: x}
    """
    homework = Homework.query.get_or_404(homework_id)
    data = request.get_json()
    
    if 'node_id' not in data:
        return jsonify({'error': 'node_id is required'}), 400
    
    node_id = data['node_id']
    node = KnowledgeNode.query.get(node_id)
    if not node:
        return jsonify({'error': 'Knowledge node not found'}), 404
    
    # Validate node belongs to same book as homework
    if homework.book_id and node.book_id != homework.book_id:
        return jsonify({'error': 'Knowledge node must belong to the same book as homework'}), 400
    
    homework.primary_node_id = node_id
    db.session.commit()
    
    return jsonify(homework.to_dict())


@bp.route('/<int:homework_id>/link-node', methods=['DELETE'])
def unlink_node(homework_id):
    """取消作业与知识点的关联"""
    homework = Homework.query.get_or_404(homework_id)
    
    homework.primary_node_id = None
    db.session.commit()
    
    return jsonify(homework.to_dict())


@bp.route('/<int:homework_id>/answer', methods=['POST'])
def update_answer(homework_id):
    """更新作业答案（保留接口，状态流转到learning）"""
    homework = Homework.query.get_or_404(homework_id)
    data = request.get_json()
    
    if 'answer' not in data:
        return jsonify({'error': 'answer is required'}), 400
    
    homework.answer = data['answer']
    # Auto-transition to learning when answer is provided
    if homework.status == 'new':
        homework.status = 'learning'
    
    db.session.commit()
    return jsonify(homework.to_dict())