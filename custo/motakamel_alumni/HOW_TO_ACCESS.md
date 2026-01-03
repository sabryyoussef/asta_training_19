# How to Access Alumni Module

## ✅ QUICK FIX APPLIED!

I've created basic views and menus so you can now access Alumni from the Odoo interface!

---

## 🚀 Access Alumni from Odoo Interface

### Step 1: Upgrade the Module
Since the module is already installed, you need to upgrade it to load the new views:

1. Go to **Apps** menu
2. Remove the "Apps" filter (click the X on the filter)
3. Search for **"Motakamel Alumni"** or **"motakamel_alumni"**
4. Click the **⋮** (three dots) menu
5. Click **"Upgrade"**

### Step 2: Access Alumni Menu
After upgrading, you'll see a new menu:

```
📋 Main Menu Bar
└── Alumni (New!)
    └── Alumni
        └── Alumni Records  ← Click here!
```

### Step 3: Create Your First Alumni
1. Click **"Alumni Records"**
2. Click **"Create"** button
3. Fill in the form:
   - First Name
   - Last Name
   - Email
   - Course
   - Graduation Date
4. Click **"Save"**

---

## 📊 What You Can Do Now

### ✅ View Alumni List
- See all alumni in a list view
- Filter by Active/Inactive
- Search by name, email, or alumni number
- Group by Course, Graduation Year, or State

### ✅ Create/Edit Alumni
- Complete alumni profile form
- Personal information
- Academic details
- Professional information
- Contact details
- Address

### ✅ Manage Alumni
- **Activate/Deactivate** alumni
- **Create Portal User** for alumni access
- Add alumni to groups
- Add notes and achievements
- Track engagement (willing to mentor/recruit)

### ✅ View Statistics
- Achievement count
- Total achievement points
- Events attended
- Jobs posted

---

## 🔧 Alternative Access Methods

### Method 1: Direct URL
After upgrading, you can access directly:
```
http://localhost:8025/web#action=motakamel_alumni.action_op_alumni&model=op.alumni&view_type=list
```

### Method 2: Settings Menu
The module should also appear in:
```
Settings → OpenEduCat → Alumni
```
(If you've enabled it in the core module settings)

### Method 3: Search Bar
Use the Odoo search bar (top right):
1. Click the search icon
2. Type "Alumni"
3. Select "Alumni Records"

---

## 📋 Features Available in the UI

### List View Features:
- ✅ Alumni Number
- ✅ Full Name
- ✅ Email
- ✅ Course
- ✅ Graduation Date
- ✅ Graduation Year
- ✅ Status (with color badges)

### Form View Features:
- ✅ **Header Buttons**:
  - Activate/Deactivate
  - Create Portal User
  - Status bar
  
- ✅ **Personal Info Tab**:
  - Photo upload
  - Name fields
  - Contact details
  - Birth date & gender
  
- ✅ **Academic Info**:
  - Course, Batch, Program
  - Admission & Graduation dates
  - Grade, CGPA, Percentage
  
- ✅ **Professional Info**:
  - Current company & designation
  - Industry & experience
  - LinkedIn & website links
  
- ✅ **Address**:
  - Complete address fields
  
- ✅ **Groups Tab**:
  - View alumni groups
  - Add to groups
  
- ✅ **Notes Tab**:
  - General notes
  - Notable achievements
  
- ✅ **Chatter**:
  - Followers
  - Activities
  - Messages/Comments

### Search & Filter Features:
- ✅ Search by name, email, alumni number
- ✅ Filter: Active/Inactive
- ✅ Filter: Willing to Mentor
- ✅ Filter: Willing to Recruit
- ✅ Group by: Course, Year, State

---

## 🎯 Quick Actions

### Create Alumni from Student
(Wizard UI not created yet, but you can use code):
```python
# In Odoo shell or Python code
student = env['op.student'].browse(STUDENT_ID)
wizard = env['convert.to.alumni.wizard'].create({
    'student_ids': [(6, 0, [student.id])],
    'graduation_date': '2024-06-15',
    'grade': 'first_class',
})
wizard.action_convert()
```

### Create Portal Access
1. Open alumni record
2. Click **"Create Portal User"** button
3. Portal invitation email sent automatically

### View Alumni Statistics
Statistics are shown in the form view:
- Achievement count
- Total points
- Events attended
- Jobs posted

---

## ⚠️ Still Missing (To Be Created)

### Views Not Yet Created:
- ❌ Alumni Groups view
- ❌ Alumni Events view
- ❌ Alumni Jobs view
- ❌ Portal templates
- ❌ Website templates
- ❌ Wizard views (Convert to Alumni, Bulk Email)
- ❌ Reports (Alumni Card, Directory)

### To Create These:
1. Create the XML files
2. Uncomment in `__manifest__.py`
3. Upgrade the module

---

## 📞 Need Help?

### Documentation:
- `README.md` - Full module documentation
- `MODULE_STRUCTURE.md` - Technical details
- `QUICK_REFERENCE.md` - Quick reference
- `INSTALLATION_FIX.md` - Installation troubleshooting

### Support:
- Website: https://www.motakamel.com
- Email: support@motakamel.com

---

## ✨ Summary

**YOU CAN NOW:**
1. ✅ Access Alumni from the main menu
2. ✅ View alumni list
3. ✅ Create/edit alumni records
4. ✅ Search and filter alumni
5. ✅ Manage alumni status
6. ✅ Create portal access
7. ✅ View statistics

**NEXT STEPS:**
- Create more alumni records
- Organize alumni into groups
- Enable portal access for alumni
- (Later) Create event and job views

---

**Status**: ✅ Basic UI Ready  
**Last Updated**: November 3, 2025  
**Access**: Via "Alumni" menu in main menu bar

