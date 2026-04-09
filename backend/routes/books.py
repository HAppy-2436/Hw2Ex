from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Book, KnowledgeNode
import fitz

bp = Blueprint('books', __name__, url_prefix='/api/books')

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf_metadata(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        total_pages = doc.page_count
        
        doc.close()
        
        return {
            'total_pages': total_pages,
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'publisher': '',
            'year': metadata.get('creationDate', '')[:4] if metadata.get('creationDate') else None
        }
    except Exception as e:
        current_app.logger.error(f"Error extracting PDF metadata: {e}")
        return None

def extract_chapters_from_pdf(pdf_path):
    chapters = []
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            lines = text.split('\n')
            for line in lines[:10]:
                line = line.strip()
                if line and len(line) < 100:
                    if any(keyword in line.lower() for keyword in ['chapter', '第', '章', 'section', '节']):
                        chapters.append({
                            'title': line,
                            'page_start': page_num + 1,
                            'content': text[:500]
                        })
                        break
        
        doc.close()
        
        if not chapters:
            chapters.append({
                'title': '全文',
                'page_start': 1,
                'page_end': doc.page_count,
                'content': 'PDF内容'
            })
        
        return chapters
    except Exception as e:
        current_app.logger.error(f"Error extracting chapters: {e}")
        return []

@bp.route('', methods=['GET'])
def get_books():
    subject_id = request.args.get('subject_id', type=int)
    
    query = Book.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    
    books = query.all()
    return jsonify([book.to_dict() for book in books])

@bp.route('', methods=['POST'])
def create_book():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only PDF files are accepted.'}), 400
    
    subject_id = request.form.get('subject_id')
    if not subject_id:
        return jsonify({'error': 'subject_id is required'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        metadata = extract_pdf_metadata(file_path)
        if not metadata:
            os.remove(file_path)
            return jsonify({'error': 'Failed to extract PDF metadata'}), 500
        
        chapters = extract_chapters_from_pdf(file_path)
        
        book = Book(
            subject_id=int(subject_id),
            title=request.form.get('title') or metadata['title'] or filename,
            author=request.form.get('author') or metadata['author'],
            publisher=request.form.get('publisher') or metadata['publisher'],
            year=request.form.get('year') or metadata['year'],
            total_pages=metadata['total_pages'],
            pdf_path=file_path,
            extracted_text={'chapters': chapters}
        )
        
        db.session.add(book)
        db.session.commit()
        
        book_dict = book.to_dict()
        book_dict['chapters'] = chapters
        
        return jsonify(book_dict), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating book: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    result = book.to_dict()
    result['chapters'] = book.extracted_text.get('chapters', []) if book.extracted_text else []
    
    return jsonify(result)

@bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'publisher' in data:
        book.publisher = data['publisher']
    if 'year' in data:
        book.year = data['year']
    
    db.session.commit()
    return jsonify(book.to_dict())

@bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if book.pdf_path and os.path.exists(book.pdf_path):
        try:
            os.remove(book.pdf_path)
        except Exception as e:
            current_app.logger.warning(f"Failed to delete PDF file: {e}")
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted successfully'})

@bp.route('/<int:book_id>/knowledge-nodes', methods=['GET'])
def get_book_knowledge_nodes(book_id):
    nodes = KnowledgeNode.query.filter_by(book_id=book_id).all()
    return jsonify([node.to_dict() for node in nodes])

@bp.route('/<int:book_id>/homework', methods=['GET'])
def get_book_homework(book_id):
    from ..models import Homework
    homework = Homework.query.filter_by(book_id=book_id).all()
    return jsonify([h.to_dict() for h in homework])