# Copyright 2026 Systango Technologies
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    expense_receipt_validation = fields.Selection(
        selection=[
            ("none", "Not enforced"),
            ("warning", "Warn if missing"),
            ("mandatory", "Required to submit"),
        ],
        default="none",
        help=(
            "Controls what happens when an employee submits an expense "
            "that has no receipt attached:\n"
            "- Not enforced: the expense can be submitted as before.\n"
            "- Warn if missing: the employee is warned but can still "
            "submit the expense report.\n"
            "- Required to submit: the expense report cannot be "
            "submitted until every expense has a receipt attached."
        ),
    )
