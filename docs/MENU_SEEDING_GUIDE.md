# Menu Seeding Guide for Alfa Agencies

This guide explains how to seed (initialize/reset) the menu and permissions system for Alfa Agencies ERP.

## When to Use Menu Seeding
- After a fresh deployment or database reset
- When you want to reset all menu permissions to default
- When new menu items or roles are added in the code

## How Menu Seeding Works
- Menu seeding populates the database with the default menu structure and permissions for all roles (Superadmin, Admin, Biller, Picker, Packer, Delivery, Store, User, etc).
- It is managed by a Django management command in the backend.

## Steps to Seed Menus

1. **Activate your backend virtual environment**
   ```sh
   cd "E:/IMC PROJECT/Alfa_Agencies/alfa-erp-backend"
   venv/Scripts/activate
   ```

2. **Run the menu seeding command**
   ```sh
   python manage.py seed_menus --clear --assign
   ```
   - `--clear` : Removes all existing menu and permission data before seeding
   - `--assign` : Assigns default permissions to all users/roles after seeding

3. **Verify in the frontend**
   - Log in as Superadmin or Admin
   - Go to User Management > Select a user > Check menu permissions
   - The sidebar should reflect the seeded menu structure

## Customizing the Menu
- To change the default menu structure, edit the menu seeding logic in `apps/accesscontrol/management/commands/seed_menus.py`.
- To change the frontend menu config, edit `src/layout/Sidebar/menuConfig.js`.
- After code changes, re-run the seeding command to update the database.

## Troubleshooting
- If menus are missing or incorrect, always re-run the seeding command.
- Make sure you are running the command in the correct backend environment.
- Check for errors in the backend terminal output.

## References
- Backend seeding logic: `alfa-erp-backend/apps/accesscontrol/management/commands/seed_menus.py`
- Frontend menu config: `alfa_agencies_frontend/src/layout/Sidebar/menuConfig.js`
- User Management: Accessible from the sidebar in the frontend

---

**Tip:** Always backup your database before running destructive operations like `--clear`.
