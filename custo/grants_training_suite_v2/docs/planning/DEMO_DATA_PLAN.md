# Demo Data Implementation Plan

## 🎯 Strategy: Step-by-Step Demo Data Creation

**Approach**: Create demo data for each model individually, test after each step, and fix any field reference errors.

---

## 📋 Demo Data Structure Plan

### **Step 1: Intake Batch Demo Data**
- **File**: `demo/intake_batch_demo.xml`
- **Records**: 3 intake batches with different states
- **Fields to Include**:
  - `name`: Batch names
  - `filename`: Sample CSV filenames
  - `state`: Different states (draft, uploaded, validated, processed)
  - `upload_date`: Recent dates
  - `total_records`: Sample numbers
  - `error_records`: Sample error counts

### **Step 2: Student Demo Data**
- **File**: `demo/student_demo.xml`
- **Records**: 10 students with varied profiles
- **Fields to Include**:
  - `name`: Full names
  - `email`: Valid email addresses
  - `phone`: Phone numbers
  - `birth_date`: Various birth dates
  - `gender`: Male/Female
  - `education_level`: Different education levels
  - `state`: Different student states
  - `intake_batch_id`: Reference to intake batches

### **Step 3: Assignment Demo Data**
- **File**: `demo/assignment_demo.xml`
- **Records**: 8 assignments linking students to agents
- **Fields to Include**:
  - `student_id`: Reference to students
  - `agent_id`: Reference to users (agents)
  - `assignment_date`: Recent dates
  - `state`: Different assignment states
  - `notes`: Sample assignment notes

### **Step 4: Document Request Demo Data**
- **File**: `demo/document_request_demo.xml`
- **Records**: 15 document requests
- **Fields to Include**:
  - `student_id`: Reference to students
  - `document_type`: Different document types
  - `state`: Different request states
  - `request_date`: Recent dates
  - `due_date`: Future dates

### **Step 5: Course Session Demo Data**
- **File**: `demo/course_session_demo.xml`
- **Records**: 12 course sessions
- **Fields to Include**:
  - `student_id`: Reference to students
  - `session_name`: Course session names
  - `session_date`: Recent dates
  - `state`: Different session states
  - `attendance_status`: Different attendance statuses

### **Step 6: Homework Attempt Demo Data**
- **File**: `demo/homework_attempt_demo.xml`
- **Records**: 20 homework attempts
- **Fields to Include**:
  - `student_id`: Reference to students
  - `homework_name`: Homework names
  - `submission_date`: Recent dates
  - `state`: Different attempt states
  - `score`: Sample scores
  - `feedback`: Sample feedback

### **Step 7: Certificate Demo Data**
- **File**: `demo/certificate_demo.xml`
- **Records**: 6 certificates
- **Fields to Include**:
  - `student_id`: Reference to students
  - `certificate_name`: Certificate names
  - `issue_date`: Recent dates
  - `state`: Different certificate states
  - `certificate_number`: Sample certificate numbers

---

## 🔧 Implementation Steps

1. **Create Demo Directory Structure**
2. **Create Intake Batch Demo Data** (Test)
3. **Create Student Demo Data** (Test)
4. **Create Assignment Demo Data** (Test)
5. **Create Document Request Demo Data** (Test)
6. **Create Course Session Demo Data** (Test)
7. **Create Homework Attempt Demo Data** (Test)
8. **Create Certificate Demo Data** (Test)
9. **Update Manifest with Demo Files**
10. **Final Integration Test**
11. **Demo Data Verification (MANDATORY RULE)**
    - After each demo file is added and the module is upgraded, run a record count check.
    - Odoo shell (recommended):
      - python3 odoo-18/odoo18/odoo-bin shell -c /home/sabry3/odoo-dev/odoo_conf/odoo.conf -d courses2 -c "print(env['gr.intake.batch'].search_count([]), env['gr.student'].search_count([]))"
    - SQL (psql):
      - psql -h localhost -U odoo18 -d courses2 -c "SELECT 'gr_intake_batch' tbl, COUNT(*) FROM gr_intake_batch UNION ALL SELECT 'gr_student', COUNT(*) FROM gr_student;"

---

## ⚠️ Error Prevention Strategy

- **Field Validation**: Check each field exists in the model before using
- **Relationship Validation**: Ensure referenced records exist
- **Data Type Validation**: Use correct data types for each field
- **State Validation**: Use only valid state values
- **Date Validation**: Use realistic dates
- **Test After Each Step**: Update module and check logs after each demo file

---

## 📊 Expected Results

- **Total Demo Records**: ~74 records across 7 models
- **Realistic Data**: Professional, realistic demo data
- **Full Workflow**: Complete student journey from intake to certification
- **Error-Free**: All demo data loads without errors
- **User-Friendly**: Easy to understand and navigate

---

*Systematic demo data creation with error prevention! 🚀*
