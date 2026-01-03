# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from unittest.mock import patch


class TestEnrollmentFixes(TransactionCase):
    """Test the enrollment fixes implemented in Phase 1.2."""

    def setUp(self):
        super(TestEnrollmentFixes, self).setUp()
        self.Student = self.env['gr.student']
        self.CourseIntegration = self.env['gr.course.integration']
        self.SlideChannel = self.env['slide.channel']
        self.TrainingProgram = self.env['gr.training.program']
        
        # Create test data
        self._create_test_data()

    def _create_test_data(self):
        """Create test data for enrollment testing."""
        
        # Create eLearning course
        self.elearning_course = self.SlideChannel.create({
            'name': 'Test English Course',
            'description': 'Test course for enrollment testing',
            'is_published': True,
            'enroll': 'public',
            'visibility': 'public',
            'channel_type': 'training',
            'user_id': self.env.user.id,
        })
        
        # Create training program
        self.training_program = self.TrainingProgram.create({
            'name': 'Test Training Program',
            'description': 'Test program for enrollment testing',
            'duration_days': 30,
            'max_students': 50,
            'status': 'active',
            'manager_id': self.env.user.id,
        })
        
        # Create course integration
        self.course_integration = self.CourseIntegration.create({
            'name': 'Test Course Integration',
            'elearning_course_id': self.elearning_course.id,
            'training_program_id': self.training_program.id,
            'auto_enroll_eligible': True,
            'completion_threshold': 80.0,
            'status': 'active',
        })
        
        # Create eligible student
        self.student = self.Student.create({
            'name': 'Test Student',
            'name_arabic': 'طالب تجريبي',
            'name_english': 'Test Student',
            'email': 'test.student@example.com',
            'phone': '+966501234567',
            'birth_date': '1990-01-01',
            'gender': 'male',
            'nationality': 'Saudi',
            'native_language': 'Arabic',
            'english_level': 'intermediate',
            'has_certificate': True,
        })

    def test_assign_agent_fixed_domain_query(self):
        """Test that the Assign Agent functionality works with the fixed domain query."""
        
        # Create an agent user with the correct group
        agent_group = self.env.ref('grants_training_suite_v2.group_agent')
        agent_user = self.env['res.users'].create({
            'name': 'Test Agent',
            'login': 'test.agent',
            'email': 'test.agent@example.com',
            'groups_id': [(6, 0, [agent_group.id])],
        })
        
        # Ensure student is eligible
        self.assertEqual(self.student.state, 'eligible')
        
        # Test assign agent action
        result = self.student.action_assign_agent()
        
        # Verify agent was assigned
        self.assertEqual(self.student.assigned_agent_id, agent_user)
        self.assertEqual(self.student.state, 'assigned')
        self.assertIsNotNone(self.student.assignment_date)

    def test_auto_enroll_with_course_integrations(self):
        """Test auto-enroll functionality with available course integrations."""
        
        # Ensure student is eligible
        self.assertEqual(self.student.state, 'eligible')
        
        # Test auto-enroll action
        result = self.student.action_auto_enroll_eligible_courses()
        
        # Verify successful enrollment
        self.assertEqual(result['params']['type'], 'success')
        self.assertIn('Auto-enrolled in', result['params']['message'])
        
        # Verify student's integration status was updated
        self.assertEqual(self.student.integration_status, 'enrolled')

    def test_auto_enroll_no_courses_available(self):
        """Test auto-enroll when no courses are available."""
        
        # Deactivate the course integration
        self.course_integration.status = 'inactive'
        
        # Ensure student is eligible
        self.assertEqual(self.student.state, 'eligible')
        
        # Test auto-enroll action
        result = self.student.action_auto_enroll_eligible_courses()
        
        # Verify warning message
        self.assertEqual(result['params']['type'], 'warning')
        self.assertIn('No eligible courses found', result['params']['message'])

    def test_auto_enroll_with_preferred_course(self):
        """Test auto-enroll with student's preferred course."""
        
        # Set preferred course for student
        self.student.preferred_course_integration_id = self.course_integration.id
        
        # Test auto-enroll action
        result = self.student.action_auto_enroll_eligible_courses()
        
        # Verify successful enrollment with preferred course
        self.assertEqual(result['params']['type'], 'success')

    def test_auto_enroll_preferred_course_not_auto_enrollable(self):
        """Test auto-enroll when preferred course is not auto-enrollable."""
        
        # Set preferred course that is not auto-enrollable
        self.course_integration.auto_enroll_eligible = False
        self.student.preferred_course_integration_id = self.course_integration.id
        
        # Test auto-enroll action - should raise UserError
        with self.assertRaises(UserError) as context:
            self.student.action_auto_enroll_eligible_courses()
        
        # Verify error message mentions preferred course
        self.assertIn('preferred course', str(context.exception))

    def test_manual_enroll_with_active_courses(self):
        """Test manual enroll when active courses are available."""
        
        # Test manual enroll action
        result = self.student.action_manual_enroll_course()
        
        # Verify window opens successfully
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'gr.course.integration')
        self.assertIn('active', result['domain'])

    def test_manual_enroll_no_courses_available(self):
        """Test manual enroll when no courses are available."""
        
        # Deactivate all course integrations
        self.CourseIntegration.search([]).write({'status': 'inactive'})
        
        # Test manual enroll action
        result = self.student.action_manual_enroll_course()
        
        # Verify warning message
        self.assertEqual(result['params']['type'], 'warning')
        self.assertIn('No active course integrations', result['params']['message'])

    def test_course_selection_fields(self):
        """Test the new course selection fields."""
        
        # Test enrollment type field
        self.student.enrollment_type = 'manual'
        self.assertEqual(self.student.enrollment_type, 'manual')
        
        # Test preferred course field
        self.student.preferred_course_integration_id = self.course_integration.id
        self.assertEqual(self.student.preferred_course_integration_id, self.course_integration)

    def test_enrollment_type_filtering(self):
        """Test filtering students by enrollment type."""
        
        # Create students with different enrollment types
        student_auto = self.Student.create({
            'name': 'Auto Student',
            'name_arabic': 'طالب تلقائي',
            'name_english': 'Auto Student',
            'email': 'auto@example.com',
            'enrollment_type': 'auto',
        })
        
        student_manual = self.Student.create({
            'name': 'Manual Student',
            'name_arabic': 'طالب يدوي',
            'name_english': 'Manual Student',
            'email': 'manual@example.com',
            'enrollment_type': 'manual',
        })
        
        # Test filtering
        auto_students = self.Student.search([('enrollment_type', '=', 'auto')])
        manual_students = self.Student.search([('enrollment_type', '=', 'manual')])
        
        self.assertIn(student_auto, auto_students)
        self.assertIn(student_manual, manual_students)
        self.assertNotIn(student_auto, manual_students)
        self.assertNotIn(student_manual, auto_students)
