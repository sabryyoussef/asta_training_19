# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class ProgressNotification(models.Model):
    _name = 'gr.progress.notification'
    _description = 'Progress Milestone Notifications'
    _order = 'create_date desc'

    name = fields.Char(
        string='Notification Title',
        required=True
    )

    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        ondelete='cascade'
    )

    progress_tracker_id = fields.Many2one(
        'gr.progress.tracker',
        string='Progress Tracker',
        ondelete='cascade'
    )

    notification_type = fields.Selection([
        ('milestone', 'Progress Milestone'),
        ('completion', 'Course Completion'),
        ('stalled', 'Progress Stalled'),
        ('achievement', 'Achievement Unlocked'),
        ('reminder', 'Reminder'),
        ('alert', 'Alert')
    ], string='Notification Type', required=True, default='milestone')

    milestone_type = fields.Selection([
        ('25_percent', '25% Progress'),
        ('50_percent', '50% Progress'),
        ('75_percent', '75% Progress'),
        ('90_percent', '90% Progress'),
        ('100_percent', '100% Completion'),
        ('first_login', 'First Login'),
        ('week_1_active', 'Week 1 Active'),
        ('week_2_active', 'Week 2 Active'),
        ('month_1_active', 'Month 1 Active'),
        ('custom', 'Custom Milestone')
    ], string='Milestone Type', default='25_percent')

    message = fields.Text(
        string='Message',
        required=True
    )

    progress_value = fields.Float(
        string='Progress Value (%)',
        help='Progress value when notification was triggered'
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('read', 'Read'),
        ('archived', 'Archived')
    ], string='Status', default='draft')

    sent_date = fields.Datetime(
        string='Sent Date'
    )

    read_date = fields.Datetime(
        string='Read Date'
    )

    # Notification Channels
    email_sent = fields.Boolean(
        string='Email Sent',
        default=False
    )

    sms_sent = fields.Boolean(
        string='SMS Sent',
        default=False
    )

    in_app_notification = fields.Boolean(
        string='In-App Notification',
        default=True
    )

    # Recipients
    recipient_user_id = fields.Many2one(
        'res.users',
        string='Recipient User',
        help='User who will receive the notification'
    )

    recipient_email = fields.Char(
        string='Recipient Email'
    )

    recipient_phone = fields.Char(
        string='Recipient Phone'
    )

    # Priority and Urgency
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='normal')

    # Auto-generated fields
    auto_generated = fields.Boolean(
        string='Auto Generated',
        default=True,
        help='Whether this notification was automatically generated'
    )

    trigger_condition = fields.Text(
        string='Trigger Condition',
        help='Condition that triggered this notification'
    )

    def action_send_notification(self):
        """Send the notification through configured channels."""
        for notification in self:
            try:
                # Send in-app notification
                if notification.in_app_notification:
                    notification._send_in_app_notification()
                
                # Send email notification
                if notification.email_sent or notification.recipient_email:
                    notification._send_email_notification()
                
                # Send SMS notification
                if notification.sms_sent or notification.recipient_phone:
                    notification._send_sms_notification()
                
                notification.status = 'sent'
                notification.sent_date = fields.Datetime.now()
                
                _logger.info('Notification sent successfully: %s', notification.name)
                
            except Exception as e:
                _logger.error('Failed to send notification %s: %s', notification.name, str(e))
                raise UserError(_('Failed to send notification: %s') % str(e))

    def _send_in_app_notification(self):
        """Send in-app notification."""
        # Create mail.activity for in-app notification
        self.env['mail.activity'].create({
            'activity_type_id': self._get_activity_type_id(),
            'res_id': self.id,
            'res_model': 'gr.progress.notification',
            'user_id': self.recipient_user_id.id or self.student_id.assigned_agent_id.user_id.id or 1,
            'summary': self.name,
            'note': self.message,
            'date_deadline': fields.Date.today(),
        })

    def _send_email_notification(self):
        """Send email notification."""
        if not self.recipient_email:
            return
        
        # Create mail.message for email notification
        mail_template = self.env.ref('grants_training_suite_v2.email_template_progress_notification', False)
        
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        else:
            # Fallback: create simple email
            self.env['mail.mail'].create({
                'subject': self.name,
                'body_html': f'<p>{self.message}</p>',
                'email_to': self.recipient_email,
                'auto_delete': True,
            }).send()

    def _send_sms_notification(self):
        """Send SMS notification."""
        # SMS functionality would require additional SMS gateway integration
        # For now, just log the SMS notification
        _logger.info('SMS notification would be sent to: %s - %s', self.recipient_phone, self.message)

    def _get_activity_type_id(self):
        """Get appropriate activity type based on notification type."""
        activity_type_mapping = {
            'milestone': 1,  # To Do
            'completion': 2,  # Call
            'stalled': 3,    # Email
            'achievement': 1,  # To Do
            'reminder': 3,   # Email
            'alert': 3,      # Email
        }
        return activity_type_mapping.get(self.notification_type, 1)

    def action_mark_as_read(self):
        """Mark notification as read."""
        self.status = 'read'
        self.read_date = fields.Datetime.now()

    def action_archive_notification(self):
        """Archive the notification."""
        self.status = 'archived'

    @api.model
    def create_milestone_notifications(self):
        """Automatically create milestone notifications for students."""
        _logger.info('Starting automatic milestone notification creation...')
        
        # Get students with recent progress updates
        recent_trackers = self.env['gr.progress.tracker'].search([
            ('status', '=', 'in_progress'),
            ('write_date', '>=', (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'))
        ])
        
        created_count = 0
        
        for tracker in recent_trackers:
            # Check for milestone achievements
            milestone = self._check_milestone_achievement(tracker)
            if milestone:
                notification = self._create_milestone_notification(tracker, milestone)
                if notification:
                    created_count += 1
        
        _logger.info('Created %d milestone notifications', created_count)
        return created_count

    def _check_milestone_achievement(self, tracker):
        """Check if tracker has achieved any new milestones."""
        progress = tracker.overall_progress
        
        # Define milestone thresholds
        milestones = [
            {'threshold': 25, 'type': '25_percent', 'message': 'Congratulations! You\'ve reached 25% completion.'},
            {'threshold': 50, 'type': '50_percent', 'message': 'Great progress! You\'re halfway through the course.'},
            {'threshold': 75, 'type': '75_percent', 'message': 'Excellent work! You\'ve completed 75% of the course.'},
            {'threshold': 90, 'type': '90_percent', 'message': 'Almost there! You\'re at 90% completion.'},
            {'threshold': 100, 'type': '100_percent', 'message': 'Congratulations! You\'ve completed the course!'},
        ]
        
        # Check if any milestone was just achieved
        for milestone in milestones:
            if progress >= milestone['threshold']:
                # Check if we already sent this milestone notification
                existing_notification = self.search([
                    ('progress_tracker_id', '=', tracker.id),
                    ('milestone_type', '=', milestone['type']),
                    ('status', 'in', ['sent', 'read'])
                ])
                
                if not existing_notification:
                    return milestone
        
        return None

    def _create_milestone_notification(self, tracker, milestone):
        """Create a milestone notification for the tracker."""
        try:
            notification = self.create({
                'name': f'Progress Milestone - {tracker.student_id.name}',
                'student_id': tracker.student_id.id,
                'progress_tracker_id': tracker.id,
                'notification_type': 'milestone',
                'milestone_type': milestone['type'],
                'message': milestone['message'],
                'progress_value': tracker.overall_progress,
                'recipient_user_id': tracker.student_id.assigned_agent_id.user_id.id if tracker.student_id.assigned_agent_id else None,
                'recipient_email': tracker.student_id.email,
                'priority': 'normal',
                'auto_generated': True,
                'trigger_condition': f'Progress reached {milestone["threshold"]}%',
                'status': 'draft'
            })
            
            # Auto-send the notification
            notification.action_send_notification()
            
            return notification
            
        except Exception as e:
            _logger.error('Failed to create milestone notification: %s', str(e))
            return None

    @api.model
    def create_stalled_progress_alerts(self):
        """Create alerts for students with stalled progress."""
        _logger.info('Checking for stalled progress...')
        
        # Find students with no progress in the last 7 days
        stalled_threshold = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        
        stalled_trackers = self.env['gr.progress.tracker'].search([
            ('status', '=', 'in_progress'),
            ('write_date', '<', stalled_threshold),
            ('overall_progress', '>', 0),  # Has started but stalled
            ('overall_progress', '<', 100)  # Not completed
        ])
        
        created_count = 0
        
        for tracker in stalled_trackers:
            # Check if we already sent a stalled notification recently
            recent_stalled_notification = self.search([
                ('progress_tracker_id', '=', tracker.id),
                ('notification_type', '=', 'stalled'),
                ('create_date', '>=', (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'))
            ])
            
            if not recent_stalled_notification:
                notification = self.create({
                    'name': f'Progress Stalled - {tracker.student_id.name}',
                    'student_id': tracker.student_id.id,
                    'progress_tracker_id': tracker.id,
                    'notification_type': 'stalled',
                    'milestone_type': 'custom',
                    'message': f'Student {tracker.student_id.name} has not made progress in 7 days. Current progress: {tracker.overall_progress}%',
                    'progress_value': tracker.overall_progress,
                    'recipient_user_id': tracker.student_id.assigned_agent_id.user_id.id if tracker.student_id.assigned_agent_id else None,
                    'priority': 'high',
                    'auto_generated': True,
                    'trigger_condition': 'No progress for 7 days',
                    'status': 'draft'
                })
                
                # Auto-send the notification
                notification.action_send_notification()
                created_count += 1
        
        _logger.info('Created %d stalled progress alerts', created_count)
        return created_count

    @api.model
    def create_completion_notifications(self):
        """Create notifications for course completions."""
        _logger.info('Checking for course completions...')
        
        # Find recently completed trackers
        recent_completions = self.env['gr.progress.tracker'].search([
            ('status', '=', 'completed'),
            ('write_date', '>=', (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S'))
        ])
        
        created_count = 0
        
        for tracker in recent_completions:
            # Check if we already sent a completion notification
            existing_notification = self.search([
                ('progress_tracker_id', '=', tracker.id),
                ('notification_type', '=', 'completion'),
                ('status', 'in', ['sent', 'read']
                )
            ])
            
            if not existing_notification:
                notification = self.create({
                    'name': f'Course Completed - {tracker.student_id.name}',
                    'student_id': tracker.student_id.id,
                    'progress_tracker_id': tracker.id,
                    'notification_type': 'completion',
                    'milestone_type': '100_percent',
                    'message': f'Congratulations! {tracker.student_id.name} has successfully completed the course "{tracker.course_integration_id.name}".',
                    'progress_value': 100.0,
                    'recipient_user_id': tracker.student_id.assigned_agent_id.user_id.id if tracker.student_id.assigned_agent_id else None,
                    'recipient_email': tracker.student_id.email,
                    'priority': 'normal',
                    'auto_generated': True,
                    'trigger_condition': 'Course completion detected',
                    'status': 'draft'
                })
                
                # Auto-send the notification
                notification.action_send_notification()
                created_count += 1
        
        _logger.info('Created %d completion notifications', created_count)
        return created_count

    @api.model
    def cleanup_old_notifications(self):
        """Clean up old notifications to keep the system clean."""
        _logger.info('Cleaning up old notifications...')
        
        # Archive notifications older than 30 days
        old_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        old_notifications = self.search([
            ('create_date', '<', old_date),
            ('status', 'in', ['sent', 'read'])
        ])
        
        archived_count = 0
        for notification in old_notifications:
            notification.action_archive_notification()
            archived_count += 1
        
        _logger.info('Archived %d old notifications', archived_count)
        return archived_count
