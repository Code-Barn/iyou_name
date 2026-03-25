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
    let initialized = false;

    // Default settings for reset functionality
    const DEFAULTS = {
        primary_background_color: '#000000',
        primary_stroke_color: '#ffffff',
        primary_font_color: '#ffffff',
        primary_birth_color: '#ffffff',
        primary_birth_place_color: '#ffffff',
        primary_death_color: '#ffffff',
        primary_death_place_color: '#ffffff',
        font_family: 'Arial',
        primary_name_font_size: 84,
        primary_date_info_font_size: 60,
        primary_place_info_font_size: 28,
        default_stroke_width: 0.5,
        primary_stroke_width: 0.5,
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
        if (initialized) {
            console.log('HUD already initialized, skipping...');
            return;
        }
        initialized = true;
        
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

        // Initialize navigation button states
        const templateInput = document.getElementById('template-input');
        const currentGen = parseInt(templateInput ? templateInput.value : '1');
        updateNavButtons(currentGen);

        // Generate initial preview using current form settings
        const userSettings = HUD.Utils.collectUserSettings(new FormData(form));
        HUD.Preview.generatePreview(userSettings).catch(err => {
            console.error('Initial preview generation failed:', err);
        });

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
        console.log('[JS DEBUG] Current template:', HUD.Main.getCurrentTemplate());
        console.log('[JS DEBUG] userSettings keys:', Object.keys(userSettings));
        console.log('[JS DEBUG] primary_background_color in userSettings:', userSettings.primary_background_color);

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
        // Get template value from hidden input (used by arrow navigation)
        const templateInput = document.getElementById('template-input');
        const templateValue = templateInput ? templateInput.value : '1';
        
        console.log("Template changed to:", templateValue);
        
        // Update current template
        HUD.Main.setCurrentTemplate(templateValue);
        
        // ⭐ CRITICAL: Also update the Generate Final Chart form's template field
        // so it's correct even if user doesn't click "Apply Settings"
        let finalChartForm = document.querySelector('form[action*="generate_final_chart"]');
        if (!finalChartForm) {
            finalChartForm = document.querySelector('form[action*="generate"]');
        }
        if (!finalChartForm) {
            finalChartForm = document.querySelector('form');
        }
        if (finalChartForm) {
            const templateField = finalChartForm.querySelector('input[name="template"]');
            if (templateField) {
                templateField.value = templateValue;
                console.log(`Updated form template to: ${templateValue}`);
            }
        }
        
        // Update display text and buttons
        const genNames = {
            1: '1 Generation',
            2: '2 Generation Chart',
            3: '3 Generation Chart',
            4: '4 Generation Chart',
            5: '5 Generation Chart',
            6: '6 Generation Chart',
            7: '7 Generation Chart'
        };
        const display = document.getElementById('current-gen-display');
        if (display) {
            display.textContent = genNames[parseInt(templateValue)] || '1 Generation';
        }
        updateNavButtons(parseInt(templateValue));
        
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
            return response.json();
        })
        .then(data => {
            settingsPanel.innerHTML = data.html;

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

        const currentGen = parseInt(templateValue);
        
        // Get current generation's settings from form
        const form = HUD.Main.getForm();
        const formData = new FormData(form);
        let userSettings = HUD.Utils.collectUserSettings(formData);

        // For 2gen, include stored 1gen settings for the buffer overlay
        if (templateValue === '2') {
            const stored1GenSettings = HUD.Storage.getStored1GenSettings();
            if (stored1GenSettings) {
                // Merge 1gen settings into user_settings (needed for buffer to detect changes)
                Object.assign(userSettings, stored1GenSettings);
                console.log('Merged stored 1gen settings into user_settings for 2gen preview:', stored1GenSettings);
            }
        } else if (templateValue === '3') {
            // Add cumulative settings from previous generations (1gen + 2gen)
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(3);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen) into user_settings for 3gen overlay:', cumulativeSettings);
            }
        } else if (templateValue === '4') {
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(4);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen) into user_settings for 4gen overlay:', cumulativeSettings);
            }
        } else if (templateValue === '5') {
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(5);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen + 4gen) into user_settings for 5gen overlay:', cumulativeSettings);
            }
        } else if (templateValue === '6') {
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(6);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen + 4gen + 5gen) into user_settings for 6gen overlay:', cumulativeSettings);
            }
        } else if (templateValue === '7') {
            const cumulativeSettings = HUD.Storage.getCumulativeSettings(7);
            if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
                Object.assign(userSettings, cumulativeSettings);
                console.log('Merged cumulative settings (1gen + 2gen + 3gen + 4gen + 5gen + 6gen) into user_settings for 7gen overlay:', cumulativeSettings);
            }
        }

        console.log(`Complete ${templateValue}gen request data being sent:`, {
            individual_id: document.querySelector('input[name="individual_id"]').value,
            user_settings: userSettings
        });

        return HUD.Preview.generatePreview(userSettings);
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

        // Name formatting sliders
        setupSlider('name-line-spacing-slider', 'name-line-spacing-value');

        // Stroke width slider
        setupSlider('default-stroke-width-slider', 'default-stroke-width-value');
        setupSlider('primary-stroke-width-slider', 'primary-stroke-width-value');
        setupSlider('primary-info-stroke-width-slider', 'primary-info-stroke-width-value');
        setupSlider('info-stroke-width-slider', 'info-stroke-width-value');

        // Flag size slider
        setupSlider('place-flag-size-slider', 'place-flag-size-value');

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

        // 2X Great-Grandparent font size sliders
        setupSlider('twox-greatgrandparent-name-font-size-slider', 'twox-greatgrandparent-name-font-size-value');
        setupSlider('twox-greatgrandparent-date-info-font-size-slider', 'twox-greatgrandparent-date-info-font-size-value');
        setupSlider('twox-greatgrandparent-place-info-font-size-slider', 'twox-greatgrandparent-place-info-font-size-value');

        // 2X Great-Grandparent position sliders
        setupSlider('twox-greatgrandparent-edge-distance-slider', 'twox-greatgrandparent-edge-distance-value');
        setupSlider('twox-greatgrandparent-date-distance-slider', 'twox-greatgrandparent-date-distance-value');
        setupSlider('twox-greatgrandparent-place-distance-slider', 'twox-greatgrandparent-place-distance-value');
        setupSlider('twox-greatgrandparent-translate-x-slider', 'twox-greatgrandparent-translate-x-value');
        setupSlider('twox-greatgrandparent-birth-translate-y-slider', 'twox-greatgrandparent-birth-translate-y-value');
        setupSlider('twox-greatgrandparent-name-rotate-slider', 'twox-greatgrandparent-name-rotate-value');

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

        // First, handle checkboxes explicitly - include all checkbox settings
        const checkboxes = document.querySelectorAll('#hud-settings-form input[type="checkbox"]');
        console.log(`Found ${checkboxes.length} checkboxes in form`);
        checkboxes.forEach(checkbox => {
            // Include checkboxes that start with 'place_' OR are specific named checkboxes
            if (checkbox.name && (checkbox.name.startsWith('place_') || checkbox.name === 'use_outside_stroke')) {
                userSettings[checkbox.name] = checkbox.checked;
                console.log(`Checkbox ${checkbox.name}: ${checkbox.checked}`);
            }
        });

        // Iterate through all formData entries and collect them
        for (const [key, value] of formData.entries()) {
            if (key === 'csrfmiddlewaretoken' || key === 'individual_id' || key === 'template' || key === 'generations') {
                continue; // Skip non-settings fields
            }

            // Include all other fields (place_ fields are included since checkboxes were handled above)

            // Convert numeric values appropriately
            if (value !== null && value !== '') {
                if (key.includes('font_size') || key.includes('translate') || key.includes('rotate') || key.includes('flag_size')) {
                    userSettings[key] = parseInt(value) || 0;
                } else if (key.includes('stroke_width')) {
                    userSettings[key] = parseFloat(value) || 0.5;
                } else {
                    userSettings[key] = value;
                }
            }
        }

        console.log('Collected all form settings:', userSettings);
        console.log('use_outside_stroke value:', userSettings.use_outside_stroke);
        return userSettings;
    }

    function updateFinalChartForm(userSettings, cumulativeSettings = null) {
        try {
            console.log('=== FORM UPDATE DEBUG ===');

            // Use cumulative settings if provided, otherwise use current settings
            const settingsToUpdate = cumulativeSettings || userSettings;
            console.log('Updating final chart form with settings:', settingsToUpdate);
            console.log('use_outside_stroke in settings:', settingsToUpdate.use_outside_stroke);
            console.log('place_year_only in settings:', settingsToUpdate.place_year_only);

            let finalChartForm = document.querySelector('form[action*="generate_final_chart"]');
            if (!finalChartForm) {
                finalChartForm = document.querySelector('form[action*="generate"]');
            }
            if (!finalChartForm) {
                finalChartForm = document.querySelector('form');
            }

            if (finalChartForm) {
                console.log('Found form:', finalChartForm);
                
                // Update the template field to match current generation
                const currentGen = HUD.Main.getCurrentTemplate();
                const templateInput = finalChartForm.querySelector('input[name="template"]');
                if (templateInput) {
                    console.log(`Updating template: ${templateInput.value} -> ${currentGen}`);
                    templateInput.value = currentGen;
                } else {
                    // Create template input if it doesn't exist
                    const newInput = document.createElement('input');
                    newInput.type = 'hidden';
                    newInput.name = 'template';
                    newInput.value = currentGen;
                    finalChartForm.appendChild(newInput);
                    console.log(`Created template input: ${currentGen}`);
                }

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
                // Handle checkboxes specially
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else {
                    input.value = value;
                }
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

// Initialize when DOM is ready (guard in init() prevents duplicates)
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM ready, initializing HUD...');
    HUD.Main.init();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState !== 'loading') {
    HUD.Main.init();
}

// Make functions available globally for onclick handlers
window.saveAndApplySettings = HUD.Settings.saveAndApplySettings;
window.handleTemplateChange = HUD.Templates.handleTemplateChange;
window.navigateGeneration = navigateGeneration;

// Navigation function for sequential generation selection
function navigateGeneration(direction) {
    const templateInput = document.getElementById('template-input');
    const currentGen = parseInt(templateInput.value) || 1;
    const newGen = currentGen + direction;
    
    if (newGen >= 1 && newGen <= 7) {
        templateInput.value = newGen;
        
        // Update display text
        const display = document.getElementById('current-gen-display');
        const genNames = {
            1: '1 Generation',
            2: '2 Generation Chart',
            3: '3 Generation Chart',
            4: '4 Generation Chart',
            5: '5 Generation Chart',
            6: '6 Generation Chart',
            7: '7 Generation Chart'
        };
        display.textContent = genNames[newGen];
        
        // Update button states
        updateNavButtons(newGen);
        
        // Trigger template change
        window.handleTemplateChange();
    }
}

function updateNavButtons(gen) {
    const prevBtn = document.getElementById('prev-gen-btn');
    const nextBtn = document.getElementById('next-gen-btn');
    
    if (prevBtn) {
        prevBtn.disabled = (gen <= 1);
        prevBtn.classList.toggle('disabled', (gen <= 1));
    }
    if (nextBtn) {
        nextBtn.disabled = (gen >= 7);
        nextBtn.classList.toggle('disabled', (gen >= 7));
    }
}
window.resetToDefaults = HUD.Settings.resetToDefaults;

// ============================================================================
// PresetManager - Handles saving/loading presets and individual settings
// ============================================================================

HUD.PresetManager = (function() {
    'use strict';

    function getCSRFToken() {
        const token = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return token ? token.value : '';
    }

    function getGedcomHash() {
        // Get from session or generate from filename
        const fileInput = document.querySelector('input[name="gedcom_file_id"]');
        if (fileInput) {
            return fileInput.value;
        }
        // Fallback: try to get from URL or generate a simple hash
        return 'default';
    }

    return {
        // --- Preset Management ---

        savePreset(name, description = '') {
            const currentGen = HUD.Main.getCurrentTemplate();
            const settings = HUD.Storage.getCumulativeSettings(parseInt(currentGen));
            
            return fetch('/storage/presets/create/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    settings_json: settings
                })
            }).then(r => r.json());
        },

        loadPreset(presetId) {
            return fetch(`/storage/presets/${presetId}/`)
                .then(r => r.json())
                .then(preset => {
                    if (preset.settings_json) {
                        const currentGen = HUD.Main.getCurrentTemplate();
                        HUD.Storage.storeGenerationSettings(
                            parseInt(currentGen),
                            preset.settings_json
                        );
                        HUD.Utils.updateFormWithStoredSettings(preset.settings_json);
                        HUD.Templates.updatePreviewImage(currentGen);
                    }
                    return preset;
                });
        },

        listPresets() {
            return fetch('/storage/presets/')
                .then(r => r.json());
        },

        deletePreset(presetId) {
            return fetch(`/storage/presets/${presetId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            }).then(r => r.json());
        },

        setDefaultPreset(presetId) {
            return fetch(`/storage/presets/${presetId}/set-default/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                }
            }).then(r => r.json());
        },

        // --- Individual Settings ---

        saveIndividualSettings(gedcomHash, individualId, individualName, settings) {
            return fetch('/storage/individual-settings/save/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gedcom_hash: gedcomHash,
                    individual_id: individualId,
                    individual_name: individualName,
                    settings_json: settings
                })
            }).then(r => r.json());
        },

        getIndividualSettings(gedcomHash, individualId) {
            return fetch(`/storage/individual-settings/${gedcomHash}/${individualId}/`)
                .then(r => r.json());
        },

        setHomePerson(gedcomHash, individualId, individualName) {
            return fetch('/storage/home-person/set/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gedcom_hash: gedcomHash,
                    individual_id: individualId,
                    individual_name: individualName
                })
            }).then(r => r.json());
        },

        getHomePerson(gedcomHash) {
            return fetch(`/storage/home-person/${gedcomHash}/`)
                .then(r => r.json());
        },

        // --- Storage Management ---

        getStorageUsage() {
            return fetch('/storage/storage/usage/')
                .then(r => r.json());
        },

        clearAllBuffers() {
            if (!confirm('This will delete all cached charts. You will need to regenerate them. Continue?')) {
                return Promise.resolve({ cancelled: true });
            }
            
            return fetch('/storage/storage/clear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            }).then(r => r.json());
        },

        // --- Auto-load settings for individual ---

        loadSettingsForIndividual(gedcomHash, individualId, individualName) {
            // First try individual-specific settings
            return this.getIndividualSettings(gedcomHash, individualId)
                .then(data => {
                    if (data.settings_json) {
                        console.log('Loaded individual settings for', individualName);
                        const currentGen = HUD.Main.getCurrentTemplate();
                        HUD.Storage.storeGenerationSettings(
                            parseInt(currentGen),
                            data.settings_json
                        );
                        HUD.Utils.updateFormWithStoredSettings(data.settings_json);
                        return data;
                    }
                    
                    // Fall back to home person settings
                    return this.getHomePerson(gedcomHash)
                        .then(homeData => {
                            if (homeData.settings_json) {
                                console.log('Loaded home person settings for', individualName);
                                const currentGen = HUD.Main.getCurrentTemplate();
                                HUD.Storage.storeGenerationSettings(
                                    parseInt(currentGen),
                                    homeData.settings_json
                                );
                                HUD.Utils.updateFormWithStoredSettings(homeData.settings_json);
                            }
                            return homeData;
                        });
                });
        },

        // --- UI Helpers ---

        showSavePresetDialog() {
            const name = prompt('Enter preset name:');
            if (!name) return Promise.resolve(null);
            
            const description = prompt('Enter description (optional):') || '';
            
            return this.savePreset(name, description);
        },

        showLoadPresetDropdown(presets) {
            // This would typically populate a dropdown menu
            // For now, just log the presets
            console.log('Available presets:', presets);
        }
    };
})();

// Expose for global use
window.HUD = HUD;
