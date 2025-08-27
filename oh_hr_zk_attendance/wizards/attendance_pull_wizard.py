# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: cybrosys(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import pytz
import datetime
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AttendancePullWizard(models.TransientModel):
    _name = 'attendance.pull.wizard'
    _description = 'Attendance Pull Wizard'

    site_id = fields.Many2one(
        'res.partner', 
        string='Site/Location',
        domain=[('is_company', '=', True)],
        help='Select the site/location to pull attendance from'
    )
    
    device_ids = fields.Many2many(
        'zk.machine',
        string='Devices',
        help='Devices at the selected site. Leave empty to pull from all devices at the site.'
    )
    
    pull_type = fields.Selection([
        ('today', 'Today Only'),
        ('date_range', 'Date Range')
    ], string='Pull Type', default='today', required=True)
    
    from_date = fields.Date(
        string='From Date',
        default=fields.Date.context_today
    )
    
    to_date = fields.Date(
        string='To Date',
        default=fields.Date.context_today
    )
    
    @api.onchange('site_id')
    def _onchange_site_id(self):
        """Update devices based on selected site"""
        if self.site_id:
            devices = self.env['zk.machine'].search([('address_id', '=', self.site_id.id)])
            self.device_ids = [(6, 0, devices.ids)]
        else:
            self.device_ids = [(6, 0, [])]
    
    @api.onchange('pull_type')
    def _onchange_pull_type(self):
        """Set dates based on pull type"""
        if self.pull_type == 'today':
            today = fields.Date.context_today(self)
            self.from_date = today
            self.to_date = today
    
    def action_pull_attendance(self):
        """Pull attendance data from selected devices for the specified date range"""
        if not self.device_ids:
            if self.site_id:
                # Get all devices for the site if none specifically selected
                devices = self.env['zk.machine'].search([('address_id', '=', self.site_id.id)])
                if not devices:
                    raise UserError(_('No devices found for the selected site.'))
            else:
                # If no site selected, get all devices
                devices = self.env['zk.machine'].search([])
                if not devices:
                    raise UserError(_('No biometric devices configured.'))
        else:
            devices = self.device_ids
        
        if self.pull_type == 'date_range' and self.from_date > self.to_date:
            raise UserError(_('From Date cannot be greater than To Date.'))
        
        # Determine date range
        if self.pull_type == 'today':
            from_date = to_date = fields.Date.context_today(self)
        else:
            from_date = self.from_date
            to_date = self.to_date
        
        # Pull attendance from each device
        pulled_count = 0
        failed_devices = []
        
        for device in devices:
            try:
                count = device.download_attendance_filtered(from_date, to_date)
                pulled_count += count
            except Exception as e:
                failed_devices.append(f"{device.name}: {str(e)}")
        
        # Prepare result message
        messages = []
        if pulled_count > 0:
            messages.append(f"Successfully pulled {pulled_count} attendance records.")
        
        if failed_devices:
            messages.append(f"Failed to connect to {len(failed_devices)} device(s):")
            messages.extend(failed_devices)
        
        if not messages:
            messages.append("No new attendance records found for the selected criteria.")
        
        # Show result in a popup
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Attendance Pull Complete'),
                'message': '\n'.join(messages),
                'type': 'success' if pulled_count > 0 else 'warning',
                'sticky': True,
            }
        }