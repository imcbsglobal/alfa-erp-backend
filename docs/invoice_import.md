# Invoice Import Behavior

Endpoint: `POST /api/sales/invoices/import/` (handled by `ImportInvoiceView`)

Behavior:
- If an invoice with the provided `invoice_no` does not exist, the request creates a new `Invoice` and its `InvoiceItem` rows (status: created).
- If an invoice with the provided `invoice_no` already exists, the endpoint will now update the existing invoice:
  - The `customer` record is upserted (`update_or_create` by `code`).
  - The `salesman` is `get_or_create` by name.
  - Invoice-level fields (`invoice_date`, `salesman`, `customer`, `created_by`, `remarks`) are updated.
  - Existing `InvoiceItem` rows for that invoice are deleted and replaced with the incoming items (full replace).
  - The authenticated `created_user` will be set if available.
  - An SSE event is emitted with the updated invoice payload.

Responses:
- 201 Created: new invoice created successfully.
- 200 OK: existing invoice updated successfully.
- 400: validation errors.
- 500: unexpected server error.

Notes & Recommendations:
- The update operation is performed inside a DB transaction to ensure data consistency.
- Updating an invoice replaces all line items. If you need to support partial updates/merging of items, we can implement item reconciliation logic (match by `item_code` and update quantities instead of full replace).
- If you want to prevent updates once processing starts (e.g., after picking has started), we can add status checks to reject updates when `invoice.status` is beyond a certain stage.

If you'd like, I can:
- Add optional reconciliation logic to merge items instead of replacing them, or
- Prevent updates when the invoice has moved to `PICKING`/`PACKED`/`DISPATCHED` states.
