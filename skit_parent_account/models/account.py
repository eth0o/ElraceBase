# -*- coding: utf-8 -*-
# -*- import of odoo -*-
from odoo import fields, models, api

# -*- Adding new fields for account.account model -*-


class Account(models.Model):

    _inherit = "account.account"

    parent_account = fields.Many2one('parent.account', string='Parent Account')
    is_parent = fields.Boolean()

# -*- Creating new model and fields -*-


class ParentAccount(models.Model):

    _name = "parent.account"
    _description = 'Parent Account'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", required=True, index=True, tracking=True)
    code = fields.Char(size=64, required=True, index=True, tracking=True)
    types = fields.Selection([('sum', 'View')], string='Type', default='sum')
    parent_account_id = fields.Many2one('parent.account',
                                        string='Parent Account')
    parent_tax_ids = fields.Many2many('account.tax', 'parent_account_rel',
                                      string='Default Taxes')
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, readonly=True,
                                 default=lambda self: self.env.company)
    parent_tag_ids = fields.Many2many('account.account.tag',
                                      'parent_account_tag_rel', string='Tags',
                                      help="Optional tags you may want to assign for custom reporting")
    parent_allowed_journal_ids = fields.Many2many('account.journal',
                                                  'parent_allowed_rel',
                                                  string="Allowed Journals",
                                                  help="Define in which journals this account can be used. If empty, can be used in all journals.")
    group_id = fields.Many2one('account.group',
                               compute='_compute_account_group',
                               store=True, readonly=True,
                               help="Account prefixes can determine account groups.")
    deprecated = fields.Boolean(index=True, default=False, tracking=True)
    root_id = fields.Many2one('account.root',
                              compute='_compute_parent_account_root',
                              store=True)

    # to Creat sequence number in side of list and kanban view
    @api.depends('code')
    def _compute_parent_account_root(self):
        for record in self:
            record.root_id = (ord(record.code[0]) * 1000 + ord(
                record.code[1:2] or '\x00')) if record.code else False

    