# In backend/authentication/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # --- CHANGE 1: ADD 'project' TO THE LIST DISPLAY ---
    list_display = ('username', 'user_type', 'admin_type', 'project', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'admin_type', 'is_active', 'is_staff', 'is_superuser', 'project')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    # --- CHANGE 2: ADD 'project' TO THE FIELDSETS ---
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        # I've added 'project' to this section.
        ('Personal info', {'fields': ('email', 'user_type', 'admin_type', 'project', 'company_name', 'registered_address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    # --- CHANGE 3: ADD 'project' TO THE ADD_FIELDSETS (for creating new users in admin) ---
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # I've added 'project' here too.
            'fields': ('username', 'password', 'password2', 'user_type', 'admin_type', 'project', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    # --- CHANGE 4 (OPTIONAL BUT RECOMMENDED): MAKE PROJECT FIELD EASIER TO USE ---
    # This turns the project field into a search box instead of a huge dropdown if you have many projects.
    raw_id_fields = ('project',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('projectName', 'projectCategory', 'commencementDate', 'deadlineDate', 'nearestPoliceStation')
    search_fields = ('projectName',)
    list_filter = ('projectCategory', 'commencementDate', 'deadlineDate')
    date_hierarchy = 'commencementDate'

    fieldsets = (
        ('Basic Information', {
            'fields': ('projectName', 'projectCategory', 'projectCapacity', 'projectLocation')
        }),
        ('Timeline', {
            'fields': ('commencementDate', 'deadlineDate')
        }),
        ('Location Details', {
            'fields': ('latitude', 'longitude')
        }),
        ('Emergency Contacts', {
            'fields': ('nearestPoliceStation', 'nearestPoliceStationContact', 'nearestHospital', 'nearestHospitalContact')
        }),
    )