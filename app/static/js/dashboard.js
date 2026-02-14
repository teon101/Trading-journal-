// Chart instances
let equityChart, winlossChart, sessionChart, mistakesChart;

// Load overall stats
async function loadOverallStats() {
    try {
        const response = await fetch('/api/statistics/overall');
        const stats = await response.json();
        
        // Update stat cards
        document.getElementById('total-pnl').textContent = `$${stats.total_profit_loss.toFixed(2)}`;
        document.getElementById('total-pnl').style.color = stats.total_profit_loss >= 0 ? '#10b981' : '#ef4444';
        
        document.getElementById('win-rate').textContent = `${stats.win_rate}%`;
        document.getElementById('expectancy').textContent = `$${stats.expectancy.toFixed(2)}`;
        document.getElementById('profit-factor').textContent = stats.profit_factor.toFixed(2);
        document.getElementById('max-drawdown').textContent = `$${stats.max_drawdown.toFixed(2)}`;
        document.getElementById('total-trades').textContent = stats.total_trades;
        
    } catch (error) {
        console.error('Error loading overall stats:', error);
    }
}

// Load equity curve
async function loadEquityCurve() {
    try {
        const response = await fetch('/api/statistics/daily/30');
        const data = await response.json();
        
        if (data.length === 0) {
            return;
        }
        
        // Calculate cumulative P/L
        let cumulative = 0;
        const chartData = data.map(day => {
            cumulative += day.profit_loss;
            return {
                date: day.date,
                value: cumulative
            };
        });
        
        const ctx = document.getElementById('equity-chart').getContext('2d');
        
        if (equityChart) {
            equityChart.destroy();
        }
        
        equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.map(d => d.date),
                datasets: [{
                    label: 'Cumulative P/L',
                    data: chartData.map(d => d.value),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading equity curve:', error);
    }
}

// Load win/loss chart
async function loadWinLossChart() {
    try {
        const response = await fetch('/api/statistics/overall');
        const stats = await response.json();
        
        const ctx = document.getElementById('winloss-chart').getContext('2d');
        
        if (winlossChart) {
            winlossChart.destroy();
        }
        
        winlossChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Wins', 'Losses'],
                datasets: [{
                    data: [stats.total_wins, stats.total_losses],
                    backgroundColor: ['#10b981', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading win/loss chart:', error);
    }
}

// Load session performance chart
async function loadSessionChart() {
    try {
        const response = await fetch('/api/statistics/session');
        const data = await response.json();
        
        if (data.length === 0) {
            return;
        }
        
        const ctx = document.getElementById('session-chart').getContext('2d');
        
        if (sessionChart) {
            sessionChart.destroy();
        }
        
        sessionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(s => s.session),
                datasets: [{
                    label: 'Total P/L',
                    data: data.map(s => s.total_pnl),
                    backgroundColor: data.map(s => s.total_pnl >= 0 ? '#10b981' : '#ef4444')
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading session chart:', error);
    }
}

// Load mistakes chart
async function loadMistakesChart() {
    try {
        const response = await fetch('/api/statistics/mistakes');
        const data = await response.json();
        
        if (data.length === 0) {
            return;
        }
        
        const ctx = document.getElementById('mistakes-chart').getContext('2d');
        
        if (mistakesChart) {
            mistakesChart.destroy();
        }
        
        mistakesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(m => m.name),
                datasets: [{
                    label: 'Frequency',
                    data: data.map(m => m.count),
                    backgroundColor: data.map(m => m.color)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
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
    try {
        const response = await fetch('/api/statistics/setup');
        const data = await response.json();
        
        const tableContainer = document.getElementById('setup-stats-table');
        
        if (data.length === 0) {
            tableContainer.innerHTML = '<p class="loading">No setup data available</p>';
            return;
        }
        
        const table = `
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
                            <td>${row.setup}</td>
                            <td>${row.total_trades}</td>
                            <td>${row.wins}</td>
                            <td>${row.losses}</td>
                            <td>${row.win_rate}%</td>
                            <td class="${row.total_pnl >= 0 ? 'positive' : 'negative'}">
                                $${row.total_pnl.toFixed(2)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        tableContainer.innerHTML = table;
        
    } catch (error) {
        console.error('Error loading setup stats:', error);
    }
}

// Load session stats table
async function loadSessionStatsTable() {
    try {
        const response = await fetch('/api/statistics/session');
        const data = await response.json();
        
        const tableContainer = document.getElementById('session-stats-table');
        
        if (data.length === 0) {
            tableContainer.innerHTML = '<p class="loading">No session data available</p>';
            return;
        }
        
        const table = `
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
                            <td>${row.session}</td>
                            <td>${row.total_trades}</td>
                            <td>${row.wins}</td>
                            <td>${row.losses}</td>
                            <td>${row.win_rate}%</td>
                            <td class="${row.total_pnl >= 0 ? 'positive' : 'negative'}">
                                $${row.total_pnl.toFixed(2)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        tableContainer.innerHTML = table;
        
    } catch (error) {
        console.error('Error loading session stats:', error);
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadOverallStats();
    loadEquityCurve();
    loadWinLossChart();
    loadSessionChart();
    loadMistakesChart();
    loadSetupStatsTable();
    loadSessionStatsTable();
});