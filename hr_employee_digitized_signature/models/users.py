# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UsersProfile(models.Model):
    _inherit = "res.users"

    emp_signature = fields.Binary(related="employee_id.signature", string="Signature")