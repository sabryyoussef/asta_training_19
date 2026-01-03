# API Documentation - OpenEduCat Fees Module

## Model API Reference

### op.fees.terms

Fee payment term template definition.

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | ✓ | Fee term name |
| `code` | Char | ✓ | Unique code identifier |
| `active` | Boolean | | Active status (default: True) |
| `fees_terms` | Selection | | Type: 'fixed_days' or 'fixed_date' |
| `note` | Text | | Terms and conditions description |
| `company_id` | Many2one | ✓ | Company (multi-company) |
| `no_days` | Integer | | Number of days (for reminders) |
| `day_type` | Selection | | 'before' or 'after' |
| `line_ids` | One2many | | Related op.fees.terms.line records |
| `discount` | Float | | Default discount percentage |

#### Methods

##### `terms_validation()`

```python
@api.constrains("line_ids")
def terms_validation(self):
    """
    Validates that fee term line percentages sum to exactly 100%
    
    Raises:
        ValidationError: If sum != 100%
    """
```

**Usage:**

```python
term = env['op.fees.terms'].create({
    'name': 'Test Term',
    'code': 'TEST',
    'line_ids': [
        (0, 0, {'due_days': 0, 'value': 50.0}),
        (0, 0, {'due_days': 30, 'value': 50.0}),  # Total: 100% ✓
    ]
})
```

---

### op.fees.terms.line

Individual installment line within a fee term.

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `due_days` | Integer | | Days after enrollment (for fixed_days) |
| `due_date` | Date | | Specific date (for fixed_date) |
| `value` | Float | ✓ | Percentage of total fee (0-100) |
| `fees_element_line` | One2many | | Related op.fees.element records |
| `fees_id` | Many2one | | Parent fee term |

#### Business Logic

```python
# For fixed_days fee terms
if fees_id.fees_terms == 'fixed_days':
    actual_due_date = enrollment_date + timedelta(days=due_days)
    
# For fixed_date fee terms
if fees_id.fees_terms == 'fixed_date':
    actual_due_date = due_date
```

---

### op.fees.element

Fee product element assigned to a term line.

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | Many2one | ✓ | Product (fee type) |
| `value` | Float | | Percentage weight within line |
| `sequence` | Integer | | Display order |
| `fees_terms_line_id` | Many2one | | Parent term line |

#### Example

```python
# Create fee element
element = env['op.fees.element'].create({
    'product_id': env.ref('openeducat_fees.op_product_7').id,  # Library Fee
    'value': 100.0,  # 100% of this line
    'fees_terms_line_id': term_line.id,
})
```

---

### op.student.fees.details

Student fee collection record (main transactional model).

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `student_id` | Many2one | ✓ | Student |
| `course_id` | Many2one | | Related course |
| `batch_id` | Many2one | | Student batch |
| `product_id` | Many2one | | Fee product |
| `amount` | Monetary | | Fee amount |
| `discount` | Float | | Discount percentage |
| `after_discount_amount` | Monetary | Computed | Amount after discount |
| `date` | Date | | Due/submit date |
| `state` | Selection | | 'draft', 'invoice', 'cancel' |
| `invoice_id` | Many2one | | Linked account.move |
| `invoice_state` | Selection | Related | Invoice state |
| `fees_line_id` | Many2one | | Source fee term line |
| `company_id` | Many2one | | Company |
| `currency_id` | Many2one | Computed | Currency |
| `fees_factor` | Float | | Multiplier factor |

#### Methods

##### `_compute_discount_amount()`

```python
@api.depends('discount')
def _compute_discount_amount(self):
    """
    Computes amount after applying discount percentage
    
    Formula: after_discount_amount = amount - (amount * discount / 100)
    """
    for record in self:
        discount_amount = record.amount * record.discount / 100.0
        record.after_discount_amount = record.amount - discount_amount
```

##### `get_invoice()`

```python
def get_invoice(self):
    """
    Creates an account.move (invoice) from fee detail
    
    Returns:
        account.move: Created invoice record
        
    Raises:
        ValidationError: If amount <= 0
        ValidationError: If product has no income account
    
    Side Effects:
        - Creates account.move
        - Links invoice to self.invoice_id
        - Changes state to 'invoice'
    """
```

**Usage:**

```python
fee_detail = env['op.student.fees.details'].browse(123)
invoice = fee_detail.get_invoice()
print(f"Invoice: {invoice.name}")
```

##### `action_get_invoice()`

```python
def action_get_invoice(self):
    """
    UI action wrapper for get_invoice()
    
    Returns:
        dict: ir.actions.act_window to open created invoice
        
    Example return:
        {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
    """
```

**Usage in XML:**

```xml
<button name="action_get_invoice" type="object" 
        string="Get Invoice" 
        invisible="state != 'draft'"/>
```

---

### op.student (Inherited)

Extended student model with fee functionality.

#### Added Fields

| Field | Type | Description |
|-------|------|-------------|
| `fees_detail_ids` | One2many | Student fee records |
| `fees_details_count` | Integer | Count of fee records (for smart button) |

#### Methods

##### `_compute_fees_details()`

```python
@api.depends('fees_detail_ids')
def _compute_fees_details(self):
    """Computes count of fee detail records"""
    for record in self:
        record.fees_details_count = len(record.fees_detail_ids)
```

##### `action_view_invoice()`

```python
def action_view_invoice(self):
    """
    Opens list view of all invoices related to student fees
    
    Returns:
        dict: ir.actions.act_window showing filtered invoices
        
    Example:
        Opens account.move list filtered to this student's fee invoices
    """
```

**Usage in XML:**

```xml
<button name="action_view_invoice" type="object"
        string="Invoices" 
        invisible="fees_details_count == 0"/>
```

---

### op.course (Inherited)

Extended course model with fee term assignment.

#### Added Fields

| Field | Type | Description |
|-------|------|-------------|
| `fees_term_id` | Many2one | Assigned fee term (op.fees.terms) |

**Usage:**

```python
course = env['op.course'].browse(COURSE_ID)
course.fees_term_id = env['op.fees.terms'].search([('code', '=', 'S1-2025')], limit=1)
```

---

### op.student.course (Inherited)

Extended student-course enrollment with fee tracking.

#### Added Fields

| Field | Type | Description |
|-------|------|-------------|
| `fees_term_id` | Many2one | Fee term for this enrollment |
| `fees_start_date` | Date | Date when fees start counting |

---

## Wizard APIs

### fees.detail.report.wizard

Report generation wizard.

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fees_filter` | Selection | ✓ | 'student' or 'course' |
| `student_id` | Many2one | | Student (if filter=student) |
| `course_id` | Many2one | | Course (if filter=course) |

#### Methods

```python
def print_report(self):
    """
    Generates PDF fees details report
    
    Returns:
        dict: Report action dictionary
    """
```

**API Usage:**

```python
wizard = env['fees.detail.report.wizard'].create({
    'fees_filter': 'student',
    'student_id': student.id,
})
report_action = wizard.print_report()
```

---

### select.fees.term.type.wizard

Fee term type selector.

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `fees_terms` | Selection | 'fixed_days' or 'fixed_date' |

#### Methods

```python
def action_open_wizard(self):
    """Opens wizard dialog"""

def select_term_type(self):
    """Returns action to create fee term with pre-filled type"""
```

---

## Report API

### report.openeducat_fees.report_fees_analysis

QWeb report abstract model.

#### Methods

```python
def get_invoice_amount(self, student_id):
    """
    Calculates total invoiced amount for student
    
    Args:
        student_id (int): Student ID
        
    Returns:
        float: Total invoice amount
    """

def get_paid_amount(self, student_id):
    """
    Calculates total paid amount
    
    Args:
        student_id (int): Student ID
        
    Returns:
        float: Total paid amount
    """

def get_unpaid_amount(self, student_id):
    """
    Calculates unpaid balance
    
    Args:
        student_id (int): Student ID
        
    Returns:
        float: Unpaid amount
    """

@api.model
def _get_report_values(self, docids, data=None):
    """
    Prepares context for report rendering
    
    Args:
        docids: Report document IDs
        data: Additional report data
        
    Returns:
        dict: Report context with computed values
    """
```

---

## External API (XML-RPC / JSON-RPC)

### Create Fee Detail via External API

```python
import xmlrpc.client

url = 'http://localhost:8069'
db = 'your_database'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Create fee detail
fee_detail_id = models.execute_kw(db, uid, password,
    'op.student.fees.details', 'create',
    [{
        'student_id': 123,
        'product_id': 456,
        'amount': 5000.0,
        'date': '2025-01-15',
        'state': 'draft',
    }])

print(f"Created fee detail: {fee_detail_id}")

# Generate invoice
invoice_id = models.execute_kw(db, uid, password,
    'op.student.fees.details', 'get_invoice',
    [[fee_detail_id]])

print(f"Created invoice: {invoice_id}")
```

---

## ORM Examples

### Search & Filter

```python
# Find all active fee terms
terms = env['op.fees.terms'].search([('active', '=', True)])

# Find draft fees for a student
fees = env['op.student.fees.details'].search([
    ('student_id', '=', student_id),
    ('state', '=', 'draft'),
])

# Find overdue fees
today = fields.Date.today()
overdue = env['op.student.fees.details'].search([
    ('date', '<', today),
    ('state', '=', 'draft'),
])
```

### Read & Browse

```python
# Browse by ID
term = env['op.fees.terms'].browse(123)
print(term.name, term.code)

# Read specific fields
data = env['op.student.fees.details'].read([456], ['student_id', 'amount', 'state'])
```

### Create

```python
# Create fee term with lines
term = env['op.fees.terms'].create({
    'name': 'Annual Fees 2025',
    'code': 'ANN-2025',
    'fees_terms': 'fixed_days',
    'line_ids': [
        (0, 0, {
            'due_days': 0,
            'value': 33.33,
        }),
        (0, 0, {
            'due_days': 120,
            'value': 33.33,
        }),
        (0, 0, {
            'due_days': 240,
            'value': 33.34,
        }),
    ]
})
```

### Update

```python
# Update fee detail
fee_detail = env['op.student.fees.details'].browse(789)
fee_detail.write({
    'discount': 10.0,
    'amount': 9000.0,
})
```

### Delete

```python
# Delete fee detail (if allowed)
fee_detail.unlink()

# Soft delete (archive)
fee_detail.state = 'cancel'
```

---

## Computed Field Examples

### Custom Computed Field

```python
class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    total_with_tax = fields.Monetary(
        compute='_compute_total_with_tax',
        currency_field='currency_id'
    )
    
    @api.depends('after_discount_amount')
    def _compute_total_with_tax(self):
        for record in self:
            tax_rate = 0.15  # 15% tax
            record.total_with_tax = record.after_discount_amount * (1 + tax_rate)
```

---

## Onchange Examples

### Auto-fill Product Amount

```python
class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.amount = self.product_id.lst_price
```

---

## Constraint Examples

### Add Custom Validation

```python
class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    @api.constrains('amount', 'discount')
    def _check_discount_limit(self):
        for record in self:
            if record.discount > 50:
                raise ValidationError(_('Discount cannot exceed 50%'))
            if record.after_discount_amount < 0:
                raise ValidationError(_('Amount after discount must be positive'))
```

---

## Action Examples

### Custom Action Method

```python
def action_send_reminder(self):
    """Send fee reminder to student"""
    self.ensure_one()
    template = self.env.ref('custom.fee_reminder_email')
    template.send_mail(self.id, force_send=True)
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'message': _('Reminder sent successfully'),
            'type': 'success',
            'sticky': False,
        }
    }
```

---

## Batch Operations

### Bulk Invoice Creation

```python
# Get all draft fees for a course
course = env['op.course'].browse(COURSE_ID)
fee_details = env['op.student.fees.details'].search([
    ('course_id', '=', course.id),
    ('state', '=', 'draft'),
])

# Create invoices in batch
invoices = env['account.move']
for fee in fee_details:
    invoice = fee.get_invoice()
    invoices |= invoice

print(f"Created {len(invoices)} invoices")
```

### Bulk Discount Application

```python
# Apply 10% discount to all draft fees in a batch
batch = env['op.batch'].browse(BATCH_ID)
fee_details = env['op.student.fees.details'].search([
    ('batch_id', '=', batch.id),
    ('state', '=', 'draft'),
])

fee_details.write({'discount': 10.0})
```

---

## Search Domain Examples

### Complex Filters

```python
# Students with unpaid fees
unpaid_fees = env['op.student.fees.details'].search([
    ('state', '=', 'invoice'),
    ('invoice_state', '!=', 'paid'),
])

# Fees due this month
from datetime import datetime
start = datetime(2025, 1, 1).date()
end = datetime(2025, 1, 31).date()

this_month = env['op.student.fees.details'].search([
    ('date', '>=', start),
    ('date', '<=', end),
    ('state', '=', 'draft'),
])

# High-value fees (> $1000)
high_value = env['op.student.fees.details'].search([
    ('amount', '>', 1000),
])
```

---

## Integration Examples

### With Accounting Module

```python
# Get invoice lines from fee
fee_detail = env['op.student.fees.details'].browse(FEE_ID)
if fee_detail.invoice_id:
    invoice_lines = fee_detail.invoice_id.invoice_line_ids
    for line in invoice_lines:
        print(f"Product: {line.product_id.name}, Amount: {line.price_total}")
```

### With Student Enrollment

```python
# Auto-generate fees when student enrolls
class OpStudentCourse(models.Model):
    _inherit = 'op.student.course'
    
    @api.model
    def create(self, vals):
        enrollment = super().create(vals)
        # Auto-generate fees based on course term
        if enrollment.course_id.fees_term_id:
            enrollment._generate_fees()
        return enrollment
    
    def _generate_fees(self):
        """Generate fee details from course fee term"""
        # Implementation here
        pass
```

---

## Scheduled Actions (Cron)

### Fee Reminder Automation

```python
# Add to your custom module

def _cron_send_fee_reminders(self):
    """Send reminders for upcoming fees (next 7 days)"""
    from datetime import timedelta
    today = fields.Date.today()
    next_week = today + timedelta(days=7)
    
    upcoming_fees = self.env['op.student.fees.details'].search([
        ('date', '>=', today),
        ('date', '<=', next_week),
        ('state', '=', 'draft'),
    ])
    
    template = self.env.ref('custom.fee_reminder_template')
    for fee in upcoming_fees:
        template.send_mail(fee.id)
```

**Register cron:**

```xml
<record id="ir_cron_fee_reminder" model="ir.cron">
    <field name="name">Send Fee Reminders</field>
    <field name="model_id" ref="model_op_student_fees_details"/>
    <field name="state">code</field>
    <field name="code">model._cron_send_fee_reminders()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
</record>
```

---

## REST API Examples (Odoo REST API)

### Using Odoo REST endpoints

```python
import requests
import json

url = "http://localhost:8069"
db = "your_database"
username = "admin"
password = "admin"

# Authenticate
session = requests.Session()
login = session.post(f"{url}/web/session/authenticate", json={
    "jsonrpc": "2.0",
    "params": {
        "db": db,
        "login": username,
        "password": password
    }
})

# Create fee detail
response = session.post(f"{url}/web/dataset/call_kw", json={
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "op.student.fees.details",
        "method": "create",
        "args": [{
            "student_id": 123,
            "amount": 5000.0,
            "product_id": 456,
            "date": "2025-01-15"
        }],
        "kwargs": {}
    }
})

fee_id = response.json()['result']
print(f"Created fee: {fee_id}")

# Generate invoice
invoice_response = session.post(f"{url}/web/dataset/call_kw", json={
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "op.student.fees.details",
        "method": "get_invoice",
        "args": [[fee_id]],
        "kwargs": {}
    }
})

print(f"Invoice: {invoice_response.json()}")
```

---

## Event Hooks

### Override Create

```python
class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    @api.model_create_multi
    def create(self, vals_list):
        # Pre-processing
        for vals in vals_list:
            vals['custom_field'] = self._compute_custom_value(vals)
        
        # Call super
        records = super().create(vals_list)
        
        # Post-processing
        for record in records:
            record._post_create_actions()
        
        return records
```

### Override Write

```python
def write(self, vals):
    # Track old values
    old_states = {rec.id: rec.state for rec in self}
    
    # Call super
    result = super().write(vals)
    
    # Post-processing
    if 'state' in vals:
        for record in self:
            if old_states[record.id] != record.state:
                record._on_state_change(old_states[record.id], record.state)
    
    return result
```

---

## Performance Tips

### Use read_group for Aggregation

```python
# BAD: Iterate all records
total = sum(env['op.student.fees.details'].search([]).mapped('amount'))

# GOOD: Use read_group
result = env['op.student.fees.details'].read_group(
    domain=[('state', '=', 'draft')],
    fields=['amount:sum'],
    groupby=[]
)
total = result[0]['amount'] if result else 0
```

### Prefetch Related Records

```python
# BAD: N+1 queries
for fee in fee_details:
    print(fee.student_id.name)  # Query per iteration

# GOOD: Prefetch
fee_details = env['op.student.fees.details'].search([...])
fee_details.mapped('student_id')  # Prefetch all at once
for fee in fee_details:
    print(fee.student_id.name)  # No additional queries
```

---

## Code Examples Repository

All examples are tested with Odoo 18.0 and `openeducat_fees` version 18.0.1.0.

---

**Last Updated:** November 3, 2025  
**Module Version:** 18.0.1.0  
**API Version:** Stable

