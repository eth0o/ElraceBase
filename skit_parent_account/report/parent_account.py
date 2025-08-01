# -*- coding: utf-8 -*-
# -*- import of odoo -*-
from odoo import models, _
from odoo.exceptions import UserError


class ReportTax(models.AbstractModel):
    _name = 'report.skit_parent_account.parent_account'

    # -*- Passing values for report  -*-
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form']}
