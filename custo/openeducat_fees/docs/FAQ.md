# FAQ - OpenEduCat Fees Module

## General Questions

### Q: What is the purpose of this module?

**A:** The OpenEduCat Fees module manages fee collection and financial operations for educational institutions. It handles fee term configuration, student fee tracking, automated invoice generation, and financial reporting.

---

### Q: Which Odoo version is supported?

**A:** This module is designed for **Odoo 18.0**. It uses modern Odoo 18 conventions including list views, modern OWL components, and updated asset syntax.

---

### Q: Can I use this module standalone?

**A:** No. This module requires:
- `openeducat_core` - Core OpenEduCat functionality
- `account` - Odoo standard accounting module

---

## Installation & Setup

### Q: Installation fails with "Module not found" error

**A:** Check:
1. Module is in the `addons_path` configured in `odoo.conf`
2. Module list updated: Apps → Update Apps List
3. Dependencies (`openeducat_core`, `account`) are installed

---

### Q: How do I assign security groups to users?

**A:** 
1. Navigate to Settings → Users & Companies → Users
2. Select user
3. Edit → Other tab → scroll to "Fees" section
4. Assign: **Fees User** or **Fees Manager**

---

### Q: Do I need to configure Chart of Accounts?

**A:** Yes! Fee invoice generation requires:
- Chart of Accounts installed (Accounting → Configuration)
- Income accounts configured on fee products
- Products must have account settings

---

## Fee Terms

### Q: What's the difference between "Fixed Days" and "Fixed Dates"?

**A:**

**Fixed Days:**
- Fees due based on **days after enrollment**
- Example: Day 0, Day 30, Day 60
- Use when: Students enroll at different times

**Fixed Dates:**
- Fees due on **specific calendar dates**
- Example: 2025-01-15, 2025-02-15
- Use when: All students pay on same dates

---

### Q: Why do I get "Fees terms must be divided as such sum up in 100%" error?

**A:** The sum of all fee term line percentages must equal exactly 100%.

**Check:**
```
Line 1: 40%
Line 2: 30%
Line 3: 30%
Total:  100% ✓ Correct
```

**Fix:**
- Edit fee term
- Adjust line values to sum to 100%
- Save

---

### Q: Can I modify a fee term after students are enrolled?

**A:** ⚠️ **Not recommended**. Changing an active fee term affects:
- Existing student fee details
- Already-generated invoices
- Financial records

**Best practice:**
- Archive old term (uncheck Active)
- Create new term for next period

---

### Q: How do I archive an old fee term?

**A:**
1. Open Fees → Fees Terms
2. Select the term
3. Uncheck **Active** field
4. Save

**Note:** Archived terms hidden from selection but data remains intact.

---

## Student Fees

### Q: Fees not auto-generating for students. Why?

**A:** Check these conditions:

1. ✓ Fee term assigned to course?
   - Courses → Select Course → Check "Fees Term" field

2. ✓ Fee term is active?
   - Fees Terms → Check "Active" checkbox

3. ✓ Student enrolled in course?
   - Students → Student record → Courses tab

4. ✓ Module logic triggered?
   - May require custom enrollment workflow

---

### Q: How do I manually add a fee for a student?

**A:**
1. Go to Fees → Student Fees Details → Create
2. Fill required fields:
   - Student
   - Product (fee type)
   - Amount
   - Date
3. Save

---

### Q: Can students have different discounts?

**A:** Yes! Two levels:

**Term-level discount:** (applies to all)
- Set in Fee Term → Discount field

**Student-level discount:** (individual)
- Set in Student Fees Details → Discount field

Student-level overrides term-level.

---

### Q: What happens if I delete a student with fee records?

**A:** 
- Fee details are NOT auto-deleted (foreign key constraint)
- You must handle fees first:
  - Cancel fees: Set state to 'cancel'
  - Delete manually if no invoices
  - Or keep for audit trail

---

## Invoices

### Q: "Get Invoice" button doesn't work. Why?

**A:** Common causes:

1. **No income account on product**
   - Fix: Products → Select product → Accounting tab → Set Income Account

2. **Amount is zero or negative**
   - Fix: Edit fee detail, set positive amount

3. **User lacks accounting rights**
   - Fix: Settings → Users → Assign accounting group

4. **Chart of Accounts not configured**
   - Fix: Accounting → Configuration → Install Chart

---

### Q: Can I generate invoices in bulk?

**A:** Yes!

1. Go to Fees → Student Fees Details
2. Filter: State = Draft
3. Select multiple records (checkboxes)
4. Action menu → Get Invoice (if action available)

Or use Python:

```python
fees = env['op.student.fees.details'].search([('state', '=', 'draft')])
for fee in fees:
    fee.get_invoice()
```

---

### Q: Invoice created but state still "Draft"?

**A:** Check:
- `get_invoice()` method completed successfully?
- Check Odoo logs for errors
- Verify invoice actually created: Accounting → Invoices

State should auto-update to 'invoice' after successful creation.

---

### Q: Can I edit a fee detail after invoice is created?

**A:** 
- **Amount/Discount:** No (invoice already exists)
- **Non-financial fields:** Yes

**To change amount:**
1. Cancel original invoice
2. Cancel fee detail (state = 'cancel')
3. Create new fee detail
4. Generate new invoice

---

## Reports

### Q: How do I generate a fees report for a specific student?

**A:**
1. Fees → Reports → Fees Details Report
2. Filter: **Student**
3. Select student from dropdown
4. Click **Print**
5. PDF downloads

---

### Q: Report shows wrong amounts

**A:** Check:
- Discount applied correctly?
- Currency conversion (multi-currency)?
- Data caching issue: Refresh browser

Verify in database:

```sql
SELECT student_id, SUM(amount), SUM(after_discount_amount)
FROM op_student_fees_details
WHERE student_id = XXX
GROUP BY student_id;
```

---

## Technical Questions

### Q: Which fields are computed vs stored?

**A:**

**Computed (not stored):**
- `after_discount_amount` - Calculated from amount & discount
- `currency_id` - From company
- `fees_details_count` - Count of related records
- `invoice_state` - Related field from invoice

**Stored:**
- All other fields (amount, discount, state, etc.)

---

### Q: How do I extend the module with custom fields?

**A:**

```python
# In your custom module
class CustomStudentFees(models.Model):
    _inherit = 'op.student.fees.details'
    
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
    ], string='Payment Method')
```

Add to view:

```xml
<xpath expr="//field[@name='discount']" position="after">
    <field name="payment_method"/>
</xpath>
```

---

### Q: Does this module support multi-company?

**A:** Yes! 
- All models have `company_id` field
- Record rules filter by company
- Users see only their company's data

---

### Q: Can I customize the invoice generated?

**A:** Yes! Override `get_invoice()` method:

```python
class CustomFees(models.Model):
    _inherit = 'op.student.fees.details'
    
    def get_invoice(self):
        invoice = super().get_invoice()
        # Customize invoice
        invoice.invoice_payment_term_id = self.custom_payment_term
        return invoice
```

---

## Errors & Troubleshooting

### Q: Error: "Fees Terms must be Required!"

**A:** This error means:
- Fee term is required but not set
- Usually on course or student.course

**Fix:**
- Assign fee term to course before enrolling students

---

### Q: Error: "The value of the deposit amount must be positive"

**A:**
- Fee amount must be > 0
- Check `amount` field
- Ensure no negative values

---

### Q: Error: "There is no income account defined for this product"

**A:**
1. Go to Products → Select fee product
2. Accounting tab
3. Set **Income Account**
4. Save

Or configure in Product Categories.

---

### Q: Views showing `<tree>` instead of `<list>`

**A:** This shouldn't happen in Odoo 18. If it does:
1. Clear browser cache (Ctrl + Shift + Delete)
2. Restart Odoo completely
3. Check module version (should be 18.0.x.x)

This module uses Odoo 18 `<list>` views exclusively.

---

## Workflow Questions

### Q: What's the recommended fee collection workflow?

**A:**

**Start of Term:**
1. Create fee term for semester/year
2. Assign to all courses
3. Students enroll (fees auto-generate)

**Monthly:**
4. Generate invoices for dues this month
5. Send reminders
6. Track payments in Accounting

**End of Term:**
7. Run reports
8. Archive old fee term
9. Prepare next term

---

### Q: How do I handle late payments?

**A:**

**Option 1: Late fee (recommended)**
- Create "Late Fee" product
- Manually add to student fee details

**Option 2: Custom workflow**
- Add custom field: `late_fee_percentage`
- Override `get_invoice()` to add late charges

**Option 3: Penalty in Accounting**
- Create invoice manually with penalty line

---

### Q: Can I split payments across multiple installments?

**A:** Yes! That's the purpose of Fee Terms.

**Example:**
- Total fee: $12,000
- Term with 3 lines:
  - Line 1: 33.33% ($4,000) - Due immediately
  - Line 2: 33.33% ($4,000) - Due Day 30
  - Line 3: 33.34% ($4,000) - Due Day 60

Each generates separate fee detail + invoice.

---

## Data Questions

### Q: Can I import fee data from Excel?

**A:** Yes! Via Odoo import feature:

1. Fees → Student Fees Details → Favorites → Import Records
2. Download template
3. Fill Excel with: student_id, product_id, amount, date
4. Upload and map columns
5. Import

**Note:** Use External IDs for student_id and product_id.

---

### Q: How do I export fee data?

**A:**
1. Fees → Student Fees Details
2. Filter as needed
3. Select records (or "Select All")
4. Action → Export
5. Choose fields
6. Download CSV/Excel

---

### Q: Where is fee data stored in the database?

**A:** 
- Fee terms: `op_fees_terms` table
- Student fees: `op_student_fees_details` table
- Invoices: `account_move` table (standard Odoo)

Query example:

```sql
SELECT s.name AS student, f.amount, f.state, i.name AS invoice
FROM op_student_fees_details f
JOIN op_student s ON s.id = f.student_id
LEFT JOIN account_move i ON i.id = f.invoice_id
WHERE f.state = 'invoice';
```

---

## Integration Questions

### Q: Does this integrate with payment gateways?

**A:** Not directly. Integration happens via Odoo Accounting:
- Fees module creates invoices
- Accounting module handles payments
- Configure payment acquirers in Accounting → Configuration

---

### Q: Can I send invoices via email?

**A:** Yes! Via Accounting module:
1. Open invoice (from fee detail)
2. Click "Send by Email" button
3. Odoo sends email with PDF attachment

Or automate:

```python
invoice = fee_detail.invoice_id
template = env.ref('account.email_template_edi_invoice')
template.send_mail(invoice.id)
```

---

### Q: Does this work with student portal?

**A:** 
- Fees module itself doesn't provide portal views
- Invoices are accessible via Accounting portal
- Students can view/pay invoices through Odoo portal

**Extend for portal:**
```python
# Add to your custom module
_inherit = ['op.student.fees.details', 'portal.mixin']
```

---

## Customization Questions

### Q: Can I add custom states to fee details?

**A:** Yes!

```python
class CustomFees(models.Model):
    _inherit = 'op.student.fees.details'
    
    state = fields.Selection(
        selection_add=[
            ('partial', 'Partially Paid'),
            ('overdue', 'Overdue'),
        ],
        ondelete={'partial': 'set default', 'overdue': 'set default'}
    )
```

---

### Q: Can I change the invoice template?

**A:** Yes! Invoices use standard `account.move`:
- Customize via Accounting module settings
- Or inherit QWeb invoice template
- Modify in: Accounting → Configuration → Invoice Layout

---

## Best Practices

### Q: What's the best way to structure fee products?

**A:**

**Categorize by type:**
```
Product Category: Academic Fees
├── Tuition Fees
├── Lab Fees
└── Examination Fees

Product Category: Non-Academic Fees
├── Library Fees
├── Transportation Fees
└── Hostel Fees
```

**Benefits:**
- Better reporting
- Easier filtering
- Clear accounting

---

### Q: Should I use percentage or fixed amount in fee elements?

**A:** 
- **Percentage** (`value` field) - For flexible fee distribution
- **Product price** - Set actual amount

**Example:**
- Product "Tuition" has price: $5,000
- Fee element value: 100%
- Calculated amount: $5,000 × 100% = $5,000

---

### Q: How often should I archive old fee terms?

**A:**
- Archive at end of each academic period
- Keep current + next term active
- Archive doesn't delete data, just hides from UI

---

## Troubleshooting

### Q: Students can't see their fees in portal

**A:**
- Fees module doesn't provide portal views by default
- Students see invoices via Accounting portal
- Extend module for custom portal views

---

### Q: Discount not applying correctly

**A:** Check:

1. Discount field filled? (0-100)
2. Computed field refreshed? (save record)
3. Check calculation:
   ```python
   discount_amount = amount * (discount / 100.0)
   final = amount - discount_amount
   ```

---

### Q: Invoice shows wrong company

**A:**
- Check user's company
- Check fee detail `company_id`
- Verify company on course/student

Multi-company issues usually stem from mismatched company_id.

---

## Performance

### Q: Slow when generating many invoices

**A:** For bulk operations:

```python
# Use with self.env.norecompute()
with self.env.norecompute():
    for fee in fee_details:
        fee.get_invoice()
self.env['account.move'].recompute()
```

Or process in batches (100-500 at a time).

---

### Q: Database growing too large

**A:**

**Archive old records:**
- Archive fee terms (uncheck Active)
- Don't delete (maintain audit trail)

**Purge if absolutely necessary:**
```sql
-- Backup first!
DELETE FROM op_student_fees_details 
WHERE state = 'cancel' 
AND create_date < '2020-01-01';
```

---

## Migration

### Q: How do I upgrade from Odoo 17?

**A:**
1. Backup database completely
2. Update Odoo to 18
3. Update module code (tree → list views)
4. Run upgrade: `--update=openeducat_fees`
5. Test thoroughly
6. Clear caches

See [MIGRATION.md](./MIGRATION.md) for details.

---

### Q: Can I downgrade to Odoo 17?

**A:** ⚠️ **Not recommended**. 
- Odoo 18 changes are not backward compatible
- List views won't work in Odoo 17
- Restore from pre-upgrade backup instead

---

## Advanced

### Q: Can I create custom fee calculation logic?

**A:** Yes! Override compute methods:

```python
class CustomFees(models.Model):
    _inherit = 'op.student.fees.details'
    
    @api.depends('discount', 'student_id.scholarship_amount')
    def _compute_discount_amount(self):
        for record in self:
            # Custom logic
            scholarship = record.student_id.scholarship_amount
            discount = record.amount * record.discount / 100.0
            record.after_discount_amount = record.amount - discount - scholarship
```

---

### Q: Can I automate fee reminders?

**A:** Yes! Create scheduled action:

1. Settings → Technical → Automation → Scheduled Actions → Create
2. Model: `op.student.fees.details`
3. Code:
   ```python
   model._send_fee_reminders()
   ```
4. Interval: Daily

Implement `_send_fee_reminders()` in your custom module.

---

### Q: How do I add a payment gateway?

**A:**
- This module creates invoices
- Payment gateway integration happens in `account` module
- Configure: Accounting → Configuration → Payment Acquirers
- Examples: Stripe, PayPal, Authorize.net

---

## Still Have Questions?

### Resources

- [Technical Reference](./TECHNICAL.md) - Architecture details
- [User Guide](./USER_GUIDE.md) - Step-by-step instructions
- [API Documentation](./API.md) - Code examples
- [Development Guide](./DEVELOPMENT.md) - Extension guide

### Support

- **Odoo Documentation:** https://www.odoo.com/documentation/18.0/
- **Odoo Forum:** https://www.odoo.com/forum
- **GitHub Issues:** Create issue in your repository
- **Commercial Support:** https://www.edafa.org

---

**Last Updated:** November 3, 2025  
**Module Version:** 18.0.1.0

