# Dashboard & Analytics Module - Technical Blueprint

## 1. Module Overview

### Module Name
**Dashboard & Analytics Engine**

### Business Purpose
Centralized analytics and KPI dashboard providing real-time insights across all EHS modules with project-specific and system-wide views for different user roles.

### User Roles Involved
- **Master Users**: System-wide analytics across all projects and tenants
- **Project Users**: Project-specific analytics and KPIs
- **Management**: Executive dashboards with trend analysis

### Dependent Modules
- **All EHS Modules**: Data aggregation from permits, incidents, safety observations, workers
- **Authentication Module**: User context and project isolation
- **Project Isolation**: Data filtering based on user permissions

## 2. Functional Scope

### Features Included
- **Real-Time KPIs**: Live statistics with percentage change calculations
- **Trend Analysis**: Time-series data (week/month/year views)
- **Cross-Module Analytics**: Aggregated data from all EHS modules
- **Recent Activity Feed**: Latest activities across all modules
- **Status Distribution Charts**: Visual breakdown of permit/incident statuses
- **Attendance Tracking**: Daily attendance statistics

### Analytics Scope
- **Permits**: Total, pending, status distribution, approval trends
- **Safety Observations**: Count, trends, status tracking
- **Incidents**: Reporting rates, resolution times, severity analysis
- **Workers**: Active count, deployment status, attendance rates
- **Pending Approvals**: Cross-module approval queue

## 3. Technical Architecture

### Core Files
- **views_dashboard.py**: Main dashboard API endpoints with analytics logic
- **Dashboard.tsx**: Frontend dashboard interface with charts and KPIs

### Key Endpoints
```python
/api/dashboard/overview/                # Main dashboard statistics
  ?period=week|month|year              # Time period filtering
```

### Analytics Functions
```python
calculate_percentage_change(current, previous)  # KPI change calculation
get_trend_data(queryset, start_date, days)     # Time-series data
get_recent_activity(querysets)                 # Activity feed aggregation
```

### Data Aggregation Logic
```python
# Project isolation for analytics
if not is_master and user_project:
    permits_qs = permits_qs.filter(project=user_project)
    workers_qs = workers_qs.filter(project=user_project)
    incidents_qs = incidents_qs.filter(project=user_project)

# Time-based filtering
permits_this_period = permits_qs.filter(created_at__gte=start_date).count()
permits_change = calculate_percentage_change(current, previous)
```

## 4. Integration Points

### Incoming Dependencies
- **PTW Module**: Permit statistics and status data
- **Safety Observation Module**: Observation counts and trends
- **Incident Management**: Incident reporting and resolution data
- **Worker Management**: Worker counts and employment status
- **Attendance System**: Daily attendance tracking

### Outgoing Dependencies
- **Frontend Dashboard**: Real-time data updates
- **Notification System**: Alert thresholds and notifications
- **Reporting System**: Data export and report generation

## 5. Current Working State
- ✅ Real-time KPI calculations with percentage changes
- ✅ Multi-period trend analysis (week/month/year)
- ✅ Cross-module data aggregation
- ✅ Project isolation for analytics
- ✅ Master user system-wide access
- ✅ Recent activity feed across modules
- ✅ Status distribution charts

---

**Blueprint Version**: 1.0  
**Status**: Production Ready  
**Dependencies**: All EHS Modules, Authentication, Project Isolation