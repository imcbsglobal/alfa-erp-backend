from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, Max, Exists, OuterRef
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, date
import requests
import logging
import sys

from apps.accesscontrol.models import UserMenu
from .models import FollowUp, PaymentAlert
from .serializers import FollowUpSerializer, PaymentAlertSerializer

logger = logging.getLogger(__name__)
User = get_user_model()

ACC_MASTER_API_URL = getattr(
    settings,
    'ACC_MASTER_API_URL',
    'https://alfasyncapi.imcbs.com/api/get-acc-master/'
)
ACC_SERVICEMASTER_API_URL = getattr(
    settings,
    'ACC_SERVICEMASTER_API_URL',
    'https://alfasyncapi.imcbs.com/api/get-servicemaster/'
)

ACC_MASTER_AGENT_API_URL = getattr(
    settings,
    'ACC_MASTER_AGENT_API_URL',
    'https://alfasyncapi.imcbs.com/api/get-acc-master-agent/'
)


def _user_has_followup_access(user):
    if not user or not user.is_authenticated:
        return False

    if getattr(user, 'role', None) in {'ADMIN', 'SUPERADMIN'}:
        return True

    return user.menu_assignments.filter(
        is_active=True,
        menu__is_active=True,
        menu__code__startswith='followup',
    ).exists()


# ══════════════════════════════════════════════════════════════
#  HELPER — fetch all AccMaster clients from the sync API
# ══════════════════════════════════════════════════════════════

def _fetch_acc_master():
    try:
        print(f"🔍 Calling: {ACC_MASTER_API_URL}")
        resp = requests.get(ACC_MASTER_API_URL, timeout=15)
        print(f"📡 Status: {resp.status_code}")
        payload = resp.json()
        clients = payload.get('data', [])
        print(f"📦 Total clients: {len(clients)}")
        filtered = [c for c in clients if c.get('super_code') in ('SUNCR', 'DEBTO')]
        print(f"✅ Filtered clients: {len(filtered)}")
        return filtered
    except Exception as e:
        print(f"❌ FAILED: {e}")
        logger.error(f"_fetch_acc_master failed: {e}")
        return []
    
def _fetch_area_map():
    """Returns {area_code: area_name}"""
    try:
        resp = requests.get(ACC_SERVICEMASTER_API_URL, timeout=15)
        data = resp.json().get('data', [])
        return {item['code']: item['name'] for item in data if item.get('code')}
    except Exception as e:
        logger.error(f"_fetch_area_map failed: {e}")
        return {}


def _fetch_agent_map():
    """Returns {agent_code: agent_name}"""
    try:
        resp = requests.get(ACC_MASTER_AGENT_API_URL, timeout=15)
        data = resp.json().get('data', [])
        return {item['code']: item['name'] for item in data if item.get('code')}
    except Exception as e:
        logger.error(f"_fetch_agent_map failed: {e}")
        return {}

# ══════════════════════════════════════════════════════════════
#  FOLLOW-UP TRACKER  (client-level aggregated view)
# ══════════════════════════════════════════════════════════════

class FollowUpTrackerAPI(APIView):
    """
    GET /api/followup/tracker/

    Returns one row per AccMaster client with outstanding balance
    and follow-up history overlaid.

    Query params:
      filter    = overdue | due_week | all   (default: all)
      search    = free text (client name, code, agent, area)
      agent     = agent code
      area      = area code
      page      = page number  (default: 1)
      page_size = items per page (default: 50)
    """
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        sys.stderr.write("🚀 TRACKER HIT\n")
        sys.stderr.flush()
        try:
            if not _user_has_followup_access(request.user):
                return Response({'detail': 'You do not have access to follow-up tracker data.'}, status=403)

            filter_type = request.query_params.get('filter', 'all')
            search      = request.query_params.get('search', '').strip().lower()
            agent       = request.query_params.get('agent', '').strip().lower()
            area        = request.query_params.get('area', '').strip().lower()
            page        = int(request.query_params.get('page', 1))
            page_size   = int(request.query_params.get('page_size', 50))

            today    = date.today()
            week_end = today + timedelta(days=7)

            # ── 1. Fetch clients from sync API ────────────────────────────
            clients = _fetch_acc_master()

            # ── 2. Fetch area & agent name lookups from sync API ─────────
            area_map  = _fetch_area_map()
            agent_map = _fetch_agent_map()

            # ── 3. Pull follow-up stats per client_code in bulk ───────────
            fu_stats = (
                FollowUp.objects
                .values('client_code')
                .annotate(
                    followup_count=Count('id'),
                    last_followup_date=Max('created_at'),
                )
            )
            fu_map = {row['client_code']: row for row in fu_stats}

            # Latest FollowUp object per client (for outcome & next date)
            all_latest_fu = {}
            for fu in FollowUp.objects.order_by('client_code', '-created_at'):
                if fu.client_code not in all_latest_fu:
                    all_latest_fu[fu.client_code] = fu

            # ── 4. Build result rows ──────────────────────────────────────
            results = []
            for client in clients:
                code       = client.get('code', '')
                name       = client.get('name', '')
                agent_code = client.get('agent') or ''
                area_code  = client.get('area')  or ''
                c_agent    = agent_map.get(agent_code, agent_code) or ''
                c_area     = area_map.get(area_code,  area_code)  or ''

                # Filters
                if agent and agent not in {agent_code.lower(), c_agent.lower()}:
                    continue
                if area and area not in {area_code.lower(), c_area.lower()}:
                    continue
                if search and not any([
                    search in name.lower(),
                    search in code.lower(),
                    search in c_agent.lower(),
                    search in c_area.lower(),
                ]):
                    continue

                debit       = float(client.get('debit')  or 0)
                credit      = float(client.get('credit') or 0)
                outstanding = round(debit - credit, 2)

                stats   = fu_map.get(code, {})
                last_fu = all_latest_fu.get(code)

                followup_count     = stats.get('followup_count', 0)
                last_followup_date = stats.get('last_followup_date')
                next_followup_date = last_fu.next_followup_date if last_fu else None
                last_outcome       = last_fu.outcome if last_fu else None
                last_escalated_to  = last_fu.escalated_to if last_fu else None

                # Days since last follow-up (None = never followed up)
                if last_followup_date:
                    days_since_followup = (today - last_followup_date.date()).days
                else:
                    days_since_followup = None

                # Risk scoring
                if outstanding <= 0:
                    risk = 'None'
                elif outstanding > 50000 or (days_since_followup is not None and days_since_followup > 60) or days_since_followup is None:
                    risk = 'High'
                elif outstanding > 10000 or (days_since_followup is not None and days_since_followup > 30):
                    risk = 'Med'
                else:
                    risk = 'Low'

                # ── Filter: overdue ───────────────────────────────────────
                if filter_type == 'overdue':
                    if outstanding <= 0:
                        continue
                    if next_followup_date and next_followup_date > today:
                        continue

                # ── Filter: due_week ──────────────────────────────────────
                elif filter_type == 'due_week':
                    if not next_followup_date:
                        continue
                    if not (today <= next_followup_date <= week_end):
                        continue

                results.append({
                    'code':               code,
                    'name':               name,
                    'agent':              c_agent or None,
                    'agent_code':         agent_code or None,
                    'area':               c_area  or None,
                    'area_code':          area_code or None,
                    'debit':              debit,
                    'credit':             credit,
                    'outstanding':        outstanding,
                    'oldest_due_days':    days_since_followup if outstanding > 0 else 0,
                    'risk':               risk,
                    'followup_count':     followup_count,
                    'last_outcome':       last_outcome,
                    'last_escalated_to':  last_escalated_to,
                    'last_followup_date': str(last_followup_date.date()) if last_followup_date else None,
                    'next_followup_date': str(next_followup_date) if next_followup_date else None,
                })

            # ── 5. Sort: outstanding desc → days_since_followup desc ──────
            results.sort(key=lambda r: (-r['outstanding'], -(r['oldest_due_days'] or 0)))

            # ── 6. Paginate ───────────────────────────────────────────────
            total_count  = len(results)
            start        = (page - 1) * page_size
            page_results = results[start: start + page_size]

            return Response({
                'count':   total_count,
                'filter':  filter_type,
                'results': page_results,
            })

        except Exception as e:
            import traceback
            logger.error(f"FollowUpTrackerAPI Error: {traceback.format_exc()}")
            return Response({'error': str(e)}, status=500)


class EscalationRecipientsAPI(APIView):
    """GET /api/followup/escalation-recipients/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            eligible = {}

            for user in User.objects.filter(is_active=True, role='ADMIN'):
                eligible[str(user.id)] = {
                    'id': str(user.id),
                    'name': user.get_full_name() or user.name or user.email,
                    'email': user.email,
                    'role': user.role,
                    'source': 'admin',
                }

            followup_menu_users = (
                User.objects.filter(
                    is_active=True,
                    menu_assignments__is_active=True,
                    menu_assignments__menu__code__startswith='followup',
                )
                .distinct()
            )

            for user in followup_menu_users:
                key = str(user.id)
                if key not in eligible:
                    eligible[key] = {
                        'id': str(user.id),
                        'name': user.get_full_name() or user.name or user.email,
                        'email': user.email,
                        'role': user.role,
                        'source': 'followup',
                    }

            recipients = sorted(
                eligible.values(),
                key=lambda item: (item['name'] or '').lower()
            )

            return Response({
                'count': len(recipients),
                'results': recipients,
            })
        except Exception as e:
            logger.error(f"EscalationRecipientsAPI Error: {e}")
            return Response({'error': str(e)}, status=500)


# ══════════════════════════════════════════════════════════════
#  FOLLOW-UP LOG  CRUD
# ══════════════════════════════════════════════════════════════

class FollowUpListCreateAPI(ListCreateAPIView):
    serializer_class   = FollowUpSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs          = FollowUp.objects.select_related('created_by')
        client_code = self.request.query_params.get('client_code')
        outcome     = self.request.query_params.get('outcome')
        start_date  = self.request.query_params.get('start_date')
        end_date    = self.request.query_params.get('end_date')
        search      = self.request.query_params.get('search', '').strip()

        if client_code:
            qs = qs.filter(client_code=client_code)
        if outcome:
            qs = qs.filter(outcome=outcome)
        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)
        if search:
            qs = qs.filter(
                Q(client_name__icontains=search) |
                Q(client_code__icontains=search) |
                Q(notes__icontains=search)
            )
        return qs

    def create(self, request, *args, **kwargs):
        client_code = request.data.get('client_code')

        if client_code:
            escalated_alert = (
                PaymentAlert.objects
                .filter(
                    client_code=client_code,
                    alert_type='ESCALATED',
                    is_resolved=False,
                )
                .order_by('-created_at')
                .first()
            )

            if escalated_alert and escalated_alert.assigned_to and escalated_alert.assigned_to != request.user:
                return Response(
                    {'detail': 'This escalated follow-up is assigned to another user.'},
                    status=403,
                )

        return super().create(request, *args, **kwargs)


class FollowUpDetailAPI(RetrieveUpdateDestroyAPIView):
    serializer_class   = FollowUpSerializer
    permission_classes = [IsAuthenticated]
    queryset           = FollowUp.objects.select_related('created_by')


# ══════════════════════════════════════════════════════════════
#  ALERTS
# ══════════════════════════════════════════════════════════════

class AlertListAPI(ListCreateAPIView):
    serializer_class   = PaymentAlertSerializer
    permission_classes = [IsAuthenticated]   # ← change from AllowAny to IsAuthenticated

    def get_queryset(self):
        user = self.request.user
        qs = PaymentAlert.objects.annotate(
            has_followup=Exists(
                FollowUp.objects.filter(client_code=OuterRef('client_code'))
            )
        )

        if not _user_has_followup_access(user):
            return qs.none()

        severity   = self.request.query_params.get('severity')
        alert_type = self.request.query_params.get('alert_type')
        resolved   = self.request.query_params.get('resolved')
        search     = self.request.query_params.get('search', '').strip()

        if severity:
            qs = qs.filter(severity=severity)
        if alert_type:
            qs = qs.filter(alert_type=alert_type)
        if resolved is not None:
            qs = qs.filter(is_resolved=(resolved.lower() == 'true'))
        if search:
            qs = qs.filter(
                Q(client_name__icontains=search) |
                Q(client_code__icontains=search)
            )
        return qs


class AlertResolveAPI(APIView):
    """PATCH /api/followup/alerts/<pk>/resolve/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            alert             = PaymentAlert.objects.get(pk=pk)

            if alert.assigned_to and alert.assigned_to != request.user:
                return Response(
                    {'error': 'This alert is assigned to another user.'},
                    status=403,
                )

            alert.is_resolved = True
            alert.resolved_at = timezone.now()
            alert.resolved_by = request.user
            alert.save()
            return Response({'message': 'Alert resolved', 'id': pk})
        except PaymentAlert.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


# ══════════════════════════════════════════════════════════════
#  REPORT  — summary stats
# ══════════════════════════════════════════════════════════════

class FollowUpReportAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date   = request.query_params.get('end_date')
        agent      = request.query_params.get('agent', '').strip()
        outcome    = request.query_params.get('outcome', '').strip()
        search     = request.query_params.get('search', '').strip()

        qs = FollowUp.objects.all()
        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)
        if agent:
            qs = qs.filter(agent=agent)
        if outcome:
            qs = qs.filter(outcome=outcome)
        if search:
            qs = qs.filter(
                Q(client_name__icontains=search) |
                Q(client_code__icontains=search) |
                Q(notes__icontains=search)
            )

        total      = qs.count()
        by_outcome = {}
        for row in qs.values('outcome').annotate(count=Count('id')):
            by_outcome[row['outcome']] = row['count']

        total_outstanding = qs.aggregate(s=Sum('outstanding_amount'))['s'] or 0

        return Response({
            'total_followups':   total,
            'by_outcome':        by_outcome,
            'total_outstanding': float(total_outstanding),
            'date_range': {
                'start': start_date,
                'end':   end_date,
            }
        })