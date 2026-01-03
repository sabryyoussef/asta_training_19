/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";
import publicWidget from "@web/legacy/js/public/public_widget";

/**
 * Application Wizard Widget - Phase 1 Enhancement
 * Multi-step form with validation, progress tracking, and auto-save
 */
publicWidget.registry.ApplicationWizard = publicWidget.Widget.extend({
    selector: '.admission-wizard',
    events: {
        'click .btn-wizard-next': '_onNext',
        'click .btn-wizard-prev': '_onPrevious',
        'click .review-edit-btn': '_onEditStep',
        'click .btn-wizard-submit': '_onSubmit',
        'submit form': '_onFormSubmit',
        'change input, select, textarea': '_onFieldChange',
        'blur input[name="email"]': '_onEmailBlur',
        'blur input[name="mobile"]': '_onPhoneBlur',
        'blur input[name="phone"]': '_onPhoneBlur',
        'blur input[name="birth_date"]': '_onBirthDateBlur',
    },

    /**
     * Initialize the wizard
     */
    start: function () {
        this._super.apply(this, arguments);
        
        this.currentStep = 1;
        this.totalSteps = 5;
        this.formData = {};
        this.validationCache = {};
        
        // Load saved draft if exists
        this._loadDraft();
        
        // Setup auto-save interval (every 30 seconds)
        this.autoSaveInterval = setInterval(() => {
            this._autoSave();
        }, 30000);
        
        // Show first step
        this._showStep(1);
        this._updateProgress();
        
        // Setup validation for all fields
        this._setupFieldValidation();
    },

    /**
     * Cleanup when widget is destroyed
     */
    destroy: function () {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        this._super.apply(this, arguments);
    },

    /**
     * Show specific step
     */
    _showStep: function (stepNumber) {
        // Hide all steps
        this.$('.wizard-step').removeClass('active');
        
        // Show target step
        this.$('.wizard-step[data-step="' + stepNumber + '"]').addClass('active');
        
        // Update step indicators
        this.$('.step').removeClass('active completed');
        this.$('.step').each((index, step) => {
            const stepNum = index + 1;
            if (stepNum < stepNumber) {
                $(step).addClass('completed');
            } else if (stepNum === stepNumber) {
                $(step).addClass('active');
            }
        });
        
        // Update navigation buttons
        this.$('.btn-wizard-prev').toggle(stepNumber > 1);
        this.$('.btn-wizard-next').toggle(stepNumber < this.totalSteps);
        this.$('.btn-wizard-submit').toggle(stepNumber === this.totalSteps);
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        this.currentStep = stepNumber;
        this._updateProgress();
    },

    /**
     * Update progress bar
     */
    _updateProgress: function () {
        const progress = (this.currentStep / this.totalSteps) * 100;
        this.$('.progress-fill').css('width', progress + '%');
    },

    /**
     * Navigate to next step
     */
    _onNext: function (ev) {
        ev.preventDefault();
        
        if (this._validateCurrentStep()) {
            this._collectStepData();
            this._showStep(this.currentStep + 1);
            this._autoSave();
            
            // Populate review step if moving to step 5
            if (this.currentStep === 5) {
                this._populateReview();
            }
        } else {
            this._showValidationSummary();
        }
    },

    /**
     * Navigate to previous step
     */
    _onPrevious: function (ev) {
        ev.preventDefault();
        this._collectStepData();
        this._showStep(this.currentStep - 1);
    },

    /**
     * Edit specific step from review
     */
    _onEditStep: function (ev) {
        ev.preventDefault();
        const stepNumber = parseInt($(ev.currentTarget).data('step'));
        this._showStep(stepNumber);
    },

    /**
     * Handle submit button click
     */
    _onSubmit: function (ev) {
        ev.preventDefault();
        
        // Collect all form data from all steps before submission
        this._collectAllStepData();
        
        // Validate all steps before submitting
        let allValid = true;
        for (let step = 1; step <= this.totalSteps; step++) {
            this._showStep(step);
            if (!this._validateCurrentStep()) {
                allValid = false;
                this._showValidationSummary();
                // Go back to review step to show errors
                this._showStep(this.totalSteps);
                return;
            }
        }
        
        // If all valid, populate form and submit
        if (allValid) {
            this._populateFormFields();
            // Show loading state
            const $submitBtn = this.$('.btn-wizard-submit');
            $submitBtn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Submitting...');
            // Submit the form
            this.$el.find('form')[0].submit();
        }
    },

    /**
     * Handle form submit event (fallback)
     */
    _onFormSubmit: function (ev) {
        // Collect all data from all steps one final time
        this._collectAllStepData();
        this._populateFormFields();
        
        // Allow form to submit normally
        return true;
    },

    /**
     * Collect data from all steps, not just current one
     */
    _collectAllStepData: function () {
        const currentStep = this.currentStep;
        
        // Collect data from each step
        for (let step = 1; step <= this.totalSteps; step++) {
            this._showStep(step);
            this._collectStepData();
        }
        
        // Restore to original step
        this._showStep(currentStep);
    },

    /**
     * Populate all form fields with collected data
     */
    _populateFormFields: function () {
        const self = this;
        Object.keys(this.formData).forEach(function(key) {
            const $field = self.$('[name="' + key + '"]');
            if ($field.length) {
                if ($field.is('select')) {
                    $field.val(self.formData[key]);
                } else if ($field.is('input[type="checkbox"]')) {
                    $field.prop('checked', self.formData[key] === true || self.formData[key] === 'true');
                } else {
                    $field.val(self.formData[key]);
                }
            }
        });
    },

    /**
     * Validate current step
     */
    _validateCurrentStep: function () {
        const $currentStep = this.$('.wizard-step.active');
        const $fields = $currentStep.find('input, select, textarea').filter(':visible');
        let isValid = true;
        
        $fields.each((index, field) => {
            const $field = $(field);
            
            // Check required fields
            if ($field.prop('required') && !$field.val()) {
                this._showFieldError($field, 'This field is required');
                isValid = false;
                return;
            }
            
            // Check custom validity
            if (field.validity && !field.validity.valid) {
                this._showFieldError($field, field.validationMessage);
                isValid = false;
            } else {
                this._clearFieldError($field);
            }
        });
        
        return isValid;
    },

    /**
     * Show validation summary at top of step
     */
    _showValidationSummary: function () {
        const $summary = this.$('.wizard-step.active .step-validation-summary');
        const $invalidFields = this.$('.wizard-step.active .form-control.is-invalid');
        
        if ($invalidFields.length > 0) {
            let errorHtml = '<strong>Please fix the following errors:</strong><ul>';
            $invalidFields.each((index, field) => {
                const label = $('label[for="' + field.id + '"]').text().replace('*', '').trim();
                errorHtml += '<li>' + label + '</li>';
            });
            errorHtml += '</ul>';
            
            $summary.html(errorHtml).addClass('show');
            
            // Scroll to first error
            $invalidFields.first()[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            $invalidFields.first().focus();
        }
    },

    /**
     * Collect data from current step
     */
    _collectStepData: function () {
        const $currentStep = this.$('.wizard-step.active');
        const $fields = $currentStep.find('input, select, textarea');
        
        $fields.each((index, field) => {
            const $field = $(field);
            const name = $field.attr('name');
            
            if (name && name !== 'csrf_token') {
                if ($field.attr('type') === 'checkbox') {
                    this.formData[name] = $field.is(':checked');
                } else if ($field.attr('type') === 'file') {
                    // Handle file separately
                    if (field.files && field.files[0]) {
                        this.formData[name + '_name'] = field.files[0].name;
                    }
                } else {
                    this.formData[name] = $field.val();
                }
            }
        });
    },

    /**
     * Setup field validation
     */
    _setupFieldValidation: function () {
        // Add required indicators
        this.$('input[required], select[required], textarea[required]').each((index, field) => {
            const $label = $('label[for="' + field.id + '"]');
            if ($label.length && !$label.hasClass('required')) {
                $label.addClass('required');
            }
        });
    },

    /**
     * Field change handler
     */
    _onFieldChange: function (ev) {
        const $field = $(ev.currentTarget);
        
        // Clear validation summary when user starts fixing errors
        this.$('.step-validation-summary').removeClass('show');
        
        // Trigger field-specific validation
        if ($field.val()) {
            this._validateField($field);
        }
    },

    /**
     * Email validation with duplicate check
     */
    _onEmailBlur: async function (ev) {
        const $field = $(ev.currentTarget);
        const email = $field.val();
        
        if (!email) return;
        
        // Format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this._showFieldError($field, 'Please enter a valid email address');
            return;
        }
        
        // Show loading
        $field.addClass('validation-loading');
        
        try {
            // Check for duplicates
            const result = await jsonrpc('/admission/check-email', {
                email: email
            });
            
            $field.removeClass('validation-loading');
            
            if (result.exists) {
                this._showFieldWarning($field, 'This email already has an application. You can submit another if needed.');
            } else {
                this._showFieldSuccess($field, 'Email is available');
            }
        } catch (error) {
            $field.removeClass('validation-loading');
            console.error('Email validation error:', error);
        }
    },

    /**
     * Phone validation
     */
    _onPhoneBlur: function (ev) {
        const $field = $(ev.currentTarget);
        const phone = $field.val();
        
        if (!phone) return;
        
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        if (!phoneRegex.test(phone)) {
            this._showFieldError($field, 'Please enter a valid phone number');
        } else if (phone.length < 10) {
            this._showFieldError($field, 'Phone number must be at least 10 digits');
        } else {
            this._showFieldSuccess($field, 'Phone number is valid');
        }
    },

    /**
     * Birth date validation
     */
    _onBirthDateBlur: function (ev) {
        const $field = $(ev.currentTarget);
        const birthDate = new Date($field.val());
        const today = new Date();
        
        if (!$field.val()) return;
        
        if (birthDate >= today) {
            this._showFieldError($field, 'Birth date must be in the past');
        } else {
            // Check minimum age (16 years)
            const age = Math.floor((today - birthDate) / (365.25 * 24 * 60 * 60 * 1000));
            if (age < 16) {
                this._showFieldError($field, 'Applicant must be at least 16 years old');
            } else {
                this._showFieldSuccess($field, 'Age verified');
            }
        }
    },

    /**
     * Generic field validation
     */
    _validateField: function ($field) {
        if ($field[0].validity && $field[0].validity.valid) {
            this._showFieldSuccess($field, '');
        }
    },

    /**
     * Show field error
     */
    _showFieldError: function ($field, message) {
        $field.removeClass('is-valid is-warning').addClass('is-invalid shake');
        
        // Remove shake class after animation
        setTimeout(() => $field.removeClass('shake'), 500);
        
        // Update or create error message
        let $feedback = $field.siblings('.invalid-feedback');
        if ($feedback.length === 0) {
            $feedback = $('<div class="invalid-feedback validation-message"></div>');
            $field.after($feedback);
        }
        $feedback.text(message);
        
        $field[0].setCustomValidity(message);
    },

    /**
     * Show field success
     */
    _showFieldSuccess: function ($field, message) {
        $field.removeClass('is-invalid is-warning').addClass('is-valid');
        $field[0].setCustomValidity('');
        
        if (message) {
            let $feedback = $field.siblings('.valid-feedback');
            if ($feedback.length === 0) {
                $feedback = $('<div class="valid-feedback validation-message"></div>');
                $field.after($feedback);
            }
            $feedback.text(message);
        }
    },

    /**
     * Show field warning
     */
    _showFieldWarning: function ($field, message) {
        $field.removeClass('is-invalid is-valid').addClass('is-warning');
        $field[0].setCustomValidity('');
        
        let $feedback = $field.siblings('.warning-feedback');
        if ($feedback.length === 0) {
            $feedback = $('<div class="warning-feedback validation-message"></div>');
            $field.after($feedback);
        }
        $feedback.text(message);
    },

    /**
     * Clear field validation state
     */
    _clearFieldError: function ($field) {
        $field.removeClass('is-invalid is-valid is-warning');
        $field.siblings('.invalid-feedback, .valid-feedback, .warning-feedback').remove();
        $field[0].setCustomValidity('');
    },

    /**
     * Auto-save draft to localStorage and backend
     */
    _autoSave: function () {
        this._collectStepData();
        
        const $indicator = this.$('.autosave-indicator');
        $indicator.removeClass('saved').addClass('saving');
        $indicator.html('<span class="spinner"></span> Saving draft...');
        
        // Save to localStorage
        localStorage.setItem('admission_draft', JSON.stringify({
            currentStep: this.currentStep,
            formData: this.formData,
            timestamp: new Date().toISOString()
        }));
        
        // Save to backend session
        jsonrpc('/admission/save-draft', this.formData).then((result) => {
            $indicator.removeClass('saving').addClass('saved');
            $indicator.html('<i class="fa fa-check-circle"></i> Draft saved');
            
            setTimeout(() => {
                $indicator.removeClass('saved');
                $indicator.text('');
            }, 3000);
        }).catch((error) => {
            console.error('Auto-save error:', error);
            $indicator.removeClass('saving');
            $indicator.html('<i class="fa fa-exclamation-triangle"></i> Save failed');
        });
    },

    /**
     * Load draft from localStorage
     */
    _loadDraft: function () {
        const draftJson = localStorage.getItem('admission_draft');
        
        if (!draftJson) return;
        
        try {
            const draft = JSON.parse(draftJson);
            this.formData = draft.formData || {};
            
            // Restore field values
            Object.keys(this.formData).forEach((name) => {
                const $field = this.$('[name="' + name + '"]');
                if ($field.length) {
                    if ($field.attr('type') === 'checkbox') {
                        $field.prop('checked', this.formData[name]);
                    } else if ($field.attr('type') !== 'file') {
                        $field.val(this.formData[name]);
                    }
                }
            });
            
            // Show notification
            const timestamp = new Date(draft.timestamp);
            const timeAgo = this._getTimeAgo(timestamp);
            
            if (confirm('We found a saved draft from ' + timeAgo + '. Would you like to continue where you left off?')) {
                this._showStep(draft.currentStep || 1);
            } else {
                localStorage.removeItem('admission_draft');
            }
        } catch (error) {
            console.error('Error loading draft:', error);
            localStorage.removeItem('admission_draft');
        }
    },

    /**
     * Get human-readable time ago
     */
    _getTimeAgo: function (date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return Math.floor(seconds / 60) + ' minutes ago';
        if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
        return Math.floor(seconds / 86400) + ' days ago';
    },

    /**
     * Populate review step with summary
     */
    _populateReview: function () {
        this._collectStepData();
        
        // Personal Information
        const fullName = [this.formData.first_name, this.formData.middle_name, this.formData.last_name]
            .filter(n => n).join(' ');
        this._setReviewField('review-full-name', fullName);
        this._setReviewField('review-email', this.formData.email);
        this._setReviewField('review-mobile', this.formData.mobile);
        this._setReviewField('review-birth-date', this.formData.birth_date);
        this._setReviewField('review-gender', this._getFieldDisplay('gender'));
        
        // Address Information
        this._setReviewField('review-street', this.formData.street);
        this._setReviewField('review-city', this.formData.city);
        this._setReviewField('review-country', this._getFieldDisplay('country_id'));
        
        // Academic Information
        this._setReviewField('review-program', this._getFieldDisplay('program_id'));
        this._setReviewField('review-course', this._getFieldDisplay('course_id'));
        this._setReviewField('review-batch', this._getFieldDisplay('batch_id'));
        
        // Background Information
        this._setReviewField('review-prev-institute', this.formData.prev_institute_id);
        this._setReviewField('review-prev-course', this.formData.prev_course_id);
        this._setReviewField('review-family-business', this.formData.family_business);
    },

    /**
     * Set review field value
     */
    _setReviewField: function (id, value) {
        const $field = this.$('#' + id);
        if ($field.length) {
            if (value) {
                $field.text(value).removeClass('empty');
            } else {
                $field.text('Not provided').addClass('empty');
            }
        }
    },

    /**
     * Get display value for select fields
     */
    _getFieldDisplay: function (fieldName) {
        const $field = this.$('[name="' + fieldName + '"]');
        if ($field.length && $field.is('select')) {
            return $field.find('option:selected').text();
        }
        return this.formData[fieldName] || '';
    },

    /**
     * Clear draft after successful submission
     */
    clearDraft: function () {
        localStorage.removeItem('admission_draft');
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    },
});

