// Global variables
let currentTradeId = null;
let allTags = [];
let allTradesData = [];

// Export to CSV
async function exportToCSV() {
    try {
        const response = await fetch('/api/trades/export/csv');
        
        if (!response.ok) {
            alert('No trades to export');
            return;
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trades_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        alert('✅ Trades exported successfully!');
    } catch (error) {
        alert('❌ Export failed');
        console.error(error);
    }
}

// Calculate R:R ratio in real-time
function calculateRR() {
    const entry = parseFloat(document.getElementById('entry_price').value) || 0;
    const sl = parseFloat(document.getElementById('stop_loss').value) || 0;
    const tp = parseFloat(document.getElementById('take_profit').value) || 0;
    
    if (entry && sl && tp) {
        const risk = Math.abs(entry - sl);
        const reward = Math.abs(tp - entry);
        const rr = risk > 0 ? (reward / risk).toFixed(2) : 0;
        
        document.getElementById('rr-value').textContent = `1:${rr}`;
    }
}

// Calculate Risk Percentage in real-time
function calculateRiskPercentage() {
    const entry = parseFloat(document.getElementById('entry_price').value) || 0;
    const sl = parseFloat(document.getElementById('stop_loss').value) || 0;
   
    if (entry && sl) {
        const risk = Math.abs(entry - sl);
        const riskPct = (risk / entry * 100).toFixed(2);
       
        document.getElementById('risk-percentage').textContent = `${riskPct}%`;
    }
}

// Load all available tags
async function loadAllTags() {
    try {
        const response = await fetch('/api/tags/');
        allTags = await response.json();
    } catch (error) {
        console.error('Error loading tags:', error);
    }
}

// Open tag modal
function openTagModal(tradeId) {
    currentTradeId = tradeId;
    const modal = document.getElementById('tag-modal');
    const tagsContainer = document.getElementById('available-tags');
    
    fetch(`/api/tags/trade/${tradeId}`)
        .then(res => res.json())
        .then(tradeTags => {
            const tradeTagIds = tradeTags.map(t => t.id);
            
            tagsContainer.innerHTML = allTags.map(tag => `
                <div class="tag-selectable ${tradeTagIds.includes(tag.id) ? 'selected' : ''}" 
                     style="background-color: ${tag.color}; color: white;"
                     data-tag-id="${tag.id}"
                     onclick="toggleTag(${tag.id})">
                    ${tag.name}
                </div>
            `).join('');
            
            modal.style.display = 'block';
        });
}

// Close tag modal
function closeTagModal() {
    document.getElementById('tag-modal').style.display = 'none';
    loadTrades();
}

// Toggle tag selection
async function toggleTag(tagId) {
    const tagElement = document.querySelector(`[data-tag-id="${tagId}"]`);
    const isSelected = tagElement.classList.contains('selected');
    
    try {
        if (isSelected) {
            await fetch(`/api/tags/trade/${currentTradeId}/remove`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag_id: tagId })
            });
            tagElement.classList.remove('selected');
        } else {
            await fetch(`/api/tags/trade/${currentTradeId}/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag_id: tagId })
            });
            tagElement.classList.add('selected');
        }
    } catch (error) {
        console.error('Error toggling tag:', error);
    }
}

// Close trade function
async function closeTrade(tradeId) {
    const exitPrice = prompt('Enter exit price:');
    
    if (!exitPrice || isNaN(exitPrice)) {
        alert('Invalid exit price');
        return;
    }
    
    try {
        const response = await fetch(`/api/trades/${tradeId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ exit_price: parseFloat(exitPrice) })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const pnl = result.profit_loss;
            const message = pnl >= 0 
                ? `✅ Trade closed! Profit: $${pnl.toFixed(2)}`
                : `❌ Trade closed. Loss: $${Math.abs(pnl).toFixed(2)}`;
            alert(message);
            loadTrades();
        }
    } catch (error) {
        alert('Error closing trade');
        console.error(error);
    }
}

// Delete trade function
async function deleteTrade(tradeId) {
    if (!confirm('Are you sure you want to delete this trade?')) return;
    
    try {
        const response = await fetch(`/api/trades/${tradeId}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Trade deleted');
            loadTrades();
        }
    } catch (error) {
        alert('Error deleting trade');
        console.error(error);
    }
}

// Toggle trade card collapse
function toggleTradeCard(tradeId) {
    const tradeCard = document.querySelector(`[data-trade-id="${tradeId}"]`);
    if (tradeCard) {
        tradeCard.classList.toggle('collapsed');
    }
}

// Filter trades
function filterTrades() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const filterPair = document.getElementById('filter-pair').value;
    const filterSession = document.getElementById('filter-session').value;
    const filterSetup = document.getElementById('filter-setup').value;
   
    let filtered = allTradesData;
   
    if (searchTerm) {
        filtered = filtered.filter(trade =>
            trade.pair.toLowerCase().includes(searchTerm) ||
            trade.notes?.toLowerCase().includes(searchTerm) ||
            trade.setup_type.toLowerCase().includes(searchTerm)
        );
    }
   
    if (filterPair) filtered = filtered.filter(trade => trade.pair === filterPair);
    if (filterSession) filtered = filtered.filter(trade => trade.session === filterSession);
    if (filterSetup) filtered = filtered.filter(trade => trade.setup_type === filterSetup);
   
    renderTrades(filtered);
}

// Clear all filters
function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('filter-pair').value = '';
    document.getElementById('filter-session').value = '';
    document.getElementById('filter-setup').value = '';
    renderTrades(allTradesData);
}

// Populate filter dropdowns
function populateFilters() {
    const pairs = [...new Set(allTradesData.map(t => t.pair))];
    const setups = [...new Set(allTradesData.map(t => t.setup_type))];
   
    const pairSelect = document.getElementById('filter-pair');
    const setupSelect = document.getElementById('filter-setup');
   
    pairSelect.innerHTML = '<option value="">All Pairs</option>';
    setupSelect.innerHTML = '<option value="">All Setups</option>';
   
    pairs.forEach(pair => {
        const option = document.createElement('option');
        option.value = pair;
        option.textContent = pair;
        pairSelect.appendChild(option);
    });
   
    setups.forEach(setup => {
        const option = document.createElement('option');
        option.value = setup;
        option.textContent = setup;
        setupSelect.appendChild(option);
    });
}

// Render trades with new compact design
function renderTrades(trades) {
    const tradesList = document.getElementById('trades-list');
   
    if (trades.length === 0) {
        tradesList.innerHTML = '<p class="loading">No trades match your filters.</p>';
        return;
    }
   
    tradesList.innerHTML = trades.map(trade => {
        const confidenceStars = '★'.repeat(trade.confidence || 0) + '☆'.repeat(5 - (trade.confidence || 0));
       
        return `
            <div class="trade-item ${trade.status === 'open' ? '' : 'collapsed'}" data-trade-id="${trade.id}">
                <div class="trade-header" onclick="toggleTradeCard(${trade.id})">
                    <div class="trade-header-left">
                        <svg class="trade-collapse-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                        <div class="trade-pair">${trade.pair}</div>
                        <div class="trade-status status-${trade.status}">
                            ${trade.status.toUpperCase()}
                        </div>
                    </div>
                    <div class="trade-quick-info">
                        <span>${trade.trade_type}</span>
                        <span>R:R 1:${trade.risk_reward_ratio}</span>
                        ${trade.profit_loss !== null ? `
                            <span style="color: ${trade.profit_loss >= 0 ? 'var(--profit-green)' : 'var(--loss-red)'}">
                                ${trade.profit_loss >= 0 ? '+' : ''}$${trade.profit_loss.toFixed(2)}
                            </span>
                        ` : ''}
                    </div>
                </div>
               
                <div class="trade-body">
                    <div class="trade-metadata">
                        ${trade.confidence ? `
                        <div class="metadata-item">
                            <div class="metadata-label">Confidence</div>
                            <div class="metadata-value confidence-stars">${confidenceStars}</div>
                        </div>` : ''}
                        ${trade.emotion_before ? `
                        <div class="metadata-item">
                            <div class="metadata-label">Emotion</div>
                            <div class="metadata-value">${trade.emotion_before}</div>
                        </div>` : ''}
                        ${trade.rule_followed !== null ? `
                        <div class="metadata-item">
                            <div class="metadata-label">Rules</div>
                            <div class="metadata-value">
                                <span class="rule-badge ${trade.rule_followed ? 'yes' : 'no'}">
                                    ${trade.rule_followed ? 'Yes' : 'No'}
                                </span>
                            </div>
                        </div>` : ''}
                        ${trade.risk_percentage ? `
                        <div class="metadata-item">
                            <div class="metadata-label">Risk %</div>
                            <div class="metadata-value">${trade.risk_percentage.toFixed(2)}%</div>
                        </div>` : ''}
                    </div>
                   
                    <div class="trade-details">
                        <div class="detail-item">
                            <div class="detail-label">Type</div>
                            <div class="detail-value">${trade.trade_type}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Entry</div>
                            <div class="detail-value">${trade.entry_price}</div>
                        </div>
                        ${trade.status === 'closed' ? `
                        <div class="detail-item">
                            <div class="detail-label">Exit</div>
                            <div class="detail-value">${trade.exit_price}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">P/L</div>
                            <div class="detail-value" style="color: ${trade.profit_loss >= 0 ? 'var(--profit-green)' : 'var(--loss-red)'}">
                                $${trade.profit_loss.toFixed(2)}
                            </div>
                        </div>` : ''}
                        <div class="detail-item">
                            <div class="detail-label">Session</div>
                            <div class="detail-value">${trade.session}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Setup</div>
                            <div class="detail-value">${trade.setup_type}</div>
                        </div>
                    </div>
                   
                    ${trade.screenshot_before || trade.screenshot_after ? `
                    <div class="trade-screenshots">
                        ${trade.screenshot_before ? `
                        <div class="screenshot-item">
                            <img src="/api/screenshots/view/${trade.screenshot_before}"
                                 alt="Before"
                                 onclick="window.open(this.src, '_blank')">
                            <div class="screenshot-label">Before Entry</div>
                        </div>` : ''}
                        ${trade.screenshot_after ? `
                        <div class="screenshot-item">
                            <img src="/api/screenshots/view/${trade.screenshot_after}"
                                 alt="After"
                                 onclick="window.open(this.src, '_blank')">
                            <div class="screenshot-label">After Exit</div>
                        </div>` : ''}
                    </div>` : ''}
                   
                    <div class="trade-tags">
                        <div class="trade-tags-header">
                            <span class="trade-tags-label">Mistakes:</span>
                            <button class="btn-add-tag" onclick="openTagModal(${trade.id})">
                                + Add Tag
                            </button>
                        </div>
                        <div class="trade-tags-list">
                            ${trade.tags && trade.tags.length > 0
                                ? trade.tags.map(tag => `
                                    <span class="tag-badge" style="background-color: ${tag.color}; color: white;">
                                        ${tag.name}
                                    </span>
                                `).join('')
                                : '<span style="color: var(--text-tertiary); font-size: 0.9em;">No mistakes tagged</span>'
                            }
                        </div>
                    </div>
                   
                    <div class="trade-actions">
                        ${trade.status === 'open' ? `
                            <button class="btn-action btn-close" onclick="closeTrade(${trade.id})">
                                Close Trade
                            </button>` : ''}
                        <button class="btn-action btn-delete" onclick="deleteTrade(${trade.id})">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Load trades
async function loadTrades() {
    try {
        const response = await fetch('/api/trades/');
        const trades = await response.json();
       
        allTradesData = trades; // Store for filtering
        populateFilters();
        renderTrades(trades);
       
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

// Upload screenshot
async function uploadScreenshot(file, tradeId, type) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('trade_id', tradeId);
    formData.append('type', type);
    
    try {
        const response = await fetch('/api/screenshots/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        return result.success;
    } catch (error) {
        console.error('Screenshot upload error:', error);
        return false;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadAllTags();
    await loadTrades();
    
    // Add event listeners for risk calculation
    ['entry_price', 'stop_loss', 'take_profit'].forEach(id => {
        document.getElementById(id).addEventListener('input', () => {
            calculateRR();
            calculateRiskPercentage();
        });
    });
   
    // Add filter event listeners
    document.getElementById('search-input').addEventListener('input', filterTrades);
    document.getElementById('filter-pair').addEventListener('change', filterTrades);
    document.getElementById('filter-session').addEventListener('change', filterTrades);
    document.getElementById('filter-setup').addEventListener('change', filterTrades);
    
    document.querySelector('.close-modal')?.addEventListener('click', closeTagModal);
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('tag-modal');
        if (e.target === modal) closeTagModal();
    });
    
    document.getElementById('trade-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            pair: document.getElementById('pair').value,
            session: document.getElementById('session').value,
            timeframe: document.getElementById('timeframe').value,
            setup_type: document.getElementById('setup_type').value,
            trade_type: document.getElementById('trade_type').value,
            entry_price: document.getElementById('entry_price').value,
            stop_loss: document.getElementById('stop_loss').value,
            take_profit: document.getElementById('take_profit').value,
            position_size: document.getElementById('position_size').value,
            confidence: document.getElementById('confidence').value,
            emotion_before: document.getElementById('emotion_before').value,
            rule_followed: document.querySelector('input[name="rule_followed"]:checked').value,
            notes: document.getElementById('notes').value
        };
        
        try {
            const response = await fetch('/api/trades/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                const tradeId = result.trade_id;
                
                const screenshotFile = document.getElementById('screenshot-before')?.files[0];
                if (screenshotFile) {
                    await uploadScreenshot(screenshotFile, tradeId, 'before');
                }
                
                alert('✅ Trade added successfully!');
                document.getElementById('trade-form').reset();
                document.getElementById('rr-value').textContent = '0.00';
                await loadTrades();
            }
        } catch (error) {
            alert('❌ Error adding trade');
            console.error(error);
        }
    });
});