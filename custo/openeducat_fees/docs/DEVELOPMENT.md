# Development Guide - OpenEduCat Fees Module

## For Odoo Developers

This guide helps developers extend, customize, and maintain the OpenEduCat Fees module.

---

## Development Environment Setup

### Prerequisites

```bash
# Odoo 18.0 installed
# Python 3.10+
# PostgreSQL 12+
# PyCharm (recommended IDE)
```

### Module Location

```bash
custom_addons/motakamel_training_academy/custom-addons/motakamel/openeducat_fees/
```

### Development Mode

Enable developer mode:
- Settings → Activate Developer Mode

Or via URL:
```
http://localhost:8069/web?debug=1
```

---

## Module Architecture

### Directory Structure

```
openeducat_fees/
├── __init__.py                 # Module entry point
├── __manifest__.py             # Module metadata
├── models/                     # Business logic
│   ├── __init__.py
│   ├── course.py               # Course fee term assignment
│   ├── fees_element.py         # Fee elements
│   ├── fees_terms.py           # Fee terms & lines
│   └── student.py              # Student fee details
├── views/                      # XML views (Odoo 18 list views)
│   ├── course_view.xml
│   ├── fees_element_view.xml
│   ├── fees_terms_view.xml
│   └── student_view.xml
├── wizard/                     # Transient models
│   ├── __init__.py
│   ├── fees_detail_report_wizard.py
│   ├── fees_detail_report_wizard_view.xml
│   ├── select_term_type_wizard.py
│   └── select_term_type.xml
├── report/                     # QWeb reports
│   ├── __init__.py
│   ├── fees_analysis_report.py
│   ├── fees_analysis_report_view.xml
│   └── report_menu.xml
├── security/                   # Access control
│   ├── ir.model.access.csv     # ACL rules
│   └── op_security.xml         # Groups & record rules
├── static/                     # Frontend assets
│   ├── src/
│   │   ├── js/
│   │   │   ├── fees_term_widget.js
│   │   │   └── page_list.js
│   │   └── xml/
│   │       └── fees_term_widget_template.xml
│   └── description/            # Module icons/screenshots
├── demo/                       # Demo data
│   ├── product_demo.xml
│   ├── fees_terms_demo.xml
│   └── ...
├── i18n/                       # Translations
│   ├── ar_001.po
│   ├── es.po
│   └── ... (13+ languages)
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_fees_common.py
│   └── test_fees.py
├── docs/                       # Documentation (this folder)
└── README.rst                  # Short description
```

---

## Extending the Module

### Create Dependent Module

```bash
# Scaffold new module
./odoo-bin scaffold openeducat_fees_custom /path/to/custom_addons
```

**Manifest:**

```python
{
    'name': 'OpenEduCat Fees - Custom',
    'version': '18.0.1.0',
    'category': 'Education',
    'depends': ['openeducat_fees'],  # Dependency
    'data': [
        'security/ir.model.access.csv',
        'views/custom_views.xml',
    ],
    'installable': True,
}
```

---

## Common Customizations

### 1. Add Custom Field to Fee Details

**models/student_fees_custom.py:**

```python
from odoo import models, fields, api

class OpStudentFeesDetailsCustom(models.Model):
    _inherit = 'op.student.fees.details'
    
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit Card'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
    ], string='Payment Method', tracking=True)
    
    payment_reference = fields.Char('Payment Reference')
    payment_date = fields.Date('Actual Payment Date')
```

**views/student_fees_view.xml:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
  <record id="view_student_fees_details_form_custom" model="ir.ui.view">
    <field name="name">op.student.fees.details.form.custom</field>
    <field name="model">op.student.fees.details</field>
    <field name="inherit_id" ref="openeducat_fees.view_op_student_fees_details_form"/>
    <field name="arch" type="xml">
      <xpath expr="//field[@name='discount']" position="after">
        <field name="payment_method"/>
        <field name="payment_reference"/>
        <field name="payment_date"/>
      </xpath>
    </field>
  </record>
</odoo>
```

---

### 2. Add Automated Fee Generation

**models/student_course_custom.py:**

```python
from odoo import models, fields, api
from datetime import timedelta

class OpStudentCourseCustom(models.Model):
    _inherit = 'op.student.course'
    
    @api.model_create_multi
    def create(self, vals_list):
        enrollments = super().create(vals_list)
        
        for enrollment in enrollments:
            if enrollment.course_id.fees_term_id:
                enrollment._auto_generate_fees()
        
        return enrollments
    
    def _auto_generate_fees(self):
        """Automatically generate fee details from course fee term"""
        self.ensure_one()
        
        fee_term = self.course_id.fees_term_id
        if not fee_term:
            return
        
        for line in fee_term.line_ids:
            # Calculate due date
            if fee_term.fees_terms == 'fixed_days':
                due_date = self.fees_start_date or fields.Date.today()
                due_date = due_date + timedelta(days=line.due_days or 0)
            else:  # fixed_date
                due_date = line.due_date
            
            # Calculate amount from fee elements
            total_amount = sum(elem.product_id.lst_price * elem.value / 100.0 
                             for elem in line.fees_element_line)
            
            # Apply term line percentage
            amount = total_amount * line.value / 100.0
            
            # Create fee detail for each element
            for element in line.fees_element_line:
                self.env['op.student.fees.details'].create({
                    'student_id': self.student_id.id,
                    'course_id': self.course_id.id,
                    'batch_id': self.batch_id.id,
                    'product_id': element.product_id.id,
                    'amount': element.product_id.lst_price * line.value / 100.0,
                    'date': due_date,
                    'discount': fee_term.discount,
                    'fees_line_id': line.id,
                    'state': 'draft',
                })
```

---

### 3. Add Email Notifications

**models/student_fees_notifications.py:**

```python
from odoo import models, fields, api, _

class OpStudentFeesDetailsNotify(models.Model):
    _inherit = 'op.student.fees.details'
    
    def write(self, vals):
        # Track state changes
        old_states = {rec.id: rec.state for rec in self}
        result = super().write(vals)
        
        # Send notification on invoice creation
        if 'state' in vals:
            for record in self:
                if old_states[record.id] == 'draft' and record.state == 'invoice':
                    record._send_invoice_notification()
        
        return result
    
    def _send_invoice_notification(self):
        """Send email when invoice is created"""
        self.ensure_one()
        template = self.env.ref('custom_module.fees_invoice_email_template')
        if template:
            template.send_mail(self.id, force_send=True)
```

**data/email_template.xml:**

```xml
<record id="fees_invoice_email_template" model="mail.template">
  <field name="name">Fee Invoice Notification</field>
  <field name="model_id" ref="openeducat_fees.model_op_student_fees_details"/>
  <field name="subject">Your Fee Invoice - {{ object.product_id.name }}</field>
  <field name="body_html"><![CDATA[
    <p>Dear {{ object.student_id.name }},</p>
    <p>Your fee invoice has been generated:</p>
    <ul>
      <li>Product: {{ object.product_id.name }}</li>
      <li>Amount: {{ object.after_discount_amount }}</li>
      <li>Due Date: {{ object.date }}</li>
    </ul>
    <p>Please pay before the due date.</p>
  ]]></field>
  <field name="email_to">{{ object.student_id.email }}</field>
</record>
```

---

### 4. Add Fee Payment Tracking

**models/fees_payment.py:**

```python
from odoo import models, fields, api

class OpStudentFeesDetailsPayment(models.Model):
    _inherit = 'op.student.fees.details'
    
    payment_ids = fields.One2many(
        'account.payment',
        compute='_compute_payment_ids',
        string='Payments'
    )
    total_paid = fields.Monetary(
        compute='_compute_total_paid',
        currency_field='currency_id',
        string='Total Paid'
    )
    balance_due = fields.Monetary(
        compute='_compute_balance_due',
        currency_field='currency_id',
        string='Balance Due'
    )
    
    def _compute_payment_ids(self):
        for record in self:
            if record.invoice_id:
                record.payment_ids = record.invoice_id.payment_ids
            else:
                record.payment_ids = self.env['account.payment']
    
    @api.depends('payment_ids', 'payment_ids.amount')
    def _compute_total_paid(self):
        for record in self:
            record.total_paid = sum(record.payment_ids.mapped('amount'))
    
    @api.depends('after_discount_amount', 'total_paid')
    def _compute_balance_due(self):
        for record in self:
            record.balance_due = record.after_discount_amount - record.total_paid
```

---

### 5. Add Custom Report

**report/custom_fees_report.py:**

```python
from odoo import models, api

class CustomFeesReport(models.AbstractModel):
    _name = 'report.custom_module.custom_fees_report'
    _description = 'Custom Fees Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['op.student.fees.details'].browse(docids)
        
        # Custom calculations
        report_data = []
        for doc in docs:
            report_data.append({
                'student': doc.student_id.name,
                'amount': doc.amount,
                'paid': self._get_paid_amount(doc),
                'balance': doc.after_discount_amount - self._get_paid_amount(doc),
            })
        
        return {
            'docs': docs,
            'report_data': report_data,
            'company': self.env.company,
        }
    
    def _get_paid_amount(self, fee_detail):
        if fee_detail.invoice_id:
            return sum(fee_detail.invoice_id.payment_ids.mapped('amount'))
        return 0.0
```

---

## Testing Guidelines

### Write Unit Tests

**tests/test_custom_fees.py:**

```python
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestCustomFees(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.student = self.env.ref('openeducat_core.op_student_1')
        self.product = self.env.ref('openeducat_fees.op_product_1')
    
    def test_fee_creation(self):
        """Test creating a fee detail record"""
        fee = self.env['op.student.fees.details'].create({
            'student_id': self.student.id,
            'product_id': self.product.id,
            'amount': 5000.0,
            'date': '2025-01-15',
            'state': 'draft',
        })
        
        self.assertEqual(fee.student_id, self.student)
        self.assertEqual(fee.amount, 5000.0)
        self.assertEqual(fee.state, 'draft')
    
    def test_discount_calculation(self):
        """Test discount computation"""
        fee = self.env['op.student.fees.details'].create({
            'student_id': self.student.id,
            'product_id': self.product.id,
            'amount': 10000.0,
            'discount': 10.0,  # 10%
        })
        
        self.assertEqual(fee.after_discount_amount, 9000.0)
    
    def test_invoice_generation(self):
        """Test invoice creation"""
        fee = self.env['op.student.fees.details'].create({
            'student_id': self.student.id,
            'product_id': self.product.id,
            'amount': 5000.0,
            'date': '2025-01-15',
            'state': 'draft',
        })
        
        invoice = fee.get_invoice()
        
        self.assertTrue(invoice)
        self.assertEqual(fee.state, 'invoice')
        self.assertEqual(fee.invoice_id, invoice)
```

### Run Tests

```bash
# Run all fees tests
./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags openeducat_fees --stop-after-init

# Run specific test
./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags openeducat_fees.test_fees --stop-after-init

# PyCharm: Configure test run config with above parameters
```

---

## Odoo 18 Best Practices

### 1. Use List Views (Not Tree)

**✓ Correct (Odoo 18):**

```xml
<list string="Student Fees">
    <field name="student_id"/>
    <field name="amount"/>
    <field name="state"/>
</list>
```

**✗ Deprecated:**

```xml
<!-- Don't use <tree> in Odoo 18 -->
<tree string="Student Fees">
  ...
</tree>
```

---

### 2. Modern Invisible/Readonly Syntax

**✓ Correct (Odoo 18):**

```xml
<field name="invoice_id" invisible="state != 'invoice'"/>
<field name="amount" readonly="state == 'invoice'"/>
```

**✗ Deprecated:**

```xml
<!-- Don't use attrs in Odoo 18 -->
<field name="invoice_id" attrs="{'invisible': [('state', '!=', 'invoice')]}"/>
<field name="amount" attrs="{'readonly': [('state', '==', 'invoice')]}"/>
```

---

### 3. Use @api.model_create_multi

**✓ Correct:**

```python
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    # Post-processing
    return records
```

**✗ Old Style:**

```python
@api.model
def create(self, vals):
    record = super().create(vals)
    return record
```

---

### 4. OWL Components (Odoo 18)

**✓ Correct:**

```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class FeesTermsDisplay extends Component {
    static template = "openeducat_fees.FieldFeesTermsDisplay";
    static props = ["*"];
}

registry.category("fields").add("fees_term_display", {
    component: FeesTermsDisplay,
});
```

---

## Code Style Guide

### Python (PEP 8 + Odoo)

```python
# Imports order
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# Class definition
class OpFeesTerms(models.Model):
    """Fee payment term definition.
    
    This model manages fee term templates with installment lines
    and validation for educational institutions.
    """
    _name = 'op.fees.terms'
    _inherit = ['mail.thread']
    _description = 'Fees Terms For Course'
    
    # Fields (order: required, then optional, then computed)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)
    line_ids = fields.One2many('op.fees.terms.line', 'fees_id', 'Terms')
    
    # Constraints
    @api.constrains("line_ids")
    def terms_validation(self):
        """Validate line percentages sum to 100%"""
        for record in self:
            if not record.line_ids:
                raise ValidationError(_('Fees Terms must be Required!'))
            total = sum(record.line_ids.mapped('value'))
            if total != 100:
                raise ValidationError(_('Fees terms must be divided as such sum up in 100%'))
    
    # Business methods
    def custom_action(self):
        """Action method with docstring"""
        self.ensure_one()
        # Logic here
        return True
```

### XML Style

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
  <!-- List View -->
  <record id="view_fees_terms_list" model="ir.ui.view">
    <field name="name">op.fees.terms.list</field>
    <field name="model">op.fees.terms</field>
    <field name="arch" type="xml">
      <list string="Fees Terms">
        <field name="name"/>
        <field name="code"/>
        <field name="fees_terms"/>
        <field name="active"/>
      </list>
    </field>
  </record>

  <!-- Form View -->
  <record id="view_fees_terms_form" model="ir.ui.view">
    <field name="name">op.fees.terms.form</field>
    <field name="model">op.fees.terms</field>
    <field name="arch" type="xml">
      <form>
        <sheet>
          <group>
            <group>
              <field name="name"/>
              <field name="code"/>
            </group>
            <group>
              <field name="fees_terms" widget="fees_term_display"/>
              <field name="active"/>
            </group>
          </group>
          
          <notebook>
            <page string="Terms">
              <field name="line_ids">
                <list>
                  <field name="due_days" invisible="parent.fees_terms != 'fixed_days'"/>
                  <field name="due_date" invisible="parent.fees_terms != 'fixed_date'"/>
                  <field name="value"/>
                </list>
              </field>
            </page>
          </notebook>
        </sheet>
        
        <!-- Chatter -->
        <chatter/>
      </form>
    </field>
  </record>

  <!-- Action -->
  <record id="action_fees_terms" model="ir.actions.act_window">
    <field name="name">Fees Terms</field>
    <field name="res_model">op.fees.terms</field>
    <field name="view_mode">list,form</field>
  </record>

  <!-- Menu -->
  <menuitem id="menu_fees_terms" 
            name="Fees Terms"
            parent="menu_fees_root"
            action="action_fees_terms"
            sequence="10"/>
</odoo>
```

---

## Debugging Tips

### Enable Logging

**Python:**

```python
import logging
_logger = logging.getLogger(__name__)

class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    def get_invoice(self):
        _logger.info(f"Creating invoice for fee {self.id}, student {self.student_id.name}")
        invoice = super().get_invoice()
        _logger.info(f"Invoice {invoice.name} created successfully")
        return invoice
```

### Debug in Python Shell

```python
# Start Odoo shell
./odoo-bin shell -c odoo.conf -d your_database

# Debug fee term
>>> term = env['op.fees.terms'].browse(1)
>>> print(term.name, term.code)
>>> print(sum(term.line_ids.mapped('value')))

# Debug fee detail
>>> fee = env['op.student.fees.details'].browse(123)
>>> print(f"Amount: {fee.amount}, Discount: {fee.discount}%, Final: {fee.after_discount_amount}")

# Test invoice creation
>>> invoice = fee.get_invoice()
>>> print(f"Invoice: {invoice.name}, State: {invoice.state}")
```

### View SQL Queries

**Enable SQL logging in odoo.conf:**

```ini
[options]
log_level = debug
log_db = True
log_db_level = debug
```

---

## Performance Optimization

### 1. Avoid N+1 Queries

**✗ Bad:**

```python
for fee in fee_details:
    print(fee.student_id.name)  # Query per iteration
```

**✓ Good:**

```python
fee_details = env['op.student.fees.details'].search([...])
fee_details.mapped('student_id')  # Prefetch
for fee in fee_details:
    print(fee.student_id.name)  # No queries
```

### 2. Use read_group for Aggregates

**✗ Bad:**

```python
total = sum(env['op.student.fees.details'].search([]).mapped('amount'))
```

**✓ Good:**

```python
result = env['op.student.fees.details'].read_group(
    [('state', '=', 'draft')],
    ['amount:sum'],
    []
)
total = result[0]['amount'] if result else 0
```

### 3. Batch Operations

```python
# Use norecompute for bulk operations
with self.env.norecompute():
    for fee in large_fee_list:
        fee.discount = 10.0
# Recompute once at the end
self.env['op.student.fees.details'].recompute()
```

---

## Security Development

### Add Custom Access Rule

**security/ir.model.access.csv:**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_fees_user,op.student.fees.details.custom.user,model_op_student_fees_details,group_custom_user,1,1,1,0
```

### Add Record Rule

**security/custom_rules.xml:**

```xml
<record id="fees_detail_company_rule" model="ir.rule">
  <field name="name">Student Fees: multi-company</field>
  <field name="model_id" ref="openeducat_fees.model_op_student_fees_details"/>
  <field name="domain_force">[('company_id', 'in', company_ids)]</field>
  <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

---

## JavaScript/OWL Development

### Create Custom Widget

**static/src/js/custom_widget.js:**

```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class FeeStatusWidget extends Component {
    static template = "custom_module.FeeStatusWidget";
    static props = {
        ...standardFieldProps,
    };
    
    get statusColor() {
        const state = this.props.record.data[this.props.name];
        return {
            'draft': 'warning',
            'invoice': 'success',
            'cancel': 'danger',
        }[state] || 'secondary';
    }
}

registry.category("fields").add("fee_status", {
    component: FeeStatusWidget,
});
```

**static/src/xml/custom_widget_template.xml:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <t t-name="custom_module.FeeStatusWidget">
    <span t-att-class="'badge badge-' + statusColor">
      <t t-esc="props.record.data[props.name]"/>
    </span>
  </t>
</templates>
```

**Register in __manifest__.py:**

```python
'assets': {
    'web.assets_backend': [
        'custom_module/static/src/js/custom_widget.js',
        'custom_module/static/src/xml/custom_widget_template.xml',
    ],
},
```

---

## Migration Scripts

### Upgrade Hook Example

**migrations/18.0.1.1/post-migrate.py:**

```python
def migrate(cr, version):
    """Post-migration script for version 18.0.1.1"""
    
    # Update existing records
    cr.execute("""
        UPDATE op_student_fees_details
        SET custom_field = 'default_value'
        WHERE custom_field IS NULL
    """)
    
    # Clear caches
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.ui.view'].clear_caches()
    
    print("Migration completed successfully")
```

---

## Contribution Guidelines

### Before Submitting Changes

1. ✓ Run tests and ensure they pass
2. ✓ Follow Odoo 18 conventions (list views, no attrs)
3. ✓ Add docstrings to new methods
4. ✓ Update documentation if adding features
5. ✓ Test with demo data
6. ✓ Check security (ACL rules)
7. ✓ Verify i18n (translatable strings use `_()`)

### Code Review Checklist

- [ ] Odoo 18 compliant (list views, modern syntax)
- [ ] No `sudo()` without justification
- [ ] Proper `@api.depends` for computed fields
- [ ] Access control configured
- [ ] Tests written and passing
- [ ] Docstrings added
- [ ] No hardcoded IDs (use `ref()`)
- [ ] i18n strings wrapped with `_()`
- [ ] No business logic in `__init__` or controllers
- [ ] Performance considered (no N+1)

---

## Common Development Tasks

### Task: Add New Fee Product Type

**Steps:**

1. Create product: `demo/custom_product.xml`

```xml
<record id="product_hostel_fee" model="product.product">
  <field name="name">Hostel Fees</field>
  <field name="type">service</field>
  <field name="categ_id" ref="openeducat_fees.op_prod_cat1"/>
  <field name="lst_price">3000.0</field>
</record>
```

2. Add to fee elements as needed

---

### Task: Add Custom State to Fee Details

**models/student_custom.py:**

```python
class OpStudentFeesDetailsCustom(models.Model):
    _inherit = 'op.student.fees.details'
    
    state = fields.Selection(
        selection_add=[
            ('pending_approval', 'Pending Approval'),
        ],
        ondelete={'pending_approval': 'set default'}
    )
```

**Add state methods:**

```python
def action_approve(self):
    self.write({'state': 'draft'})
    
def action_request_approval(self):
    self.write({'state': 'pending_approval'})
```

---

### Task: Add Smart Button

**views/custom_view.xml:**

```xml
<xpath expr="//form/sheet" position="before">
  <div class="oe_button_box" name="button_box">
    <button name="action_view_related"
            type="object"
            class="oe_stat_button"
            icon="fa-list">
      <field name="related_count" widget="statinfo" string="Related"/>
    </button>
  </div>
</xpath>
```

**models/custom.py:**

```python
related_count = fields.Integer(compute='_compute_related_count')

@api.depends('related_ids')
def _compute_related_count(self):
    for record in self:
        record.related_count = len(record.related_ids)

def action_view_related(self):
    return {
        'type': 'ir.actions.act_window',
        'name': 'Related Records',
        'res_model': 'related.model',
        'view_mode': 'list,form',
        'domain': [('fees_detail_id', '=', self.id)],
    }
```

---

## Database Queries

### Useful SQL for Development

```sql
-- Check fee term line percentages
SELECT ft.name, ftl.due_days, ftl.value
FROM op_fees_terms ft
JOIN op_fees_terms_line ftl ON ftl.fees_id = ft.id
WHERE ft.id = XXX;

-- Students with unpaid fees
SELECT s.name, SUM(f.amount) as total_due
FROM op_student_fees_details f
JOIN op_student s ON s.id = f.student_id
WHERE f.state = 'draft'
GROUP BY s.name
ORDER BY total_due DESC;

-- Fee collection by course
SELECT c.name, COUNT(f.id) as fees_count, SUM(f.amount) as total_amount
FROM op_student_fees_details f
JOIN op_course c ON c.id = f.course_id
GROUP BY c.name;
```

---

## Resources

### Official Documentation

- Odoo 18 Developer Docs: https://www.odoo.com/documentation/18.0/developer/
- ORM API: https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html
- Views: https://www.odoo.com/documentation/18.0/developer/reference/frontend/views.html

### Community Resources

- Odoo Forum: https://www.odoo.com/forum
- OCA GitHub: https://github.com/OCA
- Stack Overflow: https://stackoverflow.com/questions/tagged/odoo

---

## Getting Help

### Internal

- Read [Technical Reference](./TECHNICAL.md)
- Check [API Documentation](./API.md)
- Review [FAQ](./FAQ.md)

### External

- Odoo Documentation
- Community forums
- GitHub issues

---

**Last Updated:** November 3, 2025  
**Target Audience:** Odoo Developers  
**Skill Level:** Intermediate to Advanced

