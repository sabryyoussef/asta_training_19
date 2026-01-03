# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CertificateTemplatePreview(models.Model):
    _name = 'gr.certificate.template.preview'
    _description = 'Certificate Template Preview'
    _rec_name = 'template_name'

    # Template Information
    template_id = fields.Many2one(
        'gr.certificate.template',
        string='Template',
        help='Certificate template being previewed'
    )
    
    template_name = fields.Char(
        string='Template Name',
        related='template_id.name',
        help='Name of the template'
    )
    
    # Preview Content
    header_content = fields.Html(
        string='Header Preview',
        help='Preview of the header content'
    )
    
    body_content = fields.Html(
        string='Body Preview',
        help='Preview of the body content'
    )
    
    footer_content = fields.Html(
        string='Footer Preview',
        help='Preview of the footer content'
    )
    
    # Context Data
    context_data = fields.Text(
        string='Context Data',
        help='Sample data used for preview'
    )
    
    # Full Preview
    full_preview = fields.Html(
        string='Full Preview',
        compute='_compute_full_preview',
        help='Complete certificate preview'
    )
    
    @api.depends('header_content', 'body_content', 'footer_content')
    def _compute_full_preview(self):
        """Compute the full certificate preview."""
        for preview in self:
            if preview.template_id:
                # Get template styling
                template = preview.template_id
                styles = f"""
                    <style>
                        body {{
                            font-family: {template.font_family};
                            background-color: {template.background_color};
                            color: {template.text_color};
                            margin: {template.margin_top}in {template.margin_right}in {template.margin_bottom}in {template.margin_left}in;
                        }}
                        .certificate-container {{
                            width: {template.page_width}in;
                            height: {template.page_height}in;
                            position: relative;
                        }}
                        .accent {{
                            color: {template.accent_color};
                        }}
                    </style>
                """
                
                preview.full_preview = f"""
                    {styles}
                    <div class="certificate-container">
                        {preview.header_content or ''}
                        {preview.body_content or ''}
                        {preview.footer_content or ''}
                    </div>
                """
            else:
                preview.full_preview = '<p>No template selected</p>'
    
    def action_close_preview(self):
        """Close the preview window."""
        return {'type': 'ir.actions.act_window_close'}
