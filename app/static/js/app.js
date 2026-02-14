// Global variables
let currentTradeId = null;
let allTags = [];

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
    
    // Get current trade tags
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
    loadTrades(); // Refresh trades to show updated tags
}

// Toggle tag selection
async function toggleTag(tagId) {
    const tagElement = document.querySelector(`[data-tag-id="${tagId}"]`);
    const isSelected = tagElement.classList.contains('selected');
    
    try {
        if (isSelected) {
            // Remove tag
            await fetch(`/api/tags/trade/${currentTradeId}/remove`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag_id: tagId })
            });
            tagElement.classList.remove('selected');
        } else {
            // Add tag
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
            headers: {
                'Content-Type': 'application/json'
            },
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
    if (!confirm('Are you sure you want to delete this trade?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/trades/${tradeId}`, {
            method: 'DELETE'
        });
        
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

// Load trades
async function loadTrades() {
    try {
        const response = await fetch('/api/trades/');
        const trades = await response.json();
        
        const tradesList = document.getElementById('trades-list');
        
        if (trades.length === 0) {
            tradesList.innerHTML = '<p class="loading">No trades yet. Add your first trade!</p>';
            return;
        }
        
        tradesList.innerHTML = trades.map(trade => `
            <div class="trade-item">
                <div class="trade-header">
                    <div class="trade-pair">${trade.pair}</div>
                    <div class="trade-status status-${trade.status}">
                        ${trade.status.toUpperCase()}
                    </div>
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
                        <div class="detail-value" style="color: ${trade.profit_loss >= 0 ? '#10b981' : '#ef4444'}">
                            $${trade.profit_loss.toFixed(2)}
                        </div>
                    </div>
                    ` : ''}
                    <div class="detail-item">
                        <div class="detail-label">R:R</div>
                        <div class="detail-value">1:${trade.risk_reward_ratio}</div>
                    </div>
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
                    </div>
                    ` : ''}
                    ${trade.screenshot_after ? `
                    <div class="screenshot-item">
                        <img src="/api/screenshots/view/${trade.screenshot_after}" 
                             alt="After"
                             onclick="window.open(this.src, '_blank')">
                        <div class="screenshot-label">After Exit</div>
                    </div>
                    ` : ''}
                </div>
                ` : ''}
                
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
                            : '<span style="color: #888; font-size: 0.9em;">No mistakes tagged</span>'
                        }
                    </div>
                </div>
                
                <div class="trade-actions">
                    ${trade.status === 'open' ? `
                        <button class="btn-action btn-close" onclick="closeTrade(${trade.id})">
                            Close Trade
                        </button>
                    ` : ''}
                    <button class="btn-action btn-delete" onclick="deleteTrade(${trade.id})">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');
        
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
    // Load tags and trades
    await loadAllTags();
    loadTrades();
    
    // Add event listeners for R:R calculation
    ['entry_price', 'stop_loss', 'take_profit'].forEach(id => {
        document.getElementById(id).addEventListener('input', calculateRR);
    });
    
    // Close modal when clicking X or outside
    document.querySelector('.close-modal').addEventListener('click', closeTagModal);
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('tag-modal');
        if (e.target === modal) {
            closeTagModal();
        }
    });
    
    // Handle form submission
    document.getElementById('trade-form').addEventListener('submit', async (e) => {
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
            notes: document.getElementById('notes').value
        };
        
        try {
            const response = await fetch('/api/trades/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                const tradeId = result.trade_id;
                
                // Handle screenshot upload if file is selected
                const screenshotFile = document.getElementById('screenshot-before').files[0];
                if (screenshotFile) {
                    const uploaded = await uploadScreenshot(screenshotFile, tradeId, 'before');
                    if (uploaded) {
                        console.log('Screenshot uploaded successfully');
                    }
                }
                
                alert('✅ Trade added successfully!');
                document.getElementById('trade-form').reset();
                document.getElementById('rr-value').textContent = '0.00';
                loadTrades();
            }
        } catch (error) {
            alert('❌ Error adding trade');
            console.error(error);
        }
    });
});