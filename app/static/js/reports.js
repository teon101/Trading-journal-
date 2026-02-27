// Populate month and year selectors
function populateSelectors() {
    const monthSelect = document.getElementById('month-select');
    const yearSelect = document.getElementById('year-select');
    
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    // Populate months
    months.forEach((month, index) => {
        const option = document.createElement('option');
        option.value = index + 1;
        option.textContent = month;
        monthSelect.appendChild(option);
    });
    
    // Populate years (current year and 2 years back)
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= currentYear - 2; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }
    
    // Set to current month
    const now = new Date();
    monthSelect.value = now.getMonth() + 1;
    yearSelect.value = now.getFullYear();
}

// Load monthly report
async function loadMonthlyReport() {
    const month = document.getElementById('month-select').value;
    const year = document.getElementById('year-select').value;
    
    if (!month || !year) return;
    
    const reportDiv = document.getElementById('monthly-report');
    reportDiv.innerHTML = '<p class="loading">Loading report...</p>';
    
    try {
        const response = await fetch(`/api/statistics/monthly-report/${year}/${month}`);
        const data = await response.json();
        
        if (data.total_trades === 0) {
            reportDiv.innerHTML = `
                <div class="card">
                    <p class="loading">No trades recorded for ${data.month}</p>
                </div>
            `;
            return;
        }
        
        reportDiv.innerHTML = `
            <div class="stats-grid-main">
                <div class="stat-card stat-card-large">
                    <div class="stat-icon">$</div>
                    <div class="stat-value" style="color: ${data.total_pnl >= 0 ? 'var(--profit-green)' : 'var(--loss-red)'}">
                        ${data.total_pnl >= 0 ? '+' : ''}$${data.total_pnl.toFixed(2)}
                    </div>
                    <div class="stat-label">Total P/L</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">%</div>
                    <div class="stat-value">${data.win_rate}%</div>
                    <div class="stat-label">Win Rate</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">#</div>
                    <div class="stat-value">${data.total_trades}</div>
                    <div class="stat-label">Total Trades</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">✓</div>
                    <div class="stat-value">${data.discipline_score}%</div>
                    <div class="stat-label">Discipline Score</div>
                </div>
            </div>
            
            <div class="card">
                <h3>Monthly Highlights</h3>
                <div class="report-highlights">
                    <div class="highlight-item">
                        <div class="highlight-label">Trading Days</div>
                        <div class="highlight-value">${data.trading_days}</div>
                    </div>
                    <div class="highlight-item">
                        <div class="highlight-label">Avg Win</div>
                        <div class="highlight-value" style="color: var(--profit-green)">$${data.avg_win.toFixed(2)}</div>
                    </div>
                    <div class="highlight-item">
                        <div class="highlight-label">Avg Loss</div>
                        <div class="highlight-value" style="color: var(--loss-red)">$${data.avg_loss.toFixed(2)}</div>
                    </div>
                    <div class="highlight-item">
                        <div class="highlight-label">Best Setup</div>
                        <div class="highlight-value">${data.best_setup.name}</div>
                        <small style="color: var(--text-tertiary)">${data.best_setup.trades} trades, $${data.best_setup.pnl.toFixed(2)}</small>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Best & Worst Trades</h3>
                <div class="trade-comparison">
                    <div class="comparison-item">
                        <div class="comparison-header" style="color: var(--profit-green)">Best Trade</div>
                        <div class="comparison-pair">${data.best_trade.pair}</div>
                        <div class="comparison-pnl">+$${data.best_trade.pnl.toFixed(2)}</div>
                        <div class="comparison-date">${data.best_trade.date}</div>
                    </div>
                    <div class="comparison-item">
                        <div class="comparison-header" style="color: var(--loss-red)">Worst Trade</div>
                        <div class="comparison-pair">${data.worst_trade.pair}</div>
                        <div class="comparison-pnl">$${data.worst_trade.pnl.toFixed(2)}</div>
                        <div class="comparison-date">${data.worst_trade.date}</div>
                    </div>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading report:', error);
        reportDiv.innerHTML = '<div class="card"><p class="error">Failed to load report</p></div>';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    populateSelectors();
    loadMonthlyReport();
});