from django.http import StreamingHttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
import json
import asyncio
from apps.sales.models import Invoice, PickingSession, PackingSession, DeliverySession
from apps.accounts.models import User
from apps.analytics.models import DailyHoldSnapshot


def get_or_create_today_snapshot(today):
    """
    Creates today's hold snapshot if it doesn't exist yet.
    HOLD = all invoices created BEFORE today that are still unpicked (status='INVOICED').
    Runs once per day automatically on first dashboard load.
    """
    snapshot, created = DailyHoldSnapshot.objects.get_or_create(
        snapshot_date=today,
        defaults={'hold_count': 0}
    )

    if created:
        hold_count = Invoice.objects.filter(
            created_at__date__lt=today,
            status='INVOICED'
        ).count()
        snapshot.hold_count = hold_count
        snapshot.save(update_fields=['hold_count'])

    return snapshot


def compute_today_stats(today):
    """Shared helper — computes all dashboard stats for today."""
    snapshot = get_or_create_today_snapshot(today)
    hold_invoices = snapshot.hold_count

    total_invoices_today = Invoice.objects.filter(created_at__date=today).count()

    completed_picking = PickingSession.objects.filter(
        end_time__date=today,
        picking_status='PICKED'
    ).count()

    completed_packing = PackingSession.objects.filter(
        end_time__date=today,
        packing_status='PACKED'
    ).count()

    completed_delivery = DeliverySession.objects.filter(
        end_time__date=today,
        delivery_status='DELIVERED'
    ).count()

    pending_invoices = max((hold_invoices + total_invoices_today) - completed_picking, 0)

    # completedHoldInvoices:
    # Hold invoices = invoices created BEFORE today (captured in snapshot).
    # "Completed today" = those hold invoices whose PickingSession was PICKED today.
    # This is the only accurate measure — checking invoice status alone would include
    # invoices processed on previous days, giving a wrong inflated count.
    completed_hold_invoices = PickingSession.objects.filter(
        end_time__date=today,
        picking_status='PICKED',
        invoice__created_at__date__lt=today,  # must be a hold invoice (pre-today)
    ).count()

    return {
        'holdInvoices': hold_invoices,
        'totalInvoices': total_invoices_today,
        'completedPicking': completed_picking,
        'completedPacking': completed_packing,
        'completedDelivery': completed_delivery,
        'pendingInvoices': pending_invoices,
        'completedHoldInvoices': completed_hold_invoices,  # ← NEW
    }


class DashboardStatsView(APIView):
    """
    GET /api/analytics/dashboard-stats/
    Returns real-time dashboard statistics for today.
    """
    def get(self, request):
        try:
            today = timezone.localdate()
            stats = compute_today_stats(today)
            return Response({
                'success': True,
                'date': today.isoformat(),
                'stats': stats,
            })
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)


class RecalculateHoldSnapshotView(APIView):
    """
    POST /api/analytics/recalculate-hold/
    SUPERADMIN only — deletes today's snapshot and rebuilds it from live data.
    Use when the hold count is wrong (e.g. after data corrections).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['SUPERADMIN']:
            return Response(
                {'success': False, 'message': 'Superadmin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            today = timezone.localdate()

            deleted_count, _ = DailyHoldSnapshot.objects.filter(
                snapshot_date=today
            ).delete()

            hold_count = Invoice.objects.filter(
                created_at__date__lt=today,
                status='INVOICED'
            ).count()

            DailyHoldSnapshot.objects.create(
                snapshot_date=today,
                hold_count=hold_count
            )

            stats = compute_today_stats(today)

            return Response({
                'success': True,
                'message': f'Hold snapshot recalculated successfully.',
                'date': today.isoformat(),
                'previous_snapshot_existed': deleted_count > 0,
                'stats': stats,
            })

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)


class DashboardStatsSSEView(View):
    """
    GET /api/analytics/dashboard-stats-stream/
    Server-Sent Events endpoint for real-time dashboard updates (every 5s).
    """

    async def get(self, request):
        token = request.GET.get('token')
        if not token:
            from django.http import JsonResponse
            return JsonResponse({'error': 'Authentication token required'}, status=401)

        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from asgiref.sync import sync_to_async

            access_token = AccessToken(token)
            user_id = access_token['user_id']

            get_user = sync_to_async(User.objects.get)
            user = await get_user(id=user_id)
            print(f"✅ SSE Auth success for user: {user}")

        except Exception as e:
            from django.http import JsonResponse
            print(f"❌ SSE Auth failed: {type(e).__name__}: {str(e)}")
            return JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)

        async def event_stream():
            while True:
                try:
                    today = timezone.localdate()

                    snapshot = await asyncio.to_thread(
                        lambda: get_or_create_today_snapshot(today)
                    )
                    hold_invoices = snapshot.hold_count

                    total_invoices_today = await asyncio.to_thread(
                        lambda: Invoice.objects.filter(created_at__date=today).count()
                    )
                    completed_picking = await asyncio.to_thread(
                        lambda: PickingSession.objects.filter(
                            end_time__date=today,
                            picking_status='PICKED'
                        ).count()
                    )
                    completed_packing = await asyncio.to_thread(
                        lambda: PackingSession.objects.filter(
                            end_time__date=today,
                            packing_status='PACKED'
                        ).count()
                    )
                    completed_delivery = await asyncio.to_thread(
                        lambda: DeliverySession.objects.filter(
                            end_time__date=today,
                            delivery_status='DELIVERED'
                        ).count()
                    )

                    # Count hold invoices cleared today (picked today, created before today)
                    completed_hold_invoices = await asyncio.to_thread(
                        lambda: PickingSession.objects.filter(
                            end_time__date=today,
                            picking_status='PICKED',
                            invoice__created_at__date__lt=today,
                        ).count()
                    )

                    pending_invoices = max(
                        (hold_invoices + total_invoices_today) - completed_picking, 0
                    )

                    data = {
                        'date': today.isoformat(),
                        'stats': {
                            'holdInvoices': hold_invoices,
                            'totalInvoices': total_invoices_today,
                            'completedPicking': completed_picking,
                            'completedPacking': completed_packing,
                            'completedDelivery': completed_delivery,
                            'pendingInvoices': pending_invoices,
                            'completedHoldInvoices': completed_hold_invoices,  # ← NEW
                        },
                        'timestamp': datetime.now().isoformat()
                    }

                    yield f"data: {json.dumps(data)}\n\n"
                    await asyncio.sleep(5)

                except Exception as e:
                    error_data = {
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    await asyncio.sleep(5)

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response


class StatusBreakdownView(APIView):
    """
    GET /api/analytics/status-breakdown/
    Returns live picking / packing / delivery counts for the dashboard donut charts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            today = timezone.localdate()

            # ── PICKING ──────────────────────────────────────────────────────
            picking_completed = PickingSession.objects.filter(
                end_time__date=today,
                picking_status='PICKED',
            ).count()

            picking_preparing = PickingSession.objects.filter(
                picking_status='PREPARING',
            ).count()

            picking_pending = Invoice.objects.filter(
                status='INVOICED',
                pickingsession__isnull=True,
            ).count()

            # ── PACKING ──────────────────────────────────────────────────────
            packing_completed = PackingSession.objects.filter(
                end_time__date=today,
                packing_status='PACKED',
            ).count()

            PACKING_ACTIVE_STATUSES = ['PENDING', 'CHECKING', 'CHECKING_DONE', 'PACKING']
            packing_preparing = PackingSession.objects.filter(
                packing_status__in=PACKING_ACTIVE_STATUSES,
            ).count()

            packing_pending = Invoice.objects.filter(
                status='PICKED',
                packingsession__isnull=True,
            ).count()

            # ── DELIVERY ─────────────────────────────────────────────────────
            delivery_completed = DeliverySession.objects.filter(
                end_time__date=today,
                delivery_status='DELIVERED',
            ).count()

            delivery_preparing = DeliverySession.objects.filter(
                delivery_status='IN_TRANSIT',
            ).count()

            delivery_pending = Invoice.objects.filter(
                status='PACKED',
                deliverysession__isnull=True,
            ).count()

            return Response({
                'success': True,
                'date': today.isoformat(),
                'breakdown': {
                    'picking': {
                        'completed': picking_completed,
                        'preparing': picking_preparing,
                        'pending':   picking_pending,
                    },
                    'packing': {
                        'completed': packing_completed,
                        'preparing': packing_preparing,
                        'pending':   packing_pending,
                    },
                    'delivery': {
                        'completed': delivery_completed,
                        'preparing': delivery_preparing,
                        'pending':   delivery_pending,
                    },
                },
            })

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)