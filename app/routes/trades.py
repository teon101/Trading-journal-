from flask import Blueprint, request, jsonify, current_app
from app.models.database import Database
from datetime import datetime

bp = Blueprint('trades', __name__, url_prefix='/api/trades')

def get_db():
    return Database(current_app.config['DATABASE'])

@bp.route('/', methods=['GET'])
def get_trades():
    """Get all trades with their tags"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM trades 
        ORDER BY entry_time DESC
    ''')
    
    trades = [dict(row) for row in cursor.fetchall()]
    
    # Get tags for each trade
    for trade in trades:
        cursor.execute('''
            SELECT t.* FROM tags t
            JOIN trade_tags tt ON t.id = tt.tag_id
            WHERE tt.trade_id = ?
        ''', (trade['id'],))
        trade['tags'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(trades)

@bp.route('/', methods=['POST'])
def create_trade():
    """Create a new trade"""
    data = request.json
    
    # Calculate R:R ratio
    entry = float(data['entry_price'])
    sl = float(data['stop_loss'])
    tp = float(data['take_profit'])
    
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr_ratio = round(reward / risk, 2) if risk > 0 else 0
    
    # Calculate risk and reward amounts
    position_size = float(data['position_size'])
    risk_amount = risk * position_size
    reward_amount = reward * position_size
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trades (
            pair, session, timeframe, setup_type, trade_type,
            entry_price, stop_loss, take_profit, position_size,
            risk_amount, reward_amount, risk_reward_ratio,
            entry_time, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['pair'],
        data['session'],
        data['timeframe'],
        data['setup_type'],
        data['trade_type'],
        entry,
        sl,
        tp,
        position_size,
        risk_amount,
        reward_amount,
        rr_ratio,
        data.get('entry_time', datetime.now().isoformat()),
        'open',
        data.get('notes', '')
    ))
    
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'trade_id': trade_id,
        'message': 'Trade created successfully'
    }), 201

@bp.route('/<int:trade_id>', methods=['PUT'])
def close_trade(trade_id):
    """Close a trade"""
    data = request.json
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get trade details
    cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
    trade = cursor.fetchone()
    
    if not trade:
        return jsonify({'error': 'Trade not found'}), 404
    
    exit_price = float(data['exit_price'])
    entry_price = float(trade['entry_price'])
    position_size = float(trade['position_size'])
    
    # Calculate P/L
    if trade['trade_type'].lower() == 'buy':
        profit_loss = (exit_price - entry_price) * position_size
    else:
        profit_loss = (entry_price - exit_price) * position_size
    
    cursor.execute('''
        UPDATE trades 
        SET exit_price = ?, exit_time = ?, profit_loss = ?, status = 'closed'
        WHERE id = ?
    ''', (exit_price, datetime.now().isoformat(), profit_loss, trade_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'profit_loss': round(profit_loss, 2)
    })

@bp.route('/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    """Delete a trade"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})