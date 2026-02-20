from django.http import StreamingHttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import json
import asyncio
from apps.sales.models import Invoice, PickingSession, PackingSession, DeliverySession
from apps.accounts.models import User
from apps.analytics.models import DailyHoldSnapshot


def get_hold_invoices_count():
    """
    Formula:
    Hold Invoices = (Yesterday's snapshot + Today's total invoices) - Today's completed picking
    Day 1 fallback: (0 + Today's total invoices) - Today's completed picking
    """
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    # Get yesterday's snapshot (0 if Day 1)
    yesterday_snapshot = DailyHoldSnapshot.objects.filter(
        snapshot_date=yesterday
    ).first()
    yesterday_hold = yesterday_snapshot.hold_count if yesterday_snapshot else 0

    # Today's total invoices
    today_total = Invoice.objects.filter(
        created_at__date=today
    ).count()

    # Today's completed picking
    today_picked = PickingSession.objects.filter(
        start_time__date=today,
        picking_status='PICKED'
    ).count()

    # Formula
    hold_invoices = max((yesterday_hold + today_total) - today_picked, 0)

    # Save/update today's snapshot
    DailyHoldSnapshot.objects.update_or_create(
        snapshot_date=today,
        defaults={'hold_count': hold_invoices}
    )

    return hold_invoices


class DashboardStatsView(APIView):
    """
    GET /api/analytics/dashboard-stats/
    Returns real-time dashboard statistics for today
    """
    def get(self, request):
        try:
            today = timezone.localdate()

            total_invoices = Invoice.objects.filter(
                created_at__date=today
            ).count()

            completed_picking = PickingSession.objects.filter(
                start_time__date=today,
                picking_status='PICKED'
            ).count()

            completed_packing = PackingSession.objects.filter(
                start_time__date=today,
                packing_status='PACKED'
            ).count()

            completed_delivery = DeliverySession.objects.filter(
                start_time__date=today,
                delivery_status='DELIVERED'
            ).count()

            hold_invoices = get_hold_invoices_count()

            return Response({
                'success': True,
                'date': today.isoformat(),
                'stats': {
                    'totalInvoices': total_invoices,
                    'completedPicking': completed_picking,
                    'completedPacking': completed_packing,
                    'completedDelivery': completed_delivery,
                    'holdInvoices': hold_invoices
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardStatsSSEView(View):
    """
    GET /api/analytics/dashboard-stats-stream/
    Server-Sent Events endpoint for real-time dashboard updates
    """

    async def get(self, request):
        token = request.GET.get('token')
        if not token:
            from django.http import JsonResponse
            return JsonResponse({'error': 'Authentication token required'}, status=401)

        # Verify token - all DB calls wrapped in sync_to_async
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from asgiref.sync import sync_to_async
            from apps.accounts.models import User

            # Decode token (no DB call, safe in async)
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            # DB call must use sync_to_async
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

                    total_invoices = await asyncio.to_thread(
                        lambda: Invoice.objects.filter(created_at__date=today).count()
                    )
                    completed_picking = await asyncio.to_thread(
                        lambda: PickingSession.objects.filter(
                            start_time__date=today,
                            picking_status='PICKED'
                        ).count()
                    )
                    completed_packing = await asyncio.to_thread(
                        lambda: PackingSession.objects.filter(
                            start_time__date=today,
                            packing_status='PACKED'
                        ).count()
                    )
                    completed_delivery = await asyncio.to_thread(
                        lambda: DeliverySession.objects.filter(
                            start_time__date=today,
                            delivery_status='DELIVERED'
                        ).count()
                    )
                    hold_invoices = await asyncio.to_thread(get_hold_invoices_count)

                    data = {
                        'date': today.isoformat(),
                        'stats': {
                            'totalInvoices': total_invoices,
                            'completedPicking': completed_picking,
                            'completedPacking': completed_packing,
                            'completedDelivery': completed_delivery,
                            'holdInvoices': hold_invoices
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