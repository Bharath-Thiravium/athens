# Menu Management Module – Technical Blueprint (Current Working State)

## 1. Module Overview

**Module Name:** Menu Management System  
**Purpose & Business Objective:** Provides project-wise access control for menu modules in the Athens EHS system, allowing master administrators to configure which features are available to users in different projects.  
**Key Users / Roles:**
- Master Admin: Full configuration access
- Project Admins: View-only access to their project's menu configuration
- Regular Users: Consume configured menu items based on project access

**Dependency on other modules:**
- Authentication module (user management, project isolation)
- All feature modules (controlled by menu access)
- Frontend dashboard system (menu rendering)

## 2. Functional Scope

**Features included:**
- Menu module definition and management
- Project-wise menu access configuration
- User-specific menu item retrieval based on project access
- Master admin interface for menu configuration
- API endpoints for menu CRUD operations
- Dynamic menu rendering in frontend

**Features explicitly excluded:**
- Role-based permissions within modules (handled by individual modules)
- User-level menu customization (only project-level)
- Menu module creation through UI (handled via management commands)

**Role-based access control behavior:**
- Master Admin: Can configure menu access for any project
- Project Admin: Cannot modify menu configuration
- Regular Users: Receive filtered menu based on project configuration

**Visibility rules:**
- Menu Management interface only visible to Master Admin
- Menu modules populated via Django management command
- Project menu access controlled via database configuration

## 3. Process Flow (End-to-End)

### Menu Configuration Flow (Master Admin):
1. **Trigger:** Master admin accesses Menu Management interface
2. **Validation:** System verifies master admin permissions
3. **Processing:** 
   - Load all available menu modules from database
   - Load all projects from database
   - Display configuration interface
4. **User Action:** Select project and configure module access
5. **System Action:** Save configuration to ProjectMenuAccess table
6. **Response:** Confirmation message and updated interface

### Menu Retrieval Flow (Regular User):
1. **Trigger:** User logs in and dashboard loads
2. **Validation:** System verifies user authentication and project association
3. **Processing:**
   - Query user's project from authentication data
   - Retrieve enabled menu modules for user's project
   - Filter menu items based on user role and permissions
4. **Response:** Return filtered menu structure to frontend
5. **Frontend Action:** Render navigation menu with available options

### Edge cases and constraints:
- Users without project association receive empty menu
- Master admins bypass project-based filtering
- Unapproved users receive restricted menu regardless of project configuration
- API errors result in fallback to basic menu structure

## 4. Technical Architecture

### Frontend components involved:

**Pages:**
- `/src/features/admin/components/MenuManagement.tsx` - Main configuration interface

**Components:**
- Menu configuration table with project selection
- Module toggle switches
- Save/refresh functionality

**State management:**
- Local component state for menu modules, projects, and access configuration
- API calls for data persistence

### Backend components involved:

**Views / Controllers:**
- `MenuModuleViewSet` - CRUD operations for menu modules
- `ProjectMenuAccessViewSet` - Project-specific access configuration
- `save_menu_config` - Simple configuration save endpoint
- `test_menu` - API health check endpoint

**Services:**
- Menu access filtering logic
- Project-based permission checking

**Models:**
- `MenuModule` - Available menu modules
- `ProjectMenuAccess` - Project-wise access control
- `Project` - Project information (from authentication module)

### APIs used:

**Endpoints:**
- `GET /api/menu/menu-modules/` - Retrieve all menu modules
- `GET /api/menu/project-menu-access/` - Retrieve access configurations
- `GET /api/menu/project-menu-access/by_project/?project_id=X` - Project-specific access
- `POST /api/menu/project-menu-access/update_project_access/` - Update project access
- `GET /api/menu/project-menu-access/user_menu_access/` - User's enabled modules

**Request/Response structure:**
```json
// Menu Module Response
{
  "id": 1,
  "name": "Dashboard",
  "key": "dashboard",
  "icon": "DashboardOutlined",
  "description": "",
  "is_active": true
}

// User Menu Access Response
[
  {
    "menu_module__key": "dashboard",
    "menu_module__name": "Dashboard", 
    "menu_module__icon": "DashboardOutlined"
  }
]
```

### Database entities:

**Tables:**
- `authentication_menumodule`
- `authentication_projectmenuaccess`
- `authentication_project`

**Key fields:**
- MenuModule: id, name, key, icon, description, is_active
- ProjectMenuAccess: id, project_id, menu_module_id, is_enabled, created_by_id
- Project: id, projectName, athens_tenant_id

**Relationships:**
- ProjectMenuAccess.project → Project (ForeignKey)
- ProjectMenuAccess.menu_module → MenuModule (ForeignKey)
- ProjectMenuAccess.created_by → CustomUser (ForeignKey)

## 5. File-Level Blueprint (CRITICAL)

### Backend Files:

**`/backend/authentication/menu_models.py`**
- **Responsibility:** Define database models for menu system
- **Key classes:** MenuModule, ProjectMenuAccess
- **Inputs:** Django model fields and relationships
- **Outputs:** Database table structure
- **Important conditions:** Unique constraints on project+menu_module combination

**`/backend/authentication/menu_serializers.py`**
- **Responsibility:** API serialization for menu data
- **Key classes:** MenuModuleSerializer, ProjectMenuAccessSerializer, ProjectMenuConfigSerializer
- **Inputs:** Model instances
- **Outputs:** JSON-serialized data
- **Important conditions:** Read-only fields for related model data

**`/backend/authentication/menu_views.py`**
- **Responsibility:** API endpoints for menu management
- **Key functions:** MenuModuleViewSet, ProjectMenuAccessViewSet, user_menu_access
- **Inputs:** HTTP requests with authentication
- **Outputs:** JSON responses with menu data
- **Important conditions:** Authentication required, project isolation enforced

**`/backend/authentication/menu_urls.py`**
- **Responsibility:** URL routing for menu APIs
- **Key functions:** Router configuration and URL patterns
- **Inputs:** URL patterns
- **Outputs:** Routed API endpoints
- **Important conditions:** Proper namespace and routing structure

**`/backend/authentication/management/commands/populate_menu_modules.py`**
- **Responsibility:** Initialize default menu modules
- **Key functions:** Command.handle()
- **Inputs:** Predefined menu module data
- **Outputs:** Database records for menu modules
- **Important conditions:** Idempotent operation (get_or_create)

### Frontend Files:

**`/frontend/src/features/admin/components/MenuManagement.tsx`**
- **Responsibility:** Master admin interface for menu configuration
- **Key functions:** loadInitialData, handleMenuToggle, saveMenuConfiguration
- **Inputs:** User interactions, API responses
- **Outputs:** Updated menu configuration
- **Important conditions:** Master admin role required, project selection required

**`/frontend/src/features/dashboard/config/menuConfig.tsx`**
- **Responsibility:** Static menu configuration and user-based filtering
- **Key functions:** getMenuItemsForUser, getMenuConfig
- **Inputs:** User type, authentication status, approval status
- **Outputs:** Filtered menu items array
- **Important conditions:** Role-based filtering, approval status checking

**`/frontend/src/features/dashboard/config/projectMenuConfig.tsx`**
- **Responsibility:** Project-based dynamic menu configuration
- **Key functions:** getProjectBasedMenuItems, getEnhancedMenuItemsForUser
- **Inputs:** User authentication, project association
- **Outputs:** Project-filtered menu items
- **Important conditions:** API call for user menu access, fallback handling

**`/frontend/src/features/dashboard/config/enhancedMenuConfig.tsx`**
- **Responsibility:** Enhanced menu configuration with project-wise access control
- **Key functions:** getMenuItemsForUser, getMenuConfig
- **Inputs:** User authentication data
- **Outputs:** Dynamically configured menu structure
- **Important conditions:** Async menu loading, error handling

## 6. Configuration & Setup

### Environment variables used:
- Standard Django database configuration
- Authentication settings from main Django settings

### Feature flags:
- No specific feature flags, controlled by database configuration

### Permissions & roles mapping:
- Master Admin: Full menu management access
- Project Admin: View-only access to project configuration
- Regular Users: Consume configured menu items

### Project / tenant / company isolation logic:
- Menu modules are global (not tenant-specific)
- Project menu access is project-specific
- User menu access filtered by user's project association

### Default values & assumptions:
- New menu modules default to active (is_active=True)
- New project menu access defaults to enabled (is_enabled=True)
- Users without project association receive empty menu
- Master admins bypass all project-based filtering

## 7. Integration Points

### Modules this depends on:
- Authentication module (User, Project models)
- Django REST Framework (API functionality)
- Frontend routing system (menu navigation)

### Modules that depend on this:
- Dashboard layout system (menu rendering)
- All feature modules (access control)
- Navigation components (menu structure)

### External services:
- None (self-contained within Django application)

### Auth / token / session usage:
- JWT authentication for API access
- User project association for menu filtering
- Role-based access control for configuration interface

## 8. Current Working State Validation

### Expected UI behavior:
- Master admin sees "Menu Management" option in navigation
- Menu Management interface loads with project selector and module list
- Toggle switches reflect current project configuration
- Save operation shows success message and updates interface
- Regular users see filtered menu based on project configuration

### Expected API responses:
- `/api/menu/menu-modules/` returns array of all menu modules
- `/api/menu/project-menu-access/user_menu_access/` returns user's enabled modules
- POST operations return success status and confirmation message
- Authentication errors return 401/403 status codes

### Expected DB state:
- MenuModule table populated with default modules
- ProjectMenuAccess table contains project-specific configurations
- Unique constraints enforced on project+menu_module combinations
- Foreign key relationships maintained

### Logs or indicators of success:
- Console logs in menu views showing user authentication details
- API request/response logging in browser network tab
- Django admin interface shows correct database records
- Frontend console shows successful menu loading

## 9. Known Constraints & Design Decisions

### Why certain approaches were used:
- Project-based access control chosen over user-level for scalability
- Management command used for menu module initialization to ensure consistency
- Separate serializers for different API use cases (list vs. configuration)
- Frontend fallback menus to handle API failures gracefully

### Intentional limitations:
- No user-level menu customization (only project-level)
- Menu modules cannot be created through UI (requires management command)
- No hierarchical menu permissions (flat structure)
- No real-time menu updates (requires page refresh)

### Performance or scalability considerations:
- Menu access queries optimized with select_related
- Frontend caches menu configuration in component state
- Database indexes on foreign key relationships
- Pagination disabled for menu APIs (small datasets expected)

## 10. Future Reference Notes

### What must NOT be changed casually:
- Menu module keys (used for frontend routing)
- Database model relationships (affects data integrity)
- API endpoint URLs (frontend dependencies)
- Authentication requirements (security implications)

### Files that are high-risk:
- `menu_models.py` - Database schema changes require migrations
- `menu_views.py` - Authentication logic affects security
- `menuConfig.tsx` - Menu structure affects entire application navigation
- URL routing files - Changes break frontend navigation

### Areas where bugs are likely if modified:
- User authentication checking in menu views
- Project association logic in user menu access
- Frontend menu item key matching
- Database constraint violations in ProjectMenuAccess

### Recommended debugging entry points:
- Start with `/api/menu/test/` endpoint to verify API connectivity
- Check user authentication in menu views console logs
- Verify project association in user profile data
- Examine database records in Django admin interface
- Use browser network tab to trace API request/response flow