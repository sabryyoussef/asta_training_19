# Motakamel Alumni - Quick Reference Card

## 📦 Module Information

**Module Name**: `motakamel_alumni`  
**Display Name**: Motakamel Alumni Management  
**Version**: 18.0.1.0  
**Author**: Motakamel Training Academy  
**Category**: Education  
**License**: LGPL-3

---

## 📁 Module Location

```
/home/sabry3/edu_demo/custom_addons/motakamel_training_academy/
  custom-addons/motakamel/motakamel_alumni/
```

---

## 🎯 Key Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `op.alumni` | Alumni records | name, email, course_id, graduation_date |
| `op.alumni.group` | Alumni groups | name, group_type, alumni_ids |
| `op.alumni.event` | Events | name, event_date, venue, state |
| `op.alumni.event.registration` | Event registrations | event_id, alumni_id, attended |
| `op.alumni.job` | Job postings | name, company_name, job_type |
| `op.alumni.job.application` | Job applications | job_id, applicant_id, state |

---

## 🔐 Security Groups

| Group | Access Level |
|-------|-------------|
| **Alumni User** | Read-only access to active alumni |
| **Alumni Manager** | Full CRUD access to all features |
| **Portal User** | Access to own record only |

---

## 🌐 Web Routes

### Portal Routes (Authenticated Users)
- `/my/alumni` - Alumni profile
- `/my/alumni/events` - My events
- `/my/alumni/jobs` - Job listings

### Public Routes
- `/alumni` - Alumni directory
- `/alumni/<id>` - Alumni detail
- `/alumni/events` - Events listing
- `/alumni/jobs` - Jobs board

---

## 🔢 Sequences

| Type | Prefix | Example |
|------|--------|---------|
| Alumni | `ALM/` | ALM/00001 |
| Event | `EVT/` | EVT/00001 |
| Job | `JOB/` | JOB/00001 |

---

## ⚙️ Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `motakamel_alumni.auto_create_alumni_portal` | False | Auto-create portal access |
| `motakamel_alumni.alumni_portal_access_days` | 365 | Portal access duration |

---

## 📊 Module Status

### ✅ Complete (80%)
- Models & business logic
- Controllers & routes
- Security & access rights
- Wizards
- Data files
- Documentation

### ⚠️ Pending (20%)
- XML views (list, form, kanban)
- Portal templates
- Website templates
- Reports
- Static assets (CSS, JS)

---

## 🚀 Quick Commands

### Install Module
```bash
# In Odoo
Apps → Update Apps List → Search "Motakamel Alumni" → Install
```

### Convert Students to Alumni
```python
# From student list
students.action_convert_to_alumni()
```

### Create Alumni Record
```python
alumni = env['op.alumni'].create({
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'course_id': course.id,
    'graduation_date': '2024-06-15',
    'state': 'active',
})
```

### Create Event
```python
event = env['op.alumni.event'].create({
    'name': 'Class of 2024 Reunion',
    'event_type': 'reunion',
    'event_date': '2025-06-15 18:00:00',
    'venue': 'Campus Hall',
    'state': 'published',
})
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | User guide & features |
| `MODULE_STRUCTURE.md` | Technical architecture |
| `IMPLEMENTATION_STATUS.md` | Current status |
| `QUICK_START.md` | Quick guide |
| `RENAME_SUMMARY.md` | Rename details |
| `QUICK_REFERENCE.md` | This file |

---

## 🔗 Dependencies

- `openeducat_core` (Required)
- `website` (Required)
- `portal` (Required)
- `mail` (Required)

---

## 💡 Common Tasks

### 1. Convert Graduated Students
```
Students → Select students → Action → Convert to Alumni
```

### 2. Create Alumni Group
```
Alumni → Alumni Groups → Create
```

### 3. Organize Event
```
Alumni → Events → Create → Publish
```

### 4. Send Bulk Email
```
Alumni → Select alumni → Action → Send Email
```

---

## 🎨 Branding

**Color Scheme**: (To be defined)  
**Logo**: (To be added)  
**Banner**: `motakamel_alumni_banner.jpg`

---

## 📞 Support

**Website**: https://www.motakamel.com  
**Email**: support@motakamel.com

---

**Last Updated**: November 3, 2025  
**Status**: Module structure complete, views pending

