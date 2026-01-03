# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class AlumniPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        # Get current alumni
        alumni = request.env['op.alumni'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if alumni:
            if 'alumni_event_count' in counters:
                values['alumni_event_count'] = request.env['op.alumni.event.registration'].search_count([
                    ('alumni_id', '=', alumni.id)
                ])
            if 'alumni_job_count' in counters:
                values['alumni_job_count'] = request.env['op.alumni.job'].search_count([
                    ('state', '=', 'published'),
                    ('is_published', '=', True)
                ])
        
        return values

    @http.route(['/my/alumni'], type='http', auth='user', website=True)
    def portal_my_alumni_profile(self, **kw):
        """Alumni profile page"""
        alumni = request.env['op.alumni'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not alumni:
            return request.render('motakamel_alumni.alumni_not_found')
        
        values = {
            'alumni': alumni,
            'page_name': 'alumni_profile',
        }
        return request.render('motakamel_alumni.portal_my_alumni_profile', values)

    @http.route(['/my/alumni/events', '/my/alumni/events/page/<int:page>'], 
                type='http', auth='user', website=True)
    def portal_my_alumni_events(self, page=1, sortby=None, **kw):
        """Alumni events page"""
        alumni = request.env['op.alumni'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not alumni:
            return request.render('motakamel_alumni.alumni_not_found')
        
        # Prepare domain
        domain = [('alumni_id', '=', alumni.id)]
        
        # Count
        event_count = request.env['op.alumni.event.registration'].search_count(domain)
        
        # Pager
        pager = portal_pager(
            url='/my/alumni/events',
            total=event_count,
            page=page,
            step=10,
        )
        
        # Get registrations
        registrations = request.env['op.alumni.event.registration'].search(
            domain,
            limit=10,
            offset=pager['offset']
        )
        
        values = {
            'alumni': alumni,
            'registrations': registrations,
            'pager': pager,
            'page_name': 'alumni_events',
        }
        return request.render('motakamel_alumni.portal_my_alumni_events', values)

    @http.route(['/my/alumni/jobs', '/my/alumni/jobs/page/<int:page>'], 
                type='http', auth='user', website=True)
    def portal_my_alumni_jobs(self, page=1, **kw):
        """Alumni jobs page"""
        alumni = request.env['op.alumni'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        # Get published jobs
        domain = [('state', '=', 'published'), ('is_published', '=', True)]
        
        # Count
        job_count = request.env['op.alumni.job'].sudo().search_count(domain)
        
        # Pager
        pager = portal_pager(
            url='/my/alumni/jobs',
            total=job_count,
            page=page,
            step=10,
        )
        
        # Get jobs
        jobs = request.env['op.alumni.job'].sudo().search(
            domain,
            limit=10,
            offset=pager['offset'],
            order='create_date desc'
        )
        
        values = {
            'alumni': alumni,
            'jobs': jobs,
            'pager': pager,
            'page_name': 'alumni_jobs',
        }
        return request.render('motakamel_alumni.portal_my_alumni_jobs', values)

