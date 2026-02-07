// AI Health Coach - Main JavaScript

class HealthCoach {
    constructor() {
        this.translations = window.translations || {};
        this.currentLanguage = window.currentLanguage || 'English';
        this.selectedImage = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.calculateDailyTarget();
    }

    setupEventListeners() {
        // Language selector
        const languageSelect = document.getElementById('language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }

        // Profile form changes
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            const inputs = profileForm.querySelectorAll('input, select');
            inputs.forEach(input => {
                // Listen for both 'input' and 'change' events
                input.addEventListener('input', () => {
                    this.calculateDailyTarget();
                });
                input.addEventListener('change', () => {
                    this.calculateDailyTarget();
                });
            });
        }

        // Image upload
        const imageUpload = document.getElementById('image-upload');
        if (imageUpload) {
            imageUpload.addEventListener('change', (e) => {
                this.handleImageUpload(e);
            });
        }

        // Drag and drop
        const uploadArea = document.querySelector('[for="image-upload"]');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.processImageFile(files[0]);
                }
            });
        }

        // Analyze button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.analyzeImage();
            });
        }
    }

    changeLanguage(language) {
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.set('lang', language);
        window.location.href = currentUrl.toString();
    }

    async calculateDailyTarget() {
        try {
            const formData = new FormData(document.getElementById('profile-form'));
            formData.append('language', this.currentLanguage);

            // Debug: Log form data being sent
            console.log('Daily target calculation - form data:');
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
            }

            const response = await fetch('/update_profile', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Daily target response:', data);
                if (data.success) {
                    const targetElement = document.getElementById('daily-target');
                    if (targetElement) {
                        targetElement.textContent = `${data.daily_target}`;
                    }
                }
            }
        } catch (error) {
            console.error('Error calculating daily target:', error);
        }
    }

    handleImageUpload(event) {
        const file = event.target.files[0];
        if (file) {
            this.processImageFile(file);
        }
    }

    processImageFile(file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            this.showToast('Please upload a valid image file (JPG, JPEG, or PNG)', 'error');
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            this.showToast('File size must be less than 10MB', 'error');
            return;
        }

        this.selectedImage = file;
        this.displayImagePreview(file);
        this.enableAnalyzeButton();
    }

    displayImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const uploadArea = document.getElementById('upload-area');
            const imagePreview = document.getElementById('image-preview');
            const previewImg = document.getElementById('preview-img');

            if (uploadArea && imagePreview && previewImg) {
                uploadArea.classList.add('hidden');
                imagePreview.classList.remove('hidden');
                previewImg.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
    }

    enableAnalyzeButton() {
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
        }
    }

    async analyzeImage() {
        if (!this.selectedImage) {
            this.showToast('Please upload an image first', 'warning');
            return;
        }

        this.showLoading(true);
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
        }

        try {
            const formData = new FormData(document.getElementById('profile-form'));
            formData.append('image', this.selectedImage);
            formData.append('language', this.currentLanguage);

            // Debug: Log form data
            console.log('Form data being sent:');
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
            }

            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data.result);
                this.showToast('Analysis completed successfully!', 'success');
            } else {
                if (data.error === 'RATE_LIMIT') {
                    this.showToast(data.message, 'warning');
                    // Optionally disable button for the wait time
                    if (data.wait_time) {
                        setTimeout(() => {
                            analyzeBtn.disabled = false;
                        }, data.wait_time * 1000);
                    }
                } else {
                    this.showToast(data.message || 'Analysis failed', 'error');
                    analyzeBtn.disabled = false;
                }
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showToast('An error occurred during analysis', 'error');
            const analyzeBtn = document.getElementById('analyze-btn');
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
            }
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(result) {
        // Show results section
        const resultsSection = document.getElementById('results-section');
        if (resultsSection) {
            resultsSection.classList.remove('hidden');
            resultsSection.classList.add('fade-in-up');
        }

        // Update meal impact
        this.updateMealImpact(result);

        // Update metrics
        this.updateMetrics(result);

        // Update macronutrients
        this.updateMacronutrients(result);

        // Update burn off times
        this.updateBurnOffTimes(result);

        // Update AI feedback
        this.updateAIFeedback(result);

        // Scroll to results
        resultsSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    updateMealImpact(result) {
        const impactPercentage = document.getElementById('impact-percentage');
        const progressBar = document.getElementById('progress-bar');
        const impactMessage = document.getElementById('impact-message').querySelector('p');

        if (impactPercentage) {
            impactPercentage.textContent = `${result.meal_impact_pct}%`;
        }

        if (progressBar) {
            progressBar.style.width = `${result.progress_ratio * 100}%`;
            progressBar.classList.add('progress-fill');
        }

        if (impactMessage) {
            impactMessage.textContent = this.translations.impact_msg.replace('{pct}', result.meal_impact_pct);
        }
    }

    updateMetrics(result) {
        // Calories
        const caloriesDisplay = document.getElementById('calories-display');
        if (caloriesDisplay) {
            caloriesDisplay.textContent = `${result.total_calories} kcal`;
        }

        // Health Score
        const healthScoreDisplay = document.getElementById('health-score-display');
        if (healthScoreDisplay) {
            healthScoreDisplay.textContent = `${result.health_score}/10`;
            // Update color based on score
            healthScoreDisplay.className = 'text-3xl font-bold ';
            if (result.health_score >= 8) {
                healthScoreDisplay.classList.add('health-score-excellent');
            } else if (result.health_score >= 5) {
                healthScoreDisplay.classList.add('health-score-good');
            } else {
                healthScoreDisplay.classList.add('health-score-poor');
            }
        }

        // Diet Compliance
        const complianceIcon = document.getElementById('compliance-icon');
        const complianceText = document.getElementById('compliance-text');

        if (complianceIcon && complianceText) {
            if (result.is_diet_compliant) {
                complianceIcon.innerHTML = '✅';
                complianceText.textContent = this.translations.compliant;
                complianceText.className = 'text-sm font-medium text-green-600';
            } else {
                complianceIcon.innerHTML = '⚠️';
                complianceText.textContent = this.translations.non_compliant;
                complianceText.className = 'text-sm font-medium text-red-600';
            }
        }
    }

    updateMacronutrients(result) {
        const proteinDisplay = document.getElementById('protein-display');
        const fatDisplay = document.getElementById('fat-display');
        const carbsDisplay = document.getElementById('carbs-display');

        if (proteinDisplay) proteinDisplay.textContent = result.macros.protein;
        if (fatDisplay) fatDisplay.textContent = result.macros.fat;
        if (carbsDisplay) carbsDisplay.textContent = result.macros.carbs;
    }

    updateBurnOffTimes(result) {
        const walkTime = document.getElementById('walk-time');
        const runTime = document.getElementById('run-time');
        const swimTime = document.getElementById('swim-time');

        if (walkTime) walkTime.textContent = result.burn_off.walking;
        if (runTime) runTime.textContent = result.burn_off.running;
        if (swimTime) swimTime.textContent = result.burn_off.swimming;
    }

    updateAIFeedback(result) {
        // Food items
        const foodItemsContainer = document.getElementById('food-items');
        if (foodItemsContainer && result.food_items) {
            foodItemsContainer.innerHTML = '';
            result.food_items.forEach(item => {
                const tag = document.createElement('span');
                tag.className = 'food-tag';
                tag.textContent = item;
                foodItemsContainer.appendChild(tag);
            });
        }

        // Analysis text
        const analysisText = document.getElementById('analysis-text');
        if (analysisText) {
            analysisText.textContent = result.analysis;
        }

        // Suggestion text
        const suggestionText = document.getElementById('suggestion-text');
        if (suggestionText) {
            suggestionText.textContent = result.suggestion;
        }
    }

    showLoading(show) {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            if (show) {
                loadingOverlay.classList.remove('hidden');
            } else {
                loadingOverlay.classList.add('hidden');
            }
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toast-message');
        const toastIcon = document.getElementById('toast-icon');

        if (!toast || !toastMessage || !toastIcon) return;

        // Set message
        toastMessage.textContent = message;

        // Set icon and style based on type
        toastIcon.className = 'flex-shrink-0 mr-3';
        const toastContainer = toast.querySelector('div');

        switch (type) {
            case 'success':
                toastIcon.innerHTML = '<i class="fas fa-check-circle text-green-500"></i>';
                toastContainer.className = 'bg-white rounded-lg shadow-lg p-4 max-w-sm border-l-4 border-green-500';
                break;
            case 'error':
                toastIcon.innerHTML = '<i class="fas fa-exclamation-circle text-red-500"></i>';
                toastContainer.className = 'bg-white rounded-lg shadow-lg p-4 max-w-sm border-l-4 border-red-500';
                break;
            case 'warning':
                toastIcon.innerHTML = '<i class="fas fa-exclamation-triangle text-yellow-500"></i>';
                toastContainer.className = 'bg-white rounded-lg shadow-lg p-4 max-w-sm border-l-4 border-yellow-500';
                break;
            default:
                toastIcon.innerHTML = '<i class="fas fa-info-circle text-blue-500"></i>';
                toastContainer.className = 'bg-white rounded-lg shadow-lg p-4 max-w-sm border-l-4 border-blue-500';
        }

        // Show toast
        toast.classList.remove('translate-x-full');

        // Hide after 3 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HealthCoach();
});

// Export for potential use in other scripts
window.HealthCoach = HealthCoach;
