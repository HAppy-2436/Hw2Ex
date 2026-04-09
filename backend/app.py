from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from models import db

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/i/Hw2Ex/data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = '/home/i/Hw2Ex/data/uploads'

db.init_app(app)

from routes import subjects, books, knowledge_nodes, homework, learning, ai

app.register_blueprint(subjects.bp)
app.register_blueprint(books.bp)
app.register_blueprint(knowledge_nodes.bp)
app.register_blueprint(homework.bp)
app.register_blueprint(learning.bp)
app.register_blueprint(ai.bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Learning Assistant API is running'})

@app.route('/api/version', methods=['GET'])
def version():
    return jsonify({
        'name': 'Learning Assistant',
        'version': '1.0.0',
        'author': 'Software Engineering Student'
    })

@app.route('/api/docs', methods=['GET'])
def api_docs():
    return jsonify({
        'endpoints': {
            'subjects': {
                'GET /api/subjects': 'Get all subjects',
                'POST /api/subjects': 'Create new subject',
                'GET /api/subjects/<id>': 'Get subject by ID',
                'PUT /api/subjects/<id>': 'Update subject',
                'DELETE /api/subjects/<id>': 'Delete subject',
                'GET /api/subjects/<id>/books': 'Get books for subject'
            },
            'books': {
                'GET /api/books': 'Get all books',
                'POST /api/books': 'Upload PDF book',
                'GET /api/books/<id>': 'Get book details',
                'PUT /api/books/<id>': 'Update book info',
                'DELETE /api/books/<id>': 'Delete book',
                'GET /api/books/<id>/knowledge-nodes': 'Get book knowledge nodes',
                'GET /api/books/<id>/homework': 'Get book homework'
            },
            'knowledge_nodes': {
                'GET /api/nodes': 'Get knowledge nodes (filter: book_id)',
                'POST /api/nodes': 'Create knowledge node',
                'GET /api/nodes/tree': 'Get complete knowledge tree by book_id',
                'GET /api/nodes/<id>': 'Get node details',
                'PUT /api/nodes/<id>': 'Update node',
                'DELETE /api/nodes/<id>': 'Delete node (cascade delete children)',
                'GET /api/nodes/<id>/children': 'Get node children',
                'GET /api/nodes/<id>/ancestors': 'Get node ancestors path',
                'GET /api/nodes/<id>/tree': 'Get node subtree'
            },
            'homework': {
                'GET /api/homework': 'Get homework items (filters: node_id, status, subject_id)',
                'POST /api/homework': 'Create homework item',
                'POST /api/homework/batch': 'Batch create from CSV',
                'GET /api/homework/<id>': 'Get homework details',
                'PUT /api/homework/<id>': 'Update homework',
                'DELETE /api/homework/<id>': 'Delete homework',
                'PATCH /api/homework/<id>/status': 'Update status (new→learning→reviewed→mastered)',
                'PATCH /api/homework/<id>/mastery': 'Update mastery level (0-5)',
                'POST /api/homework/<id>/link-node': 'Link homework to knowledge node',
                'DELETE /api/homework/<id>/link-node': 'Unlink homework from knowledge node',
                'POST /api/homework/<id>/answer': 'Update answer'
            },
            'learning': {
                'GET /api/learning/records': 'Get learning records',
                'POST /api/learning/records': 'Create learning record',
                'GET /api/learning/records/<id>': 'Get record details',
                'PUT /api/learning/records/<id>': 'Update record',
                'POST /api/learning/records/<id>/practice': 'Record practice result',
                'GET /api/learning/nodes/<id>/status': 'Get node learning status',
                'GET /api/learning/review-plan': 'Get review plan',
                'GET /api/learning/stats': 'Get learning statistics'
            }
        }
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('../data', exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)