from django.urls import path
from .menu_views import UserMenuAccessView, MenuCategoriesView, CompanyMenuManagementView, ProjectMenuAccessByProjectView, ProjectMenuAccessUpdateView
from .project_views import ProjectListView
from .test_menu_views import TestMenuView
from .simple_menu import simple_menu_data

urlpatterns = [
    path('simple/', simple_menu_data, name='simple_menu'),
    path('test/', TestMenuView.as_view(), name='test_menu'),
    path('user-menu/', UserMenuAccessView.as_view(), name='user_menu'),
    path('menu-modules/', UserMenuAccessView.as_view(), name='menu_modules'),
    path('project-menu-access/by_project/', ProjectMenuAccessByProjectView.as_view(), name='project_menu_access'),
    path('project-menu-access/update_project_access/', ProjectMenuAccessUpdateView.as_view(), name='project_menu_access_update'),
    path('project-menu-access/user_menu_access/', UserMenuAccessView.as_view(), name='user_menu_access_legacy'),
    path('projects/', ProjectListView.as_view(), name='projects_simple'),
    path('categories/', MenuCategoriesView.as_view(), name='menu_categories'),
    path('company-access/', CompanyMenuManagementView.as_view(), name='company_menu_access'),
]
