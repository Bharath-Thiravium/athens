from django.contrib import admin
from authentication.models_notification import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'read', 'created_at', 'sender']
    list_filter = ['notification_type', 'read', 'created_at']
    search_fields = ['title', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('read', 'read_at')
        }),
        ('Additional Info', {
            'fields': ('data', 'link', 'sender'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'sender')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'push_notifications', 'meeting_notifications', 'approval_notifications']
    list_filter = ['email_notifications', 'push_notifications', 'meeting_notifications', 'approval_notifications']
    search_fields = ['user__username', 'user__email']