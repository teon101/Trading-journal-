from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from app.services.statistics import StatisticsService
from datetime import datetime
from calendar import monthrange

bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')

def get_stats_service():
    return StatisticsService(current_app.config['DATABASE'], user_id=current_user.id)

@bp.route('/overall')
@login_required
def get_overall_stats():
    """Get overall trading statistics for current user"""
    service = get_stats_service()
    stats = service.get_overall_stats()
    return jsonify(stats)

@bp.route('/daily/<int:days>')
@login_required
def get_daily_stats(days):
    """Get daily statistics for current user"""
    service = get_stats_service()
    stats = service.get_stats_by_timeframe(days)
    return jsonify(stats)

@bp.route('/session')
@login_required
def get_session_stats():
    """Get statistics by trading session for current user"""
    service = get_stats_service()
    stats = service.get_stats_by_session()
    return jsonify(stats)

@bp.route('/setup')
@login_required
def get_setup_stats():
    """Get statistics by setup type for current user"""
    service = get_stats_service()
    stats = service.get_stats_by_setup()
    return jsonify(stats)

@bp.route('/mistakes')
@login_required
def get_mistake_stats():
    """Get mistake frequency for current user"""
    service = get_stats_service()
    stats = service.get_mistake_frequency()
    return jsonify(stats)

@bp.route('/monthly-report/<int:year>/<int:month>')
@login_required
def get_monthly_report(year, month):
    """Get comprehensive monthly trading report for current user"""
    service = get_stats_service()
    db = service.db
    conn = db.get_connection()
    cursor = conn.cursor()
   
    # Get month date range
    start_date = f"{year}-{month:02d}-01"
    last_day = monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day}"
   
    # Get all trades for the month and current user
    cursor.execute('''
        SELECT * FROM trades
        WHERE status = 'closed'
        AND user_id = ?
        AND date(exit_time) BETWEEN ? AND ?
        ORDER BY exit_time
    ''', (current_user.id, start_date, end_date))
   
    trades = [dict(row) for row in cursor.fetchall()]
    conn.close()
   
    if not trades:
        return jsonify({
            'month': f"{year}-{month:02d}",
            'total_trades': 0,
            'message': 'No trades this month'
        })
   
    # Calculate monthly stats
    total_trades = len(trades)
    wins = [t for t in trades if t['profit_loss'] > 0]
    losses = [t for t in trades if t['profit_loss'] <= 0]
   
    total_pnl = sum([t['profit_loss'] for t in trades])
    win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
   
    avg_win = sum([t['profit_loss'] for t in wins]) / len(wins) if wins else 0
    avg_loss = abs(sum([t['profit_loss'] for t in losses])) / len(losses) if losses else 0
   
    best_trade = max(trades, key=lambda x: x['profit_loss'])
    worst_trade = min(trades, key=lambda x: x['profit_loss'])
   
    # Trading days
    trading_days = len(set([t['exit_time'][:10] for t in trades if t['exit_time']]))
   
    # Most profitable setup
    setups = {}
    for trade in trades:
        setup = trade['setup_type']
        if setup not in setups:
            setups[setup] = {'total': 0, 'pnl': 0}
        setups[setup]['total'] += 1
        setups[setup]['pnl'] += trade['profit_loss']
   
    best_setup = max(setups.items(), key=lambda x: x[1]['pnl']) if setups else ('N/A', {'pnl': 0})
   
    # Discipline score (percentage of trades that followed rules)
    rule_followed_count = sum([1 for t in trades if t.get('rule_followed', 1) == 1])
    discipline_score = (rule_followed_count / total_trades * 100) if total_trades > 0 else 0
   
    return jsonify({
        'month': f"{year}-{month:02d}",
        'total_trades': total_trades,
        'trading_days': trading_days,
        'total_pnl': round(total_pnl, 2),
        'win_rate': round(win_rate, 2),
        'total_wins': len(wins),
        'total_losses': len(losses),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'best_trade': {
            'pair': best_trade['pair'],
            'pnl': round(best_trade['profit_loss'], 2),
            'date': best_trade['exit_time'][:10]
        },
        'worst_trade': {
            'pair': worst_trade['pair'],
            'pnl': round(worst_trade['profit_loss'], 2),
            'date': worst_trade['exit_time'][:10]
        },
        'best_setup': {
            'name': best_setup[0],
            'pnl': round(best_setup[1]['pnl'], 2),
            'trades': best_setup[1]['total']
        },
        'discipline_score': round(discipline_score, 1)
    })