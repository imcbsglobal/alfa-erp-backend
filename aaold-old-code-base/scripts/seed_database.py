"""
Database seeder script.
Populate database with initial data for testing.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User, Role
from apps.hrm.models import Department
from apps.inventory.models import Product
from apps.sales.models import Customer
from apps.finance.models import Account


def create_roles():
    """Create default roles."""
    roles_data = [
        {
            'name': 'Administrator',
            'code': 'ADMIN',
            'description': 'Full system access',
            'permissions': {
                'users': ['create', 'read', 'update', 'delete'],
                'inventory': ['create', 'read', 'update', 'delete'],
                'sales': ['create', 'read', 'update', 'delete'],
                'finance': ['create', 'read', 'update', 'delete'],
                'hrm': ['create', 'read', 'update', 'delete'],
            }
        },
        {
            'name': 'Manager',
            'code': 'MANAGER',
            'description': 'Management access',
            'permissions': {
                'users': ['read'],
                'inventory': ['read', 'update'],
                'sales': ['create', 'read', 'update'],
                'hrm': ['read', 'update'],
            }
        },
        {
            'name': 'Finance Manager',
            'code': 'FINANCE',
            'description': 'Finance department access',
            'permissions': {
                'finance': ['create', 'read', 'update', 'delete'],
                'sales': ['read'],
            }
        },
        {
            'name': 'Sales Representative',
            'code': 'SALES',
            'description': 'Sales operations',
            'permissions': {
                'sales': ['create', 'read', 'update'],
                'inventory': ['read'],
            }
        },
        {
            'name': 'Inventory Manager',
            'code': 'INVENTORY',
            'description': 'Inventory management',
            'permissions': {
                'inventory': ['create', 'read', 'update', 'delete'],
            }
        },
    ]
    
    print("Creating roles...")
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults=role_data
        )
        if created:
            print(f"✓ Created role: {role.name}")
        else:
            print(f"- Role already exists: {role.name}")


def create_users():
    """Create default users."""
    print("\nCreating users...")
    
    # Admin user
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@erp.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        admin_role = Role.objects.get(code='ADMIN')
        admin.roles.add(admin_role)
        print("✓ Created admin user (username: admin, password: admin123)")
    else:
        print("- Admin user already exists")
    
    # Manager user
    manager, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@erp.com',
            'first_name': 'John',
            'last_name': 'Manager',
        }
    )
    if created:
        manager.set_password('manager123')
        manager.save()
        manager_role = Role.objects.get(code='MANAGER')
        manager.roles.add(manager_role)
        print("✓ Created manager user (username: manager, password: manager123)")
    else:
        print("- Manager user already exists")


def create_departments():
    """Create sample departments."""
    departments_data = [
        {'name': 'Sales', 'code': 'SALES', 'description': 'Sales Department'},
        {'name': 'Finance', 'code': 'FIN', 'description': 'Finance Department'},
        {'name': 'IT', 'code': 'IT', 'description': 'Information Technology'},
        {'name': 'HR', 'code': 'HR', 'description': 'Human Resources'},
    ]
    
    print("\nCreating departments...")
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
        if created:
            print(f"✓ Created department: {dept.name}")
        else:
            print(f"- Department already exists: {dept.name}")


def create_products():
    """Create sample products."""
    products_data = [
        {
            'name': 'Laptop',
            'sku': 'LAP-001',
            'description': '15-inch business laptop',
            'unit_price': 999.99,
            'stock_quantity': 50,
            'reorder_level': 10,
        },
        {
            'name': 'Mouse',
            'sku': 'MSE-001',
            'description': 'Wireless optical mouse',
            'unit_price': 29.99,
            'stock_quantity': 200,
            'reorder_level': 50,
        },
        {
            'name': 'Keyboard',
            'sku': 'KBD-001',
            'description': 'Mechanical keyboard',
            'unit_price': 79.99,
            'stock_quantity': 100,
            'reorder_level': 20,
        },
    ]
    
    print("\nCreating products...")
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            sku=product_data['sku'],
            defaults=product_data
        )
        if created:
            print(f"✓ Created product: {product.name}")
        else:
            print(f"- Product already exists: {product.name}")


def create_customers():
    """Create sample customers."""
    customers_data = [
        {
            'name': 'Acme Corporation',
            'email': 'contact@acme.com',
            'phone': '+1234567890',
            'company': 'Acme Corp',
            'address': '123 Business Street',
        },
        {
            'name': 'Tech Solutions Inc',
            'email': 'info@techsolutions.com',
            'phone': '+1234567891',
            'company': 'Tech Solutions',
            'address': '456 Tech Avenue',
        },
    ]
    
    print("\nCreating customers...")
    for customer_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults=customer_data
        )
        if created:
            print(f"✓ Created customer: {customer.name}")
        else:
            print(f"- Customer already exists: {customer.name}")


def create_accounts():
    """Create sample finance accounts."""
    accounts_data = [
        {
            'name': 'Cash Account',
            'account_number': '1001',
            'account_type': 'ASSET',
            'balance': 10000.00,
        },
        {
            'name': 'Revenue Account',
            'account_number': '4001',
            'account_type': 'REVENUE',
            'balance': 0.00,
        },
    ]
    
    print("\nCreating accounts...")
    for account_data in accounts_data:
        account, created = Account.objects.get_or_create(
            account_number=account_data['account_number'],
            defaults=account_data
        )
        if created:
            print(f"✓ Created account: {account.name}")
        else:
            print(f"- Account already exists: {account.name}")


def main():
    """Run all seeder functions."""
    print("=" * 50)
    print("Database Seeder")
    print("=" * 50)
    
    try:
        create_roles()
        create_users()
        create_departments()
        create_products()
        create_customers()
        create_accounts()
        
        print("\n" + "=" * 50)
        print("Seeding completed successfully!")
        print("=" * 50)
        print("\nDefault login credentials:")
        print("- Admin: username=admin, password=admin123")
        print("- Manager: username=manager, password=manager123")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
