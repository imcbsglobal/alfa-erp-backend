from django.test import TestCase
from apps.accounts.models import User


class RoleTests(TestCase):
    def test_delivery_role_exists_and_user_creation(self):
        # Ensure DELIVERY is present in the Role choices
        self.assertIn(('DELIVERY', 'Delivery'), list(User.Role.choices))

        # Create a user with DELIVERY role and verify
        user = User.objects.create_user(email='delivery@example.com', password='password123', role=User.Role.DELIVERY)
        self.assertEqual(user.role, User.Role.DELIVERY)
        self.assertEqual(user.get_role_display(), 'Delivery')
