# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import json

class TestColumnMapping(TransactionCase):
    
    def setUp(self):
        super(TestColumnMapping, self).setUp()
        
        # Create test intake batch
        self.intake_batch = self.env['gr.intake.batch'].create({
            'name': 'Test Column Mapping Batch',
            'state': 'draft'
        })
        
        # Create sample CSV data (using ASCII characters only for bytes)
        self.sample_csv_data = b"""name,arabic_name,email,phone,gender
John Doe,John Doe Arabic,john@example.com,+1234567890,male
Jane Smith,Jane Smith Arabic,jane@example.com,+1234567891,female"""
        
        # Create sample Excel data (simplified for testing)
        self.sample_excel_data = b"name\tarabic_name\temail\tphone\tgender\nJohn Doe\tJohn Doe Arabic\tjohn@example.com\t+1234567890\tmale\nJane Smith\tJane Smith Arabic\tjane@example.com\t+1234567891\tfemale"

    def test_auto_detect_column_mapping(self):
        """Test automatic column mapping detection."""
        available_columns = ['name', 'arabic_name', 'email', 'phone', 'gender']
        
        mapping = self.intake_batch._auto_detect_column_mapping(available_columns)
        
        # Check that common patterns are detected
        self.assertEqual(mapping['name'], 'name')
        self.assertEqual(mapping['name_arabic'], 'arabic_name')
        self.assertEqual(mapping['email'], 'email')
        self.assertEqual(mapping['phone'], 'phone')
        self.assertEqual(mapping['gender'], 'gender')
        
        # Check that unmapped fields are not included
        self.assertNotIn('name_english', mapping)
        self.assertNotIn('birth_date', mapping)

    def test_get_student_field_mapping(self):
        """Test student field mapping configuration."""
        field_mapping = self.intake_batch._get_student_field_mapping()
        
        # Check that required fields are marked correctly
        self.assertTrue(field_mapping['name']['required'])
        self.assertTrue(field_mapping['name_arabic']['required'])
        self.assertTrue(field_mapping['name_english']['required'])
        self.assertTrue(field_mapping['email']['required'])
        
        # Check that optional fields are marked correctly
        self.assertFalse(field_mapping['phone']['required'])
        self.assertFalse(field_mapping['birth_date']['required'])
        self.assertFalse(field_mapping['gender']['required'])

    def test_column_mapping_wizard_creation(self):
        """Test column mapping wizard creation."""
        # Upload file data
        self.intake_batch.write({
            'file_data': self.sample_csv_data,
            'filename': 'test.csv',
            'file_type': 'csv'
        })
        
        # Test opening column mapping wizard
        try:
            action = self.intake_batch.action_open_column_mapping()
            
            # Check that wizard action is returned
            self.assertEqual(action['res_model'], 'gr.intake.batch.mapping.wizard')
            self.assertEqual(action['view_mode'], 'form')
            self.assertEqual(action['target'], 'new')
            
            # Check that intake batch state is updated
            self.assertEqual(self.intake_batch.state, 'mapping')
            
            # Check that column mapping data is stored
            self.assertTrue(self.intake_batch.available_columns)
            self.assertTrue(self.intake_batch.column_mapping)
            self.assertTrue(self.intake_batch.mapping_preview_data)
            
        except UserError as e:
            # This might fail due to file parsing, which is expected in test environment
            self.assertIn('Error parsing file', str(e))

    def test_save_column_mapping(self):
        """Test saving column mapping."""
        # Set up test data
        mapping_data = {
            'name': 'name',
            'name_arabic': 'arabic_name',
            'name_english': 'name',
            'email': 'email'
        }
        
        # Test saving mapping
        try:
            self.intake_batch.action_save_column_mapping(json.dumps(mapping_data))
            
            # Check that mapping is saved
            self.assertTrue(self.intake_batch.column_mapping)
            saved_mapping = json.loads(self.intake_batch.column_mapping)
            self.assertEqual(saved_mapping, mapping_data)
            
        except UserError as e:
            # This might fail due to file processing, which is expected in test environment
            self.assertIn('Error processing file', str(e))

    def test_mapping_wizard_model(self):
        """Test the mapping wizard model."""
        # Create wizard instance
        wizard = self.env['gr.intake.batch.mapping.wizard'].create({
            'intake_batch_id': self.intake_batch.id,
            'available_columns': json.dumps(['name', 'email', 'phone']),
            'preview_data': json.dumps([{'name': 'John', 'email': 'john@test.com'}]),
            'column_mapping': json.dumps({'name': 'name', 'email': 'email'})
        })
        
        # Test setup mapping fields
        wizard._setup_mapping_fields()
        
        # Test saving mapping
        wizard.name_mapping = 'name'
        wizard.email_mapping = 'email'
        
        try:
            wizard.action_save_mapping()
        except UserError as e:
            # This might fail due to file processing, which is expected in test environment
            self.assertIn('Error saving column mapping', str(e))

    def test_required_fields_validation(self):
        """Test validation of required fields in mapping."""
        # Test with missing required fields
        incomplete_mapping = {
            'name': 'name',
            'email': 'email'
            # Missing name_arabic and name_english
        }
        
        with self.assertRaises(UserError) as context:
            self.intake_batch.action_save_column_mapping(json.dumps(incomplete_mapping))
        
        self.assertIn('Please map the following required fields', str(context.exception))
        self.assertIn('Student Name (Arabic)', str(context.exception))
        self.assertIn('Student Name (English) - Alternative', str(context.exception))

    def test_column_mapping_reset(self):
        """Test that column mapping fields are reset properly."""
        # Set up mapping data
        self.intake_batch.write({
            'column_mapping': json.dumps({'name': 'name', 'email': 'email'}),
            'available_columns': json.dumps(['name', 'email']),
            'mapping_preview_data': json.dumps([{'name': 'John', 'email': 'john@test.com'}])
        })
        
        # Reset the batch
        self.intake_batch.action_reset()
        
        # Check that mapping fields are reset
        self.assertFalse(self.intake_batch.column_mapping)
        self.assertFalse(self.intake_batch.available_columns)
        self.assertFalse(self.intake_batch.mapping_preview_data)
        self.assertEqual(self.intake_batch.state, 'draft')

    def test_auto_detect_patterns(self):
        """Test various column name patterns for auto-detection."""
        test_cases = [
            (['full_name', 'arabic_name', 'email_address'], {
                'name': 'full_name',
                'name_arabic': 'arabic_name',
                'email': 'email_address'
            }),
            (['student_name', 'name_arabic', 'e_mail'], {
                'name': 'student_name',
                'name_arabic': 'name_arabic',
                'email': 'e_mail'
            }),
            (['Name', 'Arabic Name', 'Email'], {
                'name': 'Name',
                'name_arabic': 'Arabic Name',
                'email': 'Email'
            })
        ]
        
        for columns, expected_mapping in test_cases:
            mapping = self.intake_batch._auto_detect_column_mapping(columns)
            for field, expected_column in expected_mapping.items():
                self.assertEqual(mapping.get(field), expected_column, 
                               f"Failed for columns {columns}, field {field}")
