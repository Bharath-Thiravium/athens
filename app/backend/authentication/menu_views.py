from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from .menu_models import MenuCategory, MenuModule, CompanyMenuAccess, UserMenuPermission, ProjectMenuAccess
from .menu_serializers import MenuCategorySerializer, MenuModuleSerializer, CompanyMenuAccessSerializer, ProjectMenuAccessSerializer
from .usertype_utils import is_master_user
from .menu_access_utils import get_allowed_menu_module_ids_for_tenant, sync_company_menu_access
import logging

logger = logging.getLogger(__name__)

def _is_superadmin(user):
    return getattr(user, 'user_type', None) == 'superadmin'


def _get_allowed_module_ids(athens_tenant_id):
    if not athens_tenant_id:
        return []
    allowed_ids = get_allowed_menu_module_ids_for_tenant(athens_tenant_id)
    if allowed_ids:
        return allowed_ids
    return list(
        CompanyMenuAccess.objects.filter(
            athens_tenant_id=athens_tenant_id,
            is_enabled=True
        ).values_list('module_id', flat=True)
    )

class UserMenuAccessView(APIView):
    """
    Get menu access for the current user based on company and permissions
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        project_id = request.GET.get('project_id') or getattr(user, 'project_id', None)
        
        try:
            # Get user's athens_tenant_id
            athens_tenant_id = getattr(user, 'athens_tenant_id', None)
            if not athens_tenant_id and getattr(user, 'project', None):
                athens_tenant_id = getattr(user.project, 'athens_tenant_id', None)
            allowed_company_module_ids = set(_get_allowed_module_ids(athens_tenant_id))

            allowed_project_module_ids = None
            if project_id:
                project_access_qs = ProjectMenuAccess.objects.filter(project_id=project_id)
                if project_access_qs.exists():
                    allowed_project_module_ids = set(
                        project_access_qs.filter(is_enabled=True).values_list('module_id', flat=True)
                    )
            
            # If project_id is provided, get project info
            project_info = None
            if project_id:
                try:
                    from .models import Project
                    project = Project.objects.get(id=project_id)
                    project_info = {
                        'id': project.id,
                        'name': project.projectName,
                        'category': project.projectCategory
                    }
                except:
                    pass
            
            # Get categories with accessible modules
            categories = MenuCategory.objects.filter(is_active=True).prefetch_related('modules')
            accessible_categories = []
            
            for category in categories:
                accessible_modules = []
                
                for module in category.modules.filter(is_active=True):
                    # Check company access
                    if module.id not in allowed_company_module_ids:
                        continue

                    # Check project access if configured
                    if allowed_project_module_ids is not None and module.id not in allowed_project_module_ids:
                        continue
                    
                    # Check user permission if required
                    if module.requires_permission:
                        user_permission = UserMenuPermission.objects.filter(
                            user=user, module=module
                        ).first()
                        if user_permission and not user_permission.can_access:
                            continue
                    
                    accessible_modules.append({
                        'id': module.id,
                        'key': module.key,
                        'name': module.name,
                        'icon': module.icon,
                        'path': module.path
                    })
                
                if accessible_modules:
                    accessible_categories.append({
                        'id': category.id,
                        'key': category.key,
                        'name': category.name,
                        'icon': category.icon,
                        'modules': accessible_modules
                    })
            
            response_data = accessible_categories
            if project_info:
                response_data = {
                    'project': project_info,
                    'menu': accessible_categories
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting menu access for user {user.username}: {str(e)}")
            return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProjectMenuAccessByProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_master_user(request.user):
            return Response({'error': 'Only master admin can view project menu access'}, status=status.HTTP_403_FORBIDDEN)

        project_id = request.GET.get('project_id')
        if not project_id:
            return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .models import Project
            project = Project.objects.get(id=project_id)
        except Exception:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        user_tenant_id = getattr(request.user, 'athens_tenant_id', None)
        if user_tenant_id and project.athens_tenant_id and project.athens_tenant_id != user_tenant_id:
            return Response({'error': 'Project does not belong to your tenant'}, status=status.HTTP_403_FORBIDDEN)

        allowed_module_ids = _get_allowed_module_ids(project.athens_tenant_id or user_tenant_id)
        access_records = ProjectMenuAccess.objects.filter(project=project, module_id__in=allowed_module_ids)
        serializer = ProjectMenuAccessSerializer(access_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectMenuAccessUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_master_user(request.user):
            return Response({'error': 'Only master admin can update project menu access'}, status=status.HTTP_403_FORBIDDEN)

        project_id = request.data.get('project_id')
        menu_modules = request.data.get('menu_modules', [])

        if not project_id:
            return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(menu_modules, list):
            return Response({'error': 'menu_modules must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .models import Project
            project = Project.objects.get(id=project_id)
        except Exception:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        user_tenant_id = getattr(request.user, 'athens_tenant_id', None)
        if user_tenant_id and project.athens_tenant_id and project.athens_tenant_id != user_tenant_id:
            return Response({'error': 'Project does not belong to your tenant'}, status=status.HTTP_403_FORBIDDEN)

        allowed_module_ids = set(_get_allowed_module_ids(project.athens_tenant_id or user_tenant_id))
        invalid_modules = [
            item.get('module_id')
            for item in menu_modules
            if item.get('module_id') not in allowed_module_ids
        ]
        if invalid_modules:
            return Response(
                {
                    'error': 'Some modules are not allowed for this tenant',
                    'invalid_modules': invalid_modules,
                },
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            for item in menu_modules:
                module_id = item.get('module_id')
                is_enabled = item.get('is_enabled', True)
                if module_id is None:
                    continue
                access, created = ProjectMenuAccess.objects.get_or_create(
                    project=project,
                    module_id=module_id,
                    defaults={'is_enabled': is_enabled, 'created_by': request.user}
                )
                if not created and access.is_enabled != is_enabled:
                    access.is_enabled = is_enabled
                    access.save()

        return Response({'success': True}, status=status.HTTP_200_OK)

class MenuCategoriesView(APIView):
    """
    Get all menu categories with modules
    """
    permission_classes = []

    def get(self, request):
        try:
            categories = MenuCategory.objects.filter(is_active=True)
            serializer = MenuCategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting menu categories: {str(e)}")
            return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanyMenuManagementView(APIView):
    """
    Manage company menu access
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not (is_master_user(request.user) or _is_superadmin(request.user)):
                return Response({'error': 'Only master admin or superadmin can view company menu access'}, status=status.HTTP_403_FORBIDDEN)

            athens_tenant_id = getattr(request.user, 'athens_tenant_id', None)
            if _is_superadmin(request.user):
                athens_tenant_id = request.query_params.get('tenant_id') or request.query_params.get('athens_tenant_id')

            if not athens_tenant_id:
                return Response({'error': 'athens_tenant_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            sync_company_menu_access(athens_tenant_id)
            access_records = CompanyMenuAccess.objects.filter(athens_tenant_id=athens_tenant_id, is_enabled=True)
            serializer = CompanyMenuAccessSerializer(access_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting company menu access: {str(e)}")
            return Response({'error': 'Failed to get menu access'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not _is_superadmin(request.user):
                return Response({'error': 'Only superadmin can update company menu access'}, status=status.HTTP_403_FORBIDDEN)

            athens_tenant_id = request.data.get('tenant_id') or request.data.get('athens_tenant_id')
            if not athens_tenant_id:
                return Response({'error': 'athens_tenant_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            module_id = request.data.get('module_id')
            is_enabled = request.data.get('is_enabled', True)
            
            module = MenuModule.objects.get(id=module_id)
            access, created = CompanyMenuAccess.objects.get_or_create(
                athens_tenant_id=athens_tenant_id,
                module=module,
                defaults={'is_enabled': is_enabled}
            )
            
            if not created:
                access.is_enabled = is_enabled
                access.save()
            
            return Response({'success': True}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating company menu access: {str(e)}")
            return Response({'error': 'Failed to update menu access'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
