# 🧪 Testing Guide - Admission Portal with Payment

**Module:** `edafa_website_branding`  
**Version:** 18.0.1.2  
**Last Updated:** November 3, 2025

---

## 📋 Quick Start Testing

### Prerequisites

1. **Module Installed:**
   ```bash
   python3 odoo-bin -c odoo.conf -d edu_demo -u edafa_website_branding --stop-after-init
   ```

2. **Demo Data Loaded:**
   Module should install with demo data automatically

3. **Server Running:**
   ```bash
   python3 odoo-bin -c odoo.conf -d edu_demo
   ```

---

## 🎯 Test Scenarios

### Scenario 1: Test Demo Admissions (Backend)

**Step 1: View Demo Records**

```
1. Go to: Admission → Admissions
2. You should see 3 demo applications:
   - Ahmed Hassan Mohamed (Unpaid - $50 fee)
   - Fatima Ali Khan (Paid - $50 fee)
   - John Smith (No Fee)
```

**Step 2: Test Payment Fields**

```
1. Open: Ahmed Hassan Mohamed application
2. You should see new fields:
   - Application Fee: $50.00
   - Payment Status: Unpaid
   - Access Token: demo_token_ahmed_123456789
   - Currency: (your company currency)
```

**Step 3: Test Invoice Creation**

```
1. Still in Ahmed's application
2. Click: "Create Invoice" button (if visible)
3. OR: In Python shell:
   
   admission = env['op.admission'].search([('email', '=', 'ahmed.hassan@demo.com')])
   admission.action_create_invoice()
   
4. Check: Invoice should be created
5. View: admission.invoice_id should be set
6. Payment Status: Should change to 'unpaid'
```

---

### Scenario 2: Test Payment Page (Frontend)

**Step 1: Access Payment Page**

Visit these URLs directly:

**Ahmed's Payment Page (Unpaid):**
```
http://localhost:8025/admission/1/payment?access_token=demo_token_ahmed_123456789
```

**What you should see:**
- ✅ Application summary (name, course, number)
- ✅ Amount due: $50.00
- ✅ Payment methods section
- ✅ "Pay Online" button (if Stripe installed)
- ✅ "Download Invoice" button

**Fatima's Payment Page (Already Paid):**
```
http://localhost:8025/admission/2/payment?access_token=demo_token_fatima_987654321
```

**What you should see:**
- ✅ "Payment Received!" message
- ✅ No payment buttons (already paid)
- ✅ Link to view applications

**John's Payment Page (No Fee):**
```
http://localhost:8025/admission/3/payment?access_token=demo_token_john_555666777
```

**What you should see:**
- ✅ "No payment required" message
- OR: Error (no invoice to display)

---

### Scenario 3: Test Payment Flow

**Option A: With Stripe (Requires Stripe Module)**

**Setup:**
```
1. Install Stripe module:
   Settings → Apps → Search "Stripe" → Install

2. Configure Stripe:
   Website → Configuration → Payment Providers → Stripe
   - State: Enabled
   - Published: ✓
   - Publishable Key: pk_test_51Xxxxxxx (get from stripe.com)
   - Secret Key: sk_test_51Xxxxxxx (get from stripe.com)
   - Save
```

**Test:**
```
1. Visit: http://localhost:8025/admission/1/payment?access_token=demo_token_ahmed_123456789

2. Click: "Pay with Stripe" button

3. Should redirect to Stripe payment page

4. Enter test card:
   - Card: 4242 4242 4242 4242
   - Expiry: 12/26 (any future date)
   - CVC: 123
   - ZIP: 12345

5. Submit payment

6. Should redirect to: /admission/1/payment/success

7. Verify:
   - Success message shown
   - admission.payment_status = 'paid'
   - admission.state = 'confirm' (auto-confirmed)
```

**Option B: Without Stripe (Manual Invoice)**

```
1. Visit: http://localhost:8025/admission/1/payment?access_token=demo_token_ahmed_123456789

2. Click: "Download Invoice" button

3. Invoice PDF downloads

4. In backend:
   - Go to: Accounting → Customers → Invoices
   - Find: Ahmed's invoice
   - Click: "Register Payment"
   - Enter: Amount $50, Journal: Bank
   - Confirm

5. Verify:
   - Invoice state: Paid
   - admission.payment_status should update (may need cron or manual)
```

---

### Scenario 4: Test Thank You Page with Payment Link

**Step 1: Submit New Application**

```
1. Visit: http://localhost:8025/admission/apply
2. Fill wizard (demo data pre-filled)
3. Click Next through all steps
4. Step 5: Accept terms, Submit
5. Redirected to thank you page
```

**Step 2: Check Payment Link**

On thank you page, you should see:
```
✅ Application Number: APP/2025/XXX
✅ Payment section (if fee > 0):
   - "Amount Due: $50.00"
   - "Pay Now" button
   - Link to: /admission/<id>/payment?access_token=xxxxx
```

---

### Scenario 5: Test Access Control

**Test 1: Valid Access Token**
```
URL: http://localhost:8025/admission/1/payment?access_token=demo_token_ahmed_123456789
Result: ✅ Page loads
```

**Test 2: Invalid Access Token**
```
URL: http://localhost:8025/admission/1/payment?access_token=wrong_token
Result: ❌ 403 Forbidden
```

**Test 3: No Access Token (Public)**
```
URL: http://localhost:8025/admission/1/payment
Result: ❌ 403 Forbidden (unless logged in as owner)
```

**Test 4: Logged In as Owner**
```
1. Create portal user with email: ahmed.hassan@demo.com
2. Log in
3. Visit: http://localhost:8025/admission/1/payment (no token needed)
Result: ✅ Page loads
```

---

## 🔧 Testing in Python Shell

### Test 1: Check Payment Fields

```python
# Start Odoo shell
python3 odoo-bin shell -c odoo.conf -d edu_demo

# In shell:
admission = env['op.admission'].search([('email', '=', 'ahmed.hassan@demo.com')], limit=1)

# Check fields
print(f"Application Number: {admission.application_number}")
print(f"Application Fee: {admission.application_fee}")
print(f"Payment Status: {admission.payment_status}")
print(f"Access Token: {admission.access_token}")
print(f"Has Invoice: {bool(admission.invoice_id)}")
print(f"Has Transaction: {bool(admission.payment_transaction_id)}")
```

### Test 2: Create Invoice

```python
admission = env['op.admission'].search([('email', '=', 'ahmed.hassan@demo.com')], limit=1)

# Create invoice
result = admission.action_create_invoice()

# Verify
print(f"Invoice created: {admission.invoice_id.name}")
print(f"Invoice amount: {admission.invoice_id.amount_total}")
print(f"Payment status: {admission.payment_status}")
```

### Test 3: Simulate Payment

```python
# Get admission
admission = env['op.admission'].search([('email', '=', 'ahmed.hassan@demo.com')], limit=1)

# Create invoice if doesn't exist
if not admission.invoice_id:
    admission.action_create_invoice()

# Register payment manually
payment = env['account.payment'].create({
    'payment_type': 'inbound',
    'partner_type': 'customer',
    'partner_id': admission.partner_id.id,
    'amount': admission.application_fee,
    'journal_id': env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
})

# Link to invoice
payment.action_post()
payment_line = payment.line_ids.filtered(lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable'))
invoice_line = admission.invoice_id.line_ids.filtered(lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable'))
(payment_line + invoice_line).reconcile()

# Verify
print(f"Invoice state: {admission.invoice_id.payment_state}")
print(f"Should be 'paid': {admission.invoice_id.payment_state == 'paid'}")
```

### Test 4: Get Portal URL

```python
admission = env['op.admission'].search([('email', '=', 'ahmed.hassan@demo.com')], limit=1)

url = admission._get_portal_url()
print(f"Portal URL: {url}")
print(f"Payment URL: {url.replace('/my/admission/', '/admission/')}/payment")
```

---

## 🌐 Testing URLs Cheat Sheet

### Demo Admission IDs (After Installation)

Find actual IDs in backend or use:

```python
# In Odoo shell
ahmed = env['op.admission'].search([('email', '=', 'ahmed.hassan@demo.com')])
print(f"Ahmed ID: {ahmed.id}")

fatima = env['op.admission'].search([('email', '=', 'fatima.khan@demo.com')])
print(f"Fatima ID: {fatima.id}")

john = env['op.admission'].search([('email', '=', 'john.smith@demo.com')])
print(f"John ID: {john.id}")
```

### Test URLs (Replace <ID> with actual ID)

```
# Wizard (submit new application)
http://localhost:8025/admission/apply

# Payment page (Ahmed - unpaid)
http://localhost:8025/admission/<AHMED_ID>/payment?access_token=demo_token_ahmed_123456789

# Payment page (Fatima - paid)
http://localhost:8025/admission/<FATIMA_ID>/payment?access_token=demo_token_fatima_987654321

# Check status
http://localhost:8025/admission/check-status

# My applications (need login)
http://localhost:8025/my/applications
```

---

## ✅ Testing Checklist

### Backend Tests

- [ ] Demo data loads successfully
- [ ] 3 demo admissions created
- [ ] Payment fields visible in form
- [ ] Can create invoice via button
- [ ] Invoice linked to admission
- [ ] Payment status updates correctly

### Payment Page Tests

- [ ] Payment page loads with valid token
- [ ] Payment page blocked with invalid token
- [ ] Shows correct amount
- [ ] Shows application details
- [ ] Payment providers listed (if any enabled)
- [ ] Download invoice button works

### Payment Flow Tests (With Stripe)

- [ ] "Pay Online" button appears
- [ ] Clicking redirects to Stripe
- [ ] Can enter test card
- [ ] Payment processes successfully
- [ ] Redirects to success page
- [ ] admission.payment_status = 'paid'
- [ ] admission.state = 'confirm'

### Access Control Tests

- [ ] Valid token grants access
- [ ] Invalid token denies access  
- [ ] Logged-in owner can access
- [ ] Other users can't access

---

## 🐛 Troubleshooting

### Demo Data Not Loading

**Problem:** No demo admissions after install

**Solutions:**
```bash
# Method 1: Reinstall with demo
python3 odoo-bin -c odoo.conf -d edu_demo \
    -i edafa_website_branding --stop-after-init

# Method 2: Load demo manually
python3 odoo-bin -c odoo.conf -d edu_demo \
    -u edafa_website_branding --stop-after-init

# Method 3: Python shell
env['ir.model.data'].search([
    ('module', '=', 'edafa_website_branding'),
    ('model', '=', 'op.admission')
]).unlink()  # Remove old demo
# Then reinstall
```

### Payment Page Shows 404

**Problem:** Page not found

**Check:**
1. Admission ID exists
2. Access token is correct
3. Route is registered (restart server)

### Payment Button Doesn't Appear

**Problem:** No "Pay Online" button

**Reasons:**
1. No payment providers enabled
2. Payment amount is 0
3. Already paid

**Solution:**
```
Install & enable Stripe:
Settings → Apps → Stripe → Install
Website → Payment Providers → Stripe → Enable
```

---

## 📝 Manual Testing Script

**Copy and run in Odoo shell:**

```python
# ============================================
# COMPLETE PAYMENT TESTING SCRIPT
# ============================================

# 1. Find demo admission
admission = env['op.admission'].search([('email', '=', 'ahmed.hassan@demo.com')], limit=1)
if not admission:
    print("❌ Demo admission not found - reinstall module with demo data")
else:
    print(f"✅ Found admission: {admission.application_number}")

# 2. Check payment fields
print(f"\n--- Payment Fields ---")
print(f"Application Fee: {admission.application_fee} {admission.currency_id.symbol}")
print(f"Payment Status: {admission.payment_status}")
print(f"Has Invoice: {'Yes' if admission.invoice_id else 'No'}")
print(f"Has Transaction: {'Yes' if admission.payment_transaction_id else 'No'}")

# 3. Test invoice creation
if not admission.invoice_id and admission.application_fee > 0:
    print(f"\n--- Creating Invoice ---")
    try:
        admission.action_create_invoice()
        print(f"✅ Invoice created: {admission.invoice_id.name}")
        print(f"   Amount: {admission.invoice_id.amount_total}")
        print(f"   State: {admission.invoice_id.state}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print(f"\n✅ Invoice already exists: {admission.invoice_id.name if admission.invoice_id else 'N/A'}")

# 4. Get portal URL
print(f"\n--- Portal URLs ---")
portal_url = admission._get_portal_url()
print(f"Portal URL: {portal_url}")

base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
payment_url = f"{base_url}/admission/{admission.id}/payment?access_token={admission.access_token}"
print(f"Payment URL: {payment_url}")

# 5. Test access token validation
print(f"\n--- Access Token Test ---")
is_valid = admission._check_access_token(admission.access_token)
print(f"Valid token: {'✅ Yes' if is_valid else '❌ No'}")

is_invalid = admission._check_access_token('wrong_token')
print(f"Invalid token blocks: {'✅ Yes' if not is_invalid else '❌ No'}")

# 6. Summary
print(f"\n{'='*50}")
print(f"TESTING SUMMARY")
print(f"{'='*50}")
print(f"Admission ID: {admission.id}")
print(f"Application Number: {admission.application_number}")
print(f"Email: {admission.email}")
print(f"Fee: {admission.application_fee} {admission.currency_id.symbol}")
print(f"Status: {admission.payment_status}")
print(f"\n🔗 TEST URLS:")
print(f"Payment Page: {payment_url}")
print(f"\n📝 NEXT STEPS:")
print(f"1. Copy payment URL above")
print(f"2. Open in browser")
print(f"3. Test payment flow")
print(f"{'='*50}")
```

---

## 🎨 Expected Results

### Payment Page UI

**Header Section:**
```
┌─────────────────────────────────────────┐
│  Application Summary                     │
├─────────────────────────────────────────┤
│  Application Number: APP/2025/001       │
│  Applicant: Ahmed Hassan Mohamed        │
│  Course: Computer Science               │
│  Application Date: Nov 3, 2025          │
└─────────────────────────────────────────┘
```

**Payment Section:**
```
┌─────────────────────────────────────────┐
│  Payment Required                        │
├─────────────────────────────────────────┤
│          Amount Due                      │
│            $50.00                        │
│                                          │
│  Choose Payment Method:                  │
│                                          │
│  ┌─────────────────────────────────┐   │
│  │ 💳 Pay Online (Credit/Debit)    │   │
│  │ Powered by Stripe               │   │
│  │ [Pay with Stripe]               │   │
│  └─────────────────────────────────┘   │
│                                          │
│  ┌─────────────────────────────────┐   │
│  │ 🏦 Bank Transfer / Cash         │   │
│  │ Download invoice and pay        │   │
│  │ [Download Invoice]              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 📊 Test Data Reference

### Demo Admissions

| Name | Email | Fee | Status | Access Token | ID |
|------|-------|-----|--------|--------------|-------------|
| Ahmed Hassan | ahmed.hassan@demo.com | $50 | Unpaid | demo_token_ahmed_123456789 | (check DB) |
| Fatima Khan | fatima.khan@demo.com | $50 | Paid | demo_token_fatima_987654321 | (check DB) |
| John Smith | john.smith@demo.com | $0 | None | demo_token_john_555666777 | (check DB) |

### Stripe Test Cards

| Card Number | Result | Use For |
|-------------|--------|---------|
| 4242 4242 4242 4242 | Success | Happy path |
| 4000 0000 0000 0002 | Decline | Error handling |
| 4000 0000 0000 9995 | Insufficient funds | Specific error |
| 4000 0027 6000 3184 | 3D Secure required | Auth flow |

---

## 🚀 Quick Test Commands

### Test Payment Route Exists

```bash
# Check if route is registered
curl http://localhost:8025/admission/1/payment?access_token=demo_token_ahmed_123456789

# Should return HTML (status 200), not 404
```

### Test JSON Endpoint

```bash
# Test create payment transaction
curl -X POST http://localhost:8025/admission/1/create-payment-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "provider_id": 1,
      "access_token": "demo_token_ahmed_123456789"
    }
  }'
```

---

## 📋 Acceptance Criteria

### All Tests Pass When:

✅ **Backend:**
- Demo data loads (3 admissions)
- Payment fields visible in form
- Can create invoices
- Invoices have correct amounts

✅ **Payment Page:**
- Loads with valid access token
- Blocked with invalid token
- Shows application details
- Shows amount due
- Lists payment providers (if any)

✅ **Payment Flow:**
- Can initiate payment
- Redirects to Stripe/PayPal
- Can complete test payment
- Returns to success page
- Status updates correctly

✅ **Security:**
- Access token validated
- Logged-in users authorized
- Other users blocked

---

## 🎓 Next Steps After Testing

Once payment routes are tested:

1. **Step 3:** Create payment UI templates
2. **Step 4:** Update thank you page
3. **Step 5:** Test end-to-end flow
4. **Step 6:** Move to conditional fields

---

**Ready to test!** 🧪

Run the Python shell script above to get your test URLs and verify everything works!

