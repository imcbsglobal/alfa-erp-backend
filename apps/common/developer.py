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
from django.core.cache import cache
from django.utils import timezone

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
    Stores IDs in cache to hide them from list views
    SUPERADMIN ONLY
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    CACHE_TIMEOUT = 24 * 60 * 60  # 24 hours
    
    def post(self, request):
        table_name = request.data.get('table_name', 'all')
        
        try:
            # Get current counts and store IDs in cache to hide them
            cleared_counts = {}
            
            if table_name == 'all':
                # Store all IDs in cache
                delivery_ids = list(DeliverySession.objects.values_list('id', flat=True))
                packing_ids = list(PackingSession.objects.values_list('id', flat=True))
                picking_ids = list(PickingSession.objects.values_list('id', flat=True))
                invoice_ids = list(Invoice.objects.values_list('id', flat=True))
                customer_ids = list(Customer.objects.values_list('id', flat=True))
                salesman_ids = list(Salesman.objects.values_list('id', flat=True))
                courier_ids = list(Courier.objects.values_list('courier_id', flat=True))
                
                cache.set('cleared_delivery_sessions', delivery_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_packing_sessions', packing_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_picking_sessions', picking_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_invoices', invoice_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_customers', customer_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_salesmen', salesman_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_couriers', courier_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['delivery_sessions'] = len(delivery_ids)
                cleared_counts['packing_sessions'] = len(packing_ids)
                cleared_counts['picking_sessions'] = len(picking_ids)
                cleared_counts['invoice_returns'] = InvoiceReturn.objects.count()
                cleared_counts['invoice_items'] = InvoiceItem.objects.count()
                cleared_counts['invoices'] = len(invoice_ids)
                cleared_counts['customers'] = len(customer_ids)
                cleared_counts['salesmen'] = len(salesman_ids)
                cleared_counts['couriers'] = len(courier_ids)
                
                message = "All data cleared from view (database unchanged)"
                
            elif table_name == 'invoices':
                invoice_ids = list(Invoice.objects.values_list('id', flat=True))
                cache.set('cleared_invoices', invoice_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['invoices'] = len(invoice_ids)
                cleared_counts['invoice_items'] = InvoiceItem.objects.count()
                message = "Invoices cleared from view (database unchanged)"
                
            elif table_name == 'customers':
                customer_ids = list(Customer.objects.values_list('id', flat=True))
                cache.set('cleared_customers', customer_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['customers'] = len(customer_ids)
                message = "Customers cleared from view (database unchanged)"
                
            elif table_name == 'salesmen':
                salesman_ids = list(Salesman.objects.values_list('id', flat=True))
                cache.set('cleared_salesmen', salesman_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['salesmen'] = len(salesman_ids)
                message = "Salesmen cleared from view (database unchanged)"
                
            elif table_name == 'couriers':
                courier_ids = list(Courier.objects.values_list('courier_id', flat=True))
                cache.set('cleared_couriers', courier_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['couriers'] = len(courier_ids)
                message = "Couriers cleared from view (database unchanged)"
                
            elif table_name == 'sessions':
                # Keep this for backward compatibility
                delivery_ids = list(DeliverySession.objects.values_list('id', flat=True))
                packing_ids = list(PackingSession.objects.values_list('id', flat=True))
                picking_ids = list(PickingSession.objects.values_list('id', flat=True))
                
                cache.set('cleared_delivery_sessions', delivery_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_packing_sessions', packing_ids, self.CACHE_TIMEOUT)
                cache.set('cleared_picking_sessions', picking_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['delivery_sessions'] = len(delivery_ids)
                cleared_counts['packing_sessions'] = len(packing_ids)
                cleared_counts['picking_sessions'] = len(picking_ids)
                message = "Sessions cleared from view (database unchanged)"
                
            elif table_name == 'picking_sessions':
                picking_ids = list(PickingSession.objects.values_list('id', flat=True))
                cache.set('cleared_picking_sessions', picking_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['picking_sessions'] = len(picking_ids)
                message = "Picking sessions cleared from view (database unchanged)"
                
            elif table_name == 'packing_sessions':
                packing_ids = list(PackingSession.objects.values_list('id', flat=True))
                cache.set('cleared_packing_sessions', packing_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['packing_sessions'] = len(packing_ids)
                message = "Packing sessions cleared from view (database unchanged)"
                
            elif table_name == 'delivery_sessions':
                delivery_ids = list(DeliverySession.objects.values_list('id', flat=True))
                cache.set('cleared_delivery_sessions', delivery_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['delivery_sessions'] = len(delivery_ids)
                message = "Delivery sessions cleared from view (database unchanged)"
                
            elif table_name == 'users':
                user_ids = list(User.objects.exclude(role='SUPERADMIN').values_list('id', flat=True))
                cache.set('cleared_users', user_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['users'] = len(user_ids)
                message = "Users cleared from view (database unchanged)"
                
            elif table_name == 'departments':
                dept_ids = list(Department.objects.values_list('id', flat=True))
                cache.set('cleared_departments', dept_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['departments'] = len(dept_ids)
                message = "Departments cleared from view (database unchanged)"
                
            elif table_name == 'job_titles':
                job_ids = list(JobTitle.objects.values_list('id', flat=True))
                cache.set('cleared_job_titles', job_ids, self.CACHE_TIMEOUT)
                
                cleared_counts['job_titles'] = len(job_ids)
                message = "Job titles cleared from view (database unchanged)"
                
            else:
                return Response({
                    "success": False,
                    "message": f"Invalid table name: {table_name}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Also update timestamp for when data was cleared
            cache.set(f'cleared_{table_name}_timestamp', timezone.now().isoformat(), self.CACHE_TIMEOUT)
            
            return Response({
                "success": True,
                "message": message,
                "deleted_counts": cleared_counts,
                "note": "Data cleared from frontend view only. Database remains unchanged. Data will be hidden for 24 hours."
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error clearing view: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TableStatsView(APIView):
    """
    GET /api/developer/table-stats/
    
    Get actual record counts for all tables from database
    SUPERADMIN ONLY
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    def get(self, request):
        try:
            # Return ACTUAL database counts (not cached/virtual counts)
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


class TruncateTableView(APIView):
    """
    POST /api/developer/truncate-table/
    
    PERMANENTLY DELETE data from database tables (TRUNCATE)
    This is irreversible and will delete all data from specified tables
    SUPERADMIN ONLY - EXTREMELY DANGEROUS
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    def post(self, request):
        table_name = request.data.get('table_name')
        confirm_password = request.data.get('confirm_password')
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        
        if not table_name:
            return Response({
                "success": False,
                "message": "Table name is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify user password for extra security
        if not request.user.check_password(confirm_password):
            return Response({
                "success": False,
                "message": "Invalid password. Password confirmation required for truncate operations."
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate date range if provided
        if from_date and to_date:
            try:
                from datetime import datetime
                from_dt = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_dt = datetime.strptime(to_date, '%Y-%m-%d').date()
                if from_dt > to_dt:
                    return Response({
                        "success": False,
                        "message": "From date cannot be after to date"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Log the date range for debugging
                print(f"🗓️ Deleting data from {from_dt} to {to_dt} (inclusive)")
                print(f"📅 This includes all data created on: {from_dt}, ..., {to_dt}")
                
            except ValueError:
                return Response({
                    "success": False,
                    "message": "Invalid date format. Use YYYY-MM-DD"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            deleted_counts = {}
            
            # Helper function to apply date filter
            def get_queryset(model, date_field='created_at'):
                qs = model.objects.all()
                if from_date and to_date:
                    # For DateField, use direct comparison
                    # For DateTimeField, add timezone awareness
                    from django.utils import timezone
                    from datetime import datetime
                    
                    # Check if field is DateTimeField or DateField
                    field = model._meta.get_field(date_field)
                    from django.db.models import DateTimeField, DateField
                    
                    if isinstance(field, DateTimeField):
                        # Convert to timezone-aware datetime
                        from_dt = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
                        to_dt = timezone.make_aware(datetime.strptime(to_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
                        filter_kwargs = {
                            f'{date_field}__gte': from_dt,
                            f'{date_field}__lte': to_dt
                        }
                    else:
                        # DateField - use direct date comparison
                        filter_kwargs = {
                            f'{date_field}__gte': from_date,
                            f'{date_field}__lte': to_date
                        }
                    
                    qs = qs.filter(**filter_kwargs)
                    print(f"  Filtering {model.__name__} by {date_field} between {from_date} and {to_date} (inclusive)")
                elif from_date:
                    qs = qs.filter(**{f'{date_field}__gte': from_date})
                    print(f"  Filtering {model.__name__} by {date_field} >= {from_date}")
                elif to_date:
                    qs = qs.filter(**{f'{date_field}__lte': to_date})
                    print(f"  Filtering {model.__name__} by {date_field} <= {to_date}")
                else:
                    print(f"  Deleting ALL {model.__name__} records (no date filter)")
                return qs
            
            with transaction.atomic():
                if table_name == 'all':
                    # Delete all data (CASCADE deletes related records automatically)
                    deleted_counts['delivery_sessions'] = get_queryset(DeliverySession, 'start_time').count()
                    get_queryset(DeliverySession, 'start_time').delete()
                    
                    deleted_counts['packing_sessions'] = get_queryset(PackingSession, 'start_time').count()
                    get_queryset(PackingSession, 'start_time').delete()
                    
                    deleted_counts['picking_sessions'] = get_queryset(PickingSession, 'start_time').count()
                    get_queryset(PickingSession, 'start_time').delete()
                    
                    deleted_counts['invoice_returns'] = get_queryset(InvoiceReturn, 'returned_at').count()
                    get_queryset(InvoiceReturn, 'returned_at').delete()
                    
                    deleted_counts['invoice_items'] = InvoiceItem.objects.count()
                    InvoiceItem.objects.all().delete()
                    
                    deleted_counts['invoices'] = get_queryset(Invoice).count()
                    get_queryset(Invoice).delete()
                    
                    deleted_counts['customers'] = get_queryset(Customer).count()
                    get_queryset(Customer).delete()
                    
                    deleted_counts['salesmen'] = get_queryset(Salesman).count()
                    get_queryset(Salesman).delete()
                    
                    deleted_counts['couriers'] = get_queryset(Courier).count()
                    get_queryset(Courier).delete()
                    
                    deleted_counts['users'] = get_queryset(User).exclude(role='SUPERADMIN').count()
                    get_queryset(User).exclude(role='SUPERADMIN').delete()
                    
                    deleted_counts['departments'] = get_queryset(Department).count()
                    get_queryset(Department).delete()
                    
                    deleted_counts['job_titles'] = get_queryset(JobTitle).count()
                    get_queryset(JobTitle).delete()
                    
                    # Clear cache
                    cache.clear()
                    
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ ALL DATA{date_info} PERMANENTLY DELETED FROM DATABASE"
                    
                elif table_name == 'invoices':
                    # First get the invoices that match the date filter
                    # Use invoice_date (business date) not created_at (system date)
                    invoices_to_delete = get_queryset(Invoice, 'invoice_date')
                    invoice_ids = list(invoices_to_delete.values_list('id', flat=True))
                    
                    # Log what we found for debugging
                    total_invoices = Invoice.objects.count()
                    print(f"📊 Total invoices in DB: {total_invoices}")
                    print(f"🔍 Invoices matching date filter (by invoice_date): {len(invoice_ids)}")
                    
                    if from_date and to_date and len(invoice_ids) == 0:
                        # Show sample invoice dates to help user understand
                        sample_dates = Invoice.objects.values_list('invoice_date', flat=True)[:5]
                        print(f"📅 Sample invoice_date values: {[str(d) for d in sample_dates]}")
                    
                    # Delete related data for these specific invoices
                    deleted_counts['invoice_returns'] = InvoiceReturn.objects.filter(invoice_id__in=invoice_ids).count()
                    InvoiceReturn.objects.filter(invoice_id__in=invoice_ids).delete()
                    
                    deleted_counts['invoice_items'] = InvoiceItem.objects.filter(invoice_id__in=invoice_ids).count()
                    InvoiceItem.objects.filter(invoice_id__in=invoice_ids).delete()
                    
                    deleted_counts['invoices'] = invoices_to_delete.count()
                    invoices_to_delete.delete()
                    
                    # Clear related sessions
                    deleted_counts['delivery_sessions'] = get_queryset(DeliverySession, 'start_time').count()
                    get_queryset(DeliverySession, 'start_time').delete()
                    
                    deleted_counts['packing_sessions'] = get_queryset(PackingSession, 'start_time').count()
                    get_queryset(PackingSession, 'start_time').delete()
                    
                    deleted_counts['picking_sessions'] = get_queryset(PickingSession, 'start_time').count()
                    get_queryset(PickingSession, 'start_time').delete()
                    
                    # Clear all cache keys
                    cache.delete('cleared_invoices')
                    cache.delete('cleared_picking_sessions')
                    cache.delete('cleared_packing_sessions')
                    cache.delete('cleared_delivery_sessions')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    
                    # Add helpful message if nothing was deleted due to date filter
                    if len(invoice_ids) == 0 and (from_date or to_date):
                        message = f"⚠️ No invoices found with invoice_date{date_info}. Check your date range - no records matched the filter."
                    else:
                        message = f"✅ Invoices{date_info} and related data PERMANENTLY DELETED"
                    
                elif table_name == 'customers':
                    deleted_counts['customers'] = get_queryset(Customer).count()
                    get_queryset(Customer).delete()
                    cache.delete('cleared_customers')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Customers{date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'salesmen':
                    deleted_counts['salesmen'] = get_queryset(Salesman).count()
                    get_queryset(Salesman).delete()
                    cache.delete('cleared_salesmen')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Salesmen{date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'couriers':
                    deleted_counts['couriers'] = get_queryset(Courier).count()
                    get_queryset(Courier).delete()
                    cache.delete('cleared_couriers')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Couriers{date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'picking_sessions':
                    deleted_counts['picking_sessions'] = get_queryset(PickingSession, 'start_time').count()
                    get_queryset(PickingSession, 'start_time').delete()
                    cache.delete('cleared_picking_sessions')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Picking Sessions{date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'packing_sessions':
                    deleted_counts['packing_sessions'] = get_queryset(PackingSession, 'start_time').count()
                    get_queryset(PackingSession, 'start_time').delete()
                    cache.delete('cleared_packing_sessions')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Packing Sessions{date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'delivery_sessions':
                    deleted_counts['delivery_sessions'] = get_queryset(DeliverySession, 'start_time').count()
                    get_queryset(DeliverySession, 'start_time').delete()
                    cache.delete('cleared_delivery_sessions')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Delivery Sessions{date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'users':
                    deleted_counts['users'] = get_queryset(User).exclude(role='SUPERADMIN').count()
                    get_queryset(User).exclude(role='SUPERADMIN').delete()
                    cache.delete('cleared_users')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Users (except SUPERADMIN){date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'departments':
                    deleted_counts['departments'] = get_queryset(Department).count()
                    get_queryset(Department).delete()
                    cache.delete('cleared_departments')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Departments{date_info} PERMANENTLY DELETED"
                    
                elif table_name == 'job_titles':
                    deleted_counts['job_titles'] = get_queryset(JobTitle).count()
                    get_queryset(JobTitle).delete()
                    cache.delete('cleared_job_titles')
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ Job Titles{date_info} PERMANENTLY DELETED"
                    
                else:
                    return Response({
                        "success": False,
                        "message": f"Invalid table name: {table_name}"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                "success": True,
                "message": message,
                "deleted_counts": deleted_counts,
                "warning": "⚠️ THIS WAS A PERMANENT DELETE OPERATION - DATA CANNOT BE RECOVERED"
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error truncating table: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
