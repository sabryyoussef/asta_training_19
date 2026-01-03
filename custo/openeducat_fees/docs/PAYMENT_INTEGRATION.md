# 💳 Payment Integration Guide - OpenEduCat Fees Module

**Module:** `openeducat_fees`  
**Version:** 18.0.1.0  
**Last Updated:** November 3, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Payment Providers in Odoo](#payment-providers-in-odoo)
3. [Stripe Integration](#stripe-integration)
4. [PayPal Integration](#paypal-integration)
5. [Invoice-Based Payment](#invoice-based-payment)
6. [Implementation Examples](#implementation-examples)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### Payment Options for Student Fees

OpenEduCat Fees module supports multiple payment methods:

1. **Offline/Manual Payment** (Default)
   - Bank transfer
   - Cash payment
   - Check
   - Admin manually marks as paid

2. **Online Payment via Invoice** (Built-in)
   - Generate invoice (`account.move`)
   - Student pays via Odoo payment providers
   - Automatic reconciliation

3. **Direct Payment Integration** (Custom)
   - Integrate payment gateway directly
   - Requires custom development

---

## 🔌 Payment Providers in Odoo

### What Are Payment Providers?

**Location:** Odoo Core Modules

```
odoo/addons/payment/              # Payment framework (BASE - always installed)
odoo/addons/payment_stripe/       # Stripe integration
odoo/addons/payment_paypal/       # PayPal integration
odoo/addons/payment_authorize/    # Authorize.net
odoo/addons/payment_adyen/        # Adyen
odoo/addons/payment_mollie/       # Mollie (Europe)
```

**These are NOT custom modules - they're official Odoo modules!**

### Available Providers

| Provider | Module Name | Region | Best For |
|----------|-------------|--------|----------|
| **Stripe** ⭐ | `payment_stripe` | Global (135+ countries) | Most institutions |
| **PayPal** | `payment_paypal` | Global | Alternative option |
| **Authorize.net** | `payment_authorize` | US/Canada/UK/Australia | US-based schools |
| **Adyen** | `payment_adyen` | Global | Enterprise |
| **Mollie** | `payment_mollie` | Europe | European schools |
| **AsiaPay** | `payment_asiapay` | Asia-Pacific | Asian institutions |

---

## 💳 Stripe Integration (RECOMMENDED)

### Why Stripe?

- ✅ **Global Coverage:** Works in 135+ countries
- ✅ **Easy Setup:** 10-minute configuration
- ✅ **Best UX:** Smooth checkout experience
- ✅ **PCI Compliant:** No security burden on you
- ✅ **Official Odoo Module:** Maintained by Odoo S.A.
- ✅ **Test Mode:** Full testing without real money

### Step 1: Install Stripe Module

#### Via Odoo Interface (Recommended)

```
1. Go to: Settings → Apps
2. Remove "Apps" filter (click X to show all modules)
3. Search: "Stripe"
4. Find: "Payment Provider: Stripe"
   - Author: Odoo S.A.
   - Description: "An Irish-American payment provider..."
5. Click: Install
6. Wait for installation (30 seconds)
```

#### Via Command Line

```bash
python3 odoo-bin -c odoo.conf -d your_database \
    -i payment_stripe --stop-after-init

# Restart server
python3 odoo-bin -c odoo.conf -d your_database
```

### Step 2: Create Stripe Account

```
1. Go to: https://stripe.com
2. Click "Sign up" (it's FREE)
3. Fill registration form
4. Verify email
5. Complete business profile
6. You'll land in Stripe Dashboard
```

### Step 3: Get API Keys

#### Test Mode Keys (For Development)

```
1. In Stripe Dashboard: Developers → API Keys
2. Toggle: "Test mode" ON (switch at top right)
3. Copy:
   - Publishable key: pk_test_51Xxxxx...
   - Secret key: sk_test_51Xxxxx... (click "Reveal")
```

**Important:** Test mode keys are FREE - no real money charged!

#### Live Mode Keys (For Production - Later)

```
1. Complete Stripe account verification
2. Toggle: "Test mode" OFF
3. Copy:
   - Publishable key: pk_live_51Xxxxx...
   - Secret key: sk_live_51Xxxxx...
```

### Step 4: Configure Stripe in Odoo

```
1. Go to: Website → Configuration → Payment Providers
2. Find: Stripe (should appear after module installation)
3. Click to open
4. Fill:
   - State: Enabled
   - Published: ✓ (check this box)
   - Company: Your company
   
   **Credentials tab:**
   - Publishable Key: pk_test_51Xxxxx... (paste from Stripe)
   - Secret Key: sk_test_51Xxxxx... (paste from Stripe)
   
   **Configuration tab:**
   - Payment Flow: Redirect (recommended) or Inline
   - Capture Amount: Immediately
   - Allow Saving Payment Methods: ✓ (optional)
   
5. Save
```

### Step 5: Test Stripe Payment

#### Test Card Numbers (Stripe Provides)

```
Success:
- Card: 4242 4242 4242 4242
- Expiry: Any future date (e.g., 12/26)
- CVC: Any 3 digits (e.g., 123)
- ZIP: Any 5 digits (e.g., 12345)

Decline:
- Card: 4000 0000 0000 0002
- Result: Payment declined

3D Secure (requires authentication):
- Card: 4000 0027 6000 3184
- Result: Shows authentication popup
```

#### Test Payment Flow

```
1. Go to: Fees → Student Fees Details
2. Select a fee record
3. Click: "Get Invoice"
4. In invoice: Click "Register Payment"
5. Select: Online Payment
6. Choose: Stripe
7. Enter test card: 4242 4242 4242 4242
8. Submit
9. Payment should be recorded automatically!
```

---

## 🅿️ PayPal Integration

### When to Use PayPal

- Alternative to Stripe
- Students prefer PayPal balance
- International students without credit cards

### Installation & Setup

**Install:**
```
Settings → Apps → Search "PayPal" → Install "Payment Provider: PayPal"
```

**Configure:**
```
Website → Configuration → Payment Providers → PayPal

Fill:
- Email Account: your-paypal@example.com
- PDT Identity Token: Get from PayPal
- State: Enabled
- Published: ✓
```

**Get PayPal Credentials:**
```
1. Log in to PayPal Business account
2. Go to: Account Settings → Website Payments → Website Preferences
3. Enable: Auto Return (Yes)
4. Copy: PDT Identity Token
```

---

## 📄 Invoice-Based Payment (Current Implementation)

### How It Works Now

```
Student Fee Record → Get Invoice → account.move Created → Manual Payment
```

**Code:** `openeducat_fees/models/student.py`

```python
def get_invoice(self):
    """Create invoice for fee payment"""
    # Create account.move (invoice)
    invoice = self.env['account.move'].create({
        'move_type': 'out_invoice',
        'partner_id': self.student_id.partner_id.id,
        'invoice_line_ids': [(0, 0, {
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'quantity': 1.0,
            'price_unit': self.amount,
            'account_id': account_id,
        })],
    })
    
    self.invoice_id = invoice.id
    self.state = 'invoice'
    return True
```

**Current Payment Flow:**
1. Admin/Student clicks "Get Invoice"
2. Invoice created
3. Student pays offline (bank/cash)
4. Admin clicks "Register Payment" in invoice
5. Records payment manually

**Limitation:** Manual process, no automatic reconciliation

---

## 🔗 Integrating Payment Providers with Fees

### Add Online Payment Button

**Goal:** Let students pay fee invoices online with Stripe/PayPal

#### Method 1: Via Invoice Portal

Odoo already supports this!

**How:**
```
1. Student logs into portal
2. Goes to: My Account → Invoices
3. Clicks on fee invoice
4. Clicks: "Pay Now" button (appears automatically)
5. Selects: Stripe or PayPal
6. Completes payment
7. Invoice marked as paid automatically!
```

**No code needed** - works out of the box once payment providers are configured!

#### Method 2: Direct Payment Link (Custom)

**Code to Add:**

**File:** `models/student.py`

```python
class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    payment_transaction_id = fields.Many2one('payment.transaction', 
                                            'Payment Transaction',
                                            readonly=True)
    
    def action_pay_online(self):
        """Create payment transaction for online payment"""
        self.ensure_one()
        
        # Create invoice if doesn't exist
        if not self.invoice_id:
            self.get_invoice()
        
        # Get available payment providers
        provider = self.env['payment.provider'].search([
            ('code', '=', 'stripe'),
            ('state', '=', 'enabled')
        ], limit=1)
        
        if not provider:
            raise UserError(_('No payment provider configured. '
                            'Please contact administrator.'))
        
        # Create payment transaction
        tx = self.env['payment.transaction'].create({
            'provider_id': provider.id,
            'amount': self.after_discount_amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.student_id.partner_id.id,
            'reference': f'FEE-{self.id}',
            'invoice_ids': [(4, self.invoice_id.id)],  # Link invoice
        })
        
        self.payment_transaction_id = tx.id
        
        # Return action to payment page
        return {
            'type': 'ir.actions.act_url',
            'url': f'/payment/pay?reference={tx.reference}',
            'target': 'self',
        }
```

**Add Button to Form View:**

**File:** `views/student_fees_view.xml`

```xml
<button name="action_pay_online" 
        type="object" 
        string="Pay Online"
        class="oe_highlight"
        invisible="state != 'draft' or amount &lt;= 0"
        icon="fa-credit-card"/>
```

---

## 🧪 Testing Payment Integration

### Test Environment Setup

**1. Install Stripe in Test Mode**
```
- Use pk_test_xxx keys (not pk_live_xxx)
- All payments are simulated
- No real money charged
- Can test unlimited times
```

**2. Test Student Fee Payment**

```python
# In Odoo shell
student = env['op.student'].search([], limit=1)
fee = env['op.student.fees.details'].create({
    'student_id': student.id,
    'product_id': env.ref('openeducat_fees.op_product_7').id,
    'amount': 100.00,
    'date': fields.Date.today(),
})

# Create invoice
fee.get_invoice()

# Try online payment
fee.action_pay_online()
# Opens payment page with Stripe
```

**3. Test with Test Cards**

Use Stripe test cards:
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
Insufficient Funds: 4000 0000 0000 9995
```

---

## 💡 Implementation Examples

### Example 1: Add Payment Link to Portal

**File:** `views/portal_student_fees.xml` (Create)

```xml
<template id="portal_my_fees" name="My Fees">
    <t t-call="portal.portal_layout">
        <t t-set="breadcrumbs_searchbar" t-value="True"/>
        
        <div class="container">
            <h3>My Fee Payments</h3>
            
            <table class="table">
                <thead>
                    <tr>
                        <th>Fee Type</th>
                        <th>Amount</th>
                        <th>Due Date</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <t t-foreach="fees" t-as="fee">
                        <tr>
                            <td><t t-esc="fee.product_id.name"/></td>
                            <td><span t-field="fee.after_discount_amount"/></td>
                            <td><span t-field="fee.date"/></td>
                            <td>
                                <span t-if="fee.state == 'draft'" class="badge badge-warning">Unpaid</span>
                                <span t-if="fee.state == 'invoice'" class="badge badge-success">Paid</span>
                            </td>
                            <td>
                                <t t-if="fee.state == 'draft'">
                                    <a t-attf-href="/my/fees/#{fee.id}/pay" class="btn btn-primary btn-sm">
                                        <i class="fa fa-credit-card"></i> Pay Now
                                    </a>
                                </t>
                                <t t-else="">
                                    <a t-attf-href="/my/invoices/#{fee.invoice_id.id}" class="btn btn-secondary btn-sm">
                                        <i class="fa fa-file-pdf-o"></i> View Invoice
                                    </a>
                                </t>
                            </td>
                        </tr>
                    </t>
                </tbody>
            </table>
        </div>
    </t>
</template>
```

### Example 2: Bulk Payment for Multiple Fees

```python
class OpStudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'
    
    def action_pay_multiple_online(self):
        """Pay multiple fee records in one transaction"""
        if not self:
            return
        
        total_amount = sum(self.mapped('after_discount_amount'))
        
        # Create combined invoice
        invoice_lines = []
        for fee in self:
            if not fee.invoice_id:
                invoice_lines.append((0, 0, {
                    'name': fee.product_id.name,
                    'product_id': fee.product_id.id,
                    'quantity': 1.0,
                    'price_unit': fee.after_discount_amount,
                }))
        
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self[0].student_id.partner_id.id,
            'invoice_line_ids': invoice_lines,
        })
        
        # Link invoice to all fees
        self.write({'invoice_id': invoice.id})
        
        # Create payment transaction
        provider = self.env['payment.provider'].search([
            ('code', '=', 'stripe'),
            ('state', '=', 'enabled')
        ], limit=1)
        
        tx = self.env['payment.transaction'].create({
            'provider_id': provider.id,
            'amount': total_amount,
            'currency_id': self[0].currency_id.id,
            'partner_id': self[0].student_id.partner_id.id,
            'reference': f'FEES-{",".join(str(f.id) for f in self)}',
            'invoice_ids': [(4, invoice.id)],
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/payment/pay?reference={tx.reference}',
            'target': 'self',
        }
```

### Example 3: Automatic Payment Recording

```python
class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    @api.model
    def _reconcile_after_done(self):
        """Override to update fee records after payment"""
        res = super()._reconcile_after_done()
        
        # Find related fee records
        if self.reference.startswith('FEE-'):
            fee_id = int(self.reference.split('-')[1])
            fee = self.env['op.student.fees.details'].browse(fee_id)
            
            if fee.exists() and self.state == 'done':
                # Mark as paid
                fee.write({'state': 'invoice'})
        
        return res
```

---

## 🏦 Invoice-Based Payment (Current System)

### Current Workflow

```
1. Student Fee Created (op.student.fees.details)
   ↓
2. Admin/Student clicks "Get Invoice"
   ↓
3. Invoice Created (account.move)
   ↓
4. Invoice sent to student (email)
   ↓
5. Student pays (bank/cash/online)
   ↓
6. Payment recorded in invoice
   ↓
7. Invoice state: paid
```

### How Online Payment Works with This

Once payment providers are configured:

```
1-4. Same as above (create invoice)
   ↓
5. Student clicks "Pay Now" on invoice portal
   ↓
6. Selects Stripe/PayPal
   ↓
7. Enters card details
   ↓
8. Stripe processes payment
   ↓
9. Odoo receives webhook
   ↓
10. Invoice marked as paid AUTOMATICALLY
```

**Code Required:** ZERO! Works automatically once Stripe module is installed.

---

## 🔧 Configuration Guide

### Stripe Configuration Options

**Website → Payment Providers → Stripe**

| Setting | Recommended Value | Purpose |
|---------|-------------------|---------|
| State | Enabled | Make provider active |
| Published | ✓ Checked | Show on payment pages |
| Payment Flow | Redirect | Better UX (Stripe hosted page) |
| Capture Amount | Immediately | Charge immediately |
| Allow Token | ✓ Checked | Save cards (optional) |
| Publishable Key | pk_test_xxx | Your Stripe public key |
| Secret Key | sk_test_xxx | Your Stripe private key |
| Webhook Secret | whsec_xxx | For webhook validation (optional) |

### Webhook Setup (Optional but Recommended)

**Why:** Automatic payment confirmation even if user closes browser

**How:**
```
1. In Stripe Dashboard: Developers → Webhooks
2. Click: Add endpoint
3. Endpoint URL: https://your-domain.com/payment/stripe/webhook
4. Events to send:
   - payment_intent.succeeded
   - payment_intent.payment_failed
5. Copy: Signing secret (whsec_xxx)
6. In Odoo: Paste to "Webhook Secret" field
```

---

## 📊 Payment Flow Diagrams

### Online Payment Flow

```
Student Portal
    ↓
Fee List → Click "Pay Now"
    ↓
Payment Provider Selection (Stripe/PayPal)
    ↓
Stripe Checkout Page (hosted by Stripe)
    ↓
Enter Card Details
    ↓
Stripe Processes Payment
    ↓
Redirect to Success Page
    ↓
Webhook → Odoo Receives Confirmation
    ↓
Invoice Marked as Paid
    ↓
Fee State Updated
```

### Offline Payment Flow

```
Student Fee Record
    ↓
Get Invoice
    ↓
Download PDF
    ↓
Pay at Bank/Cash
    ↓
Admin: Register Payment Manually
    ↓
Invoice Marked as Paid
```

---

## 🎯 Best Practices

### Security

1. **Use HTTPS Only**
   - Never use payment on HTTP
   - Stripe requires HTTPS in production

2. **Keep Secret Keys Secret**
   - Never commit keys to Git
   - Use environment variables
   - Odoo stores encrypted in database

3. **Validate on Server**
   - Don't trust client-side amounts
   - Always verify payment server-side

4. **Use Webhooks**
   - Don't rely only on redirects
   - Users may close browser
   - Webhooks guarantee confirmation

### User Experience

1. **Show Payment Options Clearly**
   - Display all available methods
   - Show logos (Visa, Mastercard, PayPal)
   - Indicate which cards accepted

2. **Provide Invoice Fallback**
   - Some students prefer bank transfer
   - Always offer manual payment option
   - Show bank details on invoice

3. **Send Confirmation Emails**
   - Payment received confirmation
   - Include receipt/invoice
   - Next steps instructions

---

## 🐛 Troubleshooting

### Stripe Module Not Appearing

**Problem:** Can't find Stripe in payment providers

**Solutions:**
1. Check if module installed: Apps → Search "payment_stripe"
2. If not visible, remove "Apps" filter
3. Install if not installed
4. Restart Odoo server
5. Clear browser cache

---

### Payment Button Not Working

**Problem:** "Pay Now" button does nothing

**Solutions:**
1. Check payment provider is Enabled
2. Check payment provider is Published
3. Check API keys are correct
4. Check invoice exists (create if missing)
5. Check browser console for JavaScript errors
6. Test with different browser

---

### Payment Fails

**Problem:** Payment declined or error

**Solutions:**
1. **Test Mode:** Use test card 4242 4242 4242 4242
2. **Live Mode:** Check card has funds
3. **3D Secure:** Complete authentication popup
4. **API Keys:** Verify not mixed (test key with live mode)
5. **Stripe Dashboard:** Check logs for detailed error

---

### Payment Successful But Not Recorded

**Problem:** Stripe shows success, Odoo shows unpaid

**Solutions:**
1. **Check Webhooks:** Configure webhook endpoint
2. **Check Logs:** Settings → Technical → Logging
3. **Manual Reconcile:** Odoo → Invoices → Reconcile payment
4. **Stripe Dashboard:** Verify payment actually succeeded

---

## 📚 Resources

### Odoo Documentation

- [Payment Providers](https://www.odoo.com/documentation/18.0/applications/finance/payment_providers.html)
- [Payment Acquirers API](https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html#payment)

### Stripe Documentation

- [Stripe Dashboard](https://dashboard.stripe.com)
- [Test Cards](https://stripe.com/docs/testing)
- [API Reference](https://stripe.com/docs/api)
- [Webhooks Guide](https://stripe.com/docs/webhooks)

### PayPal Documentation

- [PayPal Business](https://www.paypal.com/business)
- [Integration Guide](https://developer.paypal.com/)

---

## 🎓 FAQ

### Q: Do I need to create a custom payment module?

**A:** NO! Use Odoo's built-in `payment_stripe` or `payment_paypal` modules.

### Q: Where do payment providers live?

**A:** In Odoo core:
```
odoo/addons/payment_stripe/    # Official Stripe module
odoo/addons/payment_paypal/    # Official PayPal module
```

### Q: How much does it cost?

**A:**
- Odoo payment modules: FREE (included in Odoo)
- Stripe account: FREE to create
- Transaction fees:
  - Stripe: ~2.9% + $0.30 per transaction
  - PayPal: ~2.9% + $0.30 per transaction
  - (Varies by country and volume)

### Q: Can I use multiple payment providers?

**A:** YES! Enable both Stripe and PayPal. Students choose which to use.

### Q: What about refunds?

**A:** Handle in:
```
Accounting → Invoices → Select invoice → 
Action → Register Payment → Payment Type: Refund
```

Or in Stripe Dashboard → Payments → Refund

### Q: Is it PCI compliant?

**A:** YES! When using Stripe/PayPal:
- Card data never touches your server
- Stripe/PayPal handles PCI compliance
- You don't need PCI certification

---

## ✅ Implementation Checklist

### Initial Setup (One-time)
- [ ] Install payment_stripe module
- [ ] Create Stripe account
- [ ] Get test mode API keys
- [ ] Configure Stripe in Odoo
- [ ] Test with test card
- [ ] Verify payment recorded

### For Production
- [ ] Complete Stripe verification
- [ ] Get live mode API keys
- [ ] Update Odoo config with live keys
- [ ] Set up webhooks
- [ ] Test in production with small amount
- [ ] Monitor first few transactions

### Optional Enhancements
- [ ] Install payment_paypal (alternative)
- [ ] Add custom payment success email
- [ ] Add payment receipt download
- [ ] Add payment history to student portal
- [ ] Set up recurring payments (for installments)

---

## 🎯 Next Steps

### For Admission Portal Integration

See: `edafa_website_branding/static/doc/application_portal_enhancement/PHASE_2_REVISED.md`

This will show how to:
1. Add application_fee field to op.admission
2. Create invoice for application fee
3. Integrate with payment providers
4. Add payment page to portal

**Same pattern as fees, just for admissions!**

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Module Version:** 18.0.1.0

