from django.urls import path
from .views import SystemSettingsView, SystemLogsView, SystemLogsExportView, BackupListCreateView, BackupDetailView, BackupRestoreView, BackupDownloadView, BackupUploadView

urlpatterns = [
    path('settings/', SystemSettingsView.as_view(), name='system-settings'),
    path('logs/', SystemLogsView.as_view(), name='system-logs'),
    path('logs/export/', SystemLogsExportView.as_view(), name='system-logs-export'),

    path('backups/', BackupListCreateView.as_view(), name='backup-list-create'),
    path('backups/<int:pk>/', BackupDetailView.as_view(), name='backup-detail'),
    path('backups/<int:pk>/restore/', BackupRestoreView.as_view(), name='backup-restore'),
    path('backups/<int:pk>/download/', BackupDownloadView.as_view(), name='backup-download'),
    path('backups/upload/', BackupUploadView.as_view(), name='backup-upload'),
]

