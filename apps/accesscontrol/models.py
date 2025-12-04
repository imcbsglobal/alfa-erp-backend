"""
Menu-Based Access Control - Direct User-to-Menu Assignment
Simplified system: Users → Menus (no roles, direct assignment)
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class MenuItem(models.Model):
    """
    Navigation Menu Items for Frontend
    Represents individual menu/navbar links that can be directly assigned to users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text='Display name (e.g., Dashboard, Delivery)')
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Unique code (e.g., dashboard, delivery_management)'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='Icon class or name (e.g., fa-dashboard, IconHome)'
    )
    url = models.CharField(
        max_length=200,
        help_text='Frontend route (e.g., /dashboard, /delivery)'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text='Parent menu for nested items'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order (lower number appears first)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Direct relationship with users
    users = models.ManyToManyField(
        get_user_model(),
        through='UserMenu',
        through_fields=('menu', 'user'),
        related_name='assigned_menus',
        help_text='Users who have access to this menu'
    )
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['order', 'name']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_children(self):
        """Get child menu items"""
        return self.children.filter(is_active=True).order_by('order')

    @staticmethod
    def get_all_menu_structure():
        """
        Return the full hierarchical menu structure for all active menus.
        Useful for admins who should receive access to every menu item on login.
        """
        root_menus = MenuItem.objects.filter(parent=None, is_active=True).order_by('order')
        menu_structure = []

        for menu in root_menus:
            menu_data = {
                'id': str(menu.id),
                'name': menu.name,
                'code': menu.code,
                'icon': menu.icon,
                'url': menu.url,
                'order': menu.order,
                'children': []
            }

            children = menu.get_children()
            for child in children:
                menu_data['children'].append({
                    'id': str(child.id),
                    'name': child.name,
                    'code': child.code,
                    'icon': child.icon,
                    'url': child.url,
                    'order': child.order
                })

            menu_structure.append(menu_data)

        return menu_structure


class UserMenu(models.Model):
    """
    Direct User-to-Menu Assignment (Through Model)
    Users are assigned menus directly without roles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='menu_assignments',
        help_text='User to assign menu'
    )
    menu = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        help_text='Menu item to assign'
    )
    assigned_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menus_assigned_by_me',
        help_text='Admin who assigned this menu'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this menu assignment is active'
    )
    
    class Meta:
        db_table = 'user_menus'
        unique_together = [['user', 'menu']]
        verbose_name = 'User Menu'
        verbose_name_plural = 'User Menus'
        ordering = ['menu__order']
    
    def __str__(self):
        return f"{self.user.email} → {self.menu.name}"
    
    @staticmethod
    def get_user_menu_structure(user):
        """
        Get hierarchical menu structure for a user
        Returns nested menu with children
        """
        # Get all menu items assigned to this user (active only)
        user_menus = UserMenu.objects.filter(
            user=user,
            is_active=True,
            menu__is_active=True
        ).select_related('menu').prefetch_related('menu__children')
        
        # Get root menus (no parent)
        menu_ids = [um.menu.id for um in user_menus]
        root_menus = MenuItem.objects.filter(
            id__in=menu_ids,
            parent=None,
            is_active=True
        ).order_by('order')
        
        menu_structure = []
        
        for menu in root_menus:
            menu_data = {
                'id': str(menu.id),
                'name': menu.name,
                'code': menu.code,
                'icon': menu.icon,
                'url': menu.url,
                'order': menu.order,
                'children': []
            }
            
            # Get children that user also has access to
            children = menu.get_children().filter(id__in=menu_ids)
            if children.exists():
                for child in children:
                    menu_data['children'].append({
                        'id': str(child.id),
                        'name': child.name,
                        'code': child.code,
                        'icon': child.icon,
                        'url': child.url,
                        'order': child.order
                    })
            
            menu_structure.append(menu_data)
        
        return menu_structure
