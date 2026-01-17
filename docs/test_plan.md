# Athens Test Plan

## Goals
- Validate tenant DB routing is derived from authenticated user context only.
- Verify project scoping for all tenant-owned data.
- Ensure collaboration reads are policy-gated and read-only.
- Ensure cross-tenant writes are always rejected (403).
- Ensure WebSocket auth uses secure tokens (no query string) and origin validation.

## Test Categories
1) Control Plane (global DB)
- Tenant creation
- Subscription changes
- Collaboration project + membership + policy enforcement
- Audit log entries

2) Auth + Tenant Routing (U2, Option 3)
- Same email across multiple tenants returns list of tenants.
- Auth attempts against wrong tenant DB fail.
- JWT is tenant-bound but routing uses server-side binding.

3) Tenant Isolation
- All domain endpoints are project-scoped.
- Cross-tenant access returns 403/404.

4) Collaboration Read-only
- Federated read allowed only when SharePolicy permits.
- No write allowed across tenants (403).
- Provenance fields included in responses.

5) WebSockets
- Reject invalid Origin.
- Reject missing/invalid auth.
- Allow only scoped group membership (tenant + project or collaboration_project_id).

## Suggested Commands (adjust to project tooling)
- Backend tests: `python manage.py test`
- Specific app tests: `python manage.py test control_plane authentication <app>`
- Channels tests: `python manage.py test authentication.tests.test_websockets`

## Notes
- Avoid tests that modify production-like data outside test DBs.
- Use factory fixtures for multi-tenant scenarios.
