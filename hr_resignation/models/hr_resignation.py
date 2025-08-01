# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

date_format = "%Y-%m-%d"
RESIGNATION_TYPE = [('resigned', 'Normal Resignation'),
                    ('fired', 'Fired by the company')]


class HrResignation(models.Model):
    _name = 'hr.resignation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _description = "Resignation/Termination"

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env.user.employee_id.id,
                                  help='Name of the employee for whom the request is creating')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    help='Department of the employee')
    resign_confirm_date = fields.Date(string="Confirmed Date",
                                      help='Date on which the request is confirmed by the employee.',
                                      track_visibility="always")
    approved_revealing_date = fields.Date(string="Approved Last Day Of Employee",
                                          help='Date on which the request is confirmed by the manager.',
                                          track_visibility="always")
    joined_date = fields.Date(string="Join Date",
                              help='Joining date of the employee.i.e Start date of the first contract',related='employee_id.joining_date')

    expected_revealing_date = fields.Date(string="Last Day of Employee", required=True,
                                          help='Employee requested date on which he is revealing from the company.')
    reason = fields.Text(string="Reason", required=True,
                         help='Specify reason for leaving the company')
    notice_period = fields.Integer(string="Notice Period")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('direct_manager', 'Waiting Direct Manager Approval'),
        ('dep_manager', 'Waiting Dep.Branch Manager Approval'),
        ('hr_manager', 'Waiting HR Manager Approval'),
        ('ceo', 'Waiting CEO Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', track_visibility='onchange')
    resignation_type = fields.Selection(selection=RESIGNATION_TYPE, help="Select the type of resignation: normal "
                                                                         "resignation or fired by the company",
                                                                         default='resigned', readonly=True)
    read_only = fields.Boolean(string="check field")
    employee_contract = fields.Char(String="Contract")
    termination_type = fields.Selection([('performance', 'Performance'), ('redundancy', 'Redundancy'),('disciplinary','Disciplinary')], string='Termination Type',)
    # grade_id = fields.Char(string='Grade', related='employee_id.emp_id', readonly=True)
    grade_code = fields.Char(string='Employee Code', related='employee_id.emp_id', readonly=True)
    eos_id = fields.Many2one('hr.eos', string="EOS")
    job_id = fields.Many2one(related='employee_id.job_id',readonly=True)
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    manager_manager = fields.Many2one('res.users', related='employee_id.parent_id.parent_id.user_id', string="Manager Manager")
    current_reviewer = fields.Many2one('res.users', string='Current Reviewer')
    current_reviewer_stored = fields.Many2one('res.users', string='Current Reviewer', store=True, )

    # def _compute_next_review_user(self):
    #     for rec in self:
    #         review = rec.review_ids.sorted("sequence").filtered(
    #             lambda l: l.status == "pending"
    #         )[:1]
    #         reviewer = rec.env['res.users'].search([('name', '=', review.todo_by)])
    #         if len(reviewer) > 1:
    #             rec.current_reviewer = reviewer[0]
    #             rec.current_reviewer_stored = reviewer[0]
    #         else:
    #             rec.current_reviewer = reviewer
    #             rec.current_reviewer_stored = reviewer.id
                
    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise UserError(('You can not delete approved records, cancel it first'))
            else:
                rec.employee_id.active = True
                rec.employee_id.resigned = False
                rec.employee_id.fired = False
                rec.eos_id.unlink() if rec.eos_id else None
                return super(HrResignation, self).unlink()

    def open_eos(self):
        for rec in self:
            return {
                'name': _('End of Service'),
                'view_mode': 'tree,form',
                'res_model': 'hr.eos',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id','=',rec.eos_id.id),]
            }

    @api.onchange('requested_by')
    def _onchange_requested_by(self):
        if self.requested_by:
            if self.requested_by.has_group('hr.group_hr_user'):
                return {'domain': {'employee_id': []}}
            else:
                return {'domain': {'employee_id': ['|',('parent_id.user_id', '=', self.requested_by.id),('user_id','=',self.requested_by.id)]}}
                
    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        print(res_user.has_group('hr.group_hr_user'))
        if res_user.has_group('hr.group_hr_user'):
            self.read_only = True
        else:
            self.read_only = False

    @api.onchange('employee_id')
    def set_join_date(self):
        # self.joined_date = self.employee_id.joining_date if self.employee_id.joining_date else ''
        self.joined_date = self.employee_id.sudo().joining_date if self.employee_id.sudo().joining_date else False


    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.resignation') or _('New')
        res = super(HrResignation, self).create(vals)
        return res

    # @api.constrains('employee_id')
    # def check_employee(self):
    #     # Checking whether the user is creating leave request of his/her own
    #     for rec in self:
    #         if not self.env.user.has_group('hr.group_hr_user'):
    #             if rec.employee_id.user_id.id and rec.employee_id.user_id.id != self.env.uid:
    #                 raise ValidationError(
    #                     _('You cannot create request for other employees'))

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def check_request_existence(self):
        # Check whether any resignation request already exists
        for rec in self:
            if rec.employee_id:
                resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                         ('state', 'in', ['confirm', 'approved'])])
                if resignation_request:
                    raise ValidationError(_('There is a resignation request in confirmed or'
                                            ' approved state for this employee'))
                if rec.employee_id:
                    no_of_contract = self.env['hr.contract'].sudo().search(
                        [('employee_id', '=', self.employee_id.id)])
                    for contracts in no_of_contract:
                        if contracts.state == 'open':
                            rec.employee_contract = contracts.name
                            rec.notice_period = contracts.notice_days

    @api.constrains('joined_date')
    def _check_dates(self):
        # validating the entered dates
        for rec in self:
            resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                     ('state', 'in', ['confirm', 'approved'])])
            if resignation_request:
                raise UserError(_('There is a resignation request in confirmed or'
                                        ' approved state for this employee'))

    def action_submit(self):
        if self.joined_date:
            if self.joined_date >= self.expected_revealing_date:
                raise ValidationError(
                    _('Last date of the Employee must be anterior to Joining date'))
        # if self.grade_code <= '6' or self.resignation_type == 'fired':
        #     if not self.employee_id.department_id.manager_id:
        #         raise ValidationError(_('There is no Department Manager assigned for this employee!'))
        #     if not self.employee_id.department_id.manager_id.user_id:
        #         raise ValidationError(_('There is no user assigned for this Department Manager!'))
        #     self.env['mail.activity'].sudo().create({
        #     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
        #     'res_id': self.id,
        #     'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'hr.resignation')]).id,
        #     'summary': self.name,
        #     'note': 'This Request needs Department Manager approval',
        #     'user_id': self.employee_id.department_id.manager_id.user_id.id,
        #     })
        #     self.state = 'dep_manager'
        # else:
            if not self.employee_id.parent_id:
                raise ValidationError(_('There is no Direct Manager assigned for this employee!'))
            if not self.employee_id.parent_id.user_id:
                raise ValidationError(_('There is no user assigned for %s!' % self.employee_id.parent_id.name))
            #add activity to hr manager for approval

            self.env['mail.activity'].sudo().create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'hr.resignation')]).id,
                'summary': self.name,
                'note': 'This Request needs Direct Manager approval',
                'user_id': self.employee_id.parent_id.user_id.id,
            })
            self.state = 'direct_manager'

    def direct_approve(self):
        # if not self.employee_id.department_id.manager_id:
        #     raise ValidationError(_('There is no Department Manager assigned for this employee!'))
        # if not self.employee_id.department_id.manager_id.user_id:
        #     raise ValidationError(_('There is no user assigned for this Department Manager!'))
        # if not self.env.ref('hr.group_hr_manager').current_user_id:
        #         raise ValidationError(_('There is no User assigned to Fill the Role (HR Manager)!'))
        for rec in self:
            if not self.env.user == self.employee_id.parent_id.user_id:
                raise ValidationError(_('Only Direct Manager can Approve this Request!'))
            direct_manager = self.employee_id.parent_id.user_id
            manager_manager = self.employee_id.parent_id.parent_id.user_id
            if not rec.joined_date:
                raise ValidationError(_('Please set joining date for employee'))
            activity =rec.env['mail.activity'].sudo().search([('res_id', '=', rec.id), ('res_model', '=', 'hr.resignation')])
            if len(activity) > 1:
                for act in activity:
                    act.action_done()
                    act.unlink()
            else:
                activity.action_done()
                activity.unlink()
            hr_manager = self.env.ref('hr.group_hr_manager').users[0]
            if direct_manager.employee_id.parent_id.department_id.depth == 0:
                self.state = 'hr_manager'
                self.env['mail.activity'].sudo().create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'hr.resignation')]).id,
                    'summary': self.name,
                    'note': 'This Request needs HR Manager approval',
                    'user_id': hr_manager.id,
                    })
            else:
                self.state = 'dep_manager'
                self.env['mail.activity'].sudo().create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'hr.resignation')]).id,
                    'summary': self.name,
                    'note': 'This Request needs Department Manager approval',
                    'user_id': manager_manager.id,
                    })


    def department_approve(self):
        # if not self.env.ref('hr.group_hr_manager').current_user_id:
        #         raise ValidationError(_('There is no User assigned to Fill the Role (HR Manager)!'))
        for rec in self:
            # if not self.env.user == self.employee_id.department_id.manager_id.user_id:
            #     raise UserError(_('Only Department Manager can Approve this Request!'))
            if not self.joined_date:
                raise UserError(_('Please set joining date for employee'))
            hr_manager = self.env.ref('hr.group_hr_manager').users[0]
            activity =self.env['mail.activity'].sudo().search([('res_id', '=', rec.id), ('res_model', '=', 'hr.resignation')])
            if len(activity) > 1:   
                for act in activity:
                    act.action_done()
                    act.unlink()
            else:
                activity.action_done()
                activity.unlink()
            self.env['mail.activity'].sudo().create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'hr.resignation')]).id,
            'summary': self.name,
            'note': 'This Request needs HR Manager approval',
            'user_id': hr_manager.id,
            })
            self.state = 'hr_manager'
            self.resign_confirm_date = str(datetime.now())



    def hr_approve(self):
        for rec in self:
            activities = self.env['mail.activity'].sudo().search([('res_id', '=', rec.id), ('res_model', '=', 'hr.resignation')])
            # .action_done()
            if len(activities) > 1:
                for activity in activities:
                    activity.action_done()
                    activity.unlink()
            else:
                activities.action_done()
                activities.unlink()
            self.approve_resignation()

    def ceo_approve(self):
        for rec in self:
            if not self.env.user == self.env.ref('morals_base.ceo_group').current_user_id:
                raise ValidationError(_('Only CEO can Approve this Request!'))
            self.env['mail.activity'].sudo().search([('res_id', '=', rec.id), ('res_model', '=', 'hr.resignation')])
            self.approve_resignation()

    def confirm_resignation(self):
        if self.joined_date:
            if self.joined_date >= self.expected_revealing_date:
                raise ValidationError(
                    _('Last date of the Employee must be anterior to Joining date'))
            for rec in self:
                rec.state = 'confirm'
                rec.resign_confirm_date = str(datetime.now())
        else:
            raise ValidationError(_('Please set joining date for employee'))

    def cancel_resignation(self):
        for rec in self:
            if rec.state == 'approved':
                rec.employee_id.active = True
                rec.employee_id.resigned = False
                rec.employee_id.fired = False
                rec.eos_id.unlink()
            rec.state = 'cancel'

    def reject_resignation(self):
        for rec in self:
            activities = self.env['mail.activity'].sudo().search([('res_id', '=', rec.id), ('res_model', '=', 'hr.resignation')])
            if len(activities) > 1:
                for activity in activities:
                    # activity.action_done()
                    activity.unlink()
            else:
                # activities.action_done()
                activities.unlink()
            rec.state = 'cancel'

    def reset_to_draft(self):
        for rec in self:
            activities = self.env['mail.activity'].sudo().search([('res_id', '=', rec.id), ('res_model', '=', 'hr.resignation')])
            if len(activities) > 1:
                for activity in activities:
                    # activity.action_done()
                    activity.unlink()
            else:
                # activities.action_done()
                activities.unlink()
            rec.state = 'draft'
            

    def approve_resignation(self):
        for rec in self:
            print("****************** \n\n\n\\n\nn\n\n\n\n\nn\\n'Approve Resignation")
            if rec.expected_revealing_date:
                print("****************** \n\n\n\\n\nn\n\n\n\n\nn\\n'expected_revealing_date")
                if not rec.approved_revealing_date:
                    raise ValidationError(_('Please set Approved Revealing Date'))
                no_of_contract = self.env['hr.contract'].sudo().search(
                    [('employee_id', '=', self.employee_id.id)])
                if not no_of_contract:
                    raise ValidationError(_('No contract found for this employee')) 
                for contracts in no_of_contract:
                    print("****************** \n\n\n\\n\nn\n\n\n\n\nn\\n'no_of_contract")
                    rec.employee_contract = contracts.name
                    rec.state = 'approved'
                # Changing state of the employee if resigning today
                if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
                    print("****************** \n\n\n\\n\nn\n\n\n\n\nn\\n'employee_id.active")
                    rec.employee_id.active = False
                    print("****************** \n\n\n\\n\nn\n\n\n\n\nn\\n' FATER  employee_id.active")
                    # Changing fields in the employee table with respect to resignation
                    rec.employee_id.resign_date = rec.expected_revealing_date
                    if rec.resignation_type == 'resigned':
                        rec.employee_id.resigned = True
                    else:
                        rec.employee_id.fired = True
                    # Removing and deactivating user
                    if rec.employee_id.user_id:
                        rec.employee_id.user_id.sudo().active = False
                        rec.employee_id.sudo().user_id = None
                    if rec.employee_id.address_home_id:
                        rec.employee_id.sudo().address_home_id.sudo().active = False
                print("****************** \n\n\n\\n\nn\n\n\n\n\nn\\n'FINISHED employee_id.active")
                # create hr.eos for employee if not exists
                if not self.env['hr.eos'].search([('employee_id', '=', self.employee_id.id)]):
                    print("****************** \n\n\n\\n\nn\n\n\n\n\nn\\n'CREATED EOS")
                    eos = self.env['hr.eos'].create({
                        'employee_id': self.employee_id.id,
                        'eos_type': 'resignation' if rec.resignation_type == 'resigned' else 'termination',
                        'notice_period': rec.notice_period,
                        'eos_date': rec.approved_revealing_date - timedelta(days=rec.notice_period),
                        'termination_reason': rec.termination_type if rec.resignation_type == 'fired' else False,
                    })
                    eos.submit()
                    rec.eos_id = eos.id
            else:
                raise ValidationError(_('Please enter valid dates.'))

    def update_employee_status(self):
        resignation = self.env['hr.resignation'].search(
            [('state', '=', 'approved')])
        for rec in resignation:
            if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
                rec.employee_id.active = False
                # Changing fields in the employee table with respect to resignation
                rec.employee_id.resign_date = rec.expected_revealing_date
                if rec.resignation_type == 'resigned':
                    rec.employee_id.resigned = True
                else:
                    rec.employee_id.fired = True
                # Removing and deactivating user
                if rec.employee_id.user_id:
                    rec.employee_id.user_id.active = False
                    rec.employee_id.user_id = None


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    resign_date = fields.Date(
        'Resign Date', readonly=True, help="Date of the resignation")
    resigned = fields.Boolean(string="Resigned", default=False, store=True,
                              help="If checked then employee has resigned")
    fired = fields.Boolean(string="Fired", default=False,
                           store=True, help="If checked then employee has fired")
