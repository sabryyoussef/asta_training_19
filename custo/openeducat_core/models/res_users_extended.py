###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class ResUsersExtended(models.Model):
    """Extended res.users to fix role conversion issues in Odoo 19"""
    _inherit = "res.users"

    @api.model
    def _convert_groups_for_write(self, vals):
        """
        Convert groups_id write operations to use group.users inverse relationship.
        This fixes the issue when converting users from internal to portal in Odoo 19.
        
        In Odoo 19, groups_id is not directly writable on res.users.
        We need to use the inverse relationship through res.groups.users field.
        """
        if 'groups_id' not in vals:
            return vals
        
        # Extract groups_id commands
        groups_commands = vals.pop('groups_id')
        
        # Store for later processing
        self._pending_groups_commands = groups_commands
        
        return vals

    def write(self, vals):
        """
        Override write to handle groups_id changes properly in Odoo 19.
        This ensures role conversion (user to portal) works correctly.
        """
        # Check if groups_id is being modified
        if 'groups_id' in vals:
            vals = self._convert_groups_for_write(vals)
            has_pending_groups = hasattr(self, '_pending_groups_commands')
        else:
            has_pending_groups = False
        
        # Perform the regular write
        res = super(ResUsersExtended, self).write(vals)
        
        # Apply groups changes using the inverse relationship
        if has_pending_groups:
            groups_commands = self._pending_groups_commands
            delattr(self, '_pending_groups_commands')
            
            try:
                # Process groups_id commands
                # Command format: (0, 0, {values}), (1, id, {values}), (2, id), (3, id), (4, id), (5), (6, 0, [ids])
                
                for command in groups_commands:
                    if command[0] == 6:  # (6, 0, [ids]) - Replace all groups
                        new_group_ids = command[2]
                        
                        # Get current groups
                        current_groups = self.groups_id
                        
                        # Remove user from groups they're no longer in
                        groups_to_remove = current_groups.filtered(lambda g: g.id not in new_group_ids)
                        for group in groups_to_remove:
                            group.write({'users': [(3, self.id)]})
                        
                        # Add user to new groups
                        groups_to_add = self.env['res.groups'].browse(new_group_ids).filtered(
                            lambda g: g.id not in current_groups.ids
                        )
                        for group in groups_to_add:
                            group.write({'users': [(4, self.id)]})
                    
                    elif command[0] == 4:  # (4, id) - Add link to existing group
                        group_id = command[1]
                        group = self.env['res.groups'].browse(group_id)
                        if self not in group.users:
                            group.write({'users': [(4, self.id)]})
                    
                    elif command[0] == 3:  # (3, id) - Remove link to existing group
                        group_id = command[1]
                        group = self.env['res.groups'].browse(group_id)
                        if self in group.users:
                            group.write({'users': [(3, self.id)]})
                    
                    elif command[0] == 5:  # (5) - Remove all links
                        for group in self.groups_id:
                            group.write({'users': [(3, self.id)]})
                
                _logger.info(f"Successfully applied groups changes for user {self.id}")
                
            except Exception as e:
                _logger.error(f"Error applying groups changes for user {self.id}: {e}")
                raise
        
        return res
