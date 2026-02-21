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

class DashboardStatsView(APIView):
    """
    GET /api/analytics/dashboard-stats/
    Returns real-time dashboard statistics for today
    """
    def get(self, request):
        try:
            today = timezone.localdate()

            # ✅ Auto-snapshot: runs once per day on first dashboard load
            if not DailyHoldSnapshot.objects.filter(snapshot_date=today).exists():
                hold_count = Invoice.objects.filter(status='INVOICED').count()
                DailyHoldSnapshot.objects.create(
                    snapshot_date=today,
                    hold_count=hold_count
                )

            # Get today's fixed snapshot
            snapshot = DailyHoldSnapshot.objects.filter(snapshot_date=today).first()
            hold_invoices = snapshot.hold_count if snapshot else 0

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

            pending_invoices = max((hold_invoices + total_invoices) - completed_picking, 0)

            return Response({
                'success': True,
                'date': today.isoformat(),
                'stats': {
                    'totalInvoices': total_invoices,
                    'completedPicking': completed_picking,
                    'completedPacking': completed_packing,
                    'completedDelivery': completed_delivery,
                    'holdInvoices': hold_invoices,
                    'pendingInvoices': pending_invoices,
                }
            })
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)

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
                    # Replace with:
                    snapshot = await asyncio.to_thread(
                        lambda: DailyHoldSnapshot.objects.filter(snapshot_date=today).first()
                    )
                    hold_invoices = snapshot.hold_count if snapshot else 0

                    pending_invoices = max((hold_invoices + total_invoices) - completed_picking, 0)

                    data = {
                        'date': today.isoformat(),
                        'stats': {
                            'totalInvoices': total_invoices,
                            'completedPicking': completed_picking,
                            'completedPacking': completed_packing,
                            'completedDelivery': completed_delivery,
                            'holdInvoices': hold_invoices,
                            'pendingInvoices': pending_invoices,
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