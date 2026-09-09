# PRD — Mandatory Receipt Attachment on Expenses

| | |
|---|---|
| **Module** | `hr_expense_attachment_required` (new) |
| **Target** | Odoo 18.0 / OCA `hr-expense` |
| **Status** | Draft |
| **Owner** | ppatni@systango.com |
| **Date** | 2026-09-09 |
| **Size** | Small — one new addon, ~150 LOC + tests |

## 1. Problem

Odoo lets an employee submit an expense report with no receipt attached. Nothing in
core or in the 11 addons in this repository blocks it. In practice this means:

- Finance discovers missing receipts **after** approval, when the report is already
  posted or paid, and has to chase the employee or reverse the entry.
- Reports fail tax and audit checks because the supporting document was never
  captured, and there is no record of where it was lost.
- Approvers become the control, so the rule is applied inconsistently — some let it
  through, some reject, and neither decision is traceable.

The gap is that the requirement is a policy in a handbook, not a rule in the system.

## 2. Goal

Refuse to submit an expense report when any line that needs a receipt does not have
one, and tell the employee exactly which lines to fix — at submit time, while they
can still act on it.

### Non-goals

- Validating the *content* of the attachment (OCR, amount matching, date checks).
- Any change to approval, posting, or payment flows.
- Per-product or per-category exemptions (see §8).
- Blocking at approve/post as a second gate. Submit is the only gate in v1; once a
  report is submitted, the receipt is present by construction.

## 3. Users

| User | What changes for them |
|---|---|
| **Employee** | Cannot submit a report missing a required receipt. Gets one error listing the offending lines. |
| **Expense manager / Finance** | Stops receiving reports with missing receipts. Configures the rule once per company. |
| **Accountant** | Every posted expense above the threshold has a supporting document attached. |

## 4. Requirements

### 4.1 Configuration

Two company-level settings, exposed under *Settings → Expenses* (following the
`res.company` + `res.config.settings` pattern already used by
`hr_expense_advance_clearing`):

| Field | Type | Default | Meaning |
|---|---|---|---|
| `expense_receipt_required` | Boolean | `False` | Master switch. Off = module installed but inert. |
| `expense_receipt_min_amount` | Monetary (company currency) | `0.0` | Lines with a total **greater than or equal to** this amount require a receipt. `0.0` means every line requires one. |

Both are company-dependent so a multi-company database can apply different policies
per company. The company that governs a line is the line's own company, falling back
to the sheet's company.

### 4.2 Enforcement

**FR-1** — On submit of an expense report, if `expense_receipt_required` is on, every
expense line whose total (in company currency) is `>= expense_receipt_min_amount`
must have at least one attachment.

**FR-2** — If one or more lines fail FR-1, submit is blocked with a single
`UserError` naming each failing line and its amount, so the employee can fix them all
in one pass:

> Attach a receipt to the following expenses before submitting:
> • Taxi to airport — 45.00 EUR
> • Client dinner — 120.00 EUR

**FR-3** — An attachment on the **report** does not satisfy a line. The receipt must
be on the expense line it supports, so that the document travels with the line into
the journal entry.

**FR-4** — Lines below the threshold are never blocked, whatever their state.

**FR-5** — The rule applies to the document, not to the person submitting it. A
manager submitting on an employee's behalf is held to the same rule; there is no
bypass group in v1. Rationale: a bypass group turns the control back into a
convention, which is the problem this module exists to solve.

**FR-6** — With `expense_receipt_required` off, behaviour is byte-for-byte core Odoo.
Installing the module changes nothing until it is switched on.

### 4.3 Visibility

**FR-7** — The expense list inside a report shows a *Receipt* indicator per line
(present / required-and-missing / not required), so the employee can see what is
missing before hitting submit rather than being told by an error.

## 5. Technical notes

- New addon `hr_expense_attachment_required`, `depends: ["hr_expense"]`, AGPL-3,
  version `18.0.1.0.0`, `development_status: "Beta"`.
- Enforcement hooks `hr.expense.sheet.action_submit_sheet()` — override, run the
  check, then `super()`. Keeping the check in an overridable
  `_check_required_attachments()` lets downstream modules extend the rule (§8).
- Attachment presence is read from `hr.expense.attachment_ids` rather than a
  cached count field, so it stays correct across Odoo versions.
- Two core field names must be confirmed against the target 18.0 codebase before
  implementation, as Odoo renamed them between recent versions: the expense total in
  company currency on `hr.expense` (expected `total_amount_company`) and the
  settings-page XPath anchor `hr_expense.res_config_settings_view_form`
  (used today by `hr_expense_advance_clearing`, so likely stable).
- Follow OCA layout: `readme/DESCRIPTION.md`, `readme/USAGE.md`,
  `readme/CONTRIBUTORS.md`, `tests/`, `i18n/`.

## 6. Test plan

| # | Case | Expected |
|---|---|---|
| 1 | Setting off, line with no receipt | Submits |
| 2 | Setting on, threshold 0, line with no receipt | Blocked, line named in error |
| 3 | Setting on, threshold 0, line with receipt | Submits |
| 4 | Setting on, threshold 50, line of 40 with no receipt | Submits |
| 5 | Setting on, threshold 50, line of 50 with no receipt | Blocked (boundary is inclusive) |
| 6 | Two failing lines | One error listing both |
| 7 | Receipt on the report, not the line | Blocked (FR-3) |
| 8 | Two companies, different thresholds | Each report judged by its own company |
| 9 | Line in a foreign currency above the threshold once converted | Blocked |

## 7. Success criteria

- Expense reports reaching *Approved* with a missing receipt above the threshold:
  **zero**, measurable by query after one month.
- No increase in submit-to-approve cycle time — the rule moves the rework earlier, it
  should not add a round trip.
- No regression in the existing test suites of the other addons in this repository.

## 8. Deferred

- Per-product / per-expense-category exemptions (mileage and per-diem have no
  receipt by nature and are the most likely first follow-up).
- A configurable bypass group, if a real operational need appears.
- Attachment content validation (OCR amount/date match against the line).
- A weekly digest to managers of reports sitting in draft because of a missing
  receipt.

## 9. Open questions

1. Is mileage/per-diem already in use in the target deployment? If yes, §8's
   category exemption is not deferrable and belongs in v1.
2. Should the threshold be compared against the line total or the line total
   excluding tax? This PRD assumes the line total (tax inclusive), matching what the
   employee sees on the receipt.
