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
            cleared_counts = {}
            
            if table_name == 'all':
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
    SUPERADMIN ONLY
    """
    permission_classes = [SuperAdminOnlyPermission]
    
    def post(self, request):
        try:
            with connection.cursor() as cursor:
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

    PERMANENTLY DELETE data from database tables.
    When deleting session tables (picking/packing/delivery), the related invoices
    are also reset to their previous status so they disappear from those management pages.

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
                print(f"🗓️ Deleting data from {from_dt} to {to_dt} (inclusive)")
            except ValueError:
                return Response({
                    "success": False,
                    "message": "Invalid date format. Use YYYY-MM-DD"
                }, status=status.HTTP_400_BAD_REQUEST)

        try:
            deleted_counts = {}

            def get_queryset(model, date_field='created_at'):
                """Build a filtered queryset based on optional date range."""
                qs = model.objects.all()
                if from_date and to_date:
                    from django.utils import timezone as tz
                    from datetime import datetime
                    from django.db.models import DateTimeField, DateField

                    field = model._meta.get_field(date_field)
                    if isinstance(field, DateTimeField):
                        from_dt = tz.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
                        to_dt = tz.make_aware(datetime.strptime(to_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
                        qs = qs.filter(**{
                            f'{date_field}__gte': from_dt,
                            f'{date_field}__lte': to_dt
                        })
                    else:
                        qs = qs.filter(**{
                            f'{date_field}__gte': from_date,
                            f'{date_field}__lte': to_date
                        })
                    print(f"  Filtering {model.__name__} by {date_field} between {from_date} and {to_date}")
                elif from_date:
                    qs = qs.filter(**{f'{date_field}__gte': from_date})
                elif to_date:
                    qs = qs.filter(**{f'{date_field}__lte': to_date})
                else:
                    print(f"  Deleting ALL {model.__name__} records (no date filter)")
                return qs

            with transaction.atomic():

                # ------------------------------------------------------------------ #
                #  PICKING SESSIONS                                                   #
                #  Delete sessions + delete all related invoices (and their items,   #
                #  returns, packing/delivery sessions) that were in PICKING status   #
                # ------------------------------------------------------------------ #
                if table_name in ('picking_sessions', 'all'):
                    picking_qs = get_queryset(PickingSession, 'start_time')
                    picking_invoice_ids = list(picking_qs.values_list('invoice_id', flat=True))

                    deleted_counts['picking_sessions'] = picking_qs.count()
                    picking_qs.delete()

                    # Delete all invoices that were in PICKING status (cascade removes
                    # their items, returns, and any remaining packing/delivery sessions)
                    invoices_to_delete = Invoice.objects.filter(
                        id__in=picking_invoice_ids,
                        status__in=['PICKING', 'PICKED']
                    )
                    deleted_counts['invoices_deleted_from_picking'] = invoices_to_delete.count()
                    invoices_to_delete.delete()
                    print(f"  🗑️  Deleted {deleted_counts['invoices_deleted_from_picking']} PICKING invoices")

                    cache.delete('cleared_picking_sessions')

                # ------------------------------------------------------------------ #
                #  PACKING SESSIONS                                                   #
                #  Delete sessions + delete all related invoices (PACKING or PACKED) #
                #  and their items, returns, delivery sessions                        #
                # ------------------------------------------------------------------ #
                if table_name in ('packing_sessions', 'all'):
                    packing_qs = get_queryset(PackingSession, 'start_time')
                    packing_invoice_ids = list(packing_qs.values_list('invoice_id', flat=True))

                    deleted_counts['packing_sessions'] = packing_qs.count()
                    packing_qs.delete()

                    # Delete invoices that were in PACKING or PACKED status
                    invoices_to_delete = Invoice.objects.filter(
                        id__in=packing_invoice_ids,
                        status__in=['PACKING', 'PACKED']
                    )
                    deleted_counts['invoices_deleted_from_packing'] = invoices_to_delete.count()
                    invoices_to_delete.delete()
                    print(f"  🗑️  Deleted {deleted_counts['invoices_deleted_from_packing']} PACKING/PACKED invoices")

                    cache.delete('cleared_packing_sessions')

                # ------------------------------------------------------------------ #
                #  DELIVERY SESSIONS                                                  #
                #  Delete sessions + delete all related invoices (DISPATCHED,        #
                #  IN_TRANSIT, DELIVERED) and their items, returns                   #
                # ------------------------------------------------------------------ #
                if table_name in ('delivery_sessions', 'all'):
                    delivery_qs = get_queryset(DeliverySession, 'start_time')
                    delivery_invoice_ids = list(delivery_qs.values_list('invoice_id', flat=True))

                    deleted_counts['delivery_sessions'] = delivery_qs.count()
                    delivery_qs.delete()

                    # Delete invoices that were in DISPATCHED, IN_TRANSIT or DELIVERED status
                    invoices_to_delete = Invoice.objects.filter(
                        id__in=delivery_invoice_ids,
                        status__in=['DISPATCHED', 'IN_TRANSIT', 'DELIVERED']
                    )
                    deleted_counts['invoices_deleted_from_delivery'] = invoices_to_delete.count()
                    invoices_to_delete.delete()
                    print(f"  🗑️  Deleted {deleted_counts['invoices_deleted_from_delivery']} DISPATCHED/IN_TRANSIT/DELIVERED invoices")

                    cache.delete('cleared_delivery_sessions')

                # ------------------------------------------------------------------ #
                #  INVOICES (+ all related data)                                     #
                # ------------------------------------------------------------------ #
                if table_name == 'invoices':
                    invoices_to_delete = get_queryset(Invoice, 'invoice_date')
                    invoice_ids = list(invoices_to_delete.values_list('id', flat=True))

                    total_invoices = Invoice.objects.count()
                    print(f"📊 Total invoices in DB: {total_invoices}")
                    print(f"🔍 Invoices matching date filter: {len(invoice_ids)}")

                    # Delete all related sessions and sub-records for these invoices
                    deleted_counts['delivery_sessions'] = DeliverySession.objects.filter(invoice_id__in=invoice_ids).count()
                    DeliverySession.objects.filter(invoice_id__in=invoice_ids).delete()

                    deleted_counts['packing_sessions'] = PackingSession.objects.filter(invoice_id__in=invoice_ids).count()
                    PackingSession.objects.filter(invoice_id__in=invoice_ids).delete()

                    deleted_counts['picking_sessions'] = PickingSession.objects.filter(invoice_id__in=invoice_ids).count()
                    PickingSession.objects.filter(invoice_id__in=invoice_ids).delete()

                    deleted_counts['invoice_returns'] = InvoiceReturn.objects.filter(invoice_id__in=invoice_ids).count()
                    InvoiceReturn.objects.filter(invoice_id__in=invoice_ids).delete()

                    deleted_counts['invoice_items'] = InvoiceItem.objects.filter(invoice_id__in=invoice_ids).count()
                    InvoiceItem.objects.filter(invoice_id__in=invoice_ids).delete()

                    deleted_counts['invoices'] = invoices_to_delete.count()
                    invoices_to_delete.delete()

                    cache.delete('cleared_invoices')
                    cache.delete('cleared_picking_sessions')
                    cache.delete('cleared_packing_sessions')
                    cache.delete('cleared_delivery_sessions')

                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    if len(invoice_ids) == 0 and (from_date or to_date):
                        message = f"⚠️ No invoices found with invoice_date{date_info}. Check your date range."
                    else:
                        message = f"✅ Invoices{date_info} and all related data PERMANENTLY DELETED"

                # ------------------------------------------------------------------ #
                #  ALL DATA                                                           #
                # ------------------------------------------------------------------ #
                elif table_name == 'all':
                    # Sessions were already deleted above with status resets.
                    # Now handle invoice_returns, invoice_items, invoices, and master data.

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

                    cache.clear()

                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    message = f"✅ ALL DATA{date_info} PERMANENTLY DELETED FROM DATABASE"

                # ------------------------------------------------------------------ #
                #  MASTER DATA TABLES (no invoice-status side-effects needed)        #
                # ------------------------------------------------------------------ #
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

                elif table_name not in ('picking_sessions', 'packing_sessions', 'delivery_sessions'):
                    # table_name is something unrecognised
                    return Response({
                        "success": False,
                        "message": f"Invalid table name: {table_name}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                else:
                    # picking/packing/delivery_sessions — message not set yet
                    date_info = f" from {from_date} to {to_date}" if from_date and to_date else ""
                    labels = {
                        'picking_sessions': 'Picking Sessions',
                        'packing_sessions': 'Packing Sessions',
                        'delivery_sessions': 'Delivery Sessions',
                    }
                    message = f"✅ {labels[table_name]}{date_info} PERMANENTLY DELETED (related invoices reset to previous status)"

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