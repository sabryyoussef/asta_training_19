# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class TrainingDashboard(models.Model):
    _name = 'gr.training.dashboard'
    _description = 'Training Dashboard - Advanced Analytics and KPIs'
    _order = 'create_date desc'

    name = fields.Char(
        string='Dashboard Name',
        default='Training Analytics Dashboard',
        required=True
    )

    # Dashboard Configuration
    date_from = fields.Date(
        string='From Date',
        default=lambda self: (datetime.now() - timedelta(days=30)).date(),
        required=True
    )
    
    date_to = fields.Date(
        string='To Date',
        default=fields.Date.today,
        required=True
    )

    # KPI Metrics (Computed Fields)
    total_students = fields.Integer(
        string='Total Students',
        compute='_compute_kpi_metrics',
        store=True
    )

    enrolled_students = fields.Integer(
        string='Enrolled Students',
        compute='_compute_kpi_metrics',
        store=True
    )

    completed_students = fields.Integer(
        string='Completed Students',
        compute='_compute_kpi_metrics',
        store=True
    )

    completion_rate = fields.Float(
        string='Completion Rate (%)',
        compute='_compute_kpi_metrics',
        store=True,
        digits=(5, 2)
    )

    avg_completion_time = fields.Float(
        string='Avg Completion Time (Days)',
        compute='_compute_kpi_metrics',
        store=True,
        digits=(5, 2)
    )

    active_courses = fields.Integer(
        string='Active Courses',
        compute='_compute_kpi_metrics',
        store=True
    )

    total_enrollments = fields.Integer(
        string='Total Enrollments',
        compute='_compute_kpi_metrics',
        store=True
    )

    # Progress Analytics
    progress_distribution = fields.Text(
        string='Progress Distribution',
        compute='_compute_progress_analytics',
        store=True
    )

    monthly_enrollments = fields.Text(
        string='Monthly Enrollments',
        compute='_compute_progress_analytics',
        store=True
    )

    completion_trends = fields.Text(
        string='Completion Trends',
        compute='_compute_progress_analytics',
        store=True
    )

    # Student Performance Analytics
    top_performers = fields.Text(
        string='Top Performers',
        compute='_compute_student_analytics',
        store=True
    )

    struggling_students = fields.Text(
        string='Struggling Students',
        compute='_compute_student_analytics',
        store=True
    )

    engagement_metrics = fields.Text(
        string='Engagement Metrics',
        compute='_compute_student_analytics',
        store=True
    )

    # Course Analytics
    course_performance = fields.Text(
        string='Course Performance',
        compute='_compute_course_analytics',
        store=True
    )

    popular_courses = fields.Text(
        string='Popular Courses',
        compute='_compute_course_analytics',
        store=True
    )

    # Integration Status
    integration_status_summary = fields.Text(
        string='Integration Status Summary',
        compute='_compute_integration_analytics',
        store=True
    )

    elearning_adoption_rate = fields.Float(
        string='eLearning Adoption Rate (%)',
        compute='_compute_integration_analytics',
        store=True,
        digits=(5, 2)
    )

    # Dashboard Widgets Configuration
    widget_config = fields.Text(
        string='Widget Configuration',
        default='{}',
        help='JSON configuration for dashboard widgets'
    )

    # Real-time Updates
    last_update = fields.Datetime(
        string='Last Update',
        default=fields.Datetime.now
    )

    auto_refresh = fields.Boolean(
        string='Auto Refresh',
        default=True,
        help='Automatically refresh dashboard data'
    )

    refresh_interval = fields.Integer(
        string='Refresh Interval (minutes)',
        default=15,
        help='Dashboard refresh interval in minutes'
    )

    @api.depends('date_from', 'date_to')
    def _compute_kpi_metrics(self):
        """Compute key performance indicators."""
        for dashboard in self:
            domain = [
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ]

            # Total students in date range
            dashboard.total_students = self.env['gr.student'].search_count(domain)

            # Enrolled students
            enrolled_domain = domain + [('integration_status', 'in', ['enrolled', 'in_progress', 'completed', 'certified'])]
            dashboard.enrolled_students = self.env['gr.student'].search_count(enrolled_domain)

            # Completed students
            completed_domain = domain + [('integration_status', 'in', ['completed', 'certified'])]
            dashboard.completed_students = self.env['gr.student'].search_count(completed_domain)

            # Completion rate
            if dashboard.total_students > 0:
                dashboard.completion_rate = (dashboard.completed_students / dashboard.total_students) * 100
            else:
                dashboard.completion_rate = 0.0

            # Average completion time
            completed_students = self.env['gr.student'].search(completed_domain)
            if completed_students:
                total_days = 0
                count = 0
                for student in completed_students:
                    if student.intake_date and student.create_date:
                        days = (student.create_date.date() - student.intake_date).days
                        total_days += days
                        count += 1
                
                if count > 0:
                    dashboard.avg_completion_time = total_days / count
                else:
                    dashboard.avg_completion_time = 0.0
            else:
                dashboard.avg_completion_time = 0.0

            # Active courses
            dashboard.active_courses = self.env['gr.course.integration'].search_count([('status', '=', 'active')])

            # Total enrollments
            dashboard.total_enrollments = self.env['gr.progress.tracker'].search_count([
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ])

    @api.depends('date_from', 'date_to')
    def _compute_progress_analytics(self):
        """Compute progress analytics and trends."""
        for dashboard in self:
            # Progress distribution
            progress_data = {}
            trackers = self.env['gr.progress.tracker'].search([
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ])

            for tracker in trackers:
                progress_range = self._get_progress_range(tracker.overall_progress)
                progress_data[progress_range] = progress_data.get(progress_range, 0) + 1

            dashboard.progress_distribution = str(progress_data)

            # Monthly enrollments
            monthly_data = {}
            enrollments = self.env['gr.progress.tracker'].search([
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ])

            for enrollment in enrollments:
                month_key = enrollment.create_date.strftime('%Y-%m')
                monthly_data[month_key] = monthly_data.get(month_key, 0) + 1

            dashboard.monthly_enrollments = str(monthly_data)

            # Completion trends
            completion_data = {}
            completions = self.env['gr.student'].search([
                ('integration_status', 'in', ['completed', 'certified']),
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ])

            for completion in completions:
                month_key = completion.create_date.strftime('%Y-%m')
                completion_data[month_key] = completion_data.get(month_key, 0) + 1

            dashboard.completion_trends = str(completion_data)

    @api.depends('date_from', 'date_to')
    def _compute_student_analytics(self):
        """Compute student performance analytics."""
        for dashboard in self:
            # Top performers
            top_performers = self.env['gr.student'].search([
                ('integration_status', 'in', ['in_progress', 'completed', 'certified']),
                ('elearning_progress', '>', 80)
            ], order='elearning_progress desc', limit=10)

            top_data = []
            for student in top_performers:
                top_data.append({
                    'name': student.name,
                    'progress': student.elearning_progress,
                    'courses_completed': student.completed_courses
                })

            dashboard.top_performers = str(top_data)

            # Struggling students
            struggling_students = self.env['gr.student'].search([
                ('integration_status', 'in', ['enrolled', 'in_progress']),
                ('elearning_progress', '<', 25)
            ], order='elearning_progress asc', limit=10)

            struggling_data = []
            for student in struggling_students:
                struggling_data.append({
                    'name': student.name,
                    'progress': student.elearning_progress,
                    'last_activity': student.create_date.strftime('%Y-%m-%d')
                })

            dashboard.struggling_students = str(struggling_data)

            # Engagement metrics
            total_active = self.env['gr.student'].search_count([
                ('integration_status', 'in', ['enrolled', 'in_progress'])
            ])

            highly_engaged = self.env['gr.student'].search_count([
                ('integration_status', 'in', ['enrolled', 'in_progress']),
                ('elearning_progress', '>', 50)
            ])

            engagement_rate = (highly_engaged / total_active * 100) if total_active > 0 else 0

            dashboard.engagement_metrics = str({
                'total_active': total_active,
                'highly_engaged': highly_engaged,
                'engagement_rate': engagement_rate
            })

    @api.depends('date_from', 'date_to')
    def _compute_course_analytics(self):
        """Compute course performance analytics."""
        for dashboard in self:
            # Course performance
            courses = self.env['gr.course.integration'].search([('status', '=', 'active')])
            course_data = []

            for course in courses:
                trackers = self.env['gr.progress.tracker'].search([
                    ('course_integration_id', '=', course.id),
                    ('create_date', '>=', dashboard.date_from),
                    ('create_date', '<=', dashboard.date_to)
                ])

                if trackers:
                    avg_progress = sum(tracker.overall_progress for tracker in trackers) / len(trackers)
                    completion_count = len(trackers.filtered(lambda t: t.status == 'completed'))
                    completion_rate = (completion_count / len(trackers)) * 100

                    course_data.append({
                        'name': course.name,
                        'enrollments': len(trackers),
                        'avg_progress': avg_progress,
                        'completion_rate': completion_rate
                    })

            dashboard.course_performance = str(course_data)

            # Popular courses
            popular_courses = self.env['gr.course.integration'].search([('status', '=', 'active')])
            popular_data = []

            for course in popular_courses:
                enrollment_count = self.env['gr.progress.tracker'].search_count([
                    ('course_integration_id', '=', course.id),
                    ('create_date', '>=', dashboard.date_from),
                    ('create_date', '<=', dashboard.date_to)
                ])

                popular_data.append({
                    'name': course.name,
                    'enrollments': enrollment_count
                })

            # Sort by enrollments and take top 5
            popular_data.sort(key=lambda x: x['enrollments'], reverse=True)
            dashboard.popular_courses = str(popular_data[:5])

    @api.depends('date_from', 'date_to')
    def _compute_integration_analytics(self):
        """Compute eLearning integration analytics."""
        for dashboard in self:
            # Integration status summary
            status_counts = {}
            students = self.env['gr.student'].search([
                ('create_date', '>=', dashboard.date_from),
                ('create_date', '<=', dashboard.date_to)
            ])

            for student in students:
                status = student.integration_status
                status_counts[status] = status_counts.get(status, 0) + 1

            dashboard.integration_status_summary = str(status_counts)

            # eLearning adoption rate
            total_students = len(students)
            elearning_students = len(students.filtered(lambda s: s.integration_status != 'not_integrated'))
            
            if total_students > 0:
                dashboard.elearning_adoption_rate = (elearning_students / total_students) * 100
            else:
                dashboard.elearning_adoption_rate = 0.0

    def _get_progress_range(self, progress):
        """Get progress range category."""
        if progress < 25:
            return '0-25%'
        elif progress < 50:
            return '25-50%'
        elif progress < 75:
            return '50-75%'
        else:
            return '75-100%'

    def action_refresh_dashboard(self):
        """Manually refresh dashboard data."""
        self._compute_kpi_metrics()
        self._compute_progress_analytics()
        self._compute_student_analytics()
        self._compute_course_analytics()
        self._compute_integration_analytics()
        
        self.last_update = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_export_analytics(self):
        """Export analytics data."""
        # This would generate and download analytics reports
        # Implementation depends on specific export requirements
        raise UserError(_('Export functionality will be implemented in Phase 4'))

    def action_schedule_report(self):
        """Schedule automated reports."""
        # This would create scheduled reports
        # Implementation depends on specific scheduling requirements
        raise UserError(_('Report scheduling will be implemented in Phase 4'))

    @api.model
    def get_dashboard_data(self, dashboard_id=None):
        """Get dashboard data for API/JavaScript consumption."""
        if dashboard_id:
            dashboard = self.browse(dashboard_id)
        else:
            dashboard = self.search([], limit=1)
            if not dashboard:
                dashboard = self.create({})

        return {
            'kpi_metrics': {
                'total_students': dashboard.total_students,
                'enrolled_students': dashboard.enrolled_students,
                'completed_students': dashboard.completed_students,
                'completion_rate': dashboard.completion_rate,
                'avg_completion_time': dashboard.avg_completion_time,
                'active_courses': dashboard.active_courses,
                'total_enrollments': dashboard.total_enrollments,
            },
            'progress_analytics': {
                'progress_distribution': eval(dashboard.progress_distribution or '{}'),
                'monthly_enrollments': eval(dashboard.monthly_enrollments or '{}'),
                'completion_trends': eval(dashboard.completion_trends or '{}'),
            },
            'student_analytics': {
                'top_performers': eval(dashboard.top_performers or '[]'),
                'struggling_students': eval(dashboard.struggling_students or '[]'),
                'engagement_metrics': eval(dashboard.engagement_metrics or '{}'),
            },
            'course_analytics': {
                'course_performance': eval(dashboard.course_performance or '[]'),
                'popular_courses': eval(dashboard.popular_courses or '[]'),
            },
            'integration_analytics': {
                'integration_status_summary': eval(dashboard.integration_status_summary or '{}'),
                'elearning_adoption_rate': dashboard.elearning_adoption_rate,
            },
            'last_update': dashboard.last_update,
        }

    @api.model
    def refresh_all_dashboards(self):
        """Refresh all active dashboards."""
        _logger.info('Refreshing all active dashboards...')
        
        active_dashboards = self.search([('auto_refresh', '=', True)])
        
        for dashboard in active_dashboards:
            try:
                dashboard.action_refresh_dashboard()
            except Exception as e:
                _logger.error('Failed to refresh dashboard %s: %s', dashboard.name, str(e))
                continue
        
        _logger.info('Dashboard refresh completed for %d dashboards', len(active_dashboards))
        return len(active_dashboards)
