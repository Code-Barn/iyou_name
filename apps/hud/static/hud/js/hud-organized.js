/**
 * HUD Interactive Family Tree - Main JavaScript Module
 * Organized, clean structure for all interactive functionality
 */

// Global namespace for HUD functionality
window.HUD = window.HUD || {};

// Main HUD module
HUD.Main = (function() {
    'use strict';

    // Private variables
    let currentTemplate = '1';
    let form = null;
    let previewImg = null;

    // Default settings for reset functionality
    const DEFAULTS = {
        primary_background_color: '#FFFFFF',
        primary_stroke_color: '#000000',
        primary_font_color: '#000000',
        primary_birth_color: '#000000',
        primary_birth_place_color: '#000000',
        primary_death_color: '#000000',
        primary_death_place_color: '#000000',
        font_family: 'Arial',
        primary_name_font_size: 84,
        primary_date_info_font_size: 60,
        primary_place_info_font_size: 28,
        default_stroke_width: 0.5,
        primary_translate_x: 0,
        primary_translate_y: 0,
        primary_name_rotate: -45,
        primary_birth_translate_x: 0,
        primary_birth_translate_y: 0,
        primary_birth_rotate: -90,
        primary_birth_place_translate_x: 0,
        primary_birth_place_translate_y: 0,
        primary_birth_place_rotate: 0,
        primary_death_translate_x: 0,
        primary_death_translate_y: 0,
        primary_death_rotate: 0,
        primary_death_place_translate_x: 0,
        primary_death_place_translate_y: 0,
        primary_death_place_rotate: -90,
        spacing: 0
    };

    // Private methods
    function init() {
        console.log('HUD JavaScript module initializing...');

        // Get DOM elements
        form = document.getElementById('hud-settings-form');
        previewImg = document.getElementById('hud-preview');

        // Initialize event listeners
        initEventListeners();

        // Initialize sliders
        HUD.Sliders.initializeAll();

        // Initialize rotation display
        HUD.Rotation.resetOnNewPreview();

        console.log('HUD JavaScript module initialized successfully');
    }

    function initEventListeners() {
        // Template change listener
        const templateSelect = document.getElementById('template-select');
        if (templateSelect) {
            templateSelect.addEventListener('change', HUD.Templates.handleTemplateChange);
        }

        // Apply settings button
        const applyButton = document.getElementById('apply-settings');
        if (applyButton) {
            applyButton.addEventListener('click', HUD.Settings.saveAndApplySettings);
        }

        // Reset button
        const resetButton = document.querySelector('button[onclick*="resetToDefaults"]');
        if (resetButton) {
            resetButton.addEventListener('click', function(e) {
                e.preventDefault();
                HUD.Settings.resetToDefaults();
            });
        }
    }

    // Public API
    return {
        init: init,
        getCurrentTemplate: () => currentTemplate,
        setCurrentTemplate: (template) => { currentTemplate = template; },
        getForm: () => form,
        getPreviewImg: () => previewImg,
        getDefaults: () => DEFAULTS
    };
})();

// Settings management module
HUD.Settings = (function() {
    'use strict';

    // Public methods
    function saveAndApplySettings() {
        console.log('=== saveAndApplySettings called ===');

        try {
            // Ensure all form inputs have current values
            HUD.Utils.updateAllFormInputs();

            const form = HUD.Main.getForm();
            if (!form) {
                console.error('Form not found');
                return;
            }

            const formData = new FormData(form);

            // Collect user settings
            const userSettings = HUD.Utils.collectUserSettings(formData);

            console.log('User settings collected:', userSettings);

            // Store current generation settings for cumulative inheritance
            const currentTemplate = HUD.Main.getCurrentTemplate();
            if (currentTemplate === '1') {
                HUD.Storage.store1GenSettings(userSettings);
                console.log('Stored 1gen settings for future 2gen overlay:', userSettings);
            } else {
                HUD.Storage.storeGenerationSettings(currentTemplate, userSettings);
                console.log(`Stored ${currentTemplate}gen settings for cumulative inheritance:`, userSettings);
            }

            // Update final chart form with cumulative settings for PDF generation
            if (currentTemplate === '1') {
                // For 1gen, use current settings
                HUD.Utils.updateFinalChartForm(userSettings);
            } else {
                // For 2gen+, get cumulative settings and update form
                const cumulativeSettings = HUD.Storage.getCumulativeSettings(parseInt(currentTemplate));
                if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                    // Merge current settings with cumulative settings (current takes precedence)
                    const finalSettings = Object.assign({}, cumulativeSettings, userSettings);
                    console.log(`Updating final chart form with cumulative settings for template ${currentTemplate}:`, finalSettings);
                    HUD.Utils.updateFinalChartForm(finalSettings, cumulativeSettings);
                } else {
                    console.log(`No cumulative settings found for template ${currentTemplate}, using current settings for final chart form`);
                    HUD.Utils.updateFinalChartForm(userSettings);
                }
            }

            // Generate preview
            HUD.Preview.generatePreview(userSettings)
                .then(() => {
                    // Save to session after preview (non-critical)
                    return HUD.Session.saveSettings(formData);
                })
                .then(() => {
                    console.log('Settings applied and preview updated successfully');
                })
                .catch(error => {
                    console.error('Error in saveAndApplySettings:', error);
                });

        } catch (error) {
            console.error('Critical error in saveAndApplySettings:', error);
            alert('ERROR: Failed to apply settings. Check console for details.');
        }
    }

    function resetToDefaults() {
        console.log('=== resetToDefaults called ===');

        const defaults = HUD.Main.getDefaults();
        const form = HUD.Main.getForm();

        if (!form) {
            console.error('Form not found for reset');
            return;
        }

        // Reset color inputs
        const colorInputs = form.querySelectorAll('input[type="color"]');
        colorInputs.forEach(input => {
            const settingName = input.name;
            if (defaults[settingName] !== undefined) {
                input.value = defaults[settingName];
            }
        });

        // Reset select inputs
        const selectInputs = form.querySelectorAll('select');
        selectInputs.forEach(input => {
            const settingName = input.name;
            if (defaults[settingName] !== undefined) {
                input.value = defaults[settingName];
            }
        });

        // Reset range inputs
        const rangeInputs = form.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => {
            const settingName = input.name;
            if (defaults[settingName] !== undefined) {
                input.value = defaults[settingName];
                // Update display value
                const displayId = input.id.replace('-slider', '-value');
                const displaySpan = document.getElementById(displayId);
                if (displaySpan) {
                    displaySpan.textContent = defaults[settingName];
                }
            }
        });

        console.log('Settings reset to defaults');

        // Update final chart form
        HUD.Utils.updateFinalChartForm(defaults);
    }

    // Public API
    return {
        saveAndApplySettings: saveAndApplySettings,
        resetToDefaults: resetToDefaults
    };
})();

// Preview management module
HUD.Preview = (function() {
    'use strict';

    function generatePreview(userSettings) {
        console.log('=== generatePreview called ===');

        const currentTemplate = HUD.Main.getCurrentTemplate();
        const previewImg = HUD.Main.getPreviewImg();

        if (!previewImg) {
            console.error('Preview image element not found');
            return Promise.reject('Preview element not found');
        }

        // Build request data
        let requestData = {
            individual_id: document.querySelector('input[name="individual_id"]').value,
            user_settings: userSettings
        };

        // Note: Template-specific settings merging is now handled by updatePreviewImage()
        // This function just makes the API call with the provided settings

        // Generate preview
        const previewUrl = `/hud/get-template-preview/${currentTemplate}/`;

        return fetch(previewUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to generate preview: ' + response.status);
            }
            return response.blob();
        })
        .then(blob => {
            // Revoke any existing object URL to prevent memory leaks
            if (previewImg.dataset.currentUrl) {
                URL.revokeObjectURL(previewImg.dataset.currentUrl);
            }

            // Create object URL and set it
            const previewUrl = URL.createObjectURL(blob);
            previewImg.src = previewUrl;
            previewImg.dataset.currentUrl = previewUrl;

            console.log('Preview image loaded successfully');

            // Add error handler
            previewImg.onerror = function() {
                console.error('Failed to load preview image');
                URL.revokeObjectURL(previewUrl);
            };

            // Add load handler
            previewImg.onload = function() {
                console.log('Preview image displayed successfully');
                URL.revokeObjectURL(previewUrl);
                // Reset rotation when new preview loads
                HUD.Rotation.resetOnNewPreview();
            };

            // Add visual feedback
            previewImg.style.border = '5px solid #00FF00';
            setTimeout(() => {
                previewImg.style.border = '';
            }, 1000);
        });
    }

    // Public API
    return {
        generatePreview: generatePreview
    };
})();

// Session management module
HUD.Session = (function() {
    'use strict';

    function saveSettings(formData) {
        console.log('=== saveSettings called ===');

        // Make session save non-critical - don't let failures break the flow
        fetch('/hud/save-settings/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                console.log('Session save failed (non-critical) - settings still work via localStorage');
                return null;
            }
            return response.json();
        })
        .then(saveResponse => {
            if (saveResponse) {
                console.log('Settings saved to session:', saveResponse);
            } else {
                console.log('Session save returned null (non-critical)');
            }
        })
        .catch(error => {
            console.log('Session save error (non-critical) - settings still work via localStorage:', error.message);
        });

        // Always return resolved promise since session save is non-critical
        return Promise.resolve();
    }

    function loadSettingsFromSession() {
        console.log('=== Loading settings from session ===');

        return fetch('/hud/get-settings/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => {
            if (!response.ok) {
                console.warn('Failed to load settings from session');
                return null;
            }
            return response.json();
        })
        .then(sessionData => {
            if (sessionData && sessionData.hud_settings) {
                console.log('Loaded settings from session:', sessionData.hud_settings);
                return sessionData.hud_settings;
            }
            console.log('No settings found in session');
            return null;
        })
        .catch(error => {
            console.warn('Error loading settings from session:', error);
            return null;
        });
    }

    // Public API
    return {
        saveSettings: saveSettings,
        loadSettingsFromSession: loadSettingsFromSession
    };
})();

// Storage management module (localStorage)
HUD.Storage = (function() {
    'use strict';

    function getStored1GenSettings() {
        const storedSettings = localStorage.getItem('hud_1gen_settings');
        if (storedSettings) {
            console.log('Loading stored 1gen settings for 2gen inheritance');
            return JSON.parse(storedSettings);
        }
        return null;
    }

    function store1GenSettings(settings) {
        localStorage.setItem('hud_1gen_settings', JSON.stringify(settings));
        console.log('Stored 1gen settings for inheritance:', settings);
    }

    function storeGenerationSettings(generation, settings) {
        const key = `hud_${generation}gen_settings`;
        localStorage.setItem(key, JSON.stringify(settings));
        console.log(`Stored ${generation}gen settings for inheritance:`, settings);
    }

    function getStoredGenerationSettings(generation) {
        const key = `hud_${generation}gen_settings`;
        const stored = localStorage.getItem(key);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error(`Failed to parse stored ${generation}gen settings:`, e);
                return null;
            }
        }
        return null;
    }

    function getCumulativeSettings(currentGeneration) {
        const cumulativeSettings = {};

        // Merge all previous generation settings INCLUDING current generation
        for (let gen = 1; gen <= currentGeneration; gen++) {
            const genSettings = getStoredGenerationSettings(gen);
            if (genSettings) {
                console.log(`Retrieved ${gen}gen settings:`, genSettings);
                Object.assign(cumulativeSettings, genSettings);
            } else {
                console.log(`No stored settings found for generation ${gen}`);
            }
        }

        console.log(`Final cumulative settings for generation ${currentGeneration}:`, cumulativeSettings);
        console.log(`Cumulative settings keys:`, Object.keys(cumulativeSettings));
        return cumulativeSettings;
    }

    // Public API
    return {
        getStored1GenSettings: getStored1GenSettings,
        store1GenSettings: store1GenSettings,
        storeGenerationSettings: storeGenerationSettings,
        getStoredGenerationSettings: getStoredGenerationSettings,
        getCumulativeSettings: getCumulativeSettings
    };
})();

// Template management module
HUD.Templates = (function() {
    'use strict';

function handleTemplateChange() {
        const templateSelect = document.getElementById('template-select');
        const templateValue = templateSelect.value;
        
        console.log("Template changed to:", templateValue);
        
        // Update current template
        HUD.Main.setCurrentTemplate(templateValue);
        
        // Update hidden template input
        const hiddenTemplateInput = document.querySelector('input[name="template"]');
        if (hiddenTemplateInput) {
            hiddenTemplateInput.value = templateValue;
        }
        
        console.log("Updated current template");
        
        // ⭐ KEY FIX: Wait for settings panel to finish loading before generating preview
        loadSettingsPanel(templateValue).then(() => {
            // ⭐ Load cumulative settings first, then generate preview
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(parseInt(templateValue));
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                console.log('Cumulative settings calculated, updating form...');
                HUD.Utils.updateFormWithStoredSettings(cumulativeSettings);
            } else {
                console.log('No cumulative settings found, using current form only');
            }
            
            // Then generate preview with the updated form using the comprehensive function
            return HUD.Templates.updatePreviewImage(templateValue);
        }).catch(error => {
            console.error('Error in template change handling:', error);
        });
    }
    function loadSettingsPanel(templateValue) {
        const settingsPanel = document.getElementById('settings-panel');
        if (!settingsPanel) {
            console.error('Settings panel not found');
            return Promise.resolve();
        }

        // Show loading indicator
        settingsPanel.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading settings for template ${templateValue}...</p>
            </div>
        `;

        // Map template values to settings files
        const settingsTemplateMap = {
            '1': '1gen_settings.html',
            '2': '2gen_settings.html',
            '3': '3gen_settings.html',
            '4': '4gen_settings.html',
            '5': '5gen_settings.html',
            '6': '6gen_settings.html',
            '7': '7gen_settings.html',
        };

        const settingsFile = settingsTemplateMap[templateValue] || 'default_settings.html';

        // Fetch the appropriate settings template
        return fetch(`/hud/get-settings-panel/${settingsFile}/?template=${templateValue}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load settings panel');
            }
            return response.text();
        })
        .then(html => {
            settingsPanel.innerHTML = html;

            // Reinitialize sliders for the new settings panel
            HUD.Sliders.initializeAll();

            // Load appropriate settings based on template
            if (templateValue === '2') {
                const stored1GenSettings = HUD.Storage.getStored1GenSettings();
                if (stored1GenSettings) {
                    console.log('Loading stored 1gen settings into 2gen form:', stored1GenSettings);
                    HUD.Utils.updateFormWithStoredSettings(stored1GenSettings);
                }
            } else if (templateValue === '1') {
                // Load current 1gen settings from localStorage if available
                const stored1GenSettings = HUD.Storage.getStored1GenSettings();
                if (stored1GenSettings) {
                    console.log('Loading stored 1gen settings back into 1gen form:', stored1GenSettings);
                    HUD.Utils.updateFormWithStoredSettings(stored1GenSettings);
                }
            }

            console.log(`Loaded settings panel for template ${templateValue}`);
        })
        .catch(error => {
            console.error('Error loading settings panel:', error);
            settingsPanel.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <strong>Error:</strong> Failed to load settings for template ${templateValue}
                    <br><small>${error.message}</small>
                </div>
            `;
        });
    }

    function updatePreviewImage(templateValue) {
        const previewImg = HUD.Main.getPreviewImg();
        if (!previewImg) {
            console.error('Preview image element not found');
            return;
        }

        // For template 2, we need to send stored 1gen settings via POST
        if (templateValue === '2') {
            console.log('Template 2 selected - generating preview with stored 1gen settings');

            // Collect current form settings (for 2gen-specific fields)
            const form = HUD.Main.getForm();
            const formData = new FormData(form);
            const userSettings = HUD.Utils.collectUserSettings(formData);

            // Add stored 1gen settings for overlay
            const stored1GenSettings = HUD.Storage.getStored1GenSettings();
            if (stored1GenSettings) {
                // Merge 1gen settings into user_settings (not as separate object)
                Object.assign(userSettings, stored1GenSettings);
                console.log('Merged stored 1gen settings into user_settings for 2gen preview:', stored1GenSettings);
                console.log('Complete request data being sent:', {
                    individual_id: document.querySelector('input[name="individual_id"]').value,
                    user_settings: userSettings
                });
            } else {
                console.log('No stored 1gen settings found for 2gen preview');
            }

            // Generate 2gen preview with POST
            return HUD.Preview.generatePreview(userSettings);
        } else if (templateValue === '3') {
            console.log('Template 3 selected - generating preview with cumulative settings (1gen + 2gen)');

            // Collect current form settings (for 3gen-specific fields)
            const form = HUD.Main.getForm();
            const formData = new FormData(form);
            const userSettings = HUD.Utils.collectUserSettings(formData);

            // Add cumulative settings from previous generations (1gen + 2gen)
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(3);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                // Merge cumulative settings into user_settings
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen) into user_settings for 3gen overlay:', cumulativeSettings);
            } else {
                console.log('No cumulative settings found for 3gen preview, using current form settings only');
            }

            console.log('Complete 3gen request data being sent:', {
                individual_id: document.querySelector('input[name="individual_id"]').value,
                user_settings: userSettings
            });

            // Generate 3gen preview with POST
            return HUD.Preview.generatePreview(userSettings);
        } else if (templateValue === '4') {
            console.log('Template 4 selected - generating preview with cumulative settings (1gen + 2gen + 3gen)');

            // Collect current form settings (for 4gen-specific fields)
            const form = HUD.Main.getForm();
            const formData = new FormData(form);
            const userSettings = HUD.Utils.collectUserSettings(formData);

            // Add cumulative settings from previous generations (1gen + 2gen + 3gen)
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(4);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                // Merge cumulative settings into user_settings
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen) into user_settings for 4gen overlay:', cumulativeSettings);
            } else {
                console.log('No cumulative settings found for 4gen preview, using current form settings only');
            }

            console.log('Complete 4gen request data being sent:', {
                individual_id: document.querySelector('input[name="individual_id"]').value,
                user_settings: userSettings
            });

            // Generate 4gen preview with POST
            return HUD.Preview.generatePreview(userSettings);
        } else if (templateValue === '5') {
            console.log('Template 5 selected - generating preview with cumulative settings (1gen + 2gen + 3gen + 4gen)');

            // Collect current form settings (for 5gen-specific fields)
            const form = HUD.Main.getForm();
            const formData = new FormData(form);
            const userSettings = HUD.Utils.collectUserSettings(formData);

            // Add cumulative settings from previous generations (1gen + 2gen + 3gen + 4gen)
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(5);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                // Merge cumulative settings into user_settings
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen + 4gen) into user_settings for 5gen overlay:', cumulativeSettings);
            } else {
                console.log('No cumulative settings found for 5gen preview, using current form settings only');
            }

            console.log('Complete 5gen request data being sent:', {
                individual_id: document.querySelector('input[name="individual_id"]').value,
                user_settings: userSettings
            });

            // Generate 5gen preview with POST
            return HUD.Preview.generatePreview(userSettings);
        } else if (templateValue === '6') {
            console.log('Template 6 selected - generating preview with cumulative settings (1gen + 2gen + 3gen + 4gen + 5gen)');

            // Collect current form settings (for 6gen-specific fields)
            const form = HUD.Main.getForm();
            const formData = new FormData(form);
            const userSettings = HUD.Utils.collectUserSettings(formData);

            // Add cumulative settings from previous generations (1gen + 2gen + 3gen + 4gen + 5gen)
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(6);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                // Merge cumulative settings into user_settings
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen + 4gen + 5gen) into user_settings for 6gen overlay:', cumulativeSettings);
            } else {
                console.log('No cumulative settings found for 6gen preview, using current form settings only');
            }

            console.log('Complete 6gen request data being sent:', {
                individual_id: document.querySelector('input[name="individual_id"]').value,
                user_settings: userSettings
            });

            // Generate 6gen preview with POST
            return HUD.Preview.generatePreview(userSettings);
        } else if (templateValue === '7') {
            console.log('Template 7 selected - generating preview with cumulative settings (1gen + 2gen + 3gen + 4gen + 5gen + 6gen)');

            // Collect current form settings (for 7gen-specific fields)
            const form = HUD.Main.getForm();
            const formData = new FormData(form);
            const userSettings = HUD.Utils.collectUserSettings(formData);

            // Add cumulative settings from previous generations (1gen + 2gen + 3gen + 4gen + 5gen + 6gen)
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(7);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                // Merge cumulative settings into user_settings
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen + 4gen + 5gen + 6gen) into user_settings for 7gen overlay:', cumulativeSettings);
            } else {
                console.log('No cumulative settings found for 7gen preview, using current form settings only');
            }

            console.log('Complete 7gen request data being sent:', {
                individual_id: document.querySelector('input[name="individual_id"]').value,
                user_settings: userSettings
            });

            // Generate 7gen preview with POST
            return HUD.Preview.generatePreview(userSettings);
        } else {
            // Handle unknown template values
            console.warn(`Unknown template value: ${templateValue}`);
            return;
        }
    }

    // Public API
    return {
        handleTemplateChange: handleTemplateChange,
        loadSettingsPanel: loadSettingsPanel,
        updatePreviewImage: updatePreviewImage
    };
})();

// Slider management module
HUD.Sliders = (function() {
    'use strict';

    function setupSlider(sliderId, valueId) {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueId);

        if (slider && valueDisplay) {
            slider.addEventListener('input', function() {
                valueDisplay.textContent = this.value;
                console.log(`Slider ${sliderId} changed to: ${this.value}`);
                this.setAttribute('value', this.value);
            });
        }
    }

    function initializeAll() {
        console.log('Initializing all sliders...');

        // Font size sliders
        setupSlider('primary-name-font-size-slider', 'primary-name-font-size-value');
        setupSlider('primary-date-info-font-size-slider', 'primary-date-info-font-size-value');
        setupSlider('primary-place-info-font-size-slider', 'primary-place-info-font-size-value');

        // Stroke width slider
        setupSlider('default-stroke-width-slider', 'default-stroke-width-value');

        // Primary individual coordinates sliders
        setupSlider('primary-translate-x-slider', 'primary-translate-x-value');
        setupSlider('primary-translate-y-slider', 'primary-translate-y-value');
        setupSlider('primary-name-rotate-slider', 'primary-name-rotate-value');

        // Birth date sliders
        setupSlider('primary-birth-translate-x-slider', 'primary-birth-translate-x-value');
        setupSlider('primary-birth-translate-y-slider', 'primary-birth-translate-y-value');
        setupSlider('primary-birth-rotate-slider', 'primary-birth-rotate-value');

        // Birth place sliders
        setupSlider('primary-birth-place-translate-x-slider', 'primary-birth-place-translate-x-value');
        setupSlider('primary-birth-place-translate-y-slider', 'primary-birth-place-translate-y-value');
        setupSlider('primary-birth-place-rotate-slider', 'primary-birth-place-rotate-value');

        // Death date sliders
        setupSlider('primary-death-translate-x-slider', 'primary-death-translate-x-value');
        setupSlider('primary-death-translate-y-slider', 'primary-death-translate-y-value');
        setupSlider('primary-death-rotate-slider', 'primary-death-rotate-value');

        // Death place sliders
        setupSlider('primary-death-place-translate-x-slider', 'primary-death-place-translate-x-value');
        setupSlider('primary-death-place-translate-y-slider', 'primary-death-place-translate-y-value');
        setupSlider('primary-death-place-rotate-slider', 'primary-death-place-rotate-value');

        // 2gen specific sliders (if present)
        setupSlider('parent-father-name-font-size-slider', 'parent-father-name-font-size-value');
        setupSlider('parent-mother-name-font-size-slider', 'parent-mother-name-font-size-value');
        setupSlider('parent-date-info-font-size-slider', 'parent-date-info-font-size-value');
        setupSlider('parent-place-info-font-size-slider', 'parent-place-info-font-size-value');

        // Composite settings sliders
        setupSlider('composite-1gen-scale-slider', 'composite-1gen-scale-value');
        setupSlider('composite-overlay-x-slider', 'composite-overlay-x-value');
        setupSlider('composite-overlay-y-slider', 'composite-overlay-y-value');

        console.log('All sliders initialized');
    }

    // Public API
    return {
        setupSlider: setupSlider,
        initializeAll: initializeAll
    };
})();

// Rotation management module
HUD.Rotation = (function() {
    'use strict';

    let currentRotation = 0;
    const ROTATION_STEP = 45; // degrees per rotation

    function rotateClockwise() {
        currentRotation += ROTATION_STEP;
        updateRotation();
    }

    function rotateCounterClockwise() {
        currentRotation -= ROTATION_STEP;
        updateRotation();
    }

    function resetRotation() {
        currentRotation = 0;
        updateRotation();
    }

    function getCurrentZoom() {
        if (window.ZoomManager && typeof window.ZoomManager.getCurrentZoom === 'function') {
            return window.ZoomManager.getCurrentZoom();
        }
        return 100;
    }
    
    function updateRotation() {
        const previewImg = HUD.Main.getPreviewImg();
        if (!previewImg) {
            console.error('Preview image not found for rotation');
            return;
        }

        // Normalize rotation to 0-360 range
        let normalizedRotation = currentRotation % 360;
        if (normalizedRotation < 0) {
            normalizedRotation += 360;
        }

        // Get current zoom level to preserve it
        const zoomLevel = getCurrentZoom();
        const scale = zoomLevel / 100;
        
        // Apply combined rotation and zoom transform
        previewImg.style.transform = `rotate(${currentRotation}deg) scale(${scale})`;

        // Update display
        const rotationDisplay = document.getElementById('rotation-display');
        if (rotationDisplay) {
            rotationDisplay.textContent = `${normalizedRotation}°`;
        }

        console.log(`Rotated preview to ${currentRotation}° (normalized: ${normalizedRotation}°) with zoom ${zoomLevel}%`);
    }

    function getCurrentRotation() {
        return currentRotation;
    }

    // Reset rotation when new preview is loaded
    function resetOnNewPreview() {
        currentRotation = 0;
        updateRotation();
    }

    // Public API
    return {
        rotateClockwise: rotateClockwise,
        rotateCounterClockwise: rotateCounterClockwise,
        resetRotation: resetRotation,
        getCurrentRotation: getCurrentRotation,
        resetOnNewPreview: resetOnNewPreview
    };
})();

// Utility functions module
HUD.Utils = (function() {
    'use strict';

    function updateAllFormInputs() {
        console.log("Updating all form inputs to ensure current values...");

        const form = HUD.Main.getForm();
        if (!form) {
            console.error('Form not found');
            return;
        }

        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'range' || input.type === 'text' || input.type === 'color' || input.tagName === 'SELECT') {
                if (input.type === 'range') {
                    input.setAttribute('value', input.value);
                }
            }
        });

        console.log("Form inputs updated.");
    }

    function collectUserSettings(formData) {
        // Convert FormData to a simple object with all form fields
        const userSettings = {};

        // Iterate through all formData entries and collect them
        for (const [key, value] of formData.entries()) {
            if (key === 'csrfmiddlewaretoken' || key === 'individual_id' || key === 'template' || key === 'generations') {
                continue; // Skip non-settings fields
            }

            // Convert numeric values appropriately
            if (value !== null && value !== '') {
                if (key.includes('font_size') || key.includes('translate') || key.includes('rotate')) {
                    userSettings[key] = parseInt(value) || 0;
                } else if (key.includes('stroke_width')) {
                    userSettings[key] = parseFloat(value) || 0.5;
                } else {
                    userSettings[key] = value;
                }
            }
        }

        console.log('Collected all form settings:', userSettings);
        return userSettings;
    }

    function updateFinalChartForm(userSettings, cumulativeSettings = null) {
        try {
            console.log('=== FORM UPDATE DEBUG ===');

            // Use cumulative settings if provided, otherwise use current settings
            const settingsToUpdate = cumulativeSettings || userSettings;
            console.log('Updating final chart form with settings:', settingsToUpdate);

            let finalChartForm = document.querySelector('form[action*="generate_final_chart"]');
            if (!finalChartForm) {
                finalChartForm = document.querySelector('form[action*="generate"]');
            }
            if (!finalChartForm) {
                finalChartForm = document.querySelector('form');
            }

            if (finalChartForm) {
                console.log('Found form:', finalChartForm);

                let updatedCount = 0;
                for (const [key, value] of Object.entries(settingsToUpdate)) {
                    const input = finalChartForm.querySelector(`input[name="${key}"]`);
                    if (input) {
                        console.log(`Updating ${key}: ${input.value} -> ${value}`);
                        input.value = value;
                        updatedCount++;
                    } else {
                        // If input doesn't exist, create it dynamically
                        const newInput = document.createElement('input');
                        newInput.type = 'hidden';
                        newInput.name = key;
                        newInput.value = value;
                        finalChartForm.appendChild(newInput);
                        console.log(`Created new hidden input for ${key}: ${value}`);
                        updatedCount++;
                    }
                }
                console.log(`Successfully updated ${updatedCount} settings in final chart form`);
            } else {
                console.error('CRITICAL: Could not find final chart form to update');
            }
        } catch (error) {
            console.error('ERROR in form update:', error);
        }
    }

    function updateFormWithStoredSettings(storedSettings) {
        console.log('Updating form with stored 1gen settings:', storedSettings);

        const form = HUD.Main.getForm();
        if (!form) {
            console.error('Form not found for stored settings update');
            return;
        }

        // Update all matching form inputs with stored values
        for (const [key, value] of Object.entries(storedSettings)) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = value;
                console.log(`Updated ${key} with stored value: ${value}`);

                // If it's a slider, also update the display value
                if (input.type === 'range') {
                    const valueDisplayId = input.id.replace('-slider', '-value');
                    const displaySpan = document.getElementById(valueDisplayId);
                    if (displaySpan) {
                        displaySpan.textContent = value;
                    }
                }
            }
        }
    }

    // Public API
    return {
        updateAllFormInputs: updateAllFormInputs,
        collectUserSettings: collectUserSettings,
        updateFinalChartForm: updateFinalChartForm,
        updateFormWithStoredSettings: updateFormWithStoredSettings
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM ready, initializing HUD...');
    HUD.Main.init();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', HUD.Main.init);
} else {
    HUD.Main.init();
}

// Make functions available globally for onclick handlers
window.saveAndApplySettings = HUD.Settings.saveAndApplySettings;
window.handleTemplateChange = HUD.Templates.handleTemplateChange;
window.resetToDefaults = HUD.Settings.resetToDefaults;
