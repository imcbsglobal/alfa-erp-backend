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
    
    Clear data from frontend view only (does NOT delete from database)
    Returns current counts without modifying the database
    SUPERADMIN ONLY
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    def post(self, request):
        table_name = request.data.get('table_name', 'all')
        
        try:
            # Get current counts without deleting anything
            cleared_counts = {}
            
            if table_name == 'all':
                cleared_counts['delivery_sessions'] = DeliverySession.objects.count()
                cleared_counts['packing_sessions'] = PackingSession.objects.count()
                cleared_counts['picking_sessions'] = PickingSession.objects.count()
                cleared_counts['invoice_returns'] = InvoiceReturn.objects.count()
                cleared_counts['invoice_items'] = InvoiceItem.objects.count()
                cleared_counts['invoices'] = Invoice.objects.count()
                cleared_counts['customers'] = Customer.objects.count()
                cleared_counts['salesmen'] = Salesman.objects.count()
                cleared_counts['couriers'] = Courier.objects.count()
                
                message = "All data cleared from view (database unchanged)"
                
            elif table_name == 'invoices':
                cleared_counts['invoices'] = Invoice.objects.count()
                cleared_counts['invoice_items'] = InvoiceItem.objects.count()
                message = "Invoices cleared from view (database unchanged)"
                
            elif table_name == 'customers':
                cleared_counts['customers'] = Customer.objects.count()
                message = "Customers cleared from view (database unchanged)"
                
            elif table_name == 'salesmen':
                cleared_counts['salesmen'] = Salesman.objects.count()
                message = "Salesmen cleared from view (database unchanged)"
                
            elif table_name == 'couriers':
                cleared_counts['couriers'] = Courier.objects.count()
                message = "Couriers cleared from view (database unchanged)"
                
            elif table_name == 'sessions':
                # Keep this for backward compatibility
                cleared_counts['delivery_sessions'] = DeliverySession.objects.count()
                cleared_counts['packing_sessions'] = PackingSession.objects.count()
                cleared_counts['picking_sessions'] = PickingSession.objects.count()
                message = "Sessions cleared from view (database unchanged)"
                
            elif table_name == 'picking_sessions':
                cleared_counts['picking_sessions'] = PickingSession.objects.count()
                message = "Picking sessions cleared from view (database unchanged)"
                
            elif table_name == 'packing_sessions':
                cleared_counts['packing_sessions'] = PackingSession.objects.count()
                message = "Packing sessions cleared from view (database unchanged)"
                
            elif table_name == 'delivery_sessions':
                cleared_counts['delivery_sessions'] = DeliverySession.objects.count()
                message = "Delivery sessions cleared from view (database unchanged)"
                
            elif table_name == 'users':
                cleared_counts['users'] = User.objects.exclude(role='SUPERADMIN').count()
                message = "Users cleared from view (database unchanged)"
                
            elif table_name == 'departments':
                cleared_counts['departments'] = Department.objects.count()
                message = "Departments cleared from view (database unchanged)"
                
            elif table_name == 'job_titles':
                cleared_counts['job_titles'] = JobTitle.objects.count()
                message = "Job titles cleared from view (database unchanged)"
                
            else:
                return Response({
                    "success": False,
                    "message": f"Invalid table name: {table_name}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                "success": True,
                "message": message,
                "deleted_counts": cleared_counts,
                "note": "Data cleared from frontend view only. Database remains unchanged."
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error clearing view: {str(e)}"
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
