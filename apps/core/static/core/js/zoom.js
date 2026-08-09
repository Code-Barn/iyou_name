/**
 * Shared Zoom Functionality Module
 * Provides both scale and magnifier zoom modes for image preview elements
 */

window.ZoomManager = {
    // Configuration
    currentZoom: 100,
    minZoom: 25,
    maxZoom: 200,
    zoomStep: 10,
    zoomMode: 'scale', // 'scale' or 'magnifier'
    magnifierSize: 150,
    magnifierZoom: 2.0,
    
    // Internal references
    magnifier: null,
    mouseMoveHandler: null,
    mouseEnterHandler: null,
    mouseLeaveHandler: null,
    touchMoveHandler: null,
    
    /**
     * Initialize zoom functionality for a preview container
     * @param {string} previewContainerId - ID of the preview container element
     * @param {string} previewImageId - ID of the preview image element
     * @param {Object} options - Configuration options
     */
    init: function(previewContainerId, previewImageId, options = {}) {
        // Override default options
        Object.assign(this, options);
        
        this.previewContainerId = previewContainerId;
        this.previewImageId = previewImageId;
        
        console.log('ZoomManager initialized for:', previewContainerId, previewImageId);
        
        // Initialize keyboard shortcuts
        this.initKeyboardShortcuts();
        
        // Initialize mouse wheel zoom
        this.initMouseWheelZoom();
        
        // Initialize auto mobile zoom if enabled
        if (options.autoMobileZoom !== false) {
            this.initAutoMobileZoom();
        }
    },
    
    /**
     * Initialize magnifying glass element
     */
    initMagnifier: function() {
        if (!this.magnifier) {
            this.magnifier = document.createElement('div');
            this.magnifier.className = 'magnifying-glass';
            this.magnifier.style.width = this.magnifierSize + 'px';
            this.magnifier.style.height = this.magnifierSize + 'px';
            document.body.appendChild(this.magnifier);
        }
    },
    
    /**
     * Toggle between scale and magnifier mode
     */
    toggleZoomMode: function() {
        const preview = document.getElementById(this.previewImageId);
        const container = document.getElementById(this.previewContainerId);
        const modeToggle = document.getElementById('zoom-mode-toggle');
        const modeIcon = document.getElementById('zoom-mode-icon');
        const modeText = document.getElementById('zoom-mode-text');
        const scaleControls = document.getElementById('scale-controls');
        const magnifierControls = document.getElementById('magnifier-controls');
        
        if (this.zoomMode === 'scale') {
            this.zoomMode = 'magnifier';
            this.initMagnifier();
            this.enableMagnifier();
            
            if (modeIcon) modeIcon.className = 'bi bi-search';
            if (modeText) modeText.textContent = 'Magnifier';
            if (modeToggle) {
                modeToggle.className = 'btn btn-outline-warning btn-sm me-2';
            }
            if (scaleControls) scaleControls.style.display = 'none';
            if (magnifierControls) magnifierControls.style.display = 'inline';
            
            console.log('Switched to Magnifier mode');
        } else {
            this.zoomMode = 'scale';
            this.disableMagnifier();
            
            if (modeIcon) modeIcon.className = 'bi bi-toggle-on';
            if (modeText) modeText.textContent = 'Scale';
            if (modeToggle) {
                modeToggle.className = 'btn btn-outline-info btn-sm me-2';
            }
            if (scaleControls) scaleControls.style.display = 'inline';
            if (magnifierControls) magnifierControls.style.display = 'none';
            
            console.log('Switched to Scale mode');
        }
        
        this.updateDisplay();
    },
    
    /**
     * Enable magnifying glass functionality
     */
    enableMagnifier: function() {
        const container = document.getElementById(this.previewContainerId);
        
        if (!container) return;
        
        container.classList.add('magnifier-active');
        
        // Mouse move handler for desktop
        this.mouseMoveHandler = (e) => {
            this.updateMagnifier(e.clientX, e.clientY);
        };
        
        // Touch move handler for mobile
        this.touchMoveHandler = (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            this.updateMagnifier(touch.clientX, touch.clientY);
        };
        
        // Mouse enter/leave handlers
        this.mouseEnterHandler = () => {
            if (this.magnifier) {
                this.magnifier.classList.add('active');
            }
        };
        
        this.mouseLeaveHandler = () => {
            if (this.magnifier) {
                this.magnifier.classList.remove('active');
            }
        };
        
        container.addEventListener('mousemove', this.mouseMoveHandler);
        container.addEventListener('mouseenter', this.mouseEnterHandler);
        container.addEventListener('mouseleave', this.mouseLeaveHandler);
        container.addEventListener('touchmove', this.touchMoveHandler, { passive: false });
        container.addEventListener('touchstart', this.mouseEnterHandler);
        container.addEventListener('touchend', this.mouseLeaveHandler);
    },
    
    /**
     * Disable magnifying glass functionality
     */
    disableMagnifier: function() {
        const container = document.getElementById(this.previewContainerId);
        
        if (!container) return;
        
        container.classList.remove('magnifier-active');
        
        if (this.magnifier) {
            this.magnifier.classList.remove('active');
        }
        
        // Remove event listeners
        if (this.mouseMoveHandler) {
            container.removeEventListener('mousemove', this.mouseMoveHandler);
        }
        if (this.mouseEnterHandler) {
            container.removeEventListener('mouseenter', this.mouseEnterHandler);
        }
        if (this.mouseLeaveHandler) {
            container.removeEventListener('mouseleave', this.mouseLeaveHandler);
        }
        if (this.touchMoveHandler) {
            container.removeEventListener('touchmove', this.touchMoveHandler);
            container.removeEventListener('touchstart', this.mouseEnterHandler);
            container.removeEventListener('touchend', this.mouseLeaveHandler);
        }
    },
    
    /**
     * Update magnifier position and content
     */
    updateMagnifier: function(clientX, clientY) {
        const preview = document.getElementById(this.previewImageId);
        const container = document.getElementById(this.previewContainerId);
        
        if (!preview || !container || !this.magnifier) return;
        
        const rect = container.getBoundingClientRect();
        const previewRect = preview.getBoundingClientRect();
        
        // Check if mouse is over the preview image
        if (clientX < previewRect.left || clientX > previewRect.right ||
            clientY < previewRect.top || clientY > previewRect.bottom) {
            this.magnifier.classList.remove('active');
            return;
        }
        
        // Calculate position relative to the preview image
        const x = clientX - previewRect.left;
        const y = clientY - previewRect.top;
        
        // Position magnifier
        const magnifierX = clientX - this.magnifierSize / 2;
        const magnifierY = clientY - this.magnifierSize / 2;
        
        this.magnifier.style.left = magnifierX + 'px';
        this.magnifier.style.top = magnifierY + 'px';
        
        // Set background image and position for zoom effect
        const effectiveZoom = this.magnifierZoom * (this.currentZoom / 100);
        const bgX = -(x * effectiveZoom - this.magnifierSize / 2);
        const bgY = -(y * effectiveZoom - this.magnifierSize / 2);
        
        this.magnifier.style.backgroundImage = `url(${preview.src})`;
        this.magnifier.style.backgroundSize = `${previewRect.width * effectiveZoom}px ${previewRect.height * effectiveZoom}px`;
        this.magnifier.style.backgroundPosition = `${bgX}px ${bgY}px`;
    },
    
    /**
     * Zoom in functionality
     */
    zoomIn: function() {
        if (this.zoomMode === 'scale') {
            const newZoom = Math.min(this.currentZoom + this.zoomStep, this.maxZoom);
            this.setZoom(newZoom);
            console.log('Zoomed in to:', newZoom + '%');
        } else {
            // In magnifier mode, increase magnifier zoom
            this.magnifierZoom = Math.min(this.magnifierZoom + 0.25, 4.0);
            this.updateDisplay();
            console.log('Magnifier zoom increased to:', this.magnifierZoom + 'x');
        }
    },
    
    /**
     * Zoom out functionality
     */
    zoomOut: function() {
        if (this.zoomMode === 'scale') {
            const newZoom = Math.max(this.currentZoom - this.zoomStep, this.minZoom);
            this.setZoom(newZoom);
            console.log('Zoomed out to:', newZoom + '%');
        } else {
            // In magnifier mode, decrease magnifier zoom
            this.magnifierZoom = Math.max(this.magnifierZoom - 0.25, 1.0);
            this.updateDisplay();
            console.log('Magnifier zoom decreased to:', this.magnifierZoom + 'x');
        }
    },
    
    /**
     * Reset zoom functionality
     */
    resetZoom: function() {
        if (this.zoomMode === 'scale') {
            this.setZoom(100);
            console.log('Zoom reset to: 100%');
        } else {
            this.magnifierZoom = 2.0;
            this.updateDisplay();
            console.log('Magnifier zoom reset to: 2.0x');
        }
    },
    
    /**
     * Get current rotation from HUD.Rotation if available
     */
    getCurrentRotation: function() {
        if (window.HUD && window.HUD.Rotation && typeof window.HUD.Rotation.getCurrentRotation === 'function') {
            return window.HUD.Rotation.getCurrentRotation();
        }
        return 0;
    },
    
    /**
     * Set zoom level for scale mode
     */
    setZoom: function(zoomLevel) {
        this.currentZoom = zoomLevel;
        const preview = document.getElementById(this.previewImageId);
        const container = document.getElementById(this.previewContainerId);
        
        if (preview && container) {
            const rotation = this.getCurrentRotation();
            const scale = zoomLevel / 100;
            
            if (this.zoomMode === 'scale') {
                // Apply combined zoom and rotation transform
                preview.style.transform = `rotate(${rotation}deg) scale(${scale})`;
                
                // Add visual feedback
                container.style.boxShadow = zoomLevel > 100 ? 
                    '0 8px 16px rgba(0, 0, 0, 0.2)' : 
                    '0 4px 8px rgba(0, 0, 0, 0.1)';
            } else {
                // Reset transform in magnifier mode (keep rotation only)
                preview.style.transform = `rotate(${rotation}deg)`;
                container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
            }
            
            // Update displays
            this.updateDisplay();
            
            // Log current state
            console.log('Zoom set to:', zoomLevel + '%', 'Mode:', this.zoomMode, 'Rotation:', rotation + 'deg');
        }
    },
    
    /**
     * Update display elements
     */
    updateDisplay: function() {
        const zoomDisplay = document.getElementById('zoom-display');
        const magnifierDisplay = document.getElementById('magnifier-display');
        
        if (this.zoomMode === 'scale') {
            if (zoomDisplay) zoomDisplay.textContent = this.currentZoom + '%';
        } else {
            if (magnifierDisplay) magnifierDisplay.textContent = this.magnifierZoom.toFixed(1) + 'x';
        }
        
        // Trigger custom event for external listeners
        const event = new CustomEvent('zoomChanged', {
            detail: {
                mode: this.zoomMode,
                scaleZoom: this.currentZoom,
                magnifierZoom: this.magnifierZoom
            }
        });
        document.dispatchEvent(event);
    },
    
    /**
     * Get current zoom level
     */
    getCurrentZoom: function() {
        if (this.zoomMode === 'scale') {
            return this.currentZoom;
        } else {
            return Math.round(this.magnifierZoom * 100);
        }
    },
    
    /**
     * Initialize keyboard shortcuts
     */
    initKeyboardShortcuts: function() {
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + Plus = Zoom In
            if ((event.ctrlKey || event.metaKey) && (event.key === '+' || event.key === '=')) {
                event.preventDefault();
                this.zoomIn();
                return true;
            }
            // Ctrl/Cmd + Minus = Zoom Out
            if ((event.ctrlKey || event.metaKey) && event.key === '-') {
                event.preventDefault();
                this.zoomOut();
                return true;
            }
            // Ctrl/Cmd + 0 = Reset Zoom
            if ((event.ctrlKey || event.metaKey) && event.key === '0') {
                event.preventDefault();
                this.resetZoom();
                return true;
            }
            return false;
        });
    },
    
    /**
     * Initialize mouse wheel zoom
     */
    initMouseWheelZoom: function() {
        const container = document.getElementById(this.previewContainerId);
        if (container) {
            container.addEventListener('wheel', (event) => {
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    if (event.deltaY < 0) {
                        this.zoomIn();
                    } else {
                        this.zoomOut();
                    }
                }
            });
        }
    },
    
    /**
     * Auto-adjust zoom for mobile screens
     * Disabled by default - image should fit using CSS instead of scaling
     */
    autoAdjustMobileZoom: function() {
        // Disabled: Let the image fit using CSS max-width/max-height instead
        // This keeps the image at 100% scale on mobile
        return;
        
        // Keeping this code in case we need it later
        /*
        if (this.zoomMode === 'scale') {
            if (window.innerWidth <= 576) {
                const currentZoom = this.getCurrentZoom();
                if (currentZoom > 75) {
                    console.log('Auto-adjusting zoom for mobile screen');
                    this.setZoom(75);
                }
            } else if (window.innerWidth <= 768) {
                const currentZoom = this.getCurrentZoom();
                if (currentZoom > 90) {
                    console.log('Auto-adjusting zoom for tablet screen');
                    this.setZoom(90);
                }
            }
        }
        */
    },
    
    /**
     * Initialize auto mobile zoom listener
     */
    initAutoMobileZoom: function() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.autoAdjustMobileZoom();
            }, 250); // Debounce resize events
        });
    }
};

// Global function for backward compatibility
window.toggleZoomMode = function() {
    if (window.ZoomManager) {
        window.ZoomManager.toggleZoomMode();
    }
};

// Auto-initialize if HUD namespace exists
if (typeof window.HUD !== 'undefined') {
    window.HUD.Zoom = window.ZoomManager;
}