from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from .models import db

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = '../data/uploads'

db.init_app(app)

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

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('../data', exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)