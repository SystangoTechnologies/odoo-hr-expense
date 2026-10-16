# Copyright 2026 Systango Technologies
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hr Expense Receipt Validation",
    "summary": "Warn or block expense submission when a receipt is missing",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "website": "https://github.com/OCA/hr-expense",
    "author": "Systango Technologies, Odoo Community Association (OCA)",
    "maintainers": ["SystangoTechnologies"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_expense",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
}
