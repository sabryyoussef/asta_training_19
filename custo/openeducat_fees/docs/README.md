# OpenEduCat Fees Module - Documentation

**Module:** `openeducat_fees`  
**Version:** 18.0.1.0  
**Category:** Education  
**License:** LGPL-3  

---

## Overview

The OpenEduCat Fees module provides comprehensive fee collection and financial operations management for educational institutions in Odoo 18.

### Key Features

- ✅ Flexible fee term management (fixed days/fixed dates)
- ✅ Fee element configuration per course
- ✅ Automated invoice generation from fee details
- ✅ Fee collection tracking per student
- ✅ Discount management
- ✅ Multi-company support
- ✅ Financial reports and analysis
- ✅ Integration with Odoo Accounting

---

## Module Structure

```
openeducat_fees/
├── models/              # Business logic
│   ├── course.py        # Course fee terms
│   ├── fees_element.py  # Fee elements
│   ├── fees_terms.py    # Fee term definitions
│   └── student.py       # Student fee details
├── views/               # UI definitions (Odoo 18 list views)
│   ├── course_view.xml
│   ├── fees_element_view.xml
│   ├── fees_terms_view.xml
│   └── student_view.xml
├── wizard/              # Transient models
│   ├── fees_detail_report_wizard.py
│   └── select_term_type_wizard.py
├── report/              # QWeb reports
│   └── fees_analysis_report.py
├── security/            # Access control
│   ├── ir.model.access.csv
│   └── op_security.xml
├── demo/                # Demo data
├── i18n/                # Translations (13 languages)
├── tests/               # Unit tests
└── docs/                # This documentation
```

---

## Quick Links

- [Installation Guide](./INSTALLATION.md)
- [User Guide](./USER_GUIDE.md)
- [Technical Reference](./TECHNICAL.md)
- [API Documentation](./API.md)
- [Migration Notes](./MIGRATION.md)
- [FAQ](./FAQ.md)
- [Development Guide](./DEVELOPMENT.md)

---

## Dependencies

### Required Odoo Modules

- `openeducat_core` - Core OpenEduCat functionality
- `account` - Odoo Accounting for invoice generation

### Python Version

- Python 3.10+ (Odoo 18 compatible)

---

## Main Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `op.fees.terms` | Fee term definitions | name, code, fees_terms, line_ids |
| `op.fees.terms.line` | Fee term line items | due_days, due_date, value, fees_element_line |
| `op.fees.element` | Fee elements per term line | product_id, value, fees_terms_line_id |
| `op.student.fees.details` | Student fee collection | student_id, amount, state, invoice_id |

---

## Key Workflows

### 1. Fee Term Setup
1. Create fee term (`op.fees.terms`)
2. Configure term type (fixed days/fixed dates)
3. Add term lines with percentages
4. Assign fee elements (products) to each line

### 2. Fee Collection
1. Assign fee term to course
2. System generates fee details for enrolled students
3. Student fee details created automatically
4. Create invoices from fee details
5. Track payment status

### 3. Invoice Generation
1. Fee detail in 'draft' state
2. Click "Get Invoice" button
3. System creates `account.move` invoice
4. State changes to 'invoice'
5. Invoice linked to student

---

## Security Groups

- **User** (`group_openeducat_fees_user`) - View and manage fee records
- **Manager** (`group_op_fees_admin`) - Full access including configuration

---

## Supported Languages

Arabic, Danish, German, Spanish, Persian, French, Indonesian, Italian, Latvian, Dutch, Portuguese, Russian, Thai, Vietnamese (2 variants), Chinese (2 variants)

---

## Reports

- **Fees Details Report** - Detailed analysis by student or course
- **Fees Analysis** - Summary report with totals (paid/unpaid/invoiced)

---

## Technical Highlights

### Odoo 18 Compliance

- ✅ Uses list views (not deprecated tree views)
- ✅ Modern OWL components for widgets
- ✅ Assets bundled via Odoo 18 syntax
- ✅ Proper `@api.depends` for computed fields
- ✅ Multi-create support via standard `create` method

### Best Practices

- Mail tracking integration (`mail.thread`)
- Proper access control (ACL + record rules)
- Automated tests included
- i18n support with 13+ languages
- Company-aware (multi-company support)

---

## Getting Started

### For Users

Read the [User Guide](./USER_GUIDE.md) for step-by-step instructions on:
- Setting up fee terms
- Managing student fees
- Generating invoices
- Running reports

### For Developers

Read the [Development Guide](./DEVELOPMENT.md) for:
- Model relationships
- Extension points
- Custom field addition
- Testing guidelines

### For Administrators

Read the [Installation Guide](./INSTALLATION.md) for:
- Installation steps
- Configuration
- Security setup
- Troubleshooting

---

## Support & Resources

- **Module Author:** Edafa Inc (https://www.edafa.org)
- **Original:** OpenEduCat Inc (https://www.openeducat.org)
- **Odoo Version:** 18.0
- **License:** LGPL-3

---

## Documentation Index

1. [README.md](./README.md) - This file (overview)
2. [INSTALLATION.md](./INSTALLATION.md) - Installation and setup
3. [USER_GUIDE.md](./USER_GUIDE.md) - End-user documentation
4. [TECHNICAL.md](./TECHNICAL.md) - Technical architecture
5. [API.md](./API.md) - API reference and methods
6. [MIGRATION.md](./MIGRATION.md) - Upgrade notes and migrations
7. [FAQ.md](./FAQ.md) - Frequently asked questions
8. [DEVELOPMENT.md](./DEVELOPMENT.md) - Developer guide

---

**Last Updated:** November 3, 2025  
**Maintainer:** Motakamel Training Academy  
**Odoo Version:** 18.0

