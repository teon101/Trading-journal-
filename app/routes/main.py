from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required
from app.models.database import Database
from datetime import datetime, timedelta
import random

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@bp.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Trading Journal API is running!'
    })

@bp.route('/api/add-sample-data', methods=['POST'])
@login_required
def add_sample_data():
    """Add sample closed trades for testing"""
    db = Database(current_app.config['DATABASE'])
    conn = db.get_connection()
    cursor = conn.cursor()
    
    pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
    sessions = ['Asian', 'London', 'New York']
    setups = ['EMA + Trendline', 'Support/Resistance', 'Break & Retest']
    
    sample_trades = []
    
    for i in range(10):
        is_buy = random.choice([True, False])
        entry = random.uniform(1.05, 1.10)
        
        if is_buy:
            exit_price = entry + random.uniform(0.001, 0.003) if random.random() > 0.4 else entry - random.uniform(0.0005, 0.001)
        else:
            exit_price = entry - random.uniform(0.001, 0.003) if random.random() > 0.4 else entry + random.uniform(0.0005, 0.001)
        
        position_size = random.uniform(0.1, 1.0)
        profit_loss = (exit_price - entry) * position_size * 100000 if is_buy else (entry - exit_price) * position_size * 100000
        
        sl = entry - 0.0010 if is_buy else entry + 0.0010
        tp = entry + 0.0020 if is_buy else entry - 0.0020
        
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = round(reward / risk, 2)
        
        entry_time = datetime.now() - timedelta(days=random.randint(0, 30))
        exit_time = entry_time + timedelta(hours=random.randint(1, 24))
        
        cursor.execute('''
            INSERT INTO trades (
                user_id, pair, session, timeframe, setup_type, trade_type,
                entry_price, stop_loss, take_profit, position_size,
                risk_amount, reward_amount, risk_reward_ratio,
                entry_time, exit_time, exit_price, profit_loss, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,  # Replace with current_user.id in production
            random.choice(pairs),
            random.choice(sessions),
            'H1',
            random.choice(setups),
            'Buy' if is_buy else 'Sell',
            entry,
            sl,
            tp,
            position_size,
            risk * position_size * 100000,
            reward * position_size * 100000,
            rr_ratio,
            entry_time.isoformat(),
            exit_time.isoformat(),
            exit_price,
            profit_loss,
            'closed'
        ))
        
        sample_trades.append({'pair': random.choice(pairs), 'profit_loss': profit_loss})
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Added {len(sample_trades)} sample trades'
    })