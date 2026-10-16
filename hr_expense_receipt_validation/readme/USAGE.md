1. Create an expense line without attaching a receipt.
2. Click *Submit to Manager* on the expense report.
3. Depending on the configured mode:
   - *Not enforced*: the report is submitted as usual.
   - *Warn if missing*: the report is submitted and a warning notification
     lists the expenses without a receipt.
   - *Required to submit*: an error is raised, listing the expenses
     without a receipt, and the report stays in draft until a receipt is
     attached to each one.
