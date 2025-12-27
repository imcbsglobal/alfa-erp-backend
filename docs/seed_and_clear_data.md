# Seed and Clear Sales Data

A short reference for the sales app data helper management commands.

## seed_invoices
Create fake invoices for testing.

Usage:
- Create 20 invoices (default):
  - python manage.py seed_invoices
- Create 50 invoices:
  - python manage.py seed_invoices --count 50
- Create invoices with sessions (picking/packing/delivery):
  - python manage.py seed_invoices --count 30 --with-sessions
- Create invoices all in a specific status (e.g. INVOICED):
  - python manage.py seed_invoices --count 30 --status INVOICED
  - Supported statuses: INVOICED, PICKING, PICKED, PACKING, PACKED, DISPATCHED, DELIVERED

What it creates:
- Sample salesmen and customers
- Invoices with random statuses and priorities (LOW/MEDIUM/HIGH)
- 2–5 invoice items per invoice
- Optional picking/packing/delivery sessions

## clear_data
Clear sales-related data. Prompts for confirmation unless `--confirm` is used.

Usage:
- Clear everything (prompts):
  - python manage.py clear_data
- Clear without prompt:
  - python manage.py clear_data --confirm
- Clear only sessions:
  - python manage.py clear_data --sessions-only --confirm
- Clear only invoices and items:
  - python manage.py clear_data --invoices-only --confirm

Notes:
- The commands are located in `apps/sales/management/commands/`.
- Use with caution on production databases.
