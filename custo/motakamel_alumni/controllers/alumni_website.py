# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request


class AlumniWebsite(http.Controller):

    @http.route(['/alumni'], type='http', auth='public', website=True)
    def alumni_directory(self, **kw):
        """Alumni directory page"""
        alumni_records = request.env['op.alumni'].sudo().search([
            ('state', '=', 'active'),
            ('is_published', '=', True)
        ])
        
        values = {
            'alumni_records': alumni_records,
        }
        return request.render('motakamel_alumni.alumni_directory', values)

    @http.route(['/alumni/<int:alumni_id>'], type='http', auth='public', website=True)
    def alumni_detail(self, alumni_id, **kw):
        """Alumni detail page"""
        alumni = request.env['op.alumni'].sudo().browse(alumni_id)
        
        if not alumni.exists() or not alumni.is_published:
            return request.not_found()
        
        values = {
            'alumni': alumni,
        }
        return request.render('motakamel_alumni.alumni_detail', values)

    @http.route(['/alumni/events'], type='http', auth='public', website=True)
    def alumni_events(self, **kw):
        """Alumni events listing"""
        events = request.env['op.alumni.event'].sudo().search([
            ('state', 'in', ['published', 'registration_open']),
            ('is_published', '=', True)
        ], order='event_date desc')
        
        values = {
            'events': events,
        }
        return request.render('motakamel_alumni.alumni_events_list', values)

    @http.route(['/alumni/events/<int:event_id>'], type='http', auth='public', website=True)
    def alumni_event_detail(self, event_id, **kw):
        """Alumni event detail page"""
        event = request.env['op.alumni.event'].sudo().browse(event_id)
        
        if not event.exists() or not event.is_published:
            return request.not_found()
        
        values = {
            'event': event,
        }
        return request.render('motakamel_alumni.alumni_event_detail', values)

    @http.route(['/alumni/jobs'], type='http', auth='public', website=True)
    def alumni_jobs(self, **kw):
        """Alumni jobs listing"""
        jobs = request.env['op.alumni.job'].sudo().search([
            ('state', '=', 'published'),
            ('is_published', '=', True)
        ], order='create_date desc')
        
        values = {
            'jobs': jobs,
        }
        return request.render('motakamel_alumni.alumni_jobs_list', values)

    @http.route(['/alumni/jobs/<int:job_id>'], type='http', auth='public', website=True)
    def alumni_job_detail(self, job_id, **kw):
        """Alumni job detail page"""
        job = request.env['op.alumni.job'].sudo().browse(job_id)
        
        if not job.exists() or not job.is_published:
            return request.not_found()
        
        values = {
            'job': job,
        }
        return request.render('motakamel_alumni.alumni_job_detail', values)

