# -*- coding: utf-8 -*-
#  -*- import of odoo
from odoo import fields, models

# -*- Creating new model and fields -*-


class AccounHierarchy(models.TransientModel):
    _name = "account.hierarchy"
    _description = 'Parent Account Hierarchy'
    _inherit = "account.common.report"

    display_account = fields.Selection(
                        [('all', 'All'),
                         ('movement', 'With movements')],
                        string='Display Accounts',
                        required=True,
                        default='movement')
    report_based_on = fields.Selection(
                        [('accounts', 'Accounts'),
                         ('account_type', 'Account Type')],
                        string='Report based on', required=True,
                        default='movement')
    auto_fold = fields.Boolean(string='Auto fold', default=False)

    # Passing value to print report
    def _print_report(self, data):
        data['form'].update({'display_account': self.display_account,
                             'report_based_on': self.report_based_on})
        return self.env.ref('skit_parent_account.action_parent_account_report').report_action(self, data=data)

    # Passing value to print report in xlsx
    def check_report_xlsx(self):
        return self._print_report()
 