from django.urls import path
from .views import (
    ManpowerEntryView,
    ManpowerEntryDetailView,
    ManpowerEntryByDateView,
    IndividualManpowerEntryView,
    WorkTypeView,
    DailyManpowerSummaryView,
    manpower_dashboard_stats,
    test_endpoint,
    debug_manpower_endpoint
)

urlpatterns = [
    # Test endpoints
    path('test/', test_endpoint, name='manpower-test'),
    path('debug/', debug_manpower_endpoint, name='manpower-debug'),
    
    # Original endpoints
    path('manpower/', ManpowerEntryView.as_view(), name='manpower-entry'),
    path('manpower/individual/', ManpowerEntryView.as_view(), name='manpower-individual'),
    path('manpower/<int:pk>/', ManpowerEntryDetailView.as_view(), name='manpower-entry-detail'),
    path('manpower/by-date/', ManpowerEntryByDateView.as_view(), name='manpower-entry-by-date'),

    # Individual record CRUD
    path('record/<int:pk>/', IndividualManpowerEntryView.as_view(), name='individual-record'),

    # Enhanced endpoints
    path('work-types/', WorkTypeView.as_view(), name='work-types'),
    path('daily-summary/', DailyManpowerSummaryView.as_view(), name='daily-summary'),
    path('dashboard-stats/', manpower_dashboard_stats, name='dashboard-stats'),
]
