from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Count
from datetime import datetime, date, timedelta
import json
import asyncio
from apps.sales.models import Invoice, PickingSession, PackingSession, DeliverySession
from apps.accounts.models import User

# Create your views here.

class DashboardStatsView(APIView):
    """
    GET /api/analytics/dashboard-stats/
    Returns real-time dashboard statistics for today
    """
    def get(self, request):
        try:
            today = date.today()
            
            # Get today's invoices
            today_invoices = Invoice.objects.filter(
                created_at__date=today
            )
            total_invoices = today_invoices.count()
            
            # Get today's completed sessions
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
            
            # Get hold invoices (INVOICED status from previous days)
            yesterday = today - timedelta(days=1)
            hold_invoices = Invoice.objects.filter(
                status='INVOICED',
                created_at__date__lte=yesterday
            ).count()
            
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
    Supports token authentication via query parameter
    Uses Django View instead of DRF APIView to avoid content negotiation issues
    """
    
    async def get(self, request):
        # Manual token authentication for SSE
        token = request.GET.get('token')
        if not token:
            from django.http import JsonResponse
            return JsonResponse({
                'error': 'Authentication token required'
            }, status=401)
        
        # Verify token
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({
                'error': f'Invalid token: {str(e)}'
            }, status=401)
        
        async def event_stream():
            """Async generator that yields SSE formatted data"""
            while True:
                try:
                    today = date.today()
                    
                    # Get today's invoices (async database calls)
                    total_invoices = await asyncio.to_thread(
                        lambda: Invoice.objects.filter(created_at__date=today).count()
                    )
                    
                    # Get today's completed sessions
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
                    
                    # Get hold invoices (INVOICED status from previous days)
                    yesterday = today - timedelta(days=1)
                    hold_invoices = await asyncio.to_thread(
                        lambda: Invoice.objects.filter(
                            status='INVOICED',
                            created_at__date__lte=yesterday
                        ).count()
                    )
                    
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
                    
                    # Format as SSE
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    # Wait 5 seconds before next update (async)
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
