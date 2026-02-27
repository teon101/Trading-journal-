from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.database import Database
from datetime import datetime

bp = Blueprint('trades', __name__, url_prefix='/api/trades')

def get_db():
    return Database(current_app.config['DATABASE'])

@bp.route('/', methods=['GET'])
@login_required
def get_trades():
    """Get all trades for current user"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM trades 
        WHERE user_id = ?
        ORDER BY entry_time DESC
    ''', (current_user.id,))
    
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
@login_required
def create_trade():
    """Create a new trade for current user"""
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
    
    # Calculate risk percentage
    risk_percentage = (risk / entry * 100) if entry > 0 else 0
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trades (
            user_id, pair, session, timeframe, setup_type, trade_type,
            entry_price, stop_loss, take_profit, position_size,
            risk_amount, reward_amount, risk_reward_ratio, risk_percentage,
            confidence, emotion_before, rule_followed,
            entry_time, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_user.id,  # ADD USER ID HERE
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
        risk_percentage,
        data.get('confidence'),
        data.get('emotion_before'),
        1 if data.get('rule_followed') == 'yes' else 0,
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
@login_required
def close_trade(trade_id):
    """Close a trade (only if it belongs to current user)"""
    data = request.json
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get trade details - verify ownership
    cursor.execute('SELECT * FROM trades WHERE id = ? AND user_id = ?', (trade_id, current_user.id))
    trade = cursor.fetchone()
    
    if not trade:
        conn.close()
        return jsonify({'error': 'Trade not found or access denied'}), 404
    
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
        WHERE id = ? AND user_id = ?
    ''', (exit_price, datetime.now().isoformat(), profit_loss, trade_id, current_user.id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'profit_loss': round(profit_loss, 2)
    })

@bp.route('/<int:trade_id>', methods=['DELETE'])
@login_required
def delete_trade(trade_id):
    """Delete a trade (only if it belongs to current user)"""
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM trades WHERE id = ? AND user_id = ?', (trade_id, current_user.id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@bp.route('/export/csv', methods=['GET'])
@login_required
def export_csv():
    """Export current user's trades to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM trades WHERE user_id = ? ORDER BY entry_time DESC', (current_user.id,))
    trades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not trades:
        return jsonify({'error': 'No trades to export'}), 404
    
    # Create CSV
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=trades[0].keys())
    writer.writeheader()
    writer.writerows(trades)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=trades_export_{current_user.email}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output