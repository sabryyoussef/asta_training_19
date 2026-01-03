/** @odoo-module **/

// Pure ESM module to avoid legacy dependency resolution problems on website
import { jsonrpc } from "@web/core/network/rpc_service";
import publicWidget from "@web/legacy/js/public/public_widget";

// Note: clearDemoData function is defined inline in the template for immediate availability

publicWidget.registry.AdmissionForm = publicWidget.Widget.extend({
    selector: '.admission-form',
    events: {
        'change select[name="country_id"]': '_onCountryChange',
        'submit': '_onFormSubmit',
    },

    // Initialize the form
    start: function () {
        this._super.apply(this, arguments);
        this._setupValidation();
    },

    // Handle country selection change to update states
    _onCountryChange: function (ev) {
        const countryId = ev.currentTarget.value;
        const $stateSelect = this.$el.find('select[name="state_id"]');

        if (!countryId) {
            $stateSelect.html('<option value="">Select State...</option>');
            return;
        }

        // Fetch states for selected country
        jsonrpc('/web/dataset/call_kw', {
            model: 'res.country.state',
            method: 'search_read',
            args: [],
            kwargs: {
                domain: [['country_id', '=', parseInt(countryId)]],
                fields: ['id', 'name'],
                context: {},
            },
        }).then((states) => {
            let options = '<option value="">Select State...</option>';
            states.forEach((state) => {
                options += `<option value="${state.id}">${state.name}</option>`;
            });
            $stateSelect.html(options);
        });
    },

    // Setup form validation
    _setupValidation: function () {
        const form = this.$el.find('form')[0];
        if (!form) return;

        // Add custom validation messages
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach((field) => {
            field.addEventListener('invalid', function (e) {
                e.preventDefault();
                this.classList.add('is-invalid');
            });

            field.addEventListener('input', function () {
                if (this.validity.valid) {
                    this.classList.remove('is-invalid');
                }
            });
        });

        // Email validation
        const emailField = form.querySelector('input[type="email"]');
        if (emailField) {
            emailField.addEventListener('blur', function () {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (this.value && !emailRegex.test(this.value)) {
                    this.setCustomValidity('Please enter a valid email address');
                    this.classList.add('is-invalid');
                } else {
                    this.setCustomValidity('');
                    this.classList.remove('is-invalid');
                }
            });
        }

        // Phone validation
        const phoneField = form.querySelector('input[name="phone"]');
        if (phoneField) {
            phoneField.addEventListener('blur', function () {
                const phoneRegex = /^[\d\s\-\+\(\)]+$/;
                if (this.value && !phoneRegex.test(this.value)) {
                    this.setCustomValidity('Please enter a valid phone number');
                    this.classList.add('is-invalid');
                } else {
                    this.setCustomValidity('');
                    this.classList.remove('is-invalid');
                }
            });
        }

        // Mobile validation
        const mobileField = form.querySelector('input[name="mobile"]');
        if (mobileField) {
            mobileField.addEventListener('blur', function () {
                const phoneRegex = /^[\d\s\-\+\(\)]+$/;
                if (this.value && !phoneRegex.test(this.value)) {
                    this.setCustomValidity('Please enter a valid mobile number');
                    this.classList.add('is-invalid');
                } else {
                    this.setCustomValidity('');
                    this.classList.remove('is-invalid');
                }
            });
        }

        // Date of birth validation (must be in the past)
        const dobField = form.querySelector('input[name="birth_date"]');
        if (dobField) {
            dobField.addEventListener('blur', function () {
                const selectedDate = new Date(this.value);
                const today = new Date();
                if (selectedDate >= today) {
                    this.setCustomValidity('Date of birth must be in the past');
                    this.classList.add('is-invalid');
                } else {
                    this.setCustomValidity('');
                    this.classList.remove('is-invalid');
                }
            });
        }

        // Image file validation (size and type)
        const imageField = form.querySelector('input[name="image"]');
        if (imageField) {
            imageField.addEventListener('change', function () {
                const file = this.files[0];
                if (file) {
                    // Check file size (max 5MB)
                    if (file.size > 5 * 1024 * 1024) {
                        this.setCustomValidity('Image size must be less than 5MB');
                        this.classList.add('is-invalid');
                        this.value = '';
                        return;
                    }
                    // Check file type
                    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                    if (!allowedTypes.includes(file.type)) {
                        this.setCustomValidity('Only JPEG, PNG, and GIF images are allowed');
                        this.classList.add('is-invalid');
                        this.value = '';
                        return;
                    }
                    this.setCustomValidity('');
                    this.classList.remove('is-invalid');
                }
            });
        }
    },

    // Handle form submission
    _onFormSubmit: function (ev) {
        // Validate form before submission
        const form = this.$el.find('form')[0];
        if (form && !form.checkValidity()) {
            ev.preventDefault();
            ev.stopPropagation();
            form.classList.add('was-validated');
            
            // Scroll to first invalid field
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
            return false;
        }

        this.$el.addClass('loading');
        this.$el.find('button[type="submit"]').prop('disabled', true);
        this.$el.find('button[type="submit"]').html('<i class="fa fa-spinner fa-spin"></i> Submitting...');
    },
});

