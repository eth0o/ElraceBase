# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _name = "hr.expense.sheet"
    _inherit = ["hr.expense.sheet", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["submit", "approve", "post", "done"]

    _tier_validation_manual_config = False

    def _get_under_validation_exceptions(self):
        """Extend for more field exceptions."""
        # allow to write under validation
        return ["message_follower_ids", "access_token"]

    
    # allow to read under validation
    def read(self, fields=None, load="_classic_read"):
        if self.env.context.get("under_validation"):
            return super().read(fields=fields, load=load)
        return super().read(fields=fields, load=load)
    
    def _check_allow_write_under_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is under validation."""
        # exceptions = self._get_under_validation_exceptions()
        # if any(val not in exceptions for val in vals):
        #     return False
        return True
    
    def write(self, vals):
        for rec in self:
            # if any of all review_ids is pending, then it is not allowed
            if (
                rec.review_ids
                and rec.review_ids.filtered(lambda l: l.status == "pending")
                and rec._check_allow_write_under_validation(vals)
            ):
                if any(
                    [
                        "employee_id" in vals,
                        "expense_line_ids" in vals,
                        "payment_mode" in vals,
                        "journal_id" in vals,
                        "company_id" in vals,
                    ]
                ):
                    raise ValidationError(_("The expense report is under validation."))
                else:
                    continue
        return super().write(vals)