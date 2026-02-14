from flask import Blueprint, request, jsonify, current_app
from app.models.database import Database

bp = Blueprint('tags', __name__, url_prefix='/api/tags')

def get_db():
    return Database(current_app.config['DATABASE'])

@bp.route('/', methods=['GET'])
def get_all_tags():
    """Get all available tags"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tags ORDER BY name')
    tags = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(tags)

@bp.route('/', methods=['POST'])
def create_tag():
    """Create a new custom tag"""
    data = request.json
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO tags (name, color) VALUES (?, ?)',
            (data['name'], data.get('color', '#ef4444'))
        )
        tag_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'tag_id': tag_id
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@bp.route('/trade/<int:trade_id>', methods=['GET'])
def get_trade_tags(trade_id):
    """Get all tags for a specific trade"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.* FROM tags t
        JOIN trade_tags tt ON t.id = tt.tag_id
        WHERE tt.trade_id = ?
    ''', (trade_id,))
    
    tags = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(tags)

@bp.route('/trade/<int:trade_id>/add', methods=['POST'])
def add_tag_to_trade(trade_id):
    """Add a tag to a trade"""
    data = request.json
    tag_id = data.get('tag_id')
    
    if not tag_id:
        return jsonify({'error': 'tag_id is required'}), 400
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO trade_tags (trade_id, tag_id) VALUES (?, ?)',
            (trade_id, tag_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@bp.route('/trade/<int:trade_id>/remove', methods=['POST'])
def remove_tag_from_trade(trade_id):
    """Remove a tag from a trade"""
    data = request.json
    tag_id = data.get('tag_id')
    
    if not tag_id:
        return jsonify({'error': 'tag_id is required'}), 400
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'DELETE FROM trade_tags WHERE trade_id = ? AND tag_id = ?',
        (trade_id, tag_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})