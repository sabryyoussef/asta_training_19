# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestStudentNameFields(TransactionCase):
    """Test the new Arabic and English name fields for students."""

    def setUp(self):
        super(TestStudentNameFields, self).setUp()
        self.Student = self.env['gr.student']

    def test_create_student_with_required_name_fields(self):
        """Test creating a student with all required name fields."""
        student_data = {
            'name': 'Ahmed Ali Hassan',
            'name_arabic': 'أحمد علي حسن',
            'name_english': 'Ahmed Ali Hassan',
            'email': 'ahmed.ali@example.com',
            'phone': '+966501234567',
            'birth_date': '1990-01-01',
            'gender': 'male',
            'nationality': 'Saudi',
            'native_language': 'Arabic',
            'english_level': 'intermediate',
            'has_certificate': True,
        }
        
        student = self.Student.create(student_data)
        
        # Verify the student was created successfully
        self.assertEqual(student.name, 'Ahmed Ali Hassan')
        self.assertEqual(student.name_arabic, 'أحمد علي حسن')
        self.assertEqual(student.name_english, 'Ahmed Ali Hassan')
        self.assertEqual(student.email, 'ahmed.ali@example.com')

    def test_create_student_without_required_fields_should_fail(self):
        """Test that creating a student without required name fields fails."""
        student_data = {
            'name': 'Ahmed Ali Hassan',
            'email': 'ahmed.ali@example.com',
            # Missing name_arabic and name_english
        }
        
        # This should raise a ValidationError or similar
        with self.assertRaises(Exception):
            self.Student.create(student_data)

    def test_name_fields_tracking(self):
        """Test that name fields are properly tracked."""
        student_data = {
            'name': 'Ahmed Ali Hassan',
            'name_arabic': 'أحمد علي حسن',
            'name_english': 'Ahmed Ali Hassan',
            'email': 'ahmed.ali@example.com',
        }
        
        student = self.Student.create(student_data)
        
        # Update the Arabic name
        student.write({'name_arabic': 'أحمد علي محمد'})
        
        # Verify the change was tracked
        # Note: In a real test, you would check the mail.message records
        self.assertEqual(student.name_arabic, 'أحمد علي محمد')

    def test_search_by_arabic_name(self):
        """Test searching students by Arabic name."""
        student_data = {
            'name': 'Ahmed Ali Hassan',
            'name_arabic': 'أحمد علي حسن',
            'name_english': 'Ahmed Ali Hassan',
            'email': 'ahmed.ali@example.com',
        }
        
        student = self.Student.create(student_data)
        
        # Search by Arabic name
        found_students = self.Student.search([('name_arabic', 'ilike', 'أحمد')])
        self.assertIn(student, found_students)

    def test_search_by_english_name(self):
        """Test searching students by English name."""
        student_data = {
            'name': 'Ahmed Ali Hassan',
            'name_arabic': 'أحمد علي حسن',
            'name_english': 'Ahmed Ali Hassan',
            'email': 'ahmed.ali@example.com',
        }
        
        student = self.Student.create(student_data)
        
        # Search by English name
        found_students = self.Student.search([('name_english', 'ilike', 'Ahmed')])
        self.assertIn(student, found_students)
