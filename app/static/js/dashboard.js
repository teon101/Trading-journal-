// Animate charts on load
function animateChart(chart) {
    chart.options.animation = {
        duration: 1000,
        easing: 'easeInOutQuart'
    };
}

// Get theme colors
function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    return {
        textColor: isDark ? '#F9FAFB' : '#111827',
        gridColor: isDark ? 'rgba(255, 255, 255, 0.05)' : '#E5E7EB',
        profitGreen: '#16C784',
        lossRed: '#EA3943',
        accentBlue: '#3B82F6'
    };
}

const colors = getThemeColors();

// Chart.js defaults
Chart.defaults.color = colors.textColor;
Chart.defaults.borderColor = colors.gridColor;

// Chart instances
let equityChart, winlossChart, sessionChart, mistakesChart;

// Chart.js dark theme defaults
Chart.defaults.color = '#8b92a4';
Chart.defaults.borderColor = '#2d3548';
Chart.defaults.backgroundColor = '#1e2433';

// Load overall stats
async function loadOverallStats() {
    const pnlEl = document.getElementById('total-pnl');
    if (!pnlEl) return;

    try {
        const response = await fetch('/api/statistics/overall');
        if (!response.ok) return;
        const stats = await response.json();

        pnlEl.textContent = `$${stats.total_profit_loss.toFixed(2)}`;
        pnlEl.style.color = stats.total_profit_loss >= 0 ? '#10b981' : '#ef4444';

        const els = {
            'win-rate': `${stats.win_rate}%`,
            'expectancy': `$${stats.expectancy.toFixed(2)}`,
            'profit-factor': stats.profit_factor.toFixed(2),
            'max-drawdown': `$${stats.max_drawdown.toFixed(2)}`,
            'total-trades': stats.total_trades,
            'avg-r-multiple': `${stats.avg_r_multiple}R`,
            'risk-discipline': `${stats.risk_discipline}%`,
            'current-streak': stats.current_streak?.count > 0 
                ? `${stats.current_streak.count} ${stats.current_streak.type === 'win' ? '🟢' : '🔴'}` 
                : '-'
        };

        for (const [id, value] of Object.entries(els)) {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        }
    } catch (e) {
        console.error('Error loading overall stats:', e);
    }
}

// Load equity curve
async function loadEquityCurve() {
    const canvas = document.getElementById('equity-chart');
    if (!canvas) return;

    try {
        const response = await fetch('/api/statistics/daily/30');
        if (!response.ok) return;
        const data = await response.json();
        
        if (data.length === 0) return;
        
        let cumulative = 0;
        const chartData = data.map(day => {
            cumulative += day.profit_loss;
            return { date: day.date, value: cumulative };
        });
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (equityChart) equityChart.destroy();
        
        equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.map(d => d.date),
                datasets: [{
                    label: 'Cumulative P/L ($)',
                    data: chartData.map(d => d.value),
                    borderColor: '#2962ff',
                    backgroundColor: 'rgba(41, 98, 255, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: '#2962ff',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e2433',
                        titleColor: '#e4e6eb',
                        bodyColor: '#8b92a4',
                        borderColor: '#2d3548',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#2d3548' },
                        ticks: { callback: v => '$' + v.toFixed(0) }
                    },
                    x: { grid: { color: '#2d3548' } }
                }
            }
        });
    } catch (e) {
        console.error('Error loading equity curve:', e);
    }
}

// Load win/loss chart
async function loadWinLossChart() {
    const canvas = document.getElementById('winloss-chart');
    if (!canvas) return;

    try {
        const response = await fetch('/api/statistics/overall');
        if (!response.ok) return;
        const stats = await response.json();
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (winlossChart) winlossChart.destroy();
        
        winlossChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Wins', 'Losses'],
                datasets: [{
                    data: [stats.total_wins, stats.total_losses],
                    backgroundColor: ['#26a69a', '#ef5350'],
                    borderColor: '#1e2433',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#8b92a4', padding: 20, font: { size: 13, weight: '600' } }
                    },
                    tooltip: {
                        backgroundColor: '#1e2433',
                        titleColor: '#e4e6eb',
                        bodyColor: '#8b92a4',
                        borderColor: '#2d3548',
                        borderWidth: 1,
                        padding: 12
                    }
                }
            }
        });
    } catch (e) {
        console.error('Error loading win/loss chart:', e);
    }
}

// Load session performance chart
async function loadSessionChart() {
    const canvas = document.getElementById('session-chart');
    if (!canvas) return;

    try {
        const response = await fetch('/api/statistics/session');
        if (!response.ok) return;
        const data = await response.json();
        
        if (!data?.length) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (sessionChart) sessionChart.destroy();

        sessionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(s => s.session),
                datasets: [{
                    label: 'Total P/L ($)',
                    data: data.map(s => s.total_pnl),
                    backgroundColor: data.map(s => s.total_pnl >= 0 ? '#26a69a' : '#ef5350'),
                    borderColor: data.map(s => s.total_pnl >= 0 ? '#1e8679' : '#d32f2f'),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e2433',
                        titleColor: '#e4e6eb',
                        bodyColor: '#8b92a4',
                        borderColor: '#2d3548',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: { label: c => 'P/L: $' + c.parsed.y.toFixed(2) }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#2d3548' },
                        ticks: { callback: v => '$' + v.toFixed(0) }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch (e) {
        console.error('Error loading session chart:', e);
    }
}

// Load mistakes chart
async function loadMistakesChart() {
    try {
        const response = await fetch('/api/statistics/mistakes');
        const data = await response.json();
        
        if (data.length === 0) return;
        
        const ctx = document.getElementById('mistakes-chart').getContext('2d');
        
        if (mistakesChart) mistakesChart.destroy();
        
        mistakesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(m => m.name),
                datasets: [{
                    label: 'Frequency',
                    data: data.map(m => m.count),
                    backgroundColor: data.map(m => m.color),
                    barThickness: 30,
                    maxBarThickness: 40
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading mistakes chart:', error);
    }
}

// Load setup stats table
async function loadSetupStatsTable() {
    const container = document.getElementById('setup-stats-table');
    if (!container) return;

    try {
        const response = await fetch('/api/statistics/setup');
        if (!response.ok) return;
        const data = await response.json();
        
        if (data.length === 0) {
            container.innerHTML = '<p class="loading">No setup data available</p>';
            return;
        }
        
        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Setup</th>
                        <th>Total Trades</th>
                        <th>Wins</th>
                        <th>Losses</th>
                        <th>Win Rate</th>
                        <th>Total P/L</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(row => `
                        <tr>
                            <td><strong>${row.setup}</strong></td>
                            <td>${row.total_trades}</td>
                            <td style="color: #26a69a;">${row.wins}</td>
                            <td style="color: #ef5350;">${row.losses}</td>
                            <td>${row.win_rate}%</td>
                            <td class="${row.total_pnl >= 0 ? 'positive' : 'negative'}">
                                $${row.total_pnl.toFixed(2)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (e) {
        console.error('Error loading setup stats:', e);
    }
}

// Load session stats table
async function loadSessionStatsTable() {
    const container = document.getElementById('session-stats-table');
    if (!container) return;

    try {
        const response = await fetch('/api/statistics/session');
        if (!response.ok) return;
        const data = await response.json();
        
        if (data.length === 0) {
            container.innerHTML = '<p class="loading">No session data available</p>';
            return;
        }
        
        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Session</th>
                        <th>Total Trades</th>
                        <th>Wins</th>
                        <th>Losses</th>
                        <th>Win Rate</th>
                        <th>Total P/L</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(row => `
                        <tr>
                            <td><strong>${row.session}</strong></td>
                            <td>${row.total_trades}</td>
                            <td style="color: #26a69a;">${row.wins}</td>
                            <td style="color: #ef5350;">${row.losses}</td>
                            <td>${row.win_rate}%</td>
                            <td class="${row.total_pnl >= 0 ? 'positive' : 'negative'}">
                                $${row.total_pnl.toFixed(2)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (e) {
        console.error('Error loading session stats:', e);
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('total-pnl')) loadOverallStats();
    if (document.getElementById('equity-chart')) loadEquityCurve();
    if (document.getElementById('winloss-chart')) loadWinLossChart();
    if (document.getElementById('session-chart')) loadSessionChart();
    if (document.getElementById('mistakes-chart')) loadMistakesChart();
    if (document.getElementById('setup-stats-table')) loadSetupStatsTable();
    if (document.getElementById('session-stats-table')) loadSessionStatsTable();
});