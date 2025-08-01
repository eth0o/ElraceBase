# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models , _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "tier.validation"]
    _state_from = ["draft", "sent", "to approve"]
    _state_to = ["purchase", "approved"]

    _tier_validation_manual_config = False

    def _check_allow_write_under_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is under validation."""
        # exceptions = self._get_under_validation_exceptions()
        # if any(val not in exceptions for val in vals):
        #     return False
        return True

# allow edit after approved
    # def write(self, vals):
    #     for rec in self:
    #         if (
    #             rec.review_ids
    #             and rec.review_ids.filtered(lambda l: l.status == "pending")
    #             and rec._check_allow_write_under_validation(vals)
    #         ):
    #             raise ValidationError(_("The purchase order is under validation."))

    #     return super().write(vals)