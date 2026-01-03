###############################################################################
#
#    Edafa Website Portal - Admission Extensions
#    Copyright (C) 2024 Edafa Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import secrets
import logging

_logger = logging.getLogger(__name__)


class OpAdmission(models.Model):
    """
    Extension of op.admission model for portal and payment features.
    Inherits from openeducat_admission module, adds portal-specific functionality.
    """
    _inherit = 'op.admission'
    
    # ============================================
    # DEPARTMENT FIELD
    # ============================================
    
    department_id = fields.Many2one(
        'op.department',
        string='Department',
        required=True,
        tracking=True,
        help="Department for this admission - determines available programs and courses"
    )
    
    # ============================================
    # PORTAL ACCESS FIELDS
    # ============================================
    
    access_token = fields.Char(
        'Security Token',
        readonly=True,
        copy=False,
        help="Token for public portal access without login"
    )
    
    # ============================================
    # PAYMENT FIELDS
    # ============================================
    
    application_fee = fields.Monetary(
        'Application Fee',
        currency_field='currency_id',
        help="Fee for processing this application",
        tracking=True
    )
    
    payment_status = fields.Selection([
        ('none', 'No Payment Required'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded')
    ], string='Payment Status', default='none', tracking=True, copy=False)
    
    payment_transaction_id = fields.Many2one(
        'payment.transaction',
        string='Payment Transaction',
        readonly=True,
        copy=False,
        help="Online payment transaction reference"
    )
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Application Invoice',
        readonly=True,
        copy=False,
        help="Invoice generated for application fee"
    )
    
    payment_date = fields.Datetime(
        'Payment Date',
        readonly=True,
        copy=False,
        help="When payment was received"
    )
    
    payment_reference = fields.Char(
        'Payment Reference',
        readonly=True,
        copy=False,
        help="Payment transaction reference number"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_currency_id',
        store=True
    )
    
    # ============================================
    # COMPUTE METHODS
    # ============================================
    
    @api.depends('company_id')
    def _compute_currency_id(self):
        """Set currency from company"""
        for record in self:
            record.currency_id = record.company_id.currency_id or \
                                self.env.company.currency_id
    
    # ============================================
    # ONCHANGE METHODS
    # ============================================
    
    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Filter programs and courses when department changes"""
        if self.department_id:
            # Reset program and course when department changes
            self.program_id = False
            self.course_id = False
            
            # Return domain to filter programs and courses by department
            return {
                'domain': {
                    'program_id': [('id', 'in', self.department_id.program_ids.ids)],
                    'course_id': [('department_id', '=', self.department_id.id)]
                }
            }
        else:
            # No department selected - show all
            return {
                'domain': {
                    'program_id': [],
                    'course_id': []
                }
            }
    
    @api.onchange('program_id')
    def _onchange_program_id(self):
        """Further filter courses when program changes"""
        if self.program_id and self.department_id:
            # Reset course when program changes
            self.course_id = False
            
            # Return domain to filter courses by both department and program
            return {
                'domain': {
                    'course_id': [
                        ('department_id', '=', self.department_id.id),
                        ('program_id', '=', self.program_id.id)
                    ]
                }
            }
        elif self.department_id:
            # Only department selected - filter by department
            return {
                'domain': {
                    'course_id': [('department_id', '=', self.department_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'course_id': []
                }
            }
    
    @api.onchange('course_id', 'register_id')
    def _onchange_application_fee(self):
        """Auto-set application fee from register or course"""
        for record in self:
            # Try to get fee from admission register first
            if record.register_id and record.register_id.product_id:
                record.application_fee = record.register_id.product_id.lst_price
            # Otherwise try from course (if course has fee configured)
            elif record.course_id and hasattr(record.course_id, 'application_fee'):
                record.application_fee = record.course_id.application_fee
            else:
                # Default fee (can be configured in system parameters)
                default_fee = self.env['ir.config_parameter'].sudo().get_param(
                    'edafa.default_application_fee', '0.0'
                )
                record.application_fee = float(default_fee)
    
    # ============================================
    # CREATE/WRITE METHODS
    # ============================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate access token"""
        for vals in vals_list:
            # Generate secure access token for portal access
            if not vals.get('access_token'):
                vals['access_token'] = secrets.token_urlsafe(32)
            
            # Set initial payment status based on fee
            if vals.get('application_fee', 0) > 0 and not vals.get('payment_status'):
                vals['payment_status'] = 'unpaid'
            elif not vals.get('payment_status'):
                vals['payment_status'] = 'none'
        
        return super().create(vals_list)
    
    def write(self, vals):
        """Override write to update payment status"""
        # Update payment status based on invoice state
        if 'invoice_id' in vals and vals['invoice_id']:
            invoice = self.env['account.move'].browse(vals['invoice_id'])
            if invoice.payment_state == 'paid':
                vals['payment_status'] = 'paid'
                if not vals.get('payment_date'):
                    vals['payment_date'] = fields.Datetime.now()
        
        return super().write(vals)
    
    # ============================================
    # ACTION METHODS
    # ============================================
    
    def action_create_invoice(self):
        """
        Create invoice for application fee.
        Follows the same pattern as openeducat_fees/models/student.py
        """
        self.ensure_one()
        
        # Check if invoice already exists
        if self.invoice_id:
            raise ValidationError(_('Invoice already exists for this application'))
        
        # Check if fee amount is valid
        if not self.application_fee or self.application_fee <= 0:
            raise UserError(_('Application fee must be greater than zero'))
        
        # Get or create application fee product
        product = self.env.ref(
            'edafa_website_branding.product_application_fee',
            raise_if_not_found=False
        )
        
        if not product:
            # Create default application fee product if doesn't exist
            _logger.warning('Application fee product not found, creating default')
            product = self.env['product.product'].sudo().create({
                'name': 'Application Processing Fee',
                'type': 'service',
                'list_price': 50.0,
                'invoice_policy': 'order',
                'taxes_id': False,  # No taxes on application fee
            })
        
        # Get or create partner for student - check for existing partner first to avoid duplicates
        partner = self.partner_id
        if not partner:
            # Search for existing partner by email to avoid duplicates
            if self.email:
                partner = self.env['res.partner'].sudo().search([
                    ('email', '=', self.email)
                ], limit=1)
            
            # If no partner found by email, search by name and email combination
            if not partner and self.name and self.email:
                partner = self.env['res.partner'].sudo().search([
                    ('name', '=', self.name),
                    ('email', '=', self.email)
                ], limit=1)
            
            # If still no partner found, create a new one
            if not partner:
                partner = self.env['res.partner'].sudo().create({
                    'name': self.name,
                    'email': self.email,
                    'phone': self.mobile if self.mobile else False,
                    'street': self.street if self.street else False,
                    'city': self.city if self.city else False,
                    'zip': self.zip if self.zip else False,
                    'country_id': self.country_id.id if self.country_id else False,
                    'state_id': self.state_id.id if self.state_id else False,
                })
            else:
                # Update existing partner with any missing information
                update_vals = {}
                if not partner.name and self.name:
                    update_vals['name'] = self.name
                if not partner.phone and self.mobile:
                    update_vals['phone'] = self.mobile
                if not partner.street and self.street:
                    update_vals['street'] = self.street
                if not partner.city and self.city:
                    update_vals['city'] = self.city
                if not partner.zip and self.zip:
                    update_vals['zip'] = self.zip
                if not partner.country_id and self.country_id:
                    update_vals['country_id'] = self.country_id.id
                if not partner.state_id and self.state_id:
                    update_vals['state_id'] = self.state_id.id
                if update_vals:
                    partner.write(update_vals)
            
            self.partner_id = partner.id
        
        # Get income account from product (following openeducat_fees pattern)
        account_id = False
        if product.property_account_income_id:
            account_id = product.property_account_income_id.id
        if not account_id and product.categ_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(_(
                'No income account defined for application fee product. '
                'Please configure accounting or contact administrator.'
            ))
        
        # Create invoice (following openeducat_fees/models/student.py pattern)
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Application Fee - {self.application_number}',
                'product_id': product.id,
                'quantity': 1.0,
                'price_unit': self.application_fee,
                'account_id': account_id,
                'product_uom_id': product.uom_id.id,
            })],
        })
        
        # Compute taxes and totals
        invoice._compute_tax_totals()
        
        # Link invoice to admission
        self.invoice_id = invoice.id
        self.payment_status = 'unpaid'
        
        _logger.info(f'Invoice created for admission {self.application_number}: {invoice.name}')
        
        # Return action to view invoice
        return {
            'type': 'ir.actions.act_window',
            'name': _('Application Fee Invoice'),
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_invoice(self):
        """View application fee invoice"""
        self.ensure_one()
        
        if not self.invoice_id:
            raise UserError(_('No invoice exists for this application'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Application Fee Invoice'),
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_register_payment(self):
        """Register manual payment for application fee"""
        self.ensure_one()
        
        # Create invoice if doesn't exist
        if not self.invoice_id:
            self.action_create_invoice()
        
        # Open payment wizard (standard Odoo)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'account.move',
                'active_ids': [self.invoice_id.id],
            }
        }
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _generate_access_token(self):
        """Generate or refresh access token"""
        for record in self:
            record.access_token = secrets.token_urlsafe(32)
    
    def _check_access_token(self, access_token):
        """Verify access token is valid"""
        self.ensure_one()
        return self.access_token and self.access_token == access_token
    
    def _get_portal_url(self):
        """Get portal URL for this admission with access token"""
        self.ensure_one()
        if not self.access_token:
            self._generate_access_token()
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/my/admission/{self.id}?access_token={self.access_token}"
    
    def _update_payment_status_from_transaction(self):
        """Update payment status based on linked transaction"""
        for record in self:
            if record.payment_transaction_id:
                tx = record.payment_transaction_id
                
                if tx.state == 'done':
                    record.write({
                        'payment_status': 'paid',
                        'payment_date': tx.last_state_change or fields.Datetime.now(),
                        'payment_reference': tx.reference,
                        'state': 'confirm',  # Auto-confirm after payment
                    })
                elif tx.state == 'cancel':
                    record.write({
                        'payment_status': 'unpaid',
                    })

