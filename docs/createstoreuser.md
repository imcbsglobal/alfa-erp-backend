# `createstoreuser` Management Command

Create store/operational users (picker/packer/driver/billing) interactively or non-interactively.

Location:
- `apps/accounts/management/commands/createstoreuser.py`

Purpose:
- Similar to Django's `createsuperuser`, but prompts to pick a role from available `User.Role` choices and optionally assign department and job title.

Usage:

Interactive (recommended):

```bash
python manage.py createstoreuser
```

You'll be prompted for:
- Email (validated)
- Role (select from a numbered list)
- Name (optional)
- Password (entered twice)
- Optionally assign a Department and Job Title from active lists

Non-interactive (automation):

```bash
python manage.py createstoreuser --email picker@company.com --role PICKER --name "John Picker" --noinput
```

Notes:
- When using `--noinput`, `--email` and `--role` are required. The command currently creates a user with no usable password when run with `--noinput` (password set to unusable). For automated workflows you can either:
  - Set the password later via administrative tooling or a script (`manage.py changepassword`), or
  - Modify the command to accept a `--password` argument (recommended for CI/automation) — see *Future improvements* below.

Available roles (as of this project): `ADMIN`, `USER`, `SUPERADMIN`, `PICKER`, `PACKER`, `DRIVER`, `DELIVERY`, `BILLING`.

Examples:

Interactive example session:

```
$ python manage.py createstoreuser

Email address: picker@alfa.com

Available roles:
  1. Admin (ADMIN)
  2. User (USER)
  3. Super Admin (SUPERADMIN)
  4. Picker (PICKER)
  5. Packer (PACKER)
  6. Driver (DRIVER)
  7. Delivery (DELIVERY)
  8. Billing (BILLING)

Select role (1-8): 4
Name (optional, press Enter to skip): John Picker
Password:
Password (again):
Do you want to assign a department? (y/N): n
Do you want to assign a job title? (y/N): n

Successfully created user:
  Email: picker@alfa.com
  Role: Picker
  Name: John Picker
  Department: (none)
  Job Title: (none)
```

Non-interactive example:

```
# Creates user with no usable password (automated provisioning)
python manage.py createstoreuser --email picker@company.com --role PICKER --noinput
```

Future improvements:
- Add `--password` (and/or `--set-password-from-env`) to allow non-interactive password setting.
- Optionally add flags to create groups or assign permissions at create time.

If you want, I can update the command to accept `--password` for secure automation and add tests for the command. Want me to do that?
