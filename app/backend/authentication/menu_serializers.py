from rest_framework import serializers
from .menu_models import MenuCategory, MenuModule, CompanyMenuAccess, UserMenuPermission, ProjectMenuAccess

class MenuModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuModule
        fields = ['id', 'name', 'key', 'icon', 'path', 'order', 'is_active', 'requires_permission']

class MenuCategorySerializer(serializers.ModelSerializer):
    modules = MenuModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'key', 'icon', 'order', 'is_active', 'modules']

class CompanyMenuAccessSerializer(serializers.ModelSerializer):
    module = MenuModuleSerializer(read_only=True)
    
    class Meta:
        model = CompanyMenuAccess
        fields = ['id', 'athens_tenant_id', 'module', 'is_enabled']

class UserMenuPermissionSerializer(serializers.ModelSerializer):
    module = MenuModuleSerializer(read_only=True)
    
    class Meta:
        model = UserMenuPermission
        fields = ['id', 'module', 'can_access']


class ProjectMenuAccessSerializer(serializers.ModelSerializer):
    menu_module = serializers.IntegerField(source='module.id', read_only=True)
    menu_module_name = serializers.CharField(source='module.name', read_only=True)
    menu_module_key = serializers.CharField(source='module.key', read_only=True)
    project_name = serializers.CharField(source='project.projectName', read_only=True)

    class Meta:
        model = ProjectMenuAccess
        fields = [
            'id',
            'project',
            'menu_module',
            'menu_module_name',
            'menu_module_key',
            'is_enabled',
            'project_name',
        ]
