# User Guide - OpenEduCat Fees Module

## Table of Contents

1. [Getting Started](#getting-started)
2. [Fee Term Management](#fee-term-management)
3. [Fee Elements](#fee-elements)
4. [Course Fee Assignment](#course-fee-assignment)
5. [Student Fee Collection](#student-fee-collection)
6. [Invoice Generation](#invoice-generation)
7. [Reports](#reports)

---

## Getting Started

### Access the Fees Module

After installation, access via:
- Main menu → **Fees**

### Required Permissions

You need one of these security groups:
- **Fees User** - View and manage fees
- **Fees Manager** - Full access including configuration

---

## Fee Term Management

Fee Terms define how fees are collected over time (installments).

### Create a New Fee Term

**Navigation:** Fees → Configuration → Fees Terms → Create

**Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Descriptive name | "Semester 1 - 2025" |
| **Code** | Short unique code | "S1-2025" |
| **Active** | Enable/disable | ✓ Checked |
| **Term Type** | Payment schedule | Fixed Days / Fixed Dates |
| **Discount** | Default discount % | 5.0 |
| **Description** | Terms and conditions | Payment terms text |

### Term Types

#### Option 1: Fixed Fees of Days
Fees due based on **days after enrollment**

**Example:**
- Line 1: Day 0 (enrollment) → 40%
- Line 2: Day 30 (1 month later) → 30%
- Line 3: Day 60 (2 months later) → 30%

**Use when:** Student enrollment dates vary

#### Option 2: Fixed Fees of Dates
Fees due on **specific calendar dates**

**Example:**
- Line 1: 2025-01-15 → 50%
- Line 2: 2025-02-15 → 50%

**Use when:** All students pay on same dates

### Add Fee Term Lines

**In Fee Term form → Terms tab → Add a line**

**For Fixed Days:**
- **Due Days:** Number of days after enrollment (0, 15, 30, 60, etc.)
- **Value (%):** Percentage of total (must sum to 100%)
- **Fees Elements:** Select products (fees) for this installment

**For Fixed Dates:**
- **Due Date:** Calendar date (2025-01-15)
- **Value (%):** Percentage of total
- **Fees Elements:** Select products for this installment

### Validation Rules

⚠️ **Important:**
- Sum of all line values must equal 100%
- At least one line required per term
- Fee elements are optional but recommended

---

## Fee Elements

Fee Elements are the individual products (fee types) that make up each installment.

### Create Fee Element

**Navigation:** Fees → Configuration → Fees Elements → Create

**Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| **Product** | Fee type (from product catalog) | "Tuition Fees" |
| **Value (%)** | Weight in this installment | 100.0 |
| **Sequence** | Display order | 10 |

### Common Fee Products

Create these in **Products** first (via Accounting → Products):

- Admission Fees
- Tuition Fees
- Library Fees
- Lab Fees
- Transportation Fees
- Hostel Fees
- Examination Fees

**Product Settings:**
- Type: Service
- Income Account: Configure in Accounting
- Price: Set base price

---

## Course Fee Assignment

Assign fee terms to courses so enrolled students automatically get fee records.

### Assign Fee Term to Course

**Navigation:** Courses → Select Course → Edit

**Fields:**
- **Fees Term:** Select the appropriate fee term

**Result:**
When students enroll in this course, fee details are automatically generated based on the assigned fee term.

---

## Student Fee Collection

### View Student Fees

**Navigation:** Students → Select Student → Fees Details tab

**What you see:**
- List of all fee installments for this student
- Due dates or days
- Amounts
- Payment status
- Linked invoices

### Fee Detail States

| State | Description | Actions Available |
|-------|-------------|-------------------|
| **Draft** | Not yet invoiced | Get Invoice, Edit, Cancel |
| **Invoice Created** | Invoice generated | View Invoice, Track Payment |
| **Cancel** | Cancelled | Archive |

### Generate Student Fees Manually

If fees weren't auto-generated:

1. Go to **Fees** → Student Fees Details → Create
2. Fill fields:
   - **Student:** Select student
   - **Course:** Student's course
   - **Batch:** Student's batch
   - **Product:** Fee type
   - **Fees Amount:** Amount to charge
   - **Submit Date:** Due date
   - **Discount (%):** If applicable
3. Save

---

## Invoice Generation

### Create Invoice from Fee Detail

**Method 1: Single Invoice**

1. Open **Student** → Fees Details tab
2. Select a fee detail record in "Draft" state
3. Click **Get Invoice** button
4. System creates invoice and links it
5. State changes to "Invoice Created"

**Method 2: Bulk Invoice Generation**

1. Go to **Fees** → Student Fees Details
2. Filter: State = Draft
3. Select multiple records (checkbox)
4. Action → **Get Invoice**
5. Invoices created in batch

### View Generated Invoice

From fee detail record:
- Click **Invoice ID** field (smart button)
- Opens related invoice
- Track payment status in Accounting

### Invoice Details

Generated invoices include:
- Customer: Student's partner
- Invoice Lines: Fee products with amounts
- Due Date: From fee detail
- Amount: After discount (if any)

---

## Reports

### Fees Details Report

**Purpose:** Analyze fees by student or course

**Navigation:** Fees → Reports → Fees Details Report

**Steps:**
1. Click "Fees Details Report"
2. Select filter:
   - **By Student:** Analyze single student
   - **By Course:** Analyze all students in course
3. Select Student/Course
4. Click **Print**

**Output:** PDF report with:
- Student name
- Fee breakdown
- Total amount
- Invoiced amount
- Paid amount
- Unpaid amount

### Fees Analysis Report

**Purpose:** Financial summary

**Available Data:**
- Total fees collected
- Pending fees
- Invoice status
- Payment tracking

---

## Common Workflows

### Workflow 1: New Semester Fee Setup

```
1. Create Products (one-time)
   → Tuition, Library, Lab, etc.

2. Create Fee Term
   → "Spring 2025"
   → Fixed Days: 0, 30, 60
   → Add fee elements to each line

3. Assign to Courses
   → All courses get "Spring 2025" term

4. Students Enroll
   → Fees auto-generated

5. Generate Invoices
   → Bulk invoice creation

6. Track Payments
   → Via Accounting module
```

### Workflow 2: Individual Fee Adjustment

```
1. Find Student
   → Students menu

2. Open Fees Details tab
   → View all fee records

3. Edit Fee Detail
   → Adjust amount
   → Add discount

4. Generate Invoice
   → Click "Get Invoice"

5. Process Payment
   → In Accounting
```

### Workflow 3: Mid-Semester Discount

```
1. Find Fee Term
   → Fees → Fees Terms

2. Edit Term
   → Update Discount % field

3. Apply to Students
   → Existing fees: manual update
   → New students: auto-applied

4. Regenerate Invoices (if needed)
   → Cancel old, create new
```

---

## Tips & Best Practices

### ✅ Do's

- Create fee terms at the start of each academic period
- Use consistent naming (Semester, Year, Quarter)
- Test with one student before bulk operations
- Regular reconciliation with Accounting
- Archive old fee terms (uncheck Active)

### ❌ Don'ts

- Don't delete fee terms with student data
- Don't modify fee terms mid-semester (affects existing students)
- Don't skip Chart of Accounts setup
- Don't mix fixed days and fixed dates in same term

### 💡 Pro Tips

1. **Use Discounts wisely** - Set at term level for institutional discounts
2. **Batch operations** - Process invoices in bulk for efficiency
3. **Regular reports** - Run analysis weekly to track collections
4. **Archive old terms** - Keep interface clean
5. **Product categories** - Group fee products for better reporting

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Create New | Alt + C |
| Save | Ctrl + S |
| Discard | Ctrl + J |
| Search | Ctrl + K |

---

## Troubleshooting

### Fees not auto-generating for students

**Check:**
- Fee term assigned to course?
- Student enrolled in course?
- Fee term is active?

### Invoice creation fails

**Check:**
- Chart of Accounts configured?
- Income account set on products?
- User has accounting rights?
- Amount is positive?

### Percentage validation error

**Check:**
- Sum of all line values = 100%
- Each line has a value > 0

---

## Next Steps

- Read [Technical Reference](./TECHNICAL.md) for architecture details
- Check [FAQ](./FAQ.md) for common questions
- Review [API Documentation](./API.md) for automation

---

**Questions?** Contact your system administrator or refer to [FAQ.md](./FAQ.md)

