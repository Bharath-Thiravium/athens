from django.db import transaction
import uuid
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Count, Q, F, IntegerField, OuterRef, Subquery
from datetime import timedelta

from authentication.permissions import IsSuperAdmin
from authentication.tenant_models import AthensTenant, DEFAULT_MODULES, DEFAULT_MENUS
from authentication.models import CustomUser
from .models import TenantCompany, SaaSSubscription, SaaSAuditLog, SaaSPlatformSettings
from .serializers import (
    SaaSTenantSerializer,
    MasterUserSerializer,
    SaaSSubscriptionSerializer,
    SaaSAuditLogSerializer,
    SaaSTenantListSerializer,
    SaaSTenantStatsSerializer,
    SaaSMasterListSerializer,
    SaaSSubscriptionListSerializer,
    SaaSMetricsOverviewSerializer,
    SaaSPlatformSettingsSerializer,
)


def _audit(actor, action, entity_type, entity_id, before=None, after=None, request=None):
    try:
        SaaSAuditLog.objects.create(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            before=before,
            after=after,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None,
        )
    except Exception:
        # Do not block main flow on audit failure
        pass


class SaaSTenantViewSet(viewsets.ModelViewSet):
    queryset = TenantCompany.objects.all()
    serializer_class = SaaSTenantSerializer
    permission_classes = [IsSuperAdmin]

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        tenant = self.get_object()
        before = SaaSTenantSerializer(tenant).data
        tenant.status = TenantCompany.Status.DISABLED
        tenant.save(update_fields=['status'])
        after = SaaSTenantSerializer(tenant).data
        _audit(request.user, 'tenant_suspended', 'tenant', tenant.id, before, after, request)
        return Response(after)

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        tenant = self.get_object()
        before = SaaSTenantSerializer(tenant).data
        tenant.status = TenantCompany.Status.ACTIVE
        tenant.save(update_fields=['status'])
        after = SaaSTenantSerializer(tenant).data
        _audit(request.user, 'tenant_reactivated', 'tenant', tenant.id, before, after, request)
        return Response(after)

    def perform_create(self, serializer):
        tenant = serializer.save()
        _audit(self.request.user, 'tenant_created', 'tenant', tenant.id, None, SaaSTenantSerializer(tenant).data, self.request)

    def perform_update(self, serializer):
        tenant = self.get_object()
        before = SaaSTenantSerializer(tenant).data
        tenant = serializer.save()
        after = SaaSTenantSerializer(tenant).data
        _audit(self.request.user, 'tenant_updated', 'tenant', tenant.id, before, after, self.request)


class SaaSPlatformSettingsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        settings, _ = SaaSPlatformSettings.objects.get_or_create(id=1)
        serializer = SaaSPlatformSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        settings, _ = SaaSPlatformSettings.objects.get_or_create(id=1)
        before = SaaSPlatformSettingsSerializer(settings).data
        serializer = SaaSPlatformSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        after = serializer.data
        _audit(request.user, 'platform_settings_updated', 'settings', settings.id, before, after, request)
        return Response(after)


class SaaSTenantModulesAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    def _get_tenant(self, tenant_id):
        return AthensTenant.objects.get(pk=tenant_id)

    def get(self, request, tenant_id):
        try:
            tenant = self._get_tenant(tenant_id)
        except AthensTenant.DoesNotExist:
            return Response(
                {'detail': 'Tenant not found in AthensTenant. Sync tenant before managing modules.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'tenant_id': str(tenant.id),
            'enabled_modules': tenant.enabled_modules,
            'available_modules': DEFAULT_MODULES,
        })

    def patch(self, request, tenant_id):
        try:
            tenant = self._get_tenant(tenant_id)
        except AthensTenant.DoesNotExist:
            return Response(
                {'detail': 'Tenant not found in AthensTenant. Sync tenant before managing modules.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        enabled_modules = request.data.get('enabled_modules')
        if not isinstance(enabled_modules, list):
            return Response({'detail': 'enabled_modules must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        invalid = [m for m in enabled_modules if m not in DEFAULT_MODULES]
        if invalid:
            return Response({'detail': f'Invalid modules: {", ".join(invalid)}'}, status=status.HTTP_400_BAD_REQUEST)
        before = {'enabled_modules': tenant.enabled_modules}
        tenant.enabled_modules = enabled_modules
        tenant.save(update_fields=['enabled_modules', 'updated_at'])
        after = {'enabled_modules': tenant.enabled_modules}
        _audit(request.user, 'tenant_modules_updated', 'tenant', tenant.id, before, after, request)
        try:
            from authentication.menu_access_utils import sync_company_menu_access
            sync_company_menu_access(tenant.id)
        except Exception:
            pass
        return Response({
            'tenant_id': str(tenant.id),
            'enabled_modules': tenant.enabled_modules,
            'available_modules': DEFAULT_MODULES,
        })


class SaaSTenantSyncAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, tenant_id):
        master_admin_id = request.data.get('master_admin_id')
        tenant_name = request.data.get('tenant_name')
        company_id = request.data.get('company_id')

        if not master_admin_id:
            return Response({'detail': 'master_admin_id is required (UUID)'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            master_admin_id = uuid.UUID(str(master_admin_id))
        except Exception:
            return Response({'detail': 'master_admin_id must be a valid UUID'}, status=status.HTTP_400_BAD_REQUEST)

        if company_id:
            try:
                company_id = uuid.UUID(str(company_id))
            except Exception:
                return Response({'detail': 'company_id must be a valid UUID'}, status=status.HTTP_400_BAD_REQUEST)

        tenant_company = TenantCompany.objects.filter(pk=tenant_id).first()
        resolved_name = tenant_name or (tenant_company.display_name if tenant_company else None) or (tenant_company.name if tenant_company else None) or f"Tenant {tenant_id}"

        tenant, created = AthensTenant.objects.get_or_create(
            id=tenant_id,
            defaults={
                'master_admin_id': master_admin_id,
                'company_id': company_id,
                'enabled_modules': DEFAULT_MODULES.copy(),
                'enabled_menus': DEFAULT_MENUS.copy(),
                'is_active': True,
                'tenant_name': resolved_name,
            },
        )

        if not created:
            return Response({
                'detail': 'Tenant already synced',
                'tenant_id': str(tenant.id),
                'enabled_modules': tenant.enabled_modules,
                'enabled_menus': tenant.enabled_menus,
            })

        try:
            from authentication.menu_access_utils import sync_company_menu_access
            sync_company_menu_access(tenant.id)
        except Exception:
            pass

        _audit(
            request.user,
            'tenant_synced',
            'tenant',
            tenant.id,
            None,
            {'tenant_name': tenant.tenant_name, 'master_admin_id': str(master_admin_id)},
            request,
        )

        return Response({
            'tenant_id': str(tenant.id),
            'tenant_name': tenant.tenant_name,
            'enabled_modules': tenant.enabled_modules,
            'enabled_menus': tenant.enabled_menus,
        }, status=status.HTTP_201_CREATED)


class SaaSMasterViewSet(viewsets.ModelViewSet):
    tenant_name_subquery = TenantCompany.objects.filter(id=OuterRef('athens_tenant_id')).values('display_name')[:1]
    queryset = CustomUser.objects.filter(user_type='master').annotate(
        tenant_name=Subquery(tenant_name_subquery)
    )
    serializer_class = MasterUserSerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        user = serializer.save(created_by=self.request.user)
        _audit(self.request.user, 'master_created', 'user', user.id, None, {'username': user.username, 'tenant_id': str(user.athens_tenant_id)}, self.request)

    def perform_update(self, serializer):
        user = self.get_object()
        before = {'username': user.username, 'tenant_id': str(user.athens_tenant_id), 'is_active': user.is_active}
        user = serializer.save()
        after = {'username': user.username, 'tenant_id': str(user.athens_tenant_id), 'is_active': user.is_active}
        _audit(self.request.user, 'master_updated', 'user', user.id, before, after, self.request)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        q = request.query_params.get('q')
        tenant_id = request.query_params.get('tenant_id')
        status = request.query_params.get('status')
        if q:
            qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
        if tenant_id:
            qs = qs.filter(athens_tenant_id=tenant_id)
        if status:
            if status == 'active':
                qs = qs.filter(is_active=True)
            elif status == 'disabled':
                qs = qs.filter(is_active=False)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs.order_by('-id'), request)
        serializer = SaaSMasterListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SaaSSubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsSuperAdmin]

    def _get_subscription(self, tenant_id):
        tenant = TenantCompany.objects.get(pk=tenant_id)
        subscription, _ = SaaSSubscription.objects.get_or_create(tenant=tenant)
        return subscription

    def _resolve_tenant_id(self, tenant_id=None, tenant_pk=None, pk=None):
        return tenant_id or tenant_pk or pk

    def retrieve(self, request, pk=None, tenant_pk=None, tenant_id=None):
        resolved_id = self._resolve_tenant_id(tenant_id=tenant_id, tenant_pk=tenant_pk, pk=pk)
        sub = self._get_subscription(resolved_id)
        return Response(SaaSSubscriptionSerializer(sub).data)

    def partial_update(self, request, pk=None, tenant_pk=None, tenant_id=None):
        resolved_id = self._resolve_tenant_id(tenant_id=tenant_id, tenant_pk=tenant_pk, pk=pk)
        sub = self._get_subscription(resolved_id)
        before = SaaSSubscriptionSerializer(sub).data
        serializer = SaaSSubscriptionSerializer(sub, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        after = serializer.data
        _audit(request.user, 'subscription_updated', 'subscription', sub.tenant_id, before, after, request)
        return Response(after)


class SaaSSubscriptionListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        qs = SaaSSubscription.objects.select_related('tenant').all()
        status_param = request.query_params.get('status')
        plan = request.query_params.get('plan')
        period_end_lte = request.query_params.get('period_end_lte')
        if status_param:
            qs = qs.filter(status=status_param)
        if plan:
            qs = qs.filter(plan=plan)
        if period_end_lte:
            try:
                qs = qs.filter(current_period_end__lte=period_end_lte)
            except Exception:
                pass
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs.order_by('-updated_at'), request)
        data = SaaSSubscriptionListSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class SaaSAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaaSAuditLog.objects.select_related('actor').all()
    serializer_class = SaaSAuditLogSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        tenant_id = self.request.query_params.get('tenant_id')
        actor_id = self.request.query_params.get('actor_id')
        action = self.request.query_params.get('action')
        date_from = self.request.query_params.get('from')
        date_to = self.request.query_params.get('to')
        if tenant_id:
            qs = qs.filter(entity_type='tenant', entity_id=str(tenant_id))
        if actor_id:
            qs = qs.filter(actor_id=actor_id)
        if action:
            qs = qs.filter(action__icontains=action)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs


class SaaSMetricsOverviewAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    def _get_range(self, request):
        now = timezone.now().date()
        range_param = request.query_params.get('range')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if date_from and date_to:
            try:
                return timezone.datetime.fromisoformat(date_from).date(), timezone.datetime.fromisoformat(date_to).date()
            except Exception:
                pass
        if range_param == '30d':
            return now - timedelta(days=30), now
        if range_param == '90d':
            return now - timedelta(days=90), now
        return now - timedelta(days=7), now

    def get(self, request):
        start_date, end_date = self._get_range(request)

        tenants_qs = TenantCompany.objects.all()
        subs_qs = SaaSSubscription.objects.select_related('tenant')
        masters_qs = CustomUser.objects.filter(user_type='master')
        logs_qs = SaaSAuditLog.objects.all()

        tenants_total = tenants_qs.count()
        tenants_active = tenants_qs.filter(status=TenantCompany.Status.ACTIVE).count()
        tenants_trialing = subs_qs.filter(status=SaaSSubscription.Status.TRIALING).count()
        tenants_past_due = subs_qs.filter(status=SaaSSubscription.Status.PAST_DUE).count()
        tenants_suspended = subs_qs.filter(status=SaaSSubscription.Status.SUSPENDED).count()
        tenants_new = tenants_qs.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).count()

        masters_total = masters_qs.count()
        masters_new = masters_qs.filter(
            Q(user_detail__created_at__date__gte=start_date, user_detail__created_at__date__lte=end_date)
            | Q(last_login__date__gte=start_date, last_login__date__lte=end_date)
        ).count()
        masters_active = masters_qs.filter(is_active=True).count()
        masters_disabled = masters_qs.filter(is_active=False).count()

        plans_breakdown = list(
            subs_qs.values('plan').annotate(count=Count('id')).order_by('-count')
        )
        status_breakdown = list(
            subs_qs.values('status').annotate(count=Count('id')).order_by('-count')
        )

        activity_events = logs_qs.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        top_actions = list(
            activity_events.values('action').annotate(count=Count('id')).order_by('-count')[:5]
        )
        recent_logs = SaaSAuditLogSerializer(activity_events.select_related('actor')[:10], many=True).data

        def series_from_qs(qs, date_field, value_field='count'):
            aggregated = qs.values(date_field).annotate(val=Count('id')).order_by(date_field)
            return [{'date': item[date_field], value_field: item['val']} for item in aggregated]

        timeseries_new_tenants = series_from_qs(
            tenants_qs.filter(created_at__date__gte=start_date, created_at__date__lte=end_date),
            'created_at__date',
            'count',
        )

        # active tenants over time approximated by status active creation dates
        timeseries_active_tenants = series_from_qs(
            tenants_qs.filter(status=TenantCompany.Status.ACTIVE, created_at__date__lte=end_date),
            'created_at__date',
            'count',
        )

        timeseries_mrr = [{'date': start_date, 'value': 0}, {'date': end_date, 'value': 0}]

        payload = {
            "range": {"start": start_date, "end": end_date},
            "tenants": {
                "total": tenants_total,
                "active": tenants_active,
                "trialing": tenants_trialing,
                "past_due": tenants_past_due,
                "suspended": tenants_suspended,
                "new_in_range": tenants_new,
                "churned_in_range": 0,
            },
            "masters": {
                "total": masters_total,
                "new_in_range": masters_new,
                "active": masters_active,
                "disabled": masters_disabled,
            },
            "subscriptions": {
                "mrr": 0,
                "arr": 0,
                "avg_revenue_per_tenant": 0,
                "plans_breakdown": plans_breakdown,
                "status_breakdown": status_breakdown,
            },
            "activity": {
                "events_in_range": activity_events.count(),
                "top_actions": top_actions,
                "recent": recent_logs,
            },
            "timeseries": {
                "new_tenants": timeseries_new_tenants,
                "active_tenants": timeseries_active_tenants,
                "mrr": timeseries_mrr,
            },
        }
        return Response(payload)


class SaaSTenantListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        master_counts = CustomUser.objects.filter(
            user_type='master',
            athens_tenant_id=OuterRef('id'),
        ).values('athens_tenant_id').annotate(cnt=Count('id')).values('cnt')

        qs = TenantCompany.objects.all().select_related('saas_subscription').annotate(
            masters_count=Subquery(master_counts, output_field=IntegerField())
        )
        q = request.query_params.get('q')
        status = request.query_params.get('status')
        plan = request.query_params.get('plan')
        sub_status = request.query_params.get('sub_status')
        sort = request.query_params.get('sort')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(display_name__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if plan:
            qs = qs.filter(saas_subscription__plan=plan)
        if sub_status:
            qs = qs.filter(saas_subscription__status=sub_status)
        if sort:
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by('-created_at')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        data = SaaSTenantListSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class SaaSTenantStatsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, pk):
        tenant = TenantCompany.objects.get(pk=pk)
        masters_count = CustomUser.objects.filter(user_type='master', athens_tenant_id=tenant.id).count()
        sub = getattr(tenant, 'saas_subscription', None)
        last_activity = SaaSAuditLog.objects.filter(entity_type='tenant', entity_id=str(tenant.id)).order_by('-created_at').values_list('created_at', flat=True).first()
        payload = {
            "tenant_id": tenant.id,
            "masters_count": masters_count,
            "subscription_status": sub.status if sub else '',
            "seats": sub.seats if sub else 0,
            "current_period_end": sub.current_period_end if sub else None,
            "last_activity": last_activity,
            "created_at": tenant.created_at,
        }
        serializer = SaaSTenantStatsSerializer(payload)
        return Response(serializer.data)
