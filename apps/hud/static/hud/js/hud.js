// Family Tree Generator - Interactive HUD System
// Real-time preview and customization interface

class FamilyTreeHUD {
    constructor() {
        this.initialized = false;
        this.currentIndividual = null;
        this.currentTemplate = '4';
        this.chartParameters = {};
        this.previewMode = false;
        this.eventListeners = [];
    }

    init() {
        if (this.initialized) return;
        
        console.log('Initializing Family Tree HUD...');
        
        // Create HUD container
        this.createHUDContainer();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        this.loadInitialData();
        
        this.initialized = true;
        console.log('Family Tree HUD initialized successfully');
    }

    createHUDContainer() {
        // Create main HUD container
        this.hudContainer = document.createElement('div');
        this.hudContainer.id = 'family-tree-hud';
        this.hudContainer.className = 'hud-container';
        
        // HUD HTML structure
        this.hudContainer.innerHTML = `
            <div class="hud-header">
                <h3>Interactive Preview</h3>
                <div class="hud-controls">
                    <button id="hud-toggle" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-eye"></i> Toggle Preview
                    </button>
                    <button id="hud-reset" class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-arrow-counterclockwise"></i> Reset
                    </button>
                </div>
            </div>
            <div class="hud-content">
                <div class="hud-preview-area">
                    <div id="hud-canvas-container" class="canvas-container">
                        <canvas id="hud-canvas"></canvas>
                    </div>
                </div>
                <div class="hud-settings">
                    <div class="setting-group">
                        <label>Primary Individual</label>
                        <select id="hud-individual-select" class="form-select form-select-sm"></select>
                    </div>
                    <div class="setting-group">
                        <label>Generations</label>
                        <select id="hud-generations" class="form-select form-select-sm">
                            <option value="1">1 Generation</option>
                            <option value="4" selected>4 Generations</option>
                            <option value="10">10 Generations</option>
                        </select>
                    </div>
                    <div class="setting-group">
                        <label>Template</label>
                        <select id="hud-template" class="form-select form-select-sm">
                            <option value="1">Individual Only</option>
                            <option value="4" selected>4-Gen Chart</option>
                            <option value="10">Extended Chart</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="hud-footer">
                <button id="hud-generate" class="btn btn-primary btn-sm">
                    <i class="bi bi-file-earmark-pdf"></i> Generate Final Chart
                </button>
                <div class="hud-status">Ready</div>
            </div>
        `;
        
        // Add to document body
        document.body.appendChild(this.hudContainer);
        
        // Initialize canvas
        this.initCanvas();
    }

    initCanvas() {
        this.canvas = document.getElementById('hud-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Set initial canvas size
        this.resizeCanvas();
        
        // Add window resize listener
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        const container = document.getElementById('hud-canvas-container');
        if (container) {
            this.canvas.width = container.clientWidth;
            this.canvas.height = container.clientHeight;
            
            // Redraw if in preview mode
            if (this.previewMode) {
                this.drawPreview();
            }
        }
    }

    setupEventListeners() {
        // Toggle preview button
        document.getElementById('hud-toggle').addEventListener('click', () => {
            this.togglePreview();
        });

        // Reset button
        document.getElementById('hud-reset').addEventListener('click', () => {
            this.resetSettings();
        });

        // Generate final chart button
        document.getElementById('hud-generate').addEventListener('click', () => {
            this.generateFinalChart();
        });

        // Individual selection change
        document.getElementById('hud-individual-select').addEventListener('change', (e) => {
            this.onIndividualChange(e.target.value);
        });

        // Template change
        document.getElementById('hud-template').addEventListener('change', (e) => {
            this.onTemplateChange(e.target.value);
        });

        // Generations change
        document.getElementById('hud-generations').addEventListener('change', (e) => {
            this.onGenerationsChange(e.target.value);
        });
    }

    loadInitialData() {
        // Fetch initial data from Django backend
        this.fetchFamilyData();
        
        // Load current session data
        this.loadSessionData();
    }

    async fetchFamilyData() {
        try {
            const response = await fetch('/generator/api/family-data/');
            if (response.ok) {
                const data = await response.json();
                this.populateIndividualSelect(data.individuals);
                
                // If we have session data, use it
                if (this.currentIndividual) {
                    this.updatePreview();
                }
            }
        } catch (error) {
            console.error('Error fetching family data:', error);
            this.showStatus('Error loading data', 'error');
        }
    }

    populateIndividualSelect(individuals) {
        const select = document.getElementById('hud-individual-select');
        select.innerHTML = '';
        
        individuals.forEach(ind => {
            const option = document.createElement('option');
            option.value = ind.id;
            option.textContent = `${ind.full_name} (${ind.birth_date || 'Unknown'})`;
            
            if (ind.id === this.currentIndividual) {
                option.selected = true;
            }
            
            select.appendChild(option);
        });
    }

    loadSessionData() {
        // Load from session storage or Django session
        const sessionData = JSON.parse(sessionStorage.getItem('hudSession') || '{}');
        
        if (sessionData.individualId) {
            this.currentIndividual = sessionData.individualId;
        }
        
        if (sessionData.template) {
            this.currentTemplate = sessionData.template;
            document.getElementById('hud-template').value = sessionData.template;
        }
        
        if (sessionData.generations) {
            document.getElementById('hud-generations').value = sessionData.generations;
        }
    }

    saveSessionData() {
        const sessionData = {
            individualId: this.currentIndividual,
            template: this.currentTemplate,
            generations: document.getElementById('hud-generations').value,
            parameters: this.chartParameters
        };
        
        sessionStorage.setItem('hudSession', JSON.stringify(sessionData));
    }

    togglePreview() {
        this.previewMode = !this.previewMode;
        
        if (this.previewMode) {
            this.updatePreview();
            this.showStatus('Preview mode enabled', 'success');
        } else {
            this.clearCanvas();
            this.showStatus('Preview mode disabled', 'info');
        }
    }

    updatePreview() {
        if (!this.currentIndividual) {
            this.showStatus('Please select an individual', 'warning');
            return;
        }

        this.showStatus('Generating preview...', 'info');
        this.previewMode = true;
        
        // Fetch preview data
        this.fetchPreviewData();
    }

    async fetchPreviewData() {
        try {
            const response = await fetch(`/generator/api/preview/?
                individual_id=${this.currentIndividual}
                &template=${this.currentTemplate}
                &generations=${document.getElementById('hud-generations').value}
            `);
            
            if (response.ok) {
                const previewData = await response.json();
                this.drawPreview(previewData);
                this.showStatus('Preview ready', 'success');
            }
        } catch (error) {
            console.error('Error fetching preview:', error);
            this.showStatus('Preview error', 'error');
        }
    }

    drawPreview(previewData) {
        // Clear canvas
        this.clearCanvas();
        
        // Set up drawing context
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw preview based on data
        this.drawFamilyTree(previewData);
    }

    drawFamilyTree(data) {
        // Simplified drawing for preview
        // In a real implementation, this would draw the actual tree structure
        
        this.ctx.fillStyle = '#343a40';
        this.ctx.font = '14px Arial';
        
        // Draw primary individual
        if (data.primary) {
            this.ctx.fillText(`Primary: ${data.primary.name}`, 20, 30);
            this.ctx.fillText(`Born: ${data.primary.birth_date || 'Unknown'}`, 20, 50);
        }
        
        // Draw generations info
        this.ctx.fillText(`Generations: ${data.generations}`, 20, 80);
        this.ctx.fillText(`Template: ${data.template_name}`, 20, 100);
        
        // Draw family members count
        this.ctx.fillText(`Family Members: ${data.family_count || 0}`, 20, 130);
        
        // Draw a simple tree structure
        this.drawSimpleTreeStructure();
    }

    drawSimpleTreeStructure() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        // Draw primary individual box
        this.ctx.strokeStyle = '#0d6efd';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(centerX - 50, centerY - 20, 100, 40);
        
        // Draw connecting lines
        this.ctx.beginPath();
        this.ctx.moveTo(centerX, centerY + 20);
        this.ctx.lineTo(centerX - 80, centerY + 60);
        this.ctx.lineTo(centerX + 80, centerY + 60);
        this.ctx.stroke();
        
        // Draw parent boxes
        this.ctx.strokeRect(centerX - 100, centerY + 60, 60, 40);
        this.ctx.strokeRect(centerX + 40, centerY + 60, 60, 40);
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    showStatus(message, type = 'info') {
        const statusElement = document.querySelector('.hud-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = 'hud-status hud-status-' + type;
        }
    }

    onIndividualChange(individualId) {
        this.currentIndividual = individualId;
        this.saveSessionData();
        
        if (this.previewMode) {
            this.updatePreview();
        }
    }

    onTemplateChange(templateId) {
        this.currentTemplate = templateId;
        this.saveSessionData();
        
        if (this.previewMode) {
            this.updatePreview();
        }
    }

    onGenerationsChange(generations) {
        this.saveSessionData();
        
        if (this.previewMode) {
            this.updatePreview();
        }
    }

    resetSettings() {
        // Reset to default values
        this.currentIndividual = null;
        this.currentTemplate = '4';
        this.chartParameters = {};
        
        // Reset UI
        document.getElementById('hud-template').value = '4';
        document.getElementById('hud-generations').value = '4';
        
        // Clear preview
        this.clearCanvas();
        this.showStatus('Settings reset', 'info');
        
        // Save reset state
        this.saveSessionData();
    }

    generateFinalChart() {
        if (!this.currentIndividual) {
            this.showStatus('Please select an individual first', 'warning');
            return;
        }

        // Create form and submit to generate final chart
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/generator/generate/';
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            form.appendChild(csrfToken.cloneNode(true));
        }
        
        // Add parameters
        const individualInput = document.createElement('input');
        individualInput.type = 'hidden';
        individualInput.name = 'individual_id';
        individualInput.value = this.currentIndividual;
        form.appendChild(individualInput);
        
        const templateInput = document.createElement('input');
        templateInput.type = 'hidden';
        templateInput.name = 'template';
        templateInput.value = this.currentTemplate;
        form.appendChild(templateInput);
        
        const generationsInput = document.createElement('input');
        generationsInput.type = 'hidden';
        generationsInput.name = 'generations';
        generationsInput.value = document.getElementById('hud-generations').value;
        form.appendChild(generationsInput);
        
        // Submit form
        document.body.appendChild(form);
        form.submit();
    }

    // Utility methods
    addEventListener(event, callback) {
        this.eventListeners.push({event, callback});
    }

    removeEventListener(event, callback) {
        this.eventListeners = this.eventListeners.filter(
            listener => listener.event !== event || listener.callback !== callback
        );
    }

    destroy() {
        // Clean up event listeners
        this.eventListeners.forEach(listener => {
            // Remove listeners would go here
        });
        
        // Remove HUD from DOM
        if (this.hudContainer && this.hudContainer.parentNode) {
            this.hudContainer.parentNode.removeChild(this.hudContainer);
        }
        
        this.initialized = false;
    }
}

// Initialize HUD when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we should initialize HUD
    const shouldInitHUD = true; // Could be based on URL, user preference, etc.
    
    if (shouldInitHUD) {
        window.familyTreeHUD = new FamilyTreeHUD();
        window.familyTreeHUD.init();
    }
});
