# Athens Tenant + Collaboration Contract

## Scope
This contract defines the required invariants and enforcement rules for the Athens SaaS platform:
- DB-per-tenant architecture
- User model U2 (separate users per tenant)
- Collaboration C1a federated sharing (READ-only cross-tenant)
- Tenant truth derived only from authenticated user + tenant DB used for authentication

## Core Invariants (MUST)
- Tenant DB routing MUST be derived only from authenticated user context.
- Tenant DB selection MUST NOT be accepted from request headers, body, or query parameters.
- All tenant-owned reads MUST be project-scoped inside the tenant DB.
- All cross-tenant data access MUST be read-only and policy gated.
- Cross-tenant writes MUST be denied (HTTP 403) in all domains.
- JWT claims MUST NOT be trusted for routing unless signature is verified.
- WebSocket auth MUST NOT use query-string tokens.
- WebSocket connections MUST validate Origin and enforce tenant + project or collaboration scoping.
- Every cross-tenant access MUST be audited in the Control Plane.

## Login Flow (Option 3 — REQUIRED)
1) User submits email to a Control Plane endpoint.
2) Control Plane returns a list of tenant companies where:
   - a user exists in that tenant DB, OR
   - an invitation exists in Control Plane.
3) User selects a tenant company.
4) User authenticates against the selected tenant DB only.
5) Server issues tenant-bound JWT after successful auth.
6) Tenant routing MUST still be derived from server-side binding, not unsigned JWT claims.

## Control Plane (Global DB) Requirements
- Store Tenants, Tenant DB connection references (no secrets), subscriptions, and collaboration contracts.
- Collaboration entities:
  - CollaborationProject
  - CollaborationMembership
  - CollaborationSharePolicy (READ-only allowed actions)
  - ProjectLink (maps collaboration project to tenant-local project IDs)
- Superadmin-only APIs for onboarding, subscription control, collaboration setup, and audit review.

## Tenant Plane (Per-tenant DB) Requirements
- All operational data lives in the tenant DB.
- User model is tenant-local (U2): same email across tenants does not imply shared identity.
- Project scoping is mandatory for every domain endpoint.

## Collaboration (C1a Federated READ)
- When a collaboration project is referenced:
  - Verify tenant membership from Control Plane.
  - Check SharePolicy for domain and READ permission.
  - Fetch from peer tenant DBs in READ-only mode.
  - Merge results with provenance fields:
    - owner_tenant_id
    - source_tenant_id
    - collaboration_project_id
- Writes MUST be rejected with 403 unless executed in owner tenant DB and explicitly permitted (current default: deny).

## WebSocket Rules
- No JWT in query string.
- Authentication via Authorization header, secure cookie, or subprotocol token.
- Origin validation required at ASGI + Nginx.
- Group names MUST be server-controlled and scoped by tenant + project or collaboration_project_id.

## Auditability
- Every cross-tenant read MUST write an AuditLog entry in Control Plane.
- AuditLog fields: who, action, target, tenant_id, collaboration_project_id, request_id, timestamp.

## Mandatory Compliance Tracking
- docs/action_plan_checklist.md MUST be updated for every module change.
- docs/coverage_matrix.md MUST be updated whenever endpoints/consumers change.
- Tests MUST exist for cross-tenant deny, collab allow (READ), and cross-tenant write deny.
