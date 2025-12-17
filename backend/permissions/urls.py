from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.request_permission, name='request_permission'),
    path('approve/<int:request_id>/', views.approve_permission, name='approve_permission'),
    path('my-requests/', views.my_permission_requests, name='my_permission_requests'),
    path('check/', views.check_permission, name='check_permission'),
]