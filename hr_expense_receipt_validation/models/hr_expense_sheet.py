# Copyright 2026 Systango Technologies
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def _get_expense_lines_without_receipt(self):
        """Return the expense lines of this sheet that have no attachment."""
        return self.expense_line_ids.filtered(lambda line: not line.attachment_ids)

    def _get_missing_receipt_names(self):
        self.ensure_one()
        missing_lines = self._get_expense_lines_without_receipt()
        return "\n".join(f"- {name}" for name in missing_lines.mapped("name"))

    def action_submit_sheet(self):
        """Apply the configured receipt validation before submitting.

        Depending on the ``expense_receipt_validation`` setting of the
        sheet's company, submission can either proceed unchanged, proceed
        with a warning notification, or be blocked with an error until a
        receipt is attached to every expense line.
        """
        warning_messages = []
        for sheet in self:
            validation_mode = sheet.company_id.expense_receipt_validation
            if validation_mode in (False, "none"):
                continue
            missing_names = sheet._get_missing_receipt_names()
            if not missing_names:
                continue
            if validation_mode == "mandatory":
                raise UserError(
                    _(
                        "You cannot submit the expense report %(sheet)s "
                        "because the following expenses have no receipt "
                        "attached:\n%(missing)s\n"
                        "Please attach a receipt to each expense before "
                        "submitting the report.",
                        sheet=sheet.name,
                        missing=missing_names,
                    )
                )
            if validation_mode == "warning":
                warning_messages.append(
                    _(
                        "The expense report %(sheet)s was submitted, but "
                        "the following expenses have no receipt "
                        "attached:\n%(missing)s",
                        sheet=sheet.name,
                        missing=missing_names,
                    )
                )
        result = super().action_submit_sheet()
        if warning_messages:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Missing receipt"),
                    "message": "\n\n".join(warning_messages),
                    "type": "warning",
                    "sticky": True,
                },
            }
        return result
