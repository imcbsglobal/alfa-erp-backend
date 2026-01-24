"""
Developer Tools API
Restricted to SUPERADMIN only for database maintenance operations
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import connection, transaction
from django.apps import apps

from apps.sales.models import (
    Invoice, InvoiceItem, InvoiceReturn, 
    PickingSession, PackingSession, DeliverySession,
    Salesman, Customer
)
from apps.accounts.models import User, Department, JobTitle, Courier


class SuperAdminOnlyPermission(IsAuthenticated):
    """Only SUPERADMIN can access developer tools"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'SUPERADMIN'


class ClearDataView(APIView):
    """
    POST /api/developer/clear-data/
    
    Clear specific tables or all data
    SUPERADMIN ONLY
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    def post(self, request):
        table_name = request.data.get('table_name', 'all')
        
        try:
            with transaction.atomic():
                deleted_counts = {}
                
                if table_name == 'all':
                    # Clear all sales data
                    deleted_counts['delivery_sessions'] = DeliverySession.objects.all().delete()[0]
                    deleted_counts['packing_sessions'] = PackingSession.objects.all().delete()[0]
                    deleted_counts['picking_sessions'] = PickingSession.objects.all().delete()[0]
                    deleted_counts['invoice_returns'] = InvoiceReturn.objects.all().delete()[0]
                    deleted_counts['invoice_items'] = InvoiceItem.objects.all().delete()[0]
                    deleted_counts['invoices'] = Invoice.objects.all().delete()[0]
                    deleted_counts['customers'] = Customer.objects.all().delete()[0]
                    deleted_counts['salesmen'] = Salesman.objects.all().delete()[0]
                    deleted_counts['couriers'] = Courier.objects.all().delete()[0]
                    
                    message = "All data cleared successfully"
                    
                elif table_name == 'invoices':
                    # Clear all invoice-related data (cascade will handle related records)
                    deleted_counts['invoices'] = Invoice.objects.all().delete()[0]
                    message = "All invoices and related data cleared"
                    
                elif table_name == 'customers':
                    # Check if there are invoices referencing customers
                    if Invoice.objects.exists():
                        return Response({
                            "success": False,
                            "message": "Cannot delete customers while invoices exist. Clear invoices first."
                        }, status=status.HTTP_400_BAD_REQUEST)
                    deleted_counts['customers'] = Customer.objects.all().delete()[0]
                    message = "All customers cleared"
                    
                elif table_name == 'salesmen':
                    deleted_counts['salesmen'] = Salesman.objects.all().delete()[0]
                    message = "All salesmen cleared"
                    
                elif table_name == 'couriers':
                    deleted_counts['couriers'] = Courier.objects.all().delete()[0]
                    message = "All couriers cleared"
                    
                elif table_name == 'sessions':
                    # Clear all session data but keep invoices
                    deleted_counts['delivery_sessions'] = DeliverySession.objects.all().delete()[0]
                    deleted_counts['packing_sessions'] = PackingSession.objects.all().delete()[0]
                    deleted_counts['picking_sessions'] = PickingSession.objects.all().delete()[0]
                    message = "All session data cleared"
                    
                elif table_name == 'users':
                    # Don't allow deleting all users, keep superadmin
                    superadmin_count = User.objects.filter(role='SUPERADMIN').count()
                    if superadmin_count <= 1:
                        return Response({
                            "success": False,
                            "message": "Cannot delete all users. At least one SUPERADMIN must remain."
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Delete non-superadmin users
                    deleted_counts['users'] = User.objects.exclude(role='SUPERADMIN').delete()[0]
                    message = "All non-SUPERADMIN users cleared"
                    
                elif table_name == 'departments':
                    deleted_counts['departments'] = Department.objects.all().delete()[0]
                    message = "All departments cleared"
                    
                elif table_name == 'job_titles':
                    deleted_counts['job_titles'] = JobTitle.objects.all().delete()[0]
                    message = "All job titles cleared"
                    
                else:
                    return Response({
                        "success": False,
                        "message": f"Invalid table name: {table_name}"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    "success": True,
                    "message": message,
                    "deleted_counts": deleted_counts
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error clearing data: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TableStatsView(APIView):
    """
    GET /api/developer/table-stats/
    
    Get record counts for all tables
    SUPERADMIN ONLY
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    def get(self, request):
        try:
            stats = {
                'invoices': {
                    'count': Invoice.objects.count(),
                    'description': 'Sales invoices/orders'
                },
                'invoice_items': {
                    'count': InvoiceItem.objects.count(),
                    'description': 'Invoice line items'
                },
                'invoice_returns': {
                    'count': InvoiceReturn.objects.count(),
                    'description': 'Invoice return/review records'
                },
                'picking_sessions': {
                    'count': PickingSession.objects.count(),
                    'description': 'Picking workflow sessions'
                },
                'packing_sessions': {
                    'count': PackingSession.objects.count(),
                    'description': 'Packing workflow sessions'
                },
                'delivery_sessions': {
                    'count': DeliverySession.objects.count(),
                    'description': 'Delivery workflow sessions'
                },
                'customers': {
                    'count': Customer.objects.count(),
                    'description': 'Customer records'
                },
                'salesmen': {
                    'count': Salesman.objects.count(),
                    'description': 'Salesman records'
                },
                'couriers': {
                    'count': Courier.objects.count(),
                    'description': 'Courier service providers'
                },
                'users': {
                    'count': User.objects.count(),
                    'description': 'System users (staff)'
                },
                'departments': {
                    'count': Department.objects.count(),
                    'description': 'Organization departments'
                },
                'job_titles': {
                    'count': JobTitle.objects.count(),
                    'description': 'Job title definitions'
                }
            }
            
            # Calculate totals
            total_records = sum(table['count'] for table in stats.values())
            
            return Response({
                "success": True,
                "stats": stats,
                "total_records": total_records
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error fetching stats: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetSequencesView(APIView):
    """
    POST /api/developer/reset-sequences/
    
    Reset database auto-increment sequences
    Useful after clearing data to start IDs from 1 again
    SUPERADMIN ONLY
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    def post(self, request):
        try:
            with connection.cursor() as cursor:
                # Get all tables with sequences
                cursor.execute("""
                    SELECT sequence_name 
                    FROM information_schema.sequences 
                    WHERE sequence_schema = 'public'
                """)
                
                sequences = cursor.fetchall()
                reset_count = 0
                
                for seq in sequences:
                    seq_name = seq[0]
                    try:
                        cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1")
                        reset_count += 1
                    except Exception as e:
                        # Some sequences might be in use, skip them
                        pass
                
                return Response({
                    "success": True,
                    "message": f"Reset {reset_count} database sequences",
                    "reset_count": reset_count
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error resetting sequences: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
