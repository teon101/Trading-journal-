from datetime import datetime, timedelta
from app.models.database import Database

class StatisticsService:
    def __init__(self, db_path, user_id=None):
        self.db = Database(db_path)
        self.user_id = user_id
    
    def get_overall_stats(self):
        """Calculate overall trading statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.user_id:
            cursor.execute('''
                SELECT * FROM trades 
                WHERE status = 'closed' AND user_id = ?
                ORDER BY exit_time
            ''', (self.user_id,))
        else:
            cursor.execute('''
                SELECT * FROM trades 
                WHERE status = 'closed'
                ORDER BY exit_time
            ''')
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_profit_loss': 0,
                'expectancy': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'total_wins': 0,
                'total_losses': 0,
                'avg_r_multiple': 0,
                'risk_discipline': 0,
                'current_streak': {'type': 'none', 'count': 0}
            }
        
        total_trades = len(trades)
        wins = [t for t in trades if t.get('profit_loss') and t['profit_loss'] > 0]
        losses = [t for t in trades if t.get('profit_loss') and t['profit_loss'] <= 0]
        
        total_wins = len(wins)
        total_losses = len(losses)
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum([t['profit_loss'] for t in wins]) if wins else 0
        total_loss = abs(sum([t['profit_loss'] for t in losses])) if losses else 0
        total_profit_loss = total_profit - total_loss
        
        avg_win = total_profit / total_wins if total_wins > 0 else 0
        avg_loss = total_loss / total_losses if total_losses > 0 else 0
        
        expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss) if total_trades > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else (total_profit if total_profit > 0 else 0)
        
        max_drawdown = self._calculate_max_drawdown(trades)
        
        largest_win = max([t['profit_loss'] for t in wins]) if wins else 0
        largest_loss = min([t['profit_loss'] for t in losses]) if losses else 0
        
        avg_r_multiple = self.get_avg_r_multiple()
        risk_discipline = self.get_risk_discipline()
        current_streak = self.get_current_streak()
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'total_profit_loss': round(total_profit_loss, 2),
            'expectancy': round(expectancy, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'total_wins': total_wins,
            'total_losses': total_losses,
            'avg_r_multiple': avg_r_multiple,
            'risk_discipline': risk_discipline,
            'current_streak': current_streak
        }
    
    def get_avg_r_multiple(self):
        """Calculate average R multiple for winning trades"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.user_id:
            cursor.execute('''
                SELECT AVG(profit_loss / risk_amount) as avg_r
                FROM trades 
                WHERE status = 'closed' AND profit_loss > 0 AND risk_amount > 0 AND user_id = ?
            ''', (self.user_id,))
        else:
            cursor.execute('''
                SELECT AVG(profit_loss / risk_amount) as avg_r
                FROM trades 
                WHERE status = 'closed' AND profit_loss > 0 AND risk_amount > 0
            ''')
        
        result = cursor.fetchone()
        conn.close()
        
        avg_r = result['avg_r'] if result and result['avg_r'] else 0
        return round(avg_r, 2)

    def get_risk_discipline(self):
        """Calculate percentage of trades that followed risk rules"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.user_id:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN ABS(profit_loss) <= risk_amount * 1.1 THEN 1 ELSE 0 END) as disciplined
                FROM trades 
                WHERE status = 'closed' AND user_id = ?
            ''', (self.user_id,))
        else:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN ABS(profit_loss) <= risk_amount * 1.1 THEN 1 ELSE 0 END) as disciplined
                FROM trades 
                WHERE status = 'closed'
            ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result['total'] > 0:
            discipline = (result['disciplined'] / result['total'] * 100)
            return round(discipline, 1)
        return 0

    def get_current_streak(self):
        """Get current win/loss streak"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.user_id:
            cursor.execute('''
                SELECT profit_loss FROM trades 
                WHERE status = 'closed' AND user_id = ?
                ORDER BY exit_time DESC
                LIMIT 20
            ''', (self.user_id,))
        else:
            cursor.execute('''
                SELECT profit_loss FROM trades 
                WHERE status = 'closed'
                ORDER BY exit_time DESC
                LIMIT 20
            ''')
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not trades:
            return {'type': 'none', 'count': 0}
        
        current_is_win = trades[0]['profit_loss'] > 0
        streak = 0
        
        for trade in trades:
            is_win = trade['profit_loss'] > 0
            if is_win == current_is_win:
                streak += 1
            else:
                break
        
        return {
            'type': 'win' if current_is_win else 'loss',
            'count': streak
        }
    
    def _calculate_max_drawdown(self, trades):
        """Calculate maximum drawdown"""
        if not trades:
            return 0
        
        sorted_trades = sorted(
            [t for t in trades if t.get('exit_time')], 
            key=lambda x: x['exit_time'] or ''
        )
        
        if not sorted_trades:
            return 0
        
        balance = 0
        peak = 0
        max_drawdown = 0
        
        for trade in sorted_trades:
            if trade.get('profit_loss'):
                balance += trade['profit_loss']
                if balance > peak:
                    peak = balance
                drawdown = peak - balance
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        
        return max_drawdown
    
    def get_stats_by_timeframe(self, days=30):
        """Get statistics for a specific timeframe"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        if self.user_id:
            cursor.execute('''
                SELECT * FROM trades 
                WHERE status = 'closed' AND exit_time >= ? AND user_id = ?
                ORDER BY exit_time
            ''', (cutoff_date, self.user_id))
        else:
            cursor.execute('''
                SELECT * FROM trades 
                WHERE status = 'closed' AND exit_time >= ?
                ORDER BY exit_time
            ''', (cutoff_date,))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not trades:
            return []
        
        daily_stats = {}
        for trade in trades:
            if not trade.get('exit_time'):
                continue
            date = trade['exit_time'][:10]
            if date not in daily_stats:
                daily_stats[date] = {
                    'date': date,
                    'trades': 0,
                    'profit_loss': 0,
                    'wins': 0,
                    'losses': 0
                }
            
            daily_stats[date]['trades'] += 1
            if trade.get('profit_loss'):
                daily_stats[date]['profit_loss'] += trade['profit_loss']
                if trade['profit_loss'] > 0:
                    daily_stats[date]['wins'] += 1
                else:
                    daily_stats[date]['losses'] += 1
        
        return list(daily_stats.values())
    
    def get_stats_by_session(self):
        """Get statistics grouped by trading session"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.user_id:
            cursor.execute('''
                SELECT session, 
                       COUNT(*) as total,
                       SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN profit_loss IS NOT NULL THEN profit_loss ELSE 0 END) as total_pnl
                FROM trades 
                WHERE status = 'closed' AND user_id = ?
                GROUP BY session
            ''', (self.user_id,))
        else:
            cursor.execute('''
                SELECT session, 
                       COUNT(*) as total,
                       SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN profit_loss IS NOT NULL THEN profit_loss ELSE 0 END) as total_pnl
                FROM trades 
                WHERE status = 'closed'
                GROUP BY session
            ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        stats = []
        for row in results:
            total = row['total']
            wins = row['wins'] or 0
            win_rate = (wins / total * 100) if total > 0 else 0
            
            stats.append({
                'session': row['session'],
                'total_trades': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(row['total_pnl'] or 0, 2)
            })
        
        return stats
    
    def get_stats_by_setup(self):
        """Get statistics grouped by setup type"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.user_id:
            cursor.execute('''
                SELECT setup_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN profit_loss IS NOT NULL THEN profit_loss ELSE 0 END) as total_pnl
                FROM trades 
                WHERE status = 'closed' AND user_id = ?
                GROUP BY setup_type
            ''', (self.user_id,))
        else:
            cursor.execute('''
                SELECT setup_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN profit_loss IS NOT NULL THEN profit_loss ELSE 0 END) as total_pnl
                FROM trades 
                WHERE status = 'closed'
                GROUP BY setup_type
            ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        stats = []
        for row in results:
            total = row['total']
            wins = row['wins'] or 0
            win_rate = (wins / total * 100) if total > 0 else 0
            
            stats.append({
                'setup': row['setup_type'],
                'total_trades': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(row['total_pnl'] or 0, 2)
            })
        
        return stats
    
    def get_mistake_frequency(self):
        """Get frequency of each mistake tag"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.user_id:
            cursor.execute('''
                SELECT t.name, t.color, COUNT(tt.trade_id) as count
                FROM tags t
                LEFT JOIN trade_tags tt ON t.id = tt.tag_id
                LEFT JOIN trades tr ON tt.trade_id = tr.id
                WHERE tr.user_id = ?
                GROUP BY t.id, t.name, t.color
                HAVING count > 0
                ORDER BY count DESC
            ''', (self.user_id,))
        else:
            cursor.execute('''
                SELECT t.name, t.color, COUNT(tt.trade_id) as count
                FROM tags t
                LEFT JOIN trade_tags tt ON t.id = tt.tag_id
                GROUP BY t.id, t.name, t.color
                HAVING count > 0
                ORDER BY count DESC
            ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results