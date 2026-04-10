import os
import json
import glob
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, Response, stream_with_context
from models import db, Subject, Book, KnowledgeNode, Homework, LearningRecord, Conversation, Message, ReviewPlan, ReviewCheckpoint, UserProfile

bp = Blueprint('sync', __name__, url_prefix='/api/sync')

BACKUP_DIR = '/home/i/Hw2Ex/data/backups'
MAX_BACKUP_SIZE = 50 * 1024 * 1024  # 50MB
MAX_AUTO_BACKUPS = 10
EXPORT_VERSION = '1.0'

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)


def get_all_models():
    """Get all model classes for sync operations"""
    return {
        'subjects': Subject,
        'books': Book,
        'knowledge_nodes': KnowledgeNode,
        'homework': Homework,
        'learning_records': LearningRecord,
        'conversations': Conversation,
        'messages': Message,
        'review_plans': ReviewPlan,
        'review_checkpoints': ReviewCheckpoint,
        'user_profile': UserProfile
    }


def export_data(include_backups=False):
    """Export all data to dictionary format"""
    data = {}
    
    models = get_all_models()
    for key, model_class in models.items():
        if key == 'user_profile':
            # UserProfile is a singleton, get first or None
            profile = model_class.query.first()
            data[key] = [profile.to_dict()] if profile else []
        else:
            items = model_class.query.all()
            data[key] = [item.to_dict() for item in items]
    
    result = {
        'version': EXPORT_VERSION,
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'data': data
    }
    
    return result


def export_partial_data(data_type, ids):
    """Export specific records by type and IDs"""
    models = get_all_models()
    
    if data_type not in models:
        return None, f"Unknown data type: {data_type}"
    
    model_class = models[data_type]
    
    try:
        ids = [int(id) for id in ids.split(',')]
    except ValueError:
        return None, "Invalid ID format"
    
    items = model_class.query.filter(model_class.id.in_(ids)).all()
    
    result = {
        'version': EXPORT_VERSION,
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'data': {
            data_type: [item.to_dict() for item in items]
        }
    }
    
    return result, None


def create_backup(filename=None, is_auto=False):
    """Create a backup file"""
    if filename is None:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        prefix = 'auto_backup' if is_auto else 'backup'
        filename = f"{prefix}_{timestamp}.json"
    
    filepath = os.path.join(BACKUP_DIR, filename)
    data = export_data()
    
    # Check file size
    json_str = json.dumps(data, ensure_ascii=False)
    if len(json_str.encode('utf-8')) > MAX_BACKUP_SIZE:
        return None, "Backup exceeds 50MB limit"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Cleanup old auto backups
    if is_auto:
        cleanup_auto_backups()
    
    return filename, None


def cleanup_auto_backups():
    """Keep only the most recent MAX_AUTO_BACKUPS automatic backups"""
    pattern = os.path.join(BACKUP_DIR, 'auto_backup_*.json')
    backups = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    
    for old_backup in backups[MAX_AUTO_BACKUPS:]:
        try:
            os.remove(old_backup)
        except OSError:
            pass


def list_backups():
    """List all available backup files"""
    pattern = os.path.join(BACKUP_DIR, '*.json')
    backups = []
    
    for filepath in glob.glob(pattern):
        filename = os.path.basename(filepath)
        stat = os.stat(filepath)
        backups.append({
            'filename': filename,
            'size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat() + 'Z',
            'is_auto': filename.startswith('auto_backup')
        })
    
    return sorted(backups, key=lambda x: x['created_at'], reverse=True)


def validate_import_data(data):
    """Validate import data and return preview"""
    if 'version' not in data:
        return None, "Invalid format: missing version"
    
    if 'data' not in data:
        return None, "Invalid format: missing data"
    
    preview = {
        'will_create': {},
        'will_update': {},
        'total_records': 0
    }
    
    models = get_all_models()
    import_data = data.get('data', {})
    
    for key, records in import_data.items():
        if key not in models:
            continue
        
        model_class = models[key]
        preview['will_create'][key] = 0
        preview['will_update'][key] = 0
        
        for record in records:
            record_id = record.get('id')
            if record_id:
                existing = model_class.query.get(record_id)
                if existing:
                    preview['will_update'][key] += 1
                else:
                    preview['will_create'][key] += 1
            else:
                preview['will_create'][key] += 1
        
        preview['total_records'] += len(records)
    
    return preview, None


def import_data(data, conflict_mode='overwrite'):
    """
    Import data from JSON
    conflict_mode: 'overwrite' replaces existing records, 'skip' keeps existing
    """
    models = get_all_models()
    import_data = data.get('data', {})
    
    results = {
        'created': {},
        'updated': {},
        'skipped': {},
        'errors': []
    }
    
    # Order matters for foreign key dependencies
    model_order = ['subjects', 'books', 'knowledge_nodes', 'homework', 'learning_records', 
                   'review_plans', 'review_checkpoints', 'conversations', 'messages', 'user_profile']
    
    for key in model_order:
        if key not in import_data:
            continue
        
        model_class = models[key]
        records = import_data[key]
        
        results['created'][key] = 0
        results['updated'][key] = 0
        results['skipped'][key] = 0
        
        for record in records:
            try:
                record_id = record.pop('id', None)
                
                if record_id:
                    existing = model_class.query.get(record_id)
                    if existing:
                        if conflict_mode == 'skip':
                            results['skipped'][key] += 1
                            continue
                        
                        # Update existing record
                        for field, value in record.items():
                            if hasattr(existing, field):
                                setattr(existing, field, value)
                        results['updated'][key] += 1
                    else:
                        # Create new with ID
                        new_record = model_class(id=record_id, **record)
                        db.session.add(new_record)
                        results['created'][key] += 1
                else:
                    # Create new without ID
                    new_record = model_class(**record)
                    db.session.add(new_record)
                    results['created'][key] += 1
                    
            except Exception as e:
                results['errors'].append(f"{key}: {str(e)}")
    
    db.session.commit()
    
    results['total_created'] = sum(results['created'].values())
    results['total_updated'] = sum(results['updated'].values())
    results['total_skipped'] = sum(results['skipped'].values())
    
    return results


def restore_backup(filename):
    """Restore data from a backup file"""
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(filepath):
        return None, "Backup file not found"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return None, "Invalid JSON file"
    
    return import_data(data, conflict_mode='overwrite')


# ==================== Routes ====================

@bp.route('/export', methods=['GET'])
def export_all():
    """Export all data as JSON"""
    include_backups = request.args.get('include_backups', 'false').lower() == 'true'
    
    data = export_data(include_backups)
    
    return jsonify(data)


@bp.route('/export/partial', methods=['GET'])
def export_partial():
    """Partial export by type and IDs"""
    data_type = request.args.get('type')
    ids = request.args.get('ids', '')
    
    if not data_type:
        return jsonify({'error': 'type parameter is required'}), 400
    
    if not ids:
        return jsonify({'error': 'ids parameter is required'}), 400
    
    data, error = export_partial_data(data_type, ids)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(data)


@bp.route('/import', methods=['POST'])
def import_json():
    """Import data from JSON"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    conflict_mode = request.args.get('mode', 'overwrite')
    if conflict_mode not in ['overwrite', 'skip']:
        conflict_mode = 'overwrite'
    
    results = import_data(data, conflict_mode)
    
    return jsonify({
        'message': 'Import completed',
        'results': results
    })


@bp.route('/import/validate', methods=['POST'])
def validate_import():
    """Validate import data and return preview"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    preview, error = validate_import_data(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Validation successful',
        'preview': preview
    })


@bp.route('/backup', methods=['POST'])
def create_manual_backup():
    """Create a manual backup"""
    filename, error = create_backup(is_auto=False)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Backup created successfully',
        'filename': filename
    })


@bp.route('/backups', methods=['GET'])
def list_backups_route():
    """List all available backups"""
    backups = list_backups()
    
    return jsonify({
        'backups': backups,
        'count': len(backups)
    })


@bp.route('/backups/<filename>', methods=['GET'])
def download_backup(filename):
    """Download a specific backup file"""
    # Security: prevent path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Backup file not found'}), 404
    
    return send_file(
        filepath,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )


@bp.route('/restore/<filename>', methods=['POST'])
def restore_backup_route(filename):
    """Restore data from a backup"""
    # Security: prevent path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    # Create auto backup before restore
    create_backup(is_auto=True)
    
    results, error = restore_backup(filename)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Restore completed',
        'results': results
    })


@bp.route('/auto-backup', methods=['POST'])
def enable_auto_backup():
    """Enable or configure auto backup (placeholder for future implementation)"""
    # This could be extended to store settings in database
    return jsonify({
        'message': 'Auto backup configuration endpoint',
        'settings': {
            'enabled': True,
            'max_backups': MAX_AUTO_BACKUPS,
            'max_size_mb': MAX_BACKUP_SIZE // (1024 * 1024)
        }
    })
