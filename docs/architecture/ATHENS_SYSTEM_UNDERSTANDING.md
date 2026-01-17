# Athens EHS System - Working Understanding

This document captures my current understanding of the codebase based on a focused read of core configuration, backend modules, and frontend entry points. It is not a full exhaustive inventory of every file, but it reflects the primary architecture, cross-cutting concerns, and major flows.

## 1. System Overview
- Domain: Environmental, Health, and Safety (EHS) platform with multi-tenant isolation, project-based workflows, and multiple modules (inspection, incident management, safety observation, training, etc.).
- Stack:
  - Backend: Django 5.x + Django REST Framework + Channels (WebSocket), PostgreSQL (primary) with SQLite backup.
  - Frontend: React + TypeScript + Vite + Ant Design.
  - Deployment: Docker + Nginx, with support for traditional local dev via Vite and `manage.py runserver`.
- Core cross-cutting concerns:
  - Multi-tenant (company-level) isolation using `athens_tenant_id`.
  - Project-based scoping within a tenant.
  - JWT-based authentication and authorization (DRF SimpleJWT).
  - Real-time notifications via WebSockets.

Key entry points:
- Backend settings: `backend/backend/settings.py`
- Backend URL map: `backend/backend/urls.py`
- Frontend entry: `frontend/src/main.tsx`
- Frontend routing: `frontend/src/app/App.tsx`

## 2. Backend Architecture

### 2.1 App Layout
The backend is a multi-app Django monolith. Key apps include:
- `authentication`: custom user, project model, tenant isolation, JWT auth, menu system, and signature workflows.
- `permissions`: escalation and temporary permission grants.
- `inspection`: inspection workflows and many specialized inspection form types.
- `incidentmanagement`, `safetyobservation`, `inductiontraining`, `jobtraining`, `ptw`, `mom`, `manpower`, `worker`, `system`, `environment`, `quality`, `voice_translator`, `chatbox`, `tbt`, `ai_bot` (partially disabled in settings).

### 2.2 Multi-Tenant Isolation and Permissions
There are two isolation layers:
1. **Company (tenant) isolation** via `athens_tenant_id`.
   - Enforced in `authentication/company_isolation.py` middleware using DB session variable `current_athens_tenant_id`.
   - `TenantIsolationMixin` applies tenant filtering for model queries and ensures created/updated data stays within the tenant.
2. **Tenant resolution** via `authentication/tenant_middleware.py` + `tenant_resolver.py`.
   - Extracts tenant from JWT, header (`X-Athens-Tenant-ID`), or query parameter.
   - Validates against `AthensTenant` model and attaches context to requests.

Module-level access control:
- `TenantPermissionMiddleware` blocks access to module routes that are not enabled for a tenant.

Escalation-based permissions:
- `permissions/escalation.py` and `permissions/decorators.py` enforce edit/delete access based on escalation rules and temporary permission grants.

### 2.3 Authentication and User Models
Key models in `backend/authentication/models.py`:
- `Project`: business project entity with category, location, and dates. Projects are linked to one primary tenant (`athens_tenant_id`) but can involve other companies via client/EPC/contractor IDs.
- `CustomUser`: custom auth model with `user_type`, `admin_type`, and `project` assignment. Contains tenant ID and ESG fields.
- `UserDetail`, `CompanyDetail`, `AdminDetail`: user profile extensions and company details, including signatures and approval tracking.
- Digital signature workflows: `UserSignature`, `FormSignature`, `SignatureAuditLog`, `SignatureRequest`.

Authentication config:
- SimpleJWT with 60-minute access tokens, refresh tokens rotated.
- Debug mode and permissive CORS are currently enabled in settings.

### 2.4 Inspections Module (Backend)
Core models in `backend/inspection/models.py`:
- `Inspection`: standard inspection lifecycle with status, priority, inspector, project, timestamps.
- `InspectionItem`: checklist items tied to inspections.
- `InspectionReport`: report summary generated when inspection completes.

Main API endpoints in `backend/inspection/urls.py`:
- `inspections`, `inspection-items`, `inspection-reports`, plus many form-specific endpoints (AC Cable, ACDB, HT Cable, etc.).

Specialized inspection forms:
- Implemented in `backend/inspection/models_forms.py`, `serializers_forms.py`, and `views_forms.py`.
- `BaseInspectionFormViewSet` creates a completed `Inspection` record for each form submission and ties it to a form-specific model.
- Update/delete permissions enforce creator ownership and admin role requirements.

### 2.5 Other Module Observations (Sampled)
- Safety Observation: `backend/safetyobservation/models.py` includes risk scoring, escalation, and file attachments.
- Incident Management: `backend/incidentmanagement/models.py` is large and comprehensive (8D process, risk analysis, cost impact, etc.), with tenant + project links.

## 3. Frontend Architecture

### 3.1 Entry and Routing
Entrypoint: `frontend/src/main.tsx`
- Uses Ant Design `ConfigProvider` with a custom theme.
- Wraps the app in `ThemeProvider`, `NotificationsProvider`, and `BrowserRouter`.

Routes: `frontend/src/app/App.tsx`
- Central route tree for dashboard and all feature pages.
- Role-based access checks via `RoleBasedRoute`.
- Extensive inspection and ESG route coverage.

### 3.2 Auth, API, and Tenant Context
`frontend/src/common/store/authStore.ts`:
- Zustand-based auth state (token, refresh, projectId, user type, etc.).
- Token expiry tracked in localStorage.

`frontend/src/common/utils/axiosetup.ts`:
- Attaches JWT on every request.
- Adds `X-Athens-Tenant-ID` based on projectId.
- Handles refresh logic and logout behavior on 401.
- Blocks requests without auth for non-auth endpoints.

### 3.3 Notifications
`frontend/src/common/contexts/NotificationsContext.tsx`:
- Wraps WebSocket notification service.
- Tracks unread counts and dispatches updates on incoming messages.

### 3.4 Inspection UI (Frontend)
`frontend/src/features/inspection/components/InspectionReports.tsx`:
- Fetches reports from `inspectionService`.
- Provides filtering by status, type, date, search.
- Uses Ant Design table with basic actions (view/download placeholders).

`frontend/src/features/inspection/services/inspectionService.ts`:
- Mirrors backend routes for inspections, items, reports, and specialized forms.

## 4. Cross-Cutting Data Flow

1. User logs in and receives JWT. `authStore` persists tokens and projectId.
2. API requests:
   - JWT in Authorization header.
   - `X-Athens-Tenant-ID` header set from projectId.
3. Backend:
   - `AthensTenantMiddleware` resolves tenant context.
   - `CompanyTenantIsolationMiddleware` applies DB session tenant variable.
   - `TenantPermissionMiddleware` blocks disabled modules.
4. Domain APIs:
   - DRF viewsets provide CRUD operations.
   - Permissions decorators enforce escalation or temporary grants.
5. Notifications:
   - WebSocket channel used for real-time alerts.

## 5. Operations and Deployments
Primary docs and scripts:
- Quick start and maintenance: `README.md`, `DOCKER_SETUP_GUIDE.md`, `diagnose_system.sh`, `docker-setup.sh`.
- Nginx config: `nginx/nginx.conf`.

## 6. Notable Risks / Gaps
- Settings use `DEBUG = True` and `CORS_ALLOW_ALL_ORIGINS = True` in backend, which is not production-safe.
- Some tenant middleware/URL mapping uses path prefixes that may not fully match all DRF routes (worth verifying).
- Inspection report UI has placeholder actions and analytics stub data in `InspectionReports.tsx`.
- There is a mix of project-based and tenant-based isolation; needs careful validation of which models carry `athens_tenant_id` vs `project`.

## 7. Immediate Follow-Ups (If Needed)
If you want deeper coverage, the next layers to read would be:
- `backend/inspection/models_forms.py` and `serializers_forms.py` for inspection form fields.
- `backend/authentication` viewsets and serializers for full auth flows.
- `frontend/src/features/*` for module-specific UI behavior.
*** End Patch}윈 code: 0 error? but check. Let's run apply_patch. Need to send patch. We'll re-run with actual. reading. Actually I inserted patch inside tool call? The tool responded? I see "assistant to=functions.apply_patch" with content but not actual response because I included outside? It seems to include patch in parameters. It's fine. Wait show tool output? none? I didn't see response; I wrote patch in tool call with JSON. It's ok? I need output. Hmm I used apply_patch with JSON, but tool expects FREEFORM not JSON. Should call as freeform. Need to redo. No output indicates it might have failed? I see in response no tool output. I must redo correctly. Use apply_patch with content only. Do now. Let’s re-run correctly. We'll ensure not to include JSON. Use apply_patch. We'll check if file created. We'll use rg? We'll just reapply. Let's do. We'll call apply_patch. to=functions.apply_patch since freeform. We'll include patch. Let's do.】
