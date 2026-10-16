# Copyright 2026 Systango Technologies
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged("-at_install", "post_install")
class TestHrExpenseReceiptValidation(TestExpenseCommon):
    def _attach_receipt(self, expense_line):
        return self.env["ir.attachment"].create(
            {
                "name": "receipt.pdf",
                "res_model": "hr.expense",
                "res_id": expense_line.id,
                "datas": base64.b64encode(b"%PDF-1.4 fake receipt content"),
            }
        )

    def test_submit_without_validation_is_unaffected(self):
        """Default setting ('none') keeps the existing workflow untouched."""
        self.company_data["company"].expense_receipt_validation = "none"
        expense_sheet = self.create_expense_report()
        expense_sheet.action_submit_sheet()
        self.assertEqual(expense_sheet.state, "submit")

    def test_submit_warning_mode_without_receipt(self):
        """Warning mode allows submission but returns a warning notification."""
        self.company_data["company"].expense_receipt_validation = "warning"
        expense_sheet = self.create_expense_report()
        result = expense_sheet.action_submit_sheet()
        self.assertEqual(expense_sheet.state, "submit")
        self.assertTrue(result)
        self.assertEqual(result.get("tag"), "display_notification")
        self.assertEqual(result["params"]["type"], "warning")

    def test_submit_warning_mode_with_receipt(self):
        """Warning mode does not warn when a receipt is attached."""
        self.company_data["company"].expense_receipt_validation = "warning"
        expense_sheet = self.create_expense_report()
        self._attach_receipt(expense_sheet.expense_line_ids)
        result = expense_sheet.action_submit_sheet()
        self.assertEqual(expense_sheet.state, "submit")
        self.assertFalse(result)

    def test_submit_mandatory_mode_without_receipt_is_blocked(self):
        """Mandatory mode blocks submission until a receipt is attached."""
        self.company_data["company"].expense_receipt_validation = "mandatory"
        expense_sheet = self.create_expense_report()
        with self.assertRaises(UserError):
            expense_sheet.action_submit_sheet()
        self.assertEqual(expense_sheet.state, "draft")

    def test_submit_mandatory_mode_with_receipt(self):
        """Mandatory mode allows submission once a receipt is attached."""
        self.company_data["company"].expense_receipt_validation = "mandatory"
        expense_sheet = self.create_expense_report()
        self._attach_receipt(expense_sheet.expense_line_ids)
        expense_sheet.action_submit_sheet()
        self.assertEqual(expense_sheet.state, "submit")
