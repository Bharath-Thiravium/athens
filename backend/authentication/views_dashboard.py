"""
Dashboard statistics views for the EHS Management System
Provides aggregated data for dashboard overview
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.contrib.auth import get_user_model

# Import models from different apps
from ptw.models import Permit
from safetyobservation.models import SafetyObservation
from worker.models import Worker
from incidentmanagement.models import Incident
from manpower.models import ManpowerEntry
from authentication.models_attendance import ProjectAttendance
from authentication.models import Project

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Get comprehensive dashboard statistics
    Supports date filtering: ?period=week|month|year
    Master users get system-wide statistics, other users get project-specific data
    """
    try:
        # Debug logging for authentication

        # Get user's project and admin type
        user_project = getattr(request.user, 'project', None)
        admin_type = getattr(request.user, 'admin_type', None)
        period = request.GET.get('period', 'week')

        # Master users get system-wide access, others get project-specific
        is_master = admin_type == 'master'
        
        # Calculate date ranges
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
            previous_start = start_date - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
            previous_start = start_date - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
            previous_start = start_date - timedelta(days=365)
        else:
            start_date = now - timedelta(days=7)
            previous_start = start_date - timedelta(days=7)

        # Base querysets - master users get all data, others get project-specific
        permits_qs = Permit.objects.all()
        safety_obs_qs = SafetyObservation.objects.all()
        workers_qs = Worker.objects.all()
        incidents_qs = Incident.objects.all()
        attendance_qs = ProjectAttendance.objects.all()

        # Filter by project for non-master users
        if not is_master and user_project:
            permits_qs = permits_qs.filter(project=user_project)
            workers_qs = workers_qs.filter(project=user_project)
            incidents_qs = incidents_qs.filter(project=user_project)
            attendance_qs = attendance_qs.filter(project=user_project)
            # Safety observations don't have direct project relation, filter by created_by's project
            safety_obs_qs = safety_obs_qs.filter(created_by__project=user_project)


        # === MAIN STATISTICS ===
        
        # Permits Statistics
        total_permits = permits_qs.count()
        permits_this_period = permits_qs.filter(created_at__gte=start_date).count()
        permits_previous_period = permits_qs.filter(
            created_at__gte=previous_start, 
            created_at__lt=start_date
        ).count()
        permits_change = calculate_percentage_change(permits_this_period, permits_previous_period)
        
        # Permit Status Distribution
        permit_status_data = list(permits_qs.values('status').annotate(count=Count('id')))
        
        # Safety Observations Statistics
        total_safety_obs = safety_obs_qs.count()
        safety_obs_this_period = safety_obs_qs.filter(created_at__gte=start_date).count()
        safety_obs_previous_period = safety_obs_qs.filter(
            created_at__gte=previous_start,
            created_at__lt=start_date
        ).count()
        safety_obs_change = calculate_percentage_change(safety_obs_this_period, safety_obs_previous_period)
        
        # Workers Statistics
        total_workers = workers_qs.count()
        active_workers = workers_qs.filter(status='active').count()
        workers_this_period = workers_qs.filter(created_at__gte=start_date).count()
        workers_previous_period = workers_qs.filter(
            created_at__gte=previous_start,
            created_at__lt=start_date
        ).count()
        workers_change = calculate_percentage_change(workers_this_period, workers_previous_period)
        
        # Pending Approvals (permits + incidents)
        pending_permits = permits_qs.filter(status__in=['pending_approval', 'pending_verification']).count()
        pending_incidents = incidents_qs.filter(status__in=['reported', 'under_review']).count()
        total_pending = pending_permits + pending_incidents
        
        # === TREND DATA ===
        
        # Safety Observations Trend (last 7 days for week, last 30 days for month, etc.)
        if period == 'week':
            trend_days = 7
            date_format = '%a'  # Mon, Tue, Wed
        elif period == 'month':
            trend_days = 30
            date_format = '%d'  # 1, 2, 3... 30
        else:
            trend_days = 12
            date_format = '%b'  # Jan, Feb, Mar
            
        safety_trend_data = get_trend_data(safety_obs_qs, start_date, trend_days, period, date_format)
        
        # === RECENT ACTIVITY ===
        recent_activity = get_recent_activity(permits_qs, safety_obs_qs, incidents_qs, user_project)
        
        # === ATTENDANCE STATISTICS ===
        today = now.date()
        today_attendance = attendance_qs.filter(check_in_time__date=today).count()
        
        response_data = {
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': now.isoformat()
            },
            'statistics': {
                'permits': {
                    'total': total_permits,
                    'this_period': permits_this_period,
                    'change_percentage': permits_change,
                    'pending_approvals': pending_permits
                },
                'safety_observations': {
                    'total': total_safety_obs,
                    'this_period': safety_obs_this_period,
                    'change_percentage': safety_obs_change
                },
                'workers': {
                    'total': total_workers,
                    'active': active_workers,
                    'this_period': workers_this_period,
                    'change_percentage': workers_change
                },
                'pending_approvals': {
                    'total': total_pending,
                    'permits': pending_permits,
                    'incidents': pending_incidents
                },
                'attendance': {
                    'today': today_attendance
                }
            },
            'charts': {
                'permit_status': permit_status_data,
                'safety_trend': safety_trend_data
            },
            'recent_activity': recent_activity
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch dashboard data',
            'detail': str(e)
        }, status=500)

def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values"""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 1)

def get_trend_data(queryset, start_date, days, period, date_format):
    """Generate trend data for charts"""
    trend_data = []
    
    if period == 'year':
        # For year view, show monthly data
        for i in range(12):
            month_start = start_date + timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            count = queryset.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            trend_data.append({
                'name': month_start.strftime('%b'),
                'value': count,
                'date': month_start.strftime('%Y-%m')
            })
    else:
        # For week/month view, show daily data
        for i in range(days):
            day = start_date + timedelta(days=i)
            count = queryset.filter(created_at__date=day.date()).count()
            trend_data.append({
                'name': day.strftime(date_format),
                'value': count,
                'date': day.strftime('%Y-%m-%d')
            })
    
    return trend_data

def get_recent_activity(permits_qs, safety_obs_qs, incidents_qs, user_project):
    """Get recent activity across all modules"""
    activities = []
    
    # Recent permits (last 10)
    recent_permits = permits_qs.order_by('-created_at')[:5]
    for permit in recent_permits:
        activities.append({
            'title': f'Permit #{permit.permit_number} {permit.status}',
            'type': permit.status.title(),
            'module': 'PTW',
            'timestamp': permit.created_at.isoformat(),
            'id': permit.id
        })
    
    # Recent safety observations (last 5)
    recent_safety = safety_obs_qs.order_by('-created_at')[:5]
    for obs in recent_safety:
        activities.append({
            'title': f'Safety observation #{obs.observationID}',
            'type': obs.observationStatus or 'Reported',
            'module': 'Safety',
            'timestamp': obs.created_at.isoformat(),
            'id': obs.id
        })
    
    # Recent incidents (last 5)
    recent_incidents = incidents_qs.order_by('-created_at')[:5]
    for incident in recent_incidents:
        activities.append({
            'title': f'Incident #{incident.incident_id} reported',
            'type': incident.status.title(),
            'module': 'Incident',
            'timestamp': incident.created_at.isoformat(),
            'id': incident.id
        })
    
    # Sort by timestamp and return latest 10
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities[:10]
