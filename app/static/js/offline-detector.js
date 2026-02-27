// Offline/Online Status Detector
class OfflineDetector {
    constructor() {
        this.isOnline = navigator.onLine;
        this.init();
    }
    
    init() {
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Show initial status
        this.updateUI();
    }
    
    handleOnline() {
        this.isOnline = true;
        this.updateUI();
        this.showNotification('🟢 Back online - Data will sync automatically', 'success');
    }
    
    handleOffline() {
        this.isOnline = false;
        this.updateUI();
        this.showNotification('🔴 You\'re offline - Changes saved locally', 'warning');
    }
    
    updateUI() {
        const statusBadge = document.getElementById('online-status');
        if (statusBadge) {
            statusBadge.textContent = this.isOnline ? 'Online' : 'Offline';
            statusBadge.className = this.isOnline ? 'status-badge online' : 'status-badge offline';
        }
    }
    
    showNotification(message, type) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new OfflineDetector());
} else {
    new OfflineDetector();
}