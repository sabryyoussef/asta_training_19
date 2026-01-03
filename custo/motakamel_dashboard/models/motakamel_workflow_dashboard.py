from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MotakamelWorkflowDashboard(models.Model):
    _name = 'motakamel.workflow.dashboard'
    _description = 'Motakamel Workflow Dashboard'
    _order = 'sequence, name'

    name = fields.Char(string='Workflow Name', required=True)
    description = fields.Text(string='Description')
    diagram_content = fields.Html(string='Workflow Diagram', help="HTML/SVG content for workflow visualization")
    sequence = fields.Integer(string='Sequence', default=10)
    icon = fields.Char(string='Icon Path')
    color = fields.Char(string='Color Code', help="Hex color code for visual distinction")
    stage_ids = fields.One2many('motakamel.workflow.stage', 'workflow_id', string='Stages')
    is_active = fields.Boolean(string='Active', default=True)

    @api.model
    def get_student_lifecycle_workflow(self):
        """Get or create the Student Lifecycle workflow"""
        workflow = self.search([('name', '=', 'Student Lifecycle')], limit=1)
        if not workflow:
            workflow = self.create({
                'name': 'Student Lifecycle',
                'description': 'Complete student journey from inquiry to graduation',
                'sequence': 10,
                'icon': 'fa-graduation-cap',
                'color': '#3498db',
            })
        return workflow

    def action_open_workflow_dashboard(self):
        """Open the workflow dashboard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} Dashboard',
            'res_model': 'motakamel.workflow.dashboard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_archive(self):
        """Archive the workflow"""
        for workflow in self:
            workflow.is_active = False
        return True

    def action_unarchive(self):
        """Unarchive the workflow"""
        for workflow in self:
            workflow.is_active = True
        return True

    def unlink(self):
        """Override unlink to handle cascade deletion of stages"""
        # Delete related stages first
        for workflow in self:
            if workflow.stage_ids:
                workflow.stage_ids.unlink()
        return super(MotakamelWorkflowDashboard, self).unlink()


class MotakamelWorkflowStage(models.Model):
    _name = 'motakamel.workflow.stage'
    _description = 'Motakamel Workflow Stage'
    _order = 'sequence, name'

    name = fields.Char(string='Stage Name', required=True)
    workflow_id = fields.Many2one('motakamel.workflow.dashboard', string='Workflow', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    icon = fields.Char(string='Icon Path')
    color = fields.Char(string='Color Code')
    button_label = fields.Char(string='Button Label', default='Open')
    action_method = fields.Char(string='Action Method', default='action_open_module')
    technical_name = fields.Char(string='Technical Name', help="Technical name of the related module")
    menu_xmlid = fields.Char(string='Menu XML ID', help='XML ID of the menu to open')
    is_completed = fields.Boolean(string='Completed', default=False)
    is_current = fields.Boolean(string='Current Stage', default=False)

    def action_execute_stage(self):
        """Execute the stage action"""
        self.ensure_one()
        
        _logger.info("=" * 60)
        _logger.info("WORKFLOW: action_execute_stage called for stage: %s", self.name)
        _logger.info("Action Method: %s", self.action_method)
        _logger.info("Technical Name: %s", self.technical_name)
        _logger.info("Button Label: %s", self.button_label)
        
        # Map action methods to specific module actions
        action_mapping = {
            # Student Lifecycle Actions
            'action_open_admission_applications': {
                'type': 'ir.actions.act_window',
                'name': 'Admission Applications',
                'res_model': 'op.admission',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_admission_registers': {
                'type': 'ir.actions.act_window',
                'name': 'Admission Registers',
                'res_model': 'op.admission.register',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_module': {
                'type': 'ir.actions.act_window',
                'name': 'Student Management',
                'res_model': 'op.student',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_assignment_main': {
                'type': 'ir.actions.act_window',
                'name': 'Assignments',
                'res_model': 'op.assignment',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_exam_results': {
                'type': 'ir.actions.act_window',
                'name': 'Exam Results',
                'res_model': 'op.result.template',
                'view_mode': 'list,form',
                'target': 'current',
            },
            # Academic Operations Actions
            'action_open_timetable_main': {
                'type': 'ir.actions.act_window',
                'name': 'Timetables',
                'res_model': 'op.session',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_attendance_main': {
                'type': 'ir.actions.act_window',
                'name': 'Attendance',
                'res_model': 'op.attendance.sheet',
                'view_mode': 'list,form',
                'target': 'current',
            },
            # Financial Management Actions
            'action_open_fees_main': {
                'type': 'ir.actions.act_window',
                'name': 'Fee Terms',
                'res_model': 'op.fees.terms',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_fees_collection': {
                'type': 'ir.actions.act_window',
                'name': 'Student Fees',
                'res_model': 'op.student.fees.details',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_accounting_main': {
                'type': 'ir.actions.act_window',
                'name': 'Accounting',
                'res_model': 'account.move',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_financial_reports': {
                'type': 'ir.actions.act_window',
                'name': 'Fees Analysis',
                'res_model': 'op.student.fees.details',
                'view_mode': 'list,form',
                'target': 'current',
            },
            # Resource Administration Actions
            'action_open_facility_main': {
                'type': 'ir.actions.act_window',
                'name': 'Facilities',
                'res_model': 'op.facility',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_classroom_main': {
                'type': 'ir.actions.act_window',
                'name': 'Classrooms',
                'res_model': 'op.classroom',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_facility_maintenance': {
                'type': 'ir.actions.act_window',
                'name': 'Facility Maintenance',
                'res_model': 'op.facility.line',
                'view_mode': 'list,form',
                'target': 'current',
            },
            # Student Support Services Actions
            'action_open_activity_main': {
                'type': 'ir.actions.act_window',
                'name': 'Activities',
                'res_model': 'op.activity',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_library_main': {
                'type': 'ir.actions.act_window',
                'name': 'Library Media',
                'res_model': 'op.media',
                'view_mode': 'list,form',
                'target': 'current',
            },
            
            # Core Module Actions
            'action_open_students': {
                'type': 'ir.actions.act_window',
                'name': 'Students',
                'res_model': 'op.student',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_faculty': {
                'type': 'ir.actions.act_window',
                'name': 'Faculty',
                'res_model': 'op.faculty',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_courses': {
                'type': 'ir.actions.act_window',
                'name': 'Courses',
                'res_model': 'op.course',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_batches': {
                'type': 'ir.actions.act_window',
                'name': 'Batches',
                'res_model': 'op.batch',
                'view_mode': 'list,form',
                'target': 'current',
            },
            
            # Activity Module Actions
            'action_open_activity_types': {
                'type': 'ir.actions.act_window',
                'name': 'Activity Types',
                'res_model': 'op.activity.type',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_activity_logs': {
                'type': 'ir.actions.act_window',
                'name': 'Activity Logs',
                'res_model': 'op.activity.log',
                'view_mode': 'list,form',
                'target': 'current',
            },
            
            # Classroom Module Actions
            'action_open_classroom_types': {
                'type': 'ir.actions.act_window',
                'name': 'Classroom Types',
                'res_model': 'op.classroom.type',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_room_booking': {
                'type': 'ir.actions.act_window',
                'name': 'Room Booking',
                'res_model': 'op.classroom.booking',
                'view_mode': 'list,form',
                'target': 'current',
            },
            
            # Facility Module Actions
            'action_open_facility_lines': {
                'type': 'ir.actions.act_window',
                'name': 'Facility Lines',
                'res_model': 'op.facility.line',
                'view_mode': 'list,form',
                'target': 'current',
            },
            
            # Fees Module Actions
            'action_open_fees_payments': {
                'type': 'ir.actions.act_window',
                'name': 'Fee Payments',
                'res_model': 'op.student.fees.details',
                'view_mode': 'list,form',
                'domain': [('state', '=', 'paid')],
                'target': 'current',
            },
            
            # Student Support Services Actions
            'action_open_parent_main': {
                'type': 'ir.actions.act_window',
                'name': 'Student Support Services',
                'res_model': 'res.partner',
                'view_mode': 'list,form',
                'domain': [('is_parent', '=', True)],
                'target': 'current',
            },
            'action_open_parent_meetings': {
                'type': 'ir.actions.act_window',
                'name': 'Student Guidance Sessions',
                'res_model': 'op.parent.meeting',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_parent_communications': {
                'type': 'ir.actions.act_window',
                'name': 'Student Communications',
                'res_model': 'mail.message',
                'view_mode': 'list,form',
                'target': 'current',
            },
            
            # Timetable Module Actions
            'action_open_timetable_sessions': {
                'type': 'ir.actions.act_window',
                'name': 'Timetable Sessions',
                'res_model': 'op.session',
                'view_mode': 'list,form',
                'target': 'current',
            },
            'action_open_timetable_schedule': {
                'type': 'ir.actions.act_window',
                'name': 'Schedule Planning',
                'res_model': 'op.timing',
                'view_mode': 'list,form',
                'target': 'current',
            },
        }
        
        if self.action_method and self.action_method in action_mapping:
            action = action_mapping[self.action_method]
            _logger.info("WORKFLOW: Returning mapped action: %s", action)
            _logger.info("=" * 60)
            return action
        
        # Fallback action
        fallback_action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Stage Action',
                'message': f'Executing {self.name} stage - {self.button_label}',
                'type': 'info',
                'sticky': False,
            }
        }
        _logger.info("WORKFLOW: Returning fallback action: %s", fallback_action)
        _logger.info("=" * 60)
        return fallback_action

    def action_open_module(self):
        """Open the module menu specified by menu_xmlid"""
        self.ensure_one()
        if not self.menu_xmlid:
            return False
        
        try:
            menu = self.env.ref(self.menu_xmlid, raise_if_not_found=False)
            if menu and menu.action:
                return menu.action.read()[0]
        except Exception as e:
            _logger.warning("Failed to open menu %s: %s", self.menu_xmlid, str(e))
        
        return False
