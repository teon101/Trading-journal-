from flask import Blueprint, jsonify, current_app
from app.services.statistics import StatisticsService

bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')

def get_stats_service():
    return StatisticsService(current_app.config['DATABASE'])

@bp.route('/overall')
def get_overall_stats():
    """Get overall trading statistics"""
    service = get_stats_service()
    stats = service.get_overall_stats()
    return jsonify(stats)

@bp.route('/daily/<int:days>')
def get_daily_stats(days):
    """Get daily statistics for the last N days"""
    service = get_stats_service()
    stats = service.get_stats_by_timeframe(days)
    return jsonify(stats)

@bp.route('/session')
def get_session_stats():
    """Get statistics by trading session"""
    service = get_stats_service()
    stats = service.get_stats_by_session()
    return jsonify(stats)

@bp.route('/setup')
def get_setup_stats():
    """Get statistics by setup type"""
    service = get_stats_service()
    stats = service.get_stats_by_setup()
    return jsonify(stats)

@bp.route('/mistakes')
def get_mistake_stats():
    """Get mistake frequency"""
    service = get_stats_service()
    stats = service.get_mistake_frequency()
    return jsonify(stats)