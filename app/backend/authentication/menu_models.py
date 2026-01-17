from django.db import models
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class MenuModule(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='modules', null=True, blank=True)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50)
    path = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    requires_permission = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__order', 'order', 'name']

    def __str__(self):
        category_name = self.category.name if self.category else 'No Category'
        return f"{category_name} - {self.name}"

class CompanyMenuAccess(models.Model):
    # Use athens_tenant_id instead of Company model
    athens_tenant_id = models.UUIDField(help_text="Company tenant identifier")
    module = models.ForeignKey(MenuModule, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['athens_tenant_id', 'module']

class UserMenuPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(MenuModule, on_delete=models.CASCADE)
    can_access = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'module']


class ProjectMenuAccess(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    module = models.ForeignKey(MenuModule, on_delete=models.CASCADE, db_column='menu_module_id')
    is_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_menu_access_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'module']
