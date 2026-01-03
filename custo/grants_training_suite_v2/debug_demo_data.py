#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script to check demo data loading issues
Run this from the Odoo shell to diagnose demo data problems
"""

import odoo
from odoo import api, SUPERUSER_ID

def check_demo_data():
    """Check demo data loading status."""
    
    # Initialize Odoo environment
    odoo.cli.server.main()
    
    with api.Environment.manage():
        env = api.Environment(odoo.registry('edafa_db'), SUPERUSER_ID, {})
        
        print("=== Demo Data Diagnostic ===")
        
        # Check if models exist
        print("\n1. Checking if models exist:")
        models_to_check = [
            'gr.student',
            'gr.training.program', 
            'gr.course.integration',
            'slide.channel'
        ]
        
        for model_name in models_to_check:
            try:
                model = env[model_name]
                count = model.search_count([])
                print(f"✓ {model_name}: {count} records")
            except Exception as e:
                print(f"✗ {model_name}: ERROR - {e}")
        
        # Check demo data specifically
        print("\n2. Checking demo data:")
        
        # Check students
        students = env['gr.student'].search([])
        print(f"Students: {len(students)} records")
        for student in students[:3]:  # Show first 3
            print(f"  - {student.name} ({student.email})")
        
        # Check training programs
        programs = env['gr.training.program'].search([])
        print(f"Training Programs: {len(programs)} records")
        for program in programs[:3]:  # Show first 3
            print(f"  - {program.name} (Status: {program.status})")
        
        # Check course integrations
        integrations = env['gr.course.integration'].search([])
        print(f"Course Integrations: {len(integrations)} records")
        for integration in integrations[:3]:  # Show first 3
            print(f"  - {integration.name} (Status: {integration.status})")
        
        # Check eLearning courses
        try:
            courses = env['slide.channel'].search([])
            print(f"eLearning Courses: {len(courses)} records")
            for course in courses[:3]:  # Show first 3
                print(f"  - {course.name}")
        except Exception as e:
            print(f"eLearning Courses: ERROR - {e}")
        
        print("\n=== End Diagnostic ===")

if __name__ == '__main__':
    check_demo_data()
