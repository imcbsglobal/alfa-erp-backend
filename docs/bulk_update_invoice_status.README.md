# Bulk Update Invoice Status Command

This management command allows you to update the status of invoices from PICKED, INVOICED, or PACKED to DELIVERED.

## Usage

1. Activate your backend virtual environment and navigate to the backend directory:

```
cd alfa-erp-backend
```

2. Run the command with your desired options:

### Update all invoices in selected statuses:
```
python manage.py bulk_update_invoice_status --all
```

### Update invoices in selected statuses within a date range:
```
python manage.py bulk_update_invoice_status --from-date 2026-02-01 --to-date 2026-02-28
```

### Update only specific statuses (e.g., only PICKED):
```
python manage.py bulk_update_invoice_status --statuses PICKED
```

### Combine options:
```
python manage.py bulk_update_invoice_status --statuses PICKED PACKED --from-date 2026-02-01 --to-date 2026-02-28
```

- By default, the command updates PICKED, INVOICED, and PACKED statuses.
- Use `--all` to ignore date filters and update all matching invoices.

## Notes
- Make sure you have the correct permissions to run management commands.
- Always backup your data before running bulk updates.
