# Copyright 2026 Systango Technologies
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    expense_receipt_validation = fields.Selection(
        related="company_id.expense_receipt_validation",
        readonly=False,
    )
