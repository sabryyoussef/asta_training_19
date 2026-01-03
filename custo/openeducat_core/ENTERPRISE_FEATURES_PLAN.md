# OpenEduCat Core - Enterprise Features Implementation Plan

## Executive Summary

This document outlines a comprehensive plan to implement enterprise-level features for the OpenEduCat Core module. These features will enhance student lifecycle management, parent engagement, facility management, and overall institutional operations.

---

## Table of Contents

1. [Feature Overview](#feature-overview)
2. [Implementation Phases](#implementation-phases)
3. [Detailed Feature Specifications](#detailed-feature-specifications)
4. [Database Schema](#database-schema)
5. [Implementation Timeline](#implementation-timeline)
6. [Resource Requirements](#resource-requirements)

---

## Feature Overview

### Enterprise Features to Implement

| # | Feature | Category | Priority | Status |
|---|---------|----------|----------|--------|
| 1 | Achievement Enterprise | Student Lifecycle | High | ⚠️ Activity exists, needs enterprise upgrade |
| 2 | Activity Enterprise | Student Engagement | High | ✅ Basic exists, needs enterprise features |
| 3 | Discipline Enterprise | Student Management | High | ❌ New Module |
| 4 | Grievance Management | Student Support | High | ❌ New Module |
| 5 | Health Enterprise | Student Welfare | High | ❌ New Module |
| 6 | Subject Material Allocation | Academic Resources | Medium | ❌ New Module |
| 7 | Scholarship Enterprise | Financial Aid | Medium | ❌ New Module |
| 8 | Skill Enterprise | Competency Tracking | Medium | ❌ New Module |
| 9 | Student Mentor | Academic Support | Medium | ❌ New Module |
| 10 | Facility Enterprise | Infrastructure | Medium | ✅ Basic exists, needs enterprise features |
| 11 | Parent Enterprise | Parent Engagement | High | ✅ Basic exists, needs enterprise features |
| 12 | Convocation Management | Events | Low | ❌ New Module |
| 13 | Student Feedback | Quality Assurance | High | ❌ New Module |
| 14 | Student Withdrawal | Student Lifecycle | Medium | ❌ New Module |

---

## Implementation Phases

### Phase 1: Student Lifecycle & Support (6 weeks)
**Priority**: Critical
- Achievement Enterprise
- Discipline Enterprise
- Grievance Management
- Student Withdrawal Management

### Phase 2: Student Welfare & Development (5 weeks)
**Priority**: High
- Health Enterprise
- Scholarship Enterprise
- Skill Enterprise
- Student Mentor

### Phase 3: Academic Resources & Quality (4 weeks)
**Priority**: High
- Subject Material Allocation
- Student Feedback
- Activity Enterprise (Enhancement)

### Phase 4: Parent & Facility Enhancement (3 weeks)
**Priority**: Medium
- Parent Enterprise (Enhancement)
- Facility Enterprise (Enhancement)

### Phase 5: Events & Ceremonies (2 weeks)
**Priority**: Low
- Convocation Management

---

## Detailed Feature Specifications

### 1. Achievement Enterprise

#### Overview
Comprehensive system to track and manage student achievements including academic awards, competitions, certifications, and recognitions.

#### Models

```python
class OpAchievementType(models.Model):
    _name = 'op.achievement.type'
    _description = 'Achievement Type'
    
    name = fields.Char('Achievement Type', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    category = fields.Selection([
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('competition', 'Competition'),
        ('certification', 'Certification'),
        ('leadership', 'Leadership'),
        ('community', 'Community Service'),
        ('other', 'Other')
    ], 'Category', required=True)
    points = fields.Integer('Achievement Points', help="Points awarded for this achievement")
    certificate_required = fields.Boolean('Certificate Required')
    approval_required = fields.Boolean('Approval Required')
    active = fields.Boolean(default=True)

class OpStudentAchievement(models.Model):
    _name = 'op.student.achievement'
    _description = 'Student Achievement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'achievement_date desc'
    
    name = fields.Char('Achievement Title', required=True, tracking=True)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    achievement_type_id = fields.Many2one('op.achievement.type', 'Type', required=True, tracking=True)
    achievement_date = fields.Date('Achievement Date', required=True, default=fields.Date.today)
    
    # Details
    description = fields.Text('Description')
    level = fields.Selection([
        ('institution', 'Institution Level'),
        ('district', 'District Level'),
        ('state', 'State Level'),
        ('national', 'National Level'),
        ('international', 'International Level')
    ], 'Level', required=True, tracking=True)
    
    position = fields.Selection([
        ('first', 'First Position'),
        ('second', 'Second Position'),
        ('third', 'Third Position'),
        ('participation', 'Participation'),
        ('other', 'Other')
    ], 'Position/Rank')
    
    # Organization Details
    organized_by = fields.Char('Organized By')
    venue = fields.Char('Venue')
    
    # Documentation
    certificate = fields.Binary('Certificate/Document')
    certificate_filename = fields.Char('Certificate Filename')
    certificate_number = fields.Char('Certificate Number')
    
    # Approval Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], 'Status', default='draft', tracking=True)
    
    verified_by = fields.Many2one('res.users', 'Verified By')
    verified_date = fields.Date('Verification Date')
    approved_by = fields.Many2one('res.users', 'Approved By')
    approved_date = fields.Date('Approval Date')
    rejection_reason = fields.Text('Rejection Reason')
    
    # Points
    points_awarded = fields.Integer('Points Awarded', compute='_compute_points', store=True)
    
    # Additional Info
    team_members = fields.Text('Team Members (if applicable)')
    mentor_id = fields.Many2one('op.faculty', 'Mentor/Guide')
    
    @api.depends('achievement_type_id', 'level', 'position')
    def _compute_points(self):
        for record in self:
            base_points = record.achievement_type_id.points or 0
            # Multiply by level factor
            level_factor = {
                'institution': 1,
                'district': 2,
                'state': 3,
                'national': 5,
                'international': 10
            }.get(record.level, 1)
            
            # Multiply by position factor
            position_factor = {
                'first': 3,
                'second': 2,
                'third': 1.5,
                'participation': 1,
                'other': 1
            }.get(record.position, 1)
            
            record.points_awarded = int(base_points * level_factor * position_factor)
    
    def action_submit(self):
        self.state = 'submitted'
    
    def action_verify(self):
        self.write({
            'state': 'verified',
            'verified_by': self.env.user.id,
            'verified_date': fields.Date.today()
        })
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Date.today()
        })
    
    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Achievement',
            'res_model': 'op.achievement.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_achievement_id': self.id}
        }

class OpStudent(models.Model):
    _inherit = 'op.student'
    
    achievement_ids = fields.One2many('op.student.achievement', 'student_id', 'Achievements')
    achievement_count = fields.Integer('Total Achievements', compute='_compute_achievement_stats')
    total_achievement_points = fields.Integer('Total Points', compute='_compute_achievement_stats')
    
    @api.depends('achievement_ids', 'achievement_ids.state', 'achievement_ids.points_awarded')
    def _compute_achievement_stats(self):
        for student in self:
            approved_achievements = student.achievement_ids.filtered(lambda a: a.state == 'approved')
            student.achievement_count = len(approved_achievements)
            student.total_achievement_points = sum(approved_achievements.mapped('points_awarded'))
```

#### Views & Features
- Achievement dashboard for students
- Achievement timeline view
- Achievement certificate generation
- Achievement leaderboard
- Bulk achievement entry
- Achievement report by type/level/date
- Portal view for students to submit achievements
- Parent portal view to see child's achievements

---

### 2. Discipline Enterprise

#### Overview
Comprehensive discipline management system to track student behavior, incidents, warnings, and disciplinary actions.

#### Models

```python
class OpDisciplineType(models.Model):
    _name = 'op.discipline.type'
    _description = 'Discipline Type'
    
    name = fields.Char('Discipline Type', required=True)
    code = fields.Char('Code', required=True)
    category = fields.Selection([
        ('positive', 'Positive Behavior'),
        ('minor', 'Minor Violation'),
        ('major', 'Major Violation'),
        ('severe', 'Severe Violation')
    ], 'Category', required=True)
    severity_level = fields.Integer('Severity Level (1-10)', default=1)
    points_deduction = fields.Integer('Behavior Points Deduction')
    description = fields.Text('Description')
    active = fields.Boolean(default=True)

class OpDisciplineAction(models.Model):
    _name = 'op.discipline.action'
    _description = 'Disciplinary Action'
    
    name = fields.Char('Action Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    requires_parent_meeting = fields.Boolean('Requires Parent Meeting')
    suspension_days = fields.Integer('Suspension Days')
    active = fields.Boolean(default=True)

class OpStudentDiscipline(models.Model):
    _name = 'op.student.discipline'
    _description = 'Student Discipline Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'incident_date desc'
    
    name = fields.Char('Incident Title', required=True, tracking=True)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    discipline_type_id = fields.Many2one('op.discipline.type', 'Type', required=True, tracking=True)
    
    # Incident Details
    incident_date = fields.Datetime('Incident Date', required=True, default=fields.Datetime.now)
    incident_location = fields.Char('Location')
    description = fields.Text('Incident Description', required=True)
    
    # Reporting
    reported_by = fields.Many2one('res.users', 'Reported By', default=lambda self: self.env.user)
    witness_ids = fields.Many2many('res.users', string='Witnesses')
    
    # Action Taken
    action_ids = fields.Many2many('op.discipline.action', string='Actions Taken')
    action_description = fields.Text('Action Description')
    counseling_required = fields.Boolean('Counseling Required')
    counseling_date = fields.Date('Counseling Date')
    counselor_id = fields.Many2one('op.faculty', 'Counselor')
    
    # Parent Communication
    parent_notified = fields.Boolean('Parent Notified', tracking=True)
    parent_notification_date = fields.Datetime('Parent Notification Date')
    parent_meeting_required = fields.Boolean('Parent Meeting Required')
    parent_meeting_date = fields.Datetime('Parent Meeting Date')
    parent_meeting_notes = fields.Text('Parent Meeting Notes')
    
    # Follow-up
    follow_up_required = fields.Boolean('Follow-up Required')
    follow_up_date = fields.Date('Follow-up Date')
    follow_up_notes = fields.Text('Follow-up Notes')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('action_taken', 'Action Taken'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], 'Status', default='draft', tracking=True)
    
    # Points
    points_deducted = fields.Integer('Points Deducted', related='discipline_type_id.points_deduction')
    
    # Resolution
    resolution_date = fields.Date('Resolution Date')
    resolution_notes = fields.Text('Resolution Notes')
    
    def action_report(self):
        self.state = 'reported'
        # Notify relevant authorities
    
    def action_investigate(self):
        self.state = 'investigating'
    
    def action_take_action(self):
        self.state = 'action_taken'
    
    def action_resolve(self):
        self.state = 'resolved'
        self.resolution_date = fields.Date.today()
    
    def action_close(self):
        self.state = 'closed'
    
    def action_notify_parent(self):
        self.write({
            'parent_notified': True,
            'parent_notification_date': fields.Datetime.now()
        })
        # Send email/SMS to parent

class OpStudent(models.Model):
    _inherit = 'op.student'
    
    discipline_ids = fields.One2many('op.student.discipline', 'student_id', 'Discipline Records')
    discipline_count = fields.Integer('Discipline Incidents', compute='_compute_discipline_stats')
    behavior_points = fields.Integer('Behavior Points', compute='_compute_discipline_stats')
    
    @api.depends('discipline_ids', 'discipline_ids.state', 'discipline_ids.points_deducted')
    def _compute_discipline_stats(self):
        for student in self:
            closed_incidents = student.discipline_ids.filtered(lambda d: d.state in ['resolved', 'closed'])
            student.discipline_count = len(closed_incidents)
            # Start with 100 points, deduct for violations
            student.behavior_points = 100 - sum(closed_incidents.mapped('points_deducted'))
```

#### Features
- Incident reporting system
- Automated parent notifications
- Counseling scheduling
- Behavior tracking dashboard
- Discipline reports by type/severity
- Student behavior scorecard
- Early warning system for at-risk students

---

### 3. Grievance Management

#### Overview
Comprehensive grievance management system for students to raise concerns and track resolution.

#### Models

```python
class OpGrievanceCategory(models.Model):
    _name = 'op.grievance.category'
    _description = 'Grievance Category'
    
    name = fields.Char('Category', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    department_id = fields.Many2one('op.department', 'Responsible Department')
    escalation_days = fields.Integer('Escalation Days', default=7, 
                                     help="Days before auto-escalation")
    active = fields.Boolean(default=True)

class OpGrievance(models.Model):
    _name = 'op.grievance'
    _description = 'Student Grievance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char('Grievance Number', required=True, readonly=True, 
                      default=lambda self: 'New', copy=False)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    
    # Grievance Details
    category_id = fields.Many2one('op.grievance.category', 'Category', required=True, tracking=True)
    subject = fields.Char('Subject', required=True, tracking=True)
    description = fields.Text('Description', required=True)
    
    # Priority
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], 'Priority', default='medium', required=True, tracking=True)
    
    # Assignment
    assigned_to = fields.Many2one('res.users', 'Assigned To', tracking=True)
    department_id = fields.Many2one('op.department', 'Department', 
                                    related='category_id.department_id', store=True)
    
    # Dates
    submission_date = fields.Datetime('Submission Date', default=fields.Datetime.now, readonly=True)
    due_date = fields.Date('Due Date', compute='_compute_due_date', store=True)
    resolution_date = fields.Datetime('Resolution Date')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
        ('investigating', 'Under Investigation'),
        ('action_taken', 'Action Taken'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected')
    ], 'Status', default='draft', tracking=True)
    
    # Resolution
    resolution = fields.Text('Resolution')
    resolution_notes = fields.Text('Resolution Notes')
    satisfaction_rating = fields.Selection([
        ('1', 'Very Unsatisfied'),
        ('2', 'Unsatisfied'),
        ('3', 'Neutral'),
        ('4', 'Satisfied'),
        ('5', 'Very Satisfied')
    ], 'Satisfaction Rating')
    student_feedback = fields.Text('Student Feedback')
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Escalation
    escalated = fields.Boolean('Escalated', tracking=True)
    escalation_date = fields.Datetime('Escalation Date')
    escalated_to = fields.Many2one('res.users', 'Escalated To')
    
    # Anonymity
    anonymous = fields.Boolean('Anonymous Submission')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('op.grievance') or 'New'
        return super().create(vals)
    
    @api.depends('submission_date', 'category_id')
    def _compute_due_date(self):
        for record in self:
            if record.submission_date and record.category_id:
                days = record.category_id.escalation_days or 7
                record.due_date = (fields.Datetime.from_string(record.submission_date) + 
                                  timedelta(days=days)).date()
    
    def action_submit(self):
        self.state = 'submitted'
        # Notify assigned department
    
    def action_acknowledge(self):
        self.state = 'acknowledged'
        # Send acknowledgment to student
    
    def action_investigate(self):
        self.state = 'investigating'
    
    def action_resolve(self):
        self.write({
            'state': 'resolved',
            'resolution_date': fields.Datetime.now()
        })
        # Notify student of resolution
    
    def action_close(self):
        self.state = 'closed'
    
    def action_escalate(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Escalate Grievance',
            'res_model': 'op.grievance.escalate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_grievance_id': self.id}
        }
    
    @api.model
    def _cron_check_escalation(self):
        """Cron job to auto-escalate overdue grievances"""
        overdue = self.search([
            ('state', 'in', ['submitted', 'acknowledged', 'investigating']),
            ('due_date', '<', fields.Date.today()),
            ('escalated', '=', False)
        ])
        for grievance in overdue:
            grievance.action_escalate()
```

#### Features
- Student portal for grievance submission
- Anonymous grievance option
- Automated assignment based on category
- Email/SMS notifications
- Escalation workflow
- Resolution tracking
- Satisfaction survey
- Grievance analytics dashboard
- SLA monitoring

---

### 4. Health Enterprise

#### Overview
Comprehensive health management system for tracking student medical records, checkups, vaccinations, and health incidents.

#### Models

```python
class OpHealthRecordType(models.Model):
    _name = 'op.health.record.type'
    _description = 'Health Record Type'
    
    name = fields.Char('Record Type', required=True)
    code = fields.Char('Code', required=True)
    category = fields.Selection([
        ('checkup', 'Medical Checkup'),
        ('vaccination', 'Vaccination'),
        ('illness', 'Illness'),
        ('injury', 'Injury'),
        ('allergy', 'Allergy'),
        ('medication', 'Medication'),
        ('chronic', 'Chronic Condition'),
        ('other', 'Other')
    ], 'Category', required=True)
    active = fields.Boolean(default=True)

class OpStudentHealth(models.Model):
    _name = 'op.student.health'
    _description = 'Student Health Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'record_date desc'
    
    name = fields.Char('Record Number', required=True, readonly=True, 
                      default=lambda self: 'New', copy=False)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    
    # Record Details
    record_type_id = fields.Many2one('op.health.record.type', 'Type', required=True, tracking=True)
    record_date = fields.Date('Date', required=True, default=fields.Date.today)
    
    # Medical Details
    diagnosis = fields.Text('Diagnosis/Condition')
    symptoms = fields.Text('Symptoms')
    treatment = fields.Text('Treatment/Prescription')
    
    # Medical Professional
    doctor_name = fields.Char('Doctor/Nurse Name')
    hospital_clinic = fields.Char('Hospital/Clinic')
    
    # Vital Signs
    height = fields.Float('Height (cm)')
    weight = fields.Float('Weight (kg)')
    bmi = fields.Float('BMI', compute='_compute_bmi', store=True)
    blood_pressure = fields.Char('Blood Pressure')
    temperature = fields.Float('Temperature (°F)')
    pulse_rate = fields.Integer('Pulse Rate (bpm)')
    
    # Vaccination Details (if applicable)
    vaccine_name = fields.Char('Vaccine Name')
    vaccine_dose = fields.Char('Dose Number')
    next_dose_date = fields.Date('Next Dose Date')
    
    # Allergy Details (if applicable)
    allergen = fields.Char('Allergen')
    allergy_severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening')
    ], 'Severity')
    
    # Medication Details (if applicable)
    medication_name = fields.Char('Medication Name')
    dosage = fields.Char('Dosage')
    frequency = fields.Char('Frequency')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    
    # Documents
    prescription = fields.Binary('Prescription/Report')
    prescription_filename = fields.Char('Filename')
    medical_certificate = fields.Binary('Medical Certificate')
    certificate_filename = fields.Char('Certificate Filename')
    
    # Follow-up
    follow_up_required = fields.Boolean('Follow-up Required')
    follow_up_date = fields.Date('Follow-up Date')
    follow_up_notes = fields.Text('Follow-up Notes')
    
    # Restrictions
    activity_restrictions = fields.Text('Activity Restrictions')
    dietary_restrictions = fields.Text('Dietary Restrictions')
    restriction_start = fields.Date('Restriction Start Date')
    restriction_end = fields.Date('Restriction End Date')
    
    # Parent Notification
    parent_notified = fields.Boolean('Parent Notified')
    notification_date = fields.Datetime('Notification Date')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('archived', 'Archived')
    ], 'Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('op.student.health') or 'New'
        return super().create(vals)
    
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight and record.height > 0:
                height_m = record.height / 100  # Convert cm to meters
                record.bmi = record.weight / (height_m ** 2)
            else:
                record.bmi = 0.0
    
    def action_notify_parent(self):
        self.write({
            'parent_notified': True,
            'notification_date': fields.Datetime.now()
        })
        # Send notification to parent

class OpStudent(models.Model):
    _inherit = 'op.student'
    
    # Health Profile
    health_record_ids = fields.One2many('op.student.health', 'student_id', 'Health Records')
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ], 'Blood Group')
    
    # Current Health Status
    current_height = fields.Float('Current Height (cm)', compute='_compute_current_health')
    current_weight = fields.Float('Current Weight (kg)', compute='_compute_current_health')
    current_bmi = fields.Float('Current BMI', compute='_compute_current_health')
    
    # Allergies
    has_allergies = fields.Boolean('Has Allergies')
    allergy_details = fields.Text('Allergy Details')
    
    # Chronic Conditions
    has_chronic_condition = fields.Boolean('Has Chronic Condition')
    chronic_condition_details = fields.Text('Chronic Condition Details')
    
    # Emergency Medical Info
    emergency_medical_info = fields.Text('Emergency Medical Information')
    medical_insurance = fields.Char('Medical Insurance Number')
    insurance_provider = fields.Char('Insurance Provider')
    
    @api.depends('health_record_ids')
    def _compute_current_health(self):
        for student in self:
            latest_checkup = student.health_record_ids.filtered(
                lambda r: r.record_type_id.category == 'checkup' and r.height and r.weight
            ).sorted('record_date', reverse=True)[:1]
            
            if latest_checkup:
                student.current_height = latest_checkup.height
                student.current_weight = latest_checkup.weight
                student.current_bmi = latest_checkup.bmi
            else:
                student.current_height = 0.0
                student.current_weight = 0.0
                student.current_bmi = 0.0
```

#### Features
- Health record management
- Vaccination tracking
- Medical checkup scheduling
- Allergy alerts
- Medication tracking
- Health incident reporting
- Parent health portal
- Health analytics dashboard
- Medical certificate generation
- Emergency medical information access

---

### 5. Scholarship Enterprise

#### Overview
Comprehensive scholarship management system for tracking scholarships, applications, and disbursements.

#### Models

```python
class OpScholarshipType(models.Model):
    _name = 'op.scholarship.type'
    _description = 'Scholarship Type'
    
    name = fields.Char('Scholarship Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    
    # Scholarship Details
    category = fields.Selection([
        ('merit', 'Merit-based'),
        ('need', 'Need-based'),
        ('sports', 'Sports'),
        ('minority', 'Minority'),
        ('government', 'Government'),
        ('private', 'Private'),
        ('institutional', 'Institutional'),
        ('other', 'Other')
    ], 'Category', required=True)
    
    # Financial Details
    amount_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Fees'),
        ('variable', 'Variable')
    ], 'Amount Type', required=True)
    amount = fields.Float('Amount/Percentage')
    max_amount = fields.Float('Maximum Amount')
    
    # Eligibility Criteria
    min_gpa = fields.Float('Minimum GPA')
    min_attendance = fields.Float('Minimum Attendance %')
    income_criteria = fields.Float('Maximum Family Income')
    eligibility_description = fields.Text('Eligibility Criteria')
    
    # Application
    application_required = fields.Boolean('Application Required')
    application_start_date = fields.Date('Application Start Date')
    application_end_date = fields.Date('Application End Date')
    
    # Documents Required
    documents_required = fields.Text('Documents Required')
    
    # Availability
    total_scholarships = fields.Integer('Total Scholarships Available')
    scholarships_awarded = fields.Integer('Scholarships Awarded', compute='_compute_awarded')
    scholarships_remaining = fields.Integer('Remaining', compute='_compute_awarded')
    
    # Status
    active = fields.Boolean(default=True)
    
    @api.depends('scholarship_ids')
    def _compute_awarded(self):
        for scholarship_type in self:
            awarded = self.env['op.student.scholarship'].search_count([
                ('scholarship_type_id', '=', scholarship_type.id),
                ('state', '=', 'approved')
            ])
            scholarship_type.scholarships_awarded = awarded
            scholarship_type.scholarships_remaining = scholarship_type.total_scholarships - awarded

class OpStudentScholarship(models.Model):
    _name = 'op.student.scholarship'
    _description = 'Student Scholarship'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'application_date desc'
    
    name = fields.Char('Application Number', required=True, readonly=True, 
                      default=lambda self: 'New', copy=False)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    scholarship_type_id = fields.Many2one('op.scholarship.type', 'Scholarship', 
                                         required=True, tracking=True)
    
    # Application Details
    application_date = fields.Date('Application Date', default=fields.Date.today, readonly=True)
    academic_year_id = fields.Many2one('op.academic.year', 'Academic Year', required=True)
    
    # Financial Details
    amount_requested = fields.Float('Amount Requested')
    amount_approved = fields.Float('Amount Approved', tracking=True)
    
    # Eligibility Check
    current_gpa = fields.Float('Current GPA')
    current_attendance = fields.Float('Current Attendance %')
    family_income = fields.Float('Family Annual Income')
    
    # Application Details
    reason = fields.Text('Reason for Application', required=True)
    additional_info = fields.Text('Additional Information')
    
    # Documents
    document_ids = fields.Many2many('ir.attachment', string='Supporting Documents')
    
    # Approval Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', tracking=True)
    
    reviewed_by = fields.Many2one('res.users', 'Reviewed By')
    review_date = fields.Date('Review Date')
    review_notes = fields.Text('Review Notes')
    
    approved_by = fields.Many2one('res.users', 'Approved By')
    approval_date = fields.Date('Approval Date')
    rejection_reason = fields.Text('Rejection Reason')
    
    # Disbursement
    disbursement_ids = fields.One2many('op.scholarship.disbursement', 
                                       'scholarship_id', 'Disbursements')
    total_disbursed = fields.Float('Total Disbursed', compute='_compute_disbursed')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('op.student.scholarship') or 'New'
        return super().create(vals)
    
    @api.depends('disbursement_ids', 'disbursement_ids.amount')
    def _compute_disbursed(self):
        for record in self:
            record.total_disbursed = sum(record.disbursement_ids.mapped('amount'))
    
    def action_submit(self):
        # Check eligibility
        if not self._check_eligibility():
            raise ValidationError("Student does not meet eligibility criteria")
        self.state = 'submitted'
    
    def _check_eligibility(self):
        scholarship = self.scholarship_type_id
        if scholarship.min_gpa and self.current_gpa < scholarship.min_gpa:
            return False
        if scholarship.min_attendance and self.current_attendance < scholarship.min_attendance:
            return False
        if scholarship.income_criteria and self.family_income > scholarship.income_criteria:
            return False
        return True
    
    def action_review(self):
        self.state = 'under_review'
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Date.today()
        })
    
    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Scholarship',
            'res_model': 'op.scholarship.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_scholarship_id': self.id}
        }

class OpScholarshipDisbursement(models.Model):
    _name = 'op.scholarship.disbursement'
    _description = 'Scholarship Disbursement'
    _order = 'disbursement_date desc'
    
    scholarship_id = fields.Many2one('op.student.scholarship', 'Scholarship', required=True)
    disbursement_date = fields.Date('Disbursement Date', required=True)
    amount = fields.Float('Amount', required=True)
    payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('fee_waiver', 'Fee Waiver')
    ], 'Payment Method', required=True)
    reference = fields.Char('Reference Number')
    notes = fields.Text('Notes')
```

#### Features
- Scholarship catalog
- Online scholarship application
- Eligibility checking
- Document submission
- Approval workflow
- Disbursement tracking
- Scholarship analytics
- Student scholarship portal
- Automated notifications

---

### 6. Skill Enterprise

#### Overview
Track and manage student skills, competencies, and skill development programs.

#### Models

```python
class OpSkillCategory(models.Model):
    _name = 'op.skill.category'
    _description = 'Skill Category'
    
    name = fields.Char('Category', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    parent_id = fields.Many2one('op.skill.category', 'Parent Category')
    active = fields.Boolean(default=True)

class OpSkill(models.Model):
    _name = 'op.skill'
    _description = 'Skill'
    
    name = fields.Char('Skill Name', required=True)
    code = fields.Char('Code', required=True)
    category_id = fields.Many2one('op.skill.category', 'Category', required=True)
    description = fields.Text('Description')
    
    # Skill Type
    skill_type = fields.Selection([
        ('technical', 'Technical'),
        ('soft', 'Soft Skill'),
        ('language', 'Language'),
        ('tool', 'Tool/Software'),
        ('other', 'Other')
    ], 'Type', required=True)
    
    # Proficiency Levels
    has_levels = fields.Boolean('Has Proficiency Levels', default=True)
    level_ids = fields.One2many('op.skill.level', 'skill_id', 'Proficiency Levels')
    
    active = fields.Boolean(default=True)

class OpSkillLevel(models.Model):
    _name = 'op.skill.level'
    _description = 'Skill Proficiency Level'
    _order = 'sequence'
    
    skill_id = fields.Many2one('op.skill', 'Skill', required=True)
    name = fields.Char('Level Name', required=True)  # e.g., Beginner, Intermediate, Advanced
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')

class OpStudentSkill(models.Model):
    _name = 'op.student.skill'
    _description = 'Student Skill'
    _inherit = ['mail.thread']
    
    student_id = fields.Many2one('op.student', 'Student', required=True)
    skill_id = fields.Many2one('op.skill', 'Skill', required=True, tracking=True)
    level_id = fields.Many2one('op.skill.level', 'Proficiency Level', tracking=True)
    
    # Proficiency
    proficiency = fields.Selection([
        ('1', 'Beginner'),
        ('2', 'Elementary'),
        ('3', 'Intermediate'),
        ('4', 'Advanced'),
        ('5', 'Expert')
    ], 'Proficiency', tracking=True)
    
    # Acquisition
    acquired_date = fields.Date('Acquired Date')
    how_acquired = fields.Selection([
        ('course', 'Course/Training'),
        ('project', 'Project'),
        ('self_learned', 'Self-Learned'),
        ('certification', 'Certification'),
        ('work', 'Work Experience'),
        ('other', 'Other')
    ], 'How Acquired')
    
    # Certification
    certified = fields.Boolean('Certified')
    certification_name = fields.Char('Certification Name')
    certification_date = fields.Date('Certification Date')
    certification_document = fields.Binary('Certificate')
    certification_filename = fields.Char('Filename')
    
    # Verification
    verified = fields.Boolean('Verified')
    verified_by = fields.Many2one('res.users', 'Verified By')
    verification_date = fields.Date('Verification Date')
    
    # Additional Info
    years_experience = fields.Float('Years of Experience')
    notes = fields.Text('Notes')
    
    _sql_constraints = [
        ('unique_student_skill', 'unique(student_id, skill_id)', 
         'This skill already exists for the student!')
    ]

class OpStudent(models.Model):
    _inherit = 'op.student'
    
    skill_ids = fields.One2many('op.student.skill', 'student_id', 'Skills')
    skill_count = fields.Integer('Total Skills', compute='_compute_skill_count')
    
    @api.depends('skill_ids')
    def _compute_skill_count(self):
        for student in self:
            student.skill_count = len(student.skill_ids)
```

#### Features
- Skill catalog management
- Student skill profiles
- Skill assessment
- Certification tracking
- Skill gap analysis
- Skill development recommendations
- Skill-based student search
- Skill analytics dashboard

---

### 7. Student Mentor

#### Overview
Assign mentors to students and track mentoring activities.

#### Models

```python
class OpMentorCategory(models.Model):
    _name = 'op.mentor.category'
    _description = 'Mentor Category'
    
    name = fields.Char('Category', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    active = fields.Boolean(default=True)

class OpMentor(models.Model):
    _name = 'op.mentor'
    _description = 'Mentor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    faculty_id = fields.Many2one('op.faculty', 'Faculty', required=True)
    name = fields.Char('Name', related='faculty_id.name', store=True)
    category_id = fields.Many2one('op.mentor.category', 'Category')
    
    # Mentoring Details
    max_mentees = fields.Integer('Maximum Mentees', default=10)
    current_mentees = fields.Integer('Current Mentees', compute='_compute_mentees')
    available_slots = fields.Integer('Available Slots', compute='_compute_mentees')
    
    # Expertise
    expertise_area = fields.Text('Area of Expertise')
    
    # Availability
    available = fields.Boolean('Available for Mentoring', default=True)
    
    # Mentees
    mentee_ids = fields.One2many('op.student.mentor', 'mentor_id', 'Mentees')
    
    @api.depends('mentee_ids', 'max_mentees')
    def _compute_mentees(self):
        for mentor in self:
            active_mentees = mentor.mentee_ids.filtered(lambda m: m.state == 'active')
            mentor.current_mentees = len(active_mentees)
            mentor.available_slots = mentor.max_mentees - mentor.current_mentees

class OpStudentMentor(models.Model):
    _name = 'op.student.mentor'
    _description = 'Student Mentor Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    mentor_id = fields.Many2one('op.mentor', 'Mentor', required=True, tracking=True)
    
    # Assignment Details
    start_date = fields.Date('Start Date', required=True, default=fields.Date.today)
    end_date = fields.Date('End Date')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', tracking=True)
    
    # Meetings
    meeting_ids = fields.One2many('op.mentor.meeting', 'student_mentor_id', 'Meetings')
    meeting_count = fields.Integer('Total Meetings', compute='_compute_meetings')
    
    # Goals
    goals = fields.Text('Mentoring Goals')
    progress_notes = fields.Text('Progress Notes')
    
    @api.depends('meeting_ids')
    def _compute_meetings(self):
        for record in self:
            record.meeting_count = len(record.meeting_ids)
    
    def action_activate(self):
        self.state = 'active'
    
    def action_complete(self):
        self.state = 'completed'
        self.end_date = fields.Date.today()

class OpMentorMeeting(models.Model):
    _name = 'op.mentor.meeting'
    _description = 'Mentor Meeting'
    _order = 'meeting_date desc'
    
    student_mentor_id = fields.Many2one('op.student.mentor', 'Student-Mentor', required=True)
    student_id = fields.Many2one('op.student', 'Student', related='student_mentor_id.student_id')
    mentor_id = fields.Many2one('op.mentor', 'Mentor', related='student_mentor_id.mentor_id')
    
    # Meeting Details
    meeting_date = fields.Datetime('Meeting Date', required=True)
    duration = fields.Float('Duration (hours)')
    location = fields.Char('Location')
    meeting_type = fields.Selection([
        ('in_person', 'In Person'),
        ('online', 'Online'),
        ('phone', 'Phone')
    ], 'Type', required=True)
    
    # Discussion
    agenda = fields.Text('Agenda')
    discussion_points = fields.Text('Discussion Points')
    action_items = fields.Text('Action Items')
    
    # Follow-up
    next_meeting_date = fields.Datetime('Next Meeting Date')
    
    # Status
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='scheduled')

class OpStudent(models.Model):
    _inherit = 'op.student'
    
    mentor_ids = fields.One2many('op.student.mentor', 'student_id', 'Mentors')
    current_mentor_id = fields.Many2one('op.mentor', 'Current Mentor', 
                                        compute='_compute_current_mentor')
    
    @api.depends('mentor_ids', 'mentor_ids.state')
    def _compute_current_mentor(self):
        for student in self:
            active_mentor = student.mentor_ids.filtered(lambda m: m.state == 'active')[:1]
            student.current_mentor_id = active_mentor.mentor_id if active_mentor else False
```

#### Features
- Mentor assignment
- Meeting scheduling
- Progress tracking
- Goal setting
- Meeting notes
- Mentor-mentee portal
- Mentoring analytics
- Automated reminders

---

### 8. Subject Material Allocation

#### Overview
Manage and allocate subject materials, resources, and learning content to students.

#### Models

```python
class OpSubjectMaterialType(models.Model):
    _name = 'op.subject.material.type'
    _description = 'Subject Material Type'
    
    name = fields.Char('Material Type', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    active = fields.Boolean(default=True)

class OpSubjectMaterial(models.Model):
    _name = 'op.subject.material'
    _description = 'Subject Material'
    _inherit = ['mail.thread']
    
    name = fields.Char('Material Name', required=True, tracking=True)
    subject_id = fields.Many2one('op.subject', 'Subject', required=True, tracking=True)
    material_type_id = fields.Many2one('op.subject.material.type', 'Type', required=True)
    
    # Material Details
    description = fields.Text('Description')
    content_type = fields.Selection([
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('link', 'External Link'),
        ('book', 'Book'),
        ('other', 'Other')
    ], 'Content Type', required=True)
    
    # File/Link
    file = fields.Binary('File')
    filename = fields.Char('Filename')
    url = fields.Char('URL')
    
    # Metadata
    author = fields.Char('Author')
    publication_date = fields.Date('Publication Date')
    isbn = fields.Char('ISBN')
    
    # Availability
    available_from = fields.Date('Available From')
    available_to = fields.Date('Available To')
    
    # Access Control
    access_level = fields.Selection([
        ('public', 'Public'),
        ('enrolled', 'Enrolled Students Only'),
        ('restricted', 'Restricted')
    ], 'Access Level', default='enrolled', required=True)
    
    # Status
    active = fields.Boolean(default=True)
    
    # Allocations
    allocation_ids = fields.One2many('op.material.allocation', 'material_id', 'Allocations')

class OpMaterialAllocation(models.Model):
    _name = 'op.material.allocation'
    _description = 'Material Allocation'
    _inherit = ['mail.thread']
    
    material_id = fields.Many2one('op.subject.material', 'Material', required=True)
    
    # Allocation Target
    allocation_type = fields.Selection([
        ('student', 'Individual Student'),
        ('batch', 'Batch'),
        ('course', 'Course')
    ], 'Allocation Type', required=True)
    
    student_id = fields.Many2one('op.student', 'Student')
    batch_id = fields.Many2one('op.batch', 'Batch')
    course_id = fields.Many2one('op.course', 'Course')
    
    # Dates
    allocation_date = fields.Date('Allocation Date', default=fields.Date.today)
    due_date = fields.Date('Due Date')
    
    # Status
    state = fields.Selection([
        ('allocated', 'Allocated'),
        ('accessed', 'Accessed'),
        ('completed', 'Completed')
    ], 'Status', default='allocated', tracking=True)
    
    # Tracking
    first_access_date = fields.Datetime('First Accessed')
    last_access_date = fields.Datetime('Last Accessed')
    access_count = fields.Integer('Access Count', default=0)
    
    # Completion
    completed_date = fields.Date('Completed Date')
    completion_notes = fields.Text('Completion Notes')
    
    def action_mark_accessed(self):
        if not self.first_access_date:
            self.first_access_date = fields.Datetime.now()
        self.last_access_date = fields.Datetime.now()
        self.access_count += 1
        if self.state == 'allocated':
            self.state = 'accessed'
    
    def action_mark_completed(self):
        self.write({
            'state': 'completed',
            'completed_date': fields.Date.today()
        })
```

#### Features
- Material repository
- Batch allocation
- Individual allocation
- Access tracking
- Material analytics
- Student material portal
- Download tracking
- Completion tracking

---

### 9. Student Feedback

#### Overview
Collect and manage student feedback on courses, faculty, and facilities.

#### Models

```python
class OpFeedbackTemplate(models.Model):
    _name = 'op.feedback.template'
    _description = 'Feedback Template'
    
    name = fields.Char('Template Name', required=True)
    feedback_type = fields.Selection([
        ('course', 'Course Feedback'),
        ('faculty', 'Faculty Feedback'),
        ('facility', 'Facility Feedback'),
        ('general', 'General Feedback')
    ], 'Type', required=True)
    
    description = fields.Text('Description')
    question_ids = fields.One2many('op.feedback.question', 'template_id', 'Questions')
    active = fields.Boolean(default=True)

class OpFeedbackQuestion(models.Model):
    _name = 'op.feedback.question'
    _description = 'Feedback Question'
    _order = 'sequence'
    
    template_id = fields.Many2one('op.feedback.template', 'Template', required=True)
    sequence = fields.Integer('Sequence', default=10)
    question = fields.Text('Question', required=True)
    
    question_type = fields.Selection([
        ('rating', 'Rating (1-5)'),
        ('text', 'Text'),
        ('choice', 'Multiple Choice'),
        ('checkbox', 'Checkbox')
    ], 'Type', required=True)
    
    choices = fields.Text('Choices (one per line)')
    required = fields.Boolean('Required', default=True)

class OpStudentFeedback(models.Model):
    _name = 'op.student.feedback'
    _description = 'Student Feedback'
    _inherit = ['mail.thread']
    
    name = fields.Char('Feedback Number', required=True, readonly=True, 
                      default=lambda self: 'New', copy=False)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    template_id = fields.Many2one('op.feedback.template', 'Template', required=True)
    
    # Feedback Target
    course_id = fields.Many2one('op.course', 'Course')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    facility_id = fields.Many2one('op.facility', 'Facility')
    
    # Dates
    feedback_date = fields.Date('Feedback Date', default=fields.Date.today, readonly=True)
    academic_year_id = fields.Many2one('op.academic.year', 'Academic Year')
    academic_term_id = fields.Many2one('op.academic.term', 'Term')
    
    # Responses
    response_ids = fields.One2many('op.feedback.response', 'feedback_id', 'Responses')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ], 'Status', default='draft')
    
    # Anonymous
    anonymous = fields.Boolean('Anonymous')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('op.student.feedback') or 'New'
        return super().create(vals)
    
    def action_submit(self):
        self.state = 'submitted'

class OpFeedbackResponse(models.Model):
    _name = 'op.feedback.response'
    _description = 'Feedback Response'
    
    feedback_id = fields.Many2one('op.student.feedback', 'Feedback', required=True)
    question_id = fields.Many2one('op.feedback.question', 'Question', required=True)
    
    # Response
    rating = fields.Integer('Rating')
    text_response = fields.Text('Text Response')
    choice_response = fields.Char('Choice Response')
```

#### Features
- Feedback templates
- Course feedback
- Faculty feedback
- Anonymous feedback option
- Feedback analytics
- Automated feedback requests
- Feedback reports
- Action item tracking

---

### 10. Student Withdrawal Management

#### Overview
Manage student withdrawal process including reasons, clearance, and documentation.

#### Models

```python
class OpWithdrawalReason(models.Model):
    _name = 'op.withdrawal.reason'
    _description = 'Withdrawal Reason'
    
    name = fields.Char('Reason', required=True)
    code = fields.Char('Code', required=True)
    category = fields.Selection([
        ('academic', 'Academic'),
        ('financial', 'Financial'),
        ('personal', 'Personal'),
        ('health', 'Health'),
        ('transfer', 'Transfer'),
        ('other', 'Other')
    ], 'Category', required=True)
    active = fields.Boolean(default=True)

class OpStudentWithdrawal(models.Model):
    _name = 'op.student.withdrawal'
    _description = 'Student Withdrawal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Withdrawal Number', required=True, readonly=True, 
                      default=lambda self: 'New', copy=False)
    student_id = fields.Many2one('op.student', 'Student', required=True, tracking=True)
    
    # Withdrawal Details
    withdrawal_date = fields.Date('Withdrawal Date', required=True, tracking=True)
    reason_id = fields.Many2one('op.withdrawal.reason', 'Reason', required=True, tracking=True)
    detailed_reason = fields.Text('Detailed Reason')
    
    # Clearance
    clearance_ids = fields.One2many('op.withdrawal.clearance', 'withdrawal_id', 'Clearances')
    all_cleared = fields.Boolean('All Cleared', compute='_compute_clearance_status')
    
    # Documents
    withdrawal_letter = fields.Binary('Withdrawal Letter')
    letter_filename = fields.Char('Filename')
    
    # Refund
    refund_applicable = fields.Boolean('Refund Applicable')
    refund_amount = fields.Float('Refund Amount')
    refund_processed = fields.Boolean('Refund Processed')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('clearance', 'Clearance in Progress'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], 'Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('op.student.withdrawal') or 'New'
        return super().create(vals)
    
    @api.depends('clearance_ids', 'clearance_ids.state')
    def _compute_clearance_status(self):
        for record in self:
            if record.clearance_ids:
                record.all_cleared = all(c.state == 'cleared' for c in record.clearance_ids)
            else:
                record.all_cleared = False
    
    def action_submit(self):
        self.state = 'submitted'
        self._create_clearances()
    
    def _create_clearances(self):
        """Create clearance items for all departments"""
        clearance_depts = [
            ('library', 'Library'),
            ('accounts', 'Accounts'),
            ('hostel', 'Hostel'),
            ('transport', 'Transport'),
            ('academic', 'Academic Department')
        ]
        for code, name in clearance_depts:
            self.env['op.withdrawal.clearance'].create({
                'withdrawal_id': self.id,
                'department': code,
                'department_name': name
            })
    
    def action_approve(self):
        if not self.all_cleared:
            raise ValidationError("All clearances must be completed before approval")
        self.state = 'approved'
    
    def action_complete(self):
        self.state = 'completed'
        # Update student status
        self.student_id.write({'active': False, 'status': 'withdrawn'})

class OpWithdrawalClearance(models.Model):
    _name = 'op.withdrawal.clearance'
    _description = 'Withdrawal Clearance'
    
    withdrawal_id = fields.Many2one('op.student.withdrawal', 'Withdrawal', required=True)
    department = fields.Char('Department Code', required=True)
    department_name = fields.Char('Department', required=True)
    
    # Clearance
    state = fields.Selection([
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('hold', 'On Hold')
    ], 'Status', default='pending', tracking=True)
    
    cleared_by = fields.Many2one('res.users', 'Cleared By')
    clearance_date = fields.Date('Clearance Date')
    notes = fields.Text('Notes')
    hold_reason = fields.Text('Hold Reason')
    
    def action_clear(self):
        self.write({
            'state': 'cleared',
            'cleared_by': self.env.user.id,
            'clearance_date': fields.Date.today()
        })
    
    def action_hold(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Put on Hold',
            'res_model': 'op.clearance.hold.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_clearance_id': self.id}
        }
```

#### Features
- Withdrawal application
- Multi-department clearance
- Refund processing
- Exit interview
- Withdrawal analytics
- Certificate issuance
- Records archival

---

### 11. Convocation Management

#### Overview
Manage convocation ceremonies, invitations, and attendance.

#### Models

```python
class OpConvocation(models.Model):
    _name = 'op.convocation'
    _description = 'Convocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Convocation Name', required=True, tracking=True)
    convocation_date = fields.Datetime('Date & Time', required=True, tracking=True)
    venue = fields.Char('Venue', required=True)
    
    # Details
    description = fields.Text('Description')
    chief_guest = fields.Char('Chief Guest')
    
    # Eligibility
    academic_year_id = fields.Many2one('op.academic.year', 'Academic Year')
    program_ids = fields.Many2many('op.program', string='Programs')
    
    # Students
    student_ids = fields.Many2many('op.student', string='Invited Students')
    student_count = fields.Integer('Total Students', compute='_compute_counts')
    confirmed_count = fields.Integer('Confirmed', compute='_compute_counts')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('invitations_sent', 'Invitations Sent'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', tracking=True)
    
    # Attendance
    attendance_ids = fields.One2many('op.convocation.attendance', 'convocation_id', 'Attendance')
    
    @api.depends('student_ids', 'attendance_ids')
    def _compute_counts(self):
        for record in self:
            record.student_count = len(record.student_ids)
            record.confirmed_count = len(record.attendance_ids.filtered(lambda a: a.confirmed))

class OpConvocationAttendance(models.Model):
    _name = 'op.convocation.attendance'
    _description = 'Convocation Attendance'
    
    convocation_id = fields.Many2one('op.convocation', 'Convocation', required=True)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    
    # RSVP
    invitation_sent = fields.Boolean('Invitation Sent')
    invitation_date = fields.Date('Invitation Date')
    confirmed = fields.Boolean('Confirmed')
    confirmation_date = fields.Date('Confirmation Date')
    
    # Attendance
    attended = fields.Boolean('Attended')
    guests_count = fields.Integer('Number of Guests')
    
    # Certificate
    certificate_issued = fields.Boolean('Certificate Issued')
    certificate_number = fields.Char('Certificate Number')
```

---

## Implementation Timeline

### Phase 1: Student Lifecycle & Support (6 weeks)
**Weeks 1-2**: Achievement Enterprise
**Weeks 3-4**: Discipline Enterprise
**Weeks 5**: Grievance Management
**Week 6**: Student Withdrawal Management

### Phase 2: Student Welfare & Development (5 weeks)
**Weeks 7-8**: Health Enterprise
**Weeks 9-10**: Scholarship Enterprise
**Week 11**: Skill Enterprise & Student Mentor

### Phase 3: Academic Resources & Quality (4 weeks)
**Weeks 12-13**: Subject Material Allocation
**Week 14**: Student Feedback
**Week 15**: Activity Enterprise Enhancement

### Phase 4: Parent & Facility Enhancement (3 weeks)
**Weeks 16-17**: Parent Enterprise Enhancement
**Week 18**: Facility Enterprise Enhancement

### Phase 5: Events & Ceremonies (2 weeks)
**Weeks 19-20**: Convocation Management

**Total Duration: 20 weeks (5 months)**

---

## Resource Requirements

### Development Team
- 3 Senior Odoo Developers (full-time)
- 1 Frontend Developer (full-time)
- 1 UI/UX Designer (part-time)
- 1 QA Engineer (full-time)
- 1 Technical Writer (part-time)
- 1 Project Manager (part-time)

### Infrastructure
- Development server
- Staging server
- Testing environment
- Documentation platform

---

## Success Metrics

### Quantitative
- All 14 enterprise features implemented
- 95% test coverage
- <3 second page load time
- 90% user adoption rate

### Qualitative
- Improved student engagement
- Better parent transparency
- Enhanced institutional efficiency
- Comprehensive student lifecycle tracking

---

**Document Version**: 1.0  
**Last Updated**: November 3, 2025  
**Status**: Planning  
**Approved By**: Pending

