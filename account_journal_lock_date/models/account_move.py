# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class AccountMove(models.Model):

    _inherit = "account.move"

    def write(self, values):
        res = super().write(values)
        if "current_reviewer" in values:
            return res
        # if editing the stage, we don't want to check the lock date
        if "acc_stage_id" in values and self.user_has_groups("account.group_account_manager"):
            return res
        if "payment_id" in values:
            return res
        self._check_fiscalyear_lock_date()
        return res
# skip_account_move_synchronization

    def read(self, fields=None, load='_classic_read'):
        # Update context to enforce read-only mode
        context = dict(self.env.context or {})
        context.update({"readonly": True})
        self = self.with_context(context)
        
        return super(AccountMove, self).read(fields=fields, load=load)
    
    def _check_fiscalyear_lock_date(self):
        
        res = super()._check_fiscalyear_lock_date()
        if self.env.context.get("readonly"):
            return res
        if self.env.context.get("bypass_journal_lock_date"):
            return res
        # if the invoice is in draft state, we don't want to check the lock date
        # because the user may want to change the invoice date
        if self.filtered(lambda move: move.state == "draft"):
            return res
        for move in self:
            if self.user_has_groups("account.group_account_manager"):
                lock_date = move.journal_id.fiscalyear_lock_date or date.min
            else:
                lock_date = max(
                    move.journal_id.period_lock_date or date.min,
                    move.journal_id.fiscalyear_lock_date or date.min,
                )
            if move.date <= lock_date:
                if move.voucher_type not in ['payment_voucher', 'receipt_voucher']:
                    if move.payment_id:
                        return res  
                    #UNexclude payments as request from Mr.kadri 7/5/2025 Request back on 09/07/2025
                    lock_date = format_date(self.env, lock_date)
                    if self.user_has_groups("account.group_account_manager"):
                        message = _(
                            "You cannot add/modify entries for the journal '%s' "
                            "prior to and inclusive of the lock date %s"
                        ) % (move.journal_id.display_name, lock_date)
                    else:
                        message = _(
                            "You cannot add/modify entries for the journal '%s' "
                            "prior to and inclusive of the lock date %s. "
                            "Check the Journal settings or ask someone "
                            "with the 'Adviser' role"
                        ) % (move.journal_id.display_name, lock_date)
                    raise UserError(message)
        return res
