# Technical Reference - OpenEduCat Fees Module

## Architecture Overview

```
┌─────────────────────────────────────┐
│       op.course                     │
│  + fees_term_id (Many2one)          │
└──────────────┬──────────────────────┘
               │
               ↓ inherits term
┌──────────────────────────────────────────┐
│       op.fees.terms                      │
│  + name, code, fees_terms                │
│  + line_ids (One2many)                   │
│  + discount                              │
│  Inherits: mail.thread                   │
└──────────────┬───────────────────────────┘
               │
               ↓ has many
┌──────────────────────────────────────────┐
│     op.fees.terms.line                   │
│  + due_days / due_date                   │
│  + value (%)                             │
│  + fees_element_line (One2many)          │
└──────────────┬───────────────────────────┘
               │
               ↓ has many
┌──────────────────────────────────────────┐
│      op.fees.element                     │
│  + product_id (Many2one)                 │
│  + value (%)                             │
│  + sequence                              │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│       op.student                         │
│  + fees_detail_ids (One2many)            │
│  + fees_details_count (computed)         │
└──────────────┬───────────────────────────┘
               │
               ↓ has many
┌──────────────────────────────────────────┐
│    op.student.fees.details               │
│  + student_id, course_id, batch_id       │
│  + amount, discount                      │
│  + state (draft/invoice/cancel)          │
│  + invoice_id (Many2one account.move)    │
│  + fees_line_id (Many2one)               │
└──────────────────────────────────────────┘
```

---

## Model Details

### 1. op.fees.terms

**Purpose:** Define fee payment term templates

**Inheritance:** `mail.thread` (tracking, chatter)

**Key Fields:**

```python
name = fields.Char('Name', required=True)
code = fields.Char('Code', required=True)
active = fields.Boolean('Active', default=True)
fees_terms = fields.Selection([
    ('fixed_days', 'Fixed Fees of Days'),
    ('fixed_date', 'Fixed Fees of Dates')
], string='Term Type', default='fixed_days')
line_ids = fields.One2many('op.fees.terms.line', 'fees_id', 'Terms')
discount = fields.Float(string='Discount (%)', default=0.0)
company_id = fields.Many2one('res.company', 'Company')
```

**Constraints:**

```python
@api.constrains("line_ids")
def terms_validation(self):
    # Validates that line values sum to 100%
    total = sum(self.line_ids.mapped('value'))
    if total != 100:
        raise ValidationError(_('Fees terms must be divided as such sum up in 100%'))
```

**Important:** Fee term percentages MUST sum to exactly 100%

---

### 2. op.fees.terms.line

**Purpose:** Individual installment lines within a fee term

**Key Fields:**

```python
due_days = fields.Integer('Due Days')           # For fixed_days type
due_date = fields.Date('Due Date')              # For fixed_date type
value = fields.Float('Value (%)')               # Percentage (0-100)
fees_element_line = fields.One2many('op.fees.element', 
                                    'fees_terms_line_id', 
                                    'Fees Elements')
fees_id = fields.Many2one('op.fees.terms', 'Fees')
```

**Business Logic:**
- If fees_terms == 'fixed_days': use `due_days`
- If fees_terms == 'fixed_date': use `due_date`

---

### 3. op.fees.element

**Purpose:** Associate products (fee types) with term lines

**Key Fields:**

```python
product_id = fields.Many2one('product.product', 'Product(s)', required=True)
value = fields.Float('Value (%)')               # Weight within this line
sequence = fields.Integer('Sequence')            # Display order
fees_terms_line_id = fields.Many2one('op.fees.terms.line', 'Fees Terms')
```

**Example:**
For a line worth 40% of total:
- Admission Fee (product) → value: 50% (20% of total)
- Library Fee (product) → value: 50% (20% of total)

---

### 4. op.student.fees.details

**Purpose:** Track individual student fee obligations

**Key Fields:**

```python
student_id = fields.Many2one('op.student', 'Student', required=True)
course_id = fields.Many2one('op.course', 'Course')
batch_id = fields.Many2one('op.batch', 'Batch')
product_id = fields.Many2one('product.product', 'Product')
amount = fields.Monetary('Fees Amount', currency_field='currency_id')
discount = fields.Float(string='Discount (%)', default=0.0)
after_discount_amount = fields.Monetary(compute='_compute_discount_amount')
date = fields.Date('Submit Date')              # Due date
state = fields.Selection([
    ('draft', 'Draft'),
    ('invoice', 'Invoice Created'),
    ('cancel', 'Cancel')
], string='Status', copy=False)
invoice_id = fields.Many2one('account.move', 'Invoice ID')
invoice_state = fields.Selection(related="invoice_id.state")
fees_line_id = fields.Many2one('op.fees.terms.line', 'Fees Line')
company_id = fields.Many2one('res.company', 'Company')
currency_id = fields.Many2one('res.currency', compute='_compute_currency_id')
```

**Computed Fields:**

```python
@api.depends('discount')
def _compute_discount_amount(self):
    for record in self:
        discount_amount = record.amount * record.discount / 100.0
        record.after_discount_amount = record.amount - discount_amount
```

**Methods:**

```python
def get_invoice(self):
    """Creates account.move invoice from fee detail"""
    # Creates invoice
    # Links invoice to fee detail
    # Updates state to 'invoice'
    
def action_get_invoice(self):
    """Action wrapper for get_invoice"""
    # Returns action to open created invoice
```

---

## Database Schema

### Tables Created

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `op_fees_terms` | Fee terms | id, name, code, fees_terms, discount |
| `op_fees_terms_line` | Term lines | id, fees_id, due_days, due_date, value |
| `op_fees_element` | Fee elements | id, fees_terms_line_id, product_id, value |
| `op_student_fees_details` | Student fees | id, student_id, amount, state, invoice_id |

### Foreign Keys

```sql
-- op_fees_terms_line
fees_id → op_fees_terms(id)

-- op_fees_element  
fees_terms_line_id → op_fees_terms_line(id)
product_id → product_product(id)

-- op_student_fees_details
student_id → op_student(id)
course_id → op_course(id)
batch_id → op_batch(id)
product_id → product_product(id)
invoice_id → account_move(id)
fees_line_id → op_fees_terms_line(id)
```

---

## Views (Odoo 18 Compliant)

### List Views (NOT tree)

All views use `<list>` tag (Odoo 18 standard):

```xml
<list string="Fees Reminder Terms">
    <field name="name"/>
    <field name="code"/>
    <field name="fees_terms"/>
    <field name="active"/>
</list>
```

**Note:** No deprecated `<tree>` views in this module.

### Form Views

Use modern Odoo 18 syntax:

```xml
<!-- Modern (Odoo 18) -->
<field name="active" invisible="state != 'draft'"/>

<!-- NOT deprecated attrs -->
<!-- <field name="active" attrs="{'invisible': [('state', '!=', 'draft')]}"/> -->
```

### Search Views

Comprehensive search with filters, group_by:

```xml
<search>
    <field name="name"/>
    <field name="code"/>
    <filter name="archived" string="Archived" 
            domain="[('active', '=', False)]"/>
    <group expand="0" string="Group By">
        <filter string="Term Type" name="fees_terms" 
                context="{'group_by': 'fees_terms'}"/>
    </group>
</search>
```

---

## JavaScript/OWL Components

### FeesTermsDisplay Widget

**File:** `static/src/js/fees_term_widget.js`

**Purpose:** Visual term type selector with icons

**Component:**

```javascript
export class FeesTermsDisplay extends Component {
    static template = "website.FieldFeesTermsDisplay";
    static props = {
        ...standardFieldProps,
    };
    
    onSelectValue(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}
```

**Registration:**

```javascript
registry.category("fields").add("fees_term_display", {
    component: FeesTermsDisplay,
});
```

**Usage in views:**

```xml
<field name="fees_terms" widget="fees_term_display"/>
```

---

## Security

### Access Control (ir.model.access.csv)

| Model | Group | Read | Write | Create | Delete |
|-------|-------|------|-------|--------|--------|
| op.fees.terms | Fees User | ✓ | ✓ | ✓ | ✗ |
| op.fees.terms | Fees Manager | ✓ | ✓ | ✓ | ✓ |
| op.fees.terms.line | Fees User | ✓ | ✓ | ✓ | ✓ |
| op.fees.element | Fees User | ✓ | ✓ | ✓ | ✓ |
| op.student.fees.details | Fees User | ✓ | ✓ | ✓ | ✗ |
| op.student.fees.details | Fees Manager | ✓ | ✓ | ✓ | ✓ |

### Record Rules

Defined in `security/op_security.xml`:
- Multi-company rules (users see own company data only)
- Security groups enforce separation of concerns

---

## API Reference

### Public Methods

#### op.fees.terms

```python
@api.constrains("line_ids")
def terms_validation(self):
    """Validates fee term line percentages sum to 100%"""
```

#### op.student.fees.details

```python
def get_invoice(self):
    """
    Creates an account.move invoice from fee detail
    
    Returns:
        account.move: Created invoice record
        
    Raises:
        ValidationError: If amount <= 0
        ValidationError: If no income account on product
    """

def action_get_invoice(self):
    """
    Action wrapper to create invoice and return action to view it
    
    Returns:
        dict: ir.actions.act_window to open created invoice
    """
```

#### op.student

```python
@api.depends('fees_detail_ids')
def _compute_fees_details(self):
    """Computes count of fee detail records for smart button"""

def action_view_invoice(self):
    """
    Opens list of all invoices related to student fees
    
    Returns:
        dict: ir.actions.act_window action
    """
```

---

## Wizards

### 1. fees.detail.report.wizard

**Purpose:** Generate fee details report

**Fields:**
- `fees_filter` - Filter by student or course
- `student_id` - Selected student (if filter=student)
- `course_id` - Selected course (if filter=course)

**Method:**

```python
def print_report(self):
    """Generates PDF report with fee analysis"""
    return self.env.ref('openeducat_fees.action_report_fees_detail_analysis')\
        .report_action(self, data=data)
```

### 2. select.fees.term.type.wizard

**Purpose:** Select fee term type before creation

**Flow:**
1. User clicks "Create" on fee terms
2. Wizard appears
3. User selects type (fixed days/fixed dates)
4. Redirects to form with pre-filled type

---

## Reports

### QWeb Report: report_fees_analysis

**Template:** `report/fees_analysis_report_view.xml`

**AbstractModel:** `report.openeducat_fees.report_fees_analysis`

**Methods:**

```python
def get_invoice_amount(self, student_id):
    """Calculates total invoice amount for student"""

def get_paid_amount(self, student_id):
    """Calculates total paid amount"""

def get_unpaid_amount(self, student_id):
    """Calculates unpaid balance"""

@api.model
def _get_report_values(self, docids, data=None):
    """Prepares data for report rendering"""
```

---

## Data Flow

### Fee Generation Flow

```
1. Admin creates Fee Term
   ↓
2. Fee Term Lines added (with percentages)
   ↓
3. Fee Elements assigned to lines
   ↓
4. Fee Term assigned to Course
   ↓
5. Student enrolls in Course
   ↓
6. System generates op.student.fees.details records
   ↓
7. User clicks "Get Invoice"
   ↓
8. account.move created and linked
   ↓
9. State changes to 'invoice'
   ↓
10. Payment processed in Accounting
```

### Invoice Creation Logic

```python
# From op.student.fees.details.get_invoice()

1. Validate amount > 0
2. Get product income account
3. Create account.move:
   - move_type: 'out_invoice'
   - partner_id: student.partner_id
   - invoice_date: fee_detail.date
   - invoice_line_ids: product, amount
4. Link invoice to fee_detail
5. Update state to 'invoice'
6. Return invoice
```

---

## Extension Points

### Inherit Fees Terms

```python
class CustomFeesTerms(models.Model):
    _inherit = 'op.fees.terms'
    
    custom_field = fields.Char('Custom Field')
    
    def custom_method(self):
        # Your logic here
        pass
```

### Inherit Student Fees Details

```python
class CustomStudentFees(models.Model):
    _inherit = 'op.student.fees.details'
    
    @api.constrains('amount')
    def _check_custom_amount(self):
        # Custom validation
        pass
```

### Add Custom Invoice Logic

```python
class CustomStudentFees(models.Model):
    _inherit = 'op.student.fees.details'
    
    def get_invoice(self):
        invoice = super().get_invoice()
        # Custom post-processing
        invoice.custom_field = self.custom_value
        return invoice
```

---

## Testing

### Unit Tests

Located in: `tests/`

**Test Classes:**

```python
class TestStudentFees(TestFeesCommon):
    """Tests for op.student.fees.details"""
    
class TestStudent(TestFeesCommon):
    """Tests for student fee integration"""
    
class TestWizardFees(TestFeesCommon):
    """Tests for fee wizards"""
    
class TestFeesTerms(TestFeesCommon):
    """Tests for fee terms validation"""
```

### Run Tests

```bash
# Run all fees tests
./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags openeducat_fees --stop-after-init

# Run specific test class
./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags openeducat_fees.test_fees_common --stop-after-init
```

---

## Performance Considerations

### Indexing

Recommended database indexes:

```sql
-- Speed up student fee lookups
CREATE INDEX idx_student_fees_student ON op_student_fees_details(student_id);
CREATE INDEX idx_student_fees_course ON op_student_fees_details(course_id);
CREATE INDEX idx_student_fees_state ON op_student_fees_details(state);

-- Speed up term lookups
CREATE INDEX idx_fees_terms_code ON op_fees_terms(code);
CREATE INDEX idx_fees_terms_active ON op_fees_terms(active);
```

### Query Optimization

**Avoid:**
```python
# BAD: N+1 queries
for student in students:
    fees = student.fees_detail_ids  # Separate query per student
```

**Prefer:**
```python
# GOOD: Batch prefetch
students = self.env['op.student'].search([...])
students.fees_detail_ids  # Prefetched in batch
```

---

## Internationalization (i18n)

### Supported Languages

13 languages fully translated:
- Arabic (ar_001)
- Danish (da_DK)
- German (de)
- Spanish (es)
- Persian (fa)
- French (fr)
- Indonesian (id)
- Italian (it)
- Latvian (lt)
- Dutch (nl)
- Portuguese (pt)
- Russian (ru)
- Thai (th)
- Vietnamese (vi, vi_VN)
- Chinese (zh_CN, zh_HK)

### Translation Files

Location: `i18n/*.po`

Update translations:

```bash
# Generate .pot file
./odoo-bin -c odoo.conf -d your_db --i18n-export=openeducat_fees.pot --modules=openeducat_fees

# Import translations
./odoo-bin -c odoo.conf -d your_db --i18n-import=i18n/ar_001.po --language=ar_001
```

---

## Integration Points

### With openeducat_core

**Inherits models:**
- `op.course` - Adds `fees_term_id` field
- `op.student` - Adds `fees_detail_ids` field
- `op.student.course` - Adds `fees_term_id`, `fees_start_date`

### With account (Accounting)

**Creates:**
- `account.move` (invoices)
- `account.move.line` (invoice lines)

**Requires:**
- Chart of Accounts configured
- Income accounts on products
- Customer (partner) on student

---

## Configuration

### Module Configuration

In `__manifest__.py`:

```python
'depends': ['openeducat_core', 'account'],
'data': [
    'security/op_security.xml',           # Load first (groups)
    'security/ir.model.access.csv',       # Then ACL
    'report/report_menu.xml',
    'report/fees_analysis_report_view.xml',
    'wizard/fees_detail_report_wizard_view.xml',
    'wizard/select_term_type.xml',
    'views/fees_terms_view.xml',
    'views/student_view.xml',
    'views/course_view.xml',
    'views/fees_element_view.xml',
],
'assets': {
    'web.assets_backend': [
        'openeducat_fees/static/src/js/page_list.js',
        'openeducat_fees/static/src/js/fees_term_widget.js',
        'openeducat_fees/static/src/xml/fees_term_widget_template.xml',
    ],
},
```

### Load Order

**Critical:** Security files must load before views/data

---

## Debugging

### Common Debug Scenarios

#### Fee term validation fails

```python
# Check in Python shell
term = env['op.fees.terms'].browse(TERM_ID)
total = sum(term.line_ids.mapped('value'))
print(f"Total: {total}% (must be 100%)")
```

#### Invoice not creating

```python
# Check product income account
product = env['product.product'].browse(PRODUCT_ID)
account = product.property_account_income_id
print(f"Income account: {account.name if account else 'NOT SET'}")
```

#### Fees not auto-generating

```python
# Check course has fee term
course = env['op.course'].browse(COURSE_ID)
print(f"Fee term: {course.fees_term_id.name if course.fees_term_id else 'NOT SET'}")
```

### Enable Developer Mode

Settings → Activate Developer Mode

Provides:
- View technical info
- Edit Python code
- Debug view architecture
- SQL query logging

---

## Migration & Upgrades

### Odoo 17 → 18

**Changes Made:**
1. ✅ All `<tree>` → `<list>` in XML views
2. ✅ Removed `attrs` usage (deprecated)
3. ✅ Removed `states` attribute
4. ✅ Updated OWL components
5. ✅ Assets syntax updated

**Migration Steps:**

```python
# Clear view cache after upgrade
self.env['ir.ui.view'].clear_caches()

# Refresh security
self.env['ir.model.access'].call_cache_clearing_methods()
```

---

## Customization Examples

### Add Custom Field to Fee Details

```python
# models/student.py

class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit Card'),
        ('bank', 'Bank Transfer'),
    ], string='Payment Method')
```

**Add to view:**

```xml
<xpath expr="//field[@name='discount']" position="after">
    <field name="payment_method"/>
</xpath>
```

### Add Automated Email Reminder

```python
class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    def send_fee_reminder(self):
        """Send email reminder for pending fees"""
        template = self.env.ref('custom_module.fee_reminder_template')
        for record in self.filtered(lambda r: r.state == 'draft'):
            template.send_mail(record.id, force_send=True)
```

---

## Performance Metrics

### Database Impact

**Tables:** 4 new tables  
**Average rows:**
- op_fees_terms: ~10-50 records
- op_fees_terms_line: ~30-200 records
- op_fees_element: ~50-300 records
- op_student_fees_details: ~1,000-100,000+ records (scales with students)

**Storage:** Minimal (~1-10 MB for typical institution)

### Query Performance

**Typical queries:**
- Student fees list: < 50ms
- Invoice generation: < 200ms
- Report rendering: < 500ms (depends on student count)

---

## Dependencies Graph

```
openeducat_fees
├── openeducat_core
│   ├── base
│   ├── mail
│   └── web
└── account
    ├── base
    ├── product
    └── account_tax
```

---

## API Integration Examples

### Create Fee Term via API

```python
term = env['op.fees.terms'].create({
    'name': 'Semester 1 - 2025',
    'code': 'S1-2025',
    'fees_terms': 'fixed_days',
    'discount': 5.0,
    'line_ids': [
        (0, 0, {
            'due_days': 0,
            'value': 40.0,
            'fees_element_line': [
                (0, 0, {
                    'product_id': admission_product.id,
                    'value': 100.0,
                })
            ]
        }),
        (0, 0, {
            'due_days': 30,
            'value': 60.0,
        })
    ]
})
```

### Generate Invoices via API

```python
# Get all draft fees
fee_details = env['op.student.fees.details'].search([('state', '=', 'draft')])

# Bulk invoice creation
for fee in fee_details:
    invoice = fee.get_invoice()
    print(f"Created invoice: {invoice.name}")
```

---

## File Manifest

### Python Files (9)

- `__init__.py` - Module init
- `models/__init__.py`, `models/*.py` (4 files)
- `report/__init__.py`, `report/*.py` (1 file)
- `wizard/__init__.py`, `wizard/*.py` (2 files)
- `tests/__init__.py`, `tests/*.py` (2 files)

### XML Files (12)

- Views: 4 files
- Reports: 2 files
- Wizards: 2 files
- Security: 2 files
- Demo: 6 files

### JavaScript/Assets (3)

- `static/src/js/*.js` (2 files)
- `static/src/xml/*.xml` (1 file)

### Translation Files (17)

- `.po` files for 13+ languages
- `.pot` template file

### Static Assets (27)

- Icons and images for UI

---

## Glossary

| Term | Definition |
|------|------------|
| **Fee Term** | Payment schedule template (installment plan) |
| **Term Line** | Individual installment within a term |
| **Fee Element** | Specific fee product (tuition, library, etc.) |
| **Fee Detail** | Student's fee obligation record |
| **Fixed Days** | Fees due X days after enrollment |
| **Fixed Dates** | Fees due on specific calendar dates |

---

## Related Documentation

- [Installation Guide](./INSTALLATION.md)
- [User Guide](./USER_GUIDE.md)
- [API Documentation](./API.md)
- [FAQ](./FAQ.md)
- [Development Guide](./DEVELOPMENT.md)

---

**Module Path:** `custom_addons/motakamel_training_academy/custom-addons/motakamel/openeducat_fees/`  
**Last Updated:** November 3, 2025  
**Odoo Version:** 18.0

