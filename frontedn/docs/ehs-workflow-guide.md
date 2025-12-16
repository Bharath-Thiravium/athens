# EHS Management System — Workflow Guide

This guide details end-to-end workflows for core EHS modules, including data responsibilities, states, roles, and approvals.

## 1. Role & Approval Model
- usertype (route access): master, client, epc, contractor, clientuser, epcuser, contractoruser
- django_user_type (approval class): projectadmin (completes Admin Detail), adminuser (completes Profile)
- Master is exempt from approval gating.

## 2. Authentication & Session Flow
1. User logs in; JWT access + refresh issued
2. Axios attaches Authorization Bearer token; CSRF header on non-GET
3. 401 triggers refresh; invalid/blacklisted → forced logout
4. RoleBasedRoute guards by usertype; approval gating checks django_user_type

## 3. Profile Completion & Approval
### projectadmin (Admin Detail)
- Trigger: Banner/CTA → /dashboard/admindetail
- First-time: admin/me 404/403 → show blank form, prefill username
- Submit → pending approval by master
- Master reviews & approves → full menu access enabled

### adminuser (Profile)
- Trigger: Banner/CTA → /dashboard/profile
- Submit → pending approval (as configured)
- Approval → full access for user-level features

## 4. Incident Management Workflow
1. Report Incident
   - Inputs: time, location, type, description, attachments
   - Optional: immediate actions
2. Triage & Classification
   - Severity, category, root cause hypothesis
3. Corrective/Preventive Actions (CAPA)
   - Assign action owners, due dates
4. Verification & Closure
   - Evidence upload; approvals
5. Analytics
   - KPIs, trends, recurrence analysis

Roles:
- Reporter (any authenticated user allowed by policy)
- Incident Manager (client/epc/contractor admin roles)
- Approver (master or designated)

## 5. Safety Observation Workflow
1. Log observation (unsafe act/condition)
2. Risk ranking; assign actions
3. Follow-up; corrective steps
4. Closeout and review
5. Dashboard trends by site/department

Roles:
- All staff (capture)
- Supervisors (review/assign)
- HSE team (analysis)

## 6. Training (Induction & Job)
1. Enrollment (new joiners / role change)
2. Session scheduling and delivery
3. Attendance capture; assessment
4. Certification / competency update
5. Expiry reminders & refreshers

Data:
- Trainee, trainer, syllabus, assessment, certificate

## 7. Permit to Work (PTW)
1. Permit Request
   - Job details, location, duration
2. Hazard Identification & Controls
   - JSA, PPE, isolation, monitoring
3. Authorization
   - Permit issuer → accept/deny
4. Active Monitoring
   - Spot checks, gas tests, shift handovers
5. Closure & Post-Review
   - Sign-off, lessons learned

Roles:
- Requester (contractoruser/adminuser)
- Issuer/Approver (client/epc)
- HSE oversight (projectadmin/master)

## 8. Meetings/MoM
1. Schedule meeting; send invites (notifications)
2. Live session notes; decisions and action items
3. Distribution; action follow-up
4. Closeout and archival

## 9. Manpower & Attendance
1. Daily attendance input (per contractor/site)
2. Visualization by project/date/contractor
3. Export for payroll/planning

## 10. Company Details & Auto-Fill
- EPC: auto-fill PAN, GST, and logo for Admin Detail when available
- Sync company logo to UI headers where applicable

## 11. Notifications & Tasks
- WebSocket-driven alerts for approvals, meetings, and critical changes
- Inbox UI and toast notifications

## 12. Data Lifecycle & Retention
- Uploads: photos, signatures, attachments (object storage)
- Suggested retention policies by module (per compliance)
- Export: CSV/PDF for audits

## 13. Audit Readiness
- Immutable approvals (timestamps, user IDs)
- Digital signatures (admin/user templates)
- Traceability: who, when, what changed

## 14. Exceptions & Error Handling
- 404/403 on first-time admin detail → render blank form
- 401 with invalid token → forced logout with message
- Network fallbacks and user feedback to retry

## 15. KPIs & Reports (Examples)
- Incident closeout time; CAPA SLA adherence
- Observation count by department; risk distribution
- Training completion rate; certification expiries
- PTW durations; non-compliance events
- Attendance trends by contractor

## 16. Implementation Checklist
- Configure roles/usertypes and django_user_types
- Company details (logo, PAN/GST)
- Enable modules and routing
- Notification endpoints and policy
- Backup and monitoring

## 17. Handover & Admin SOP
- Approver matrix maintenance
- Periodic data quality checks
- Quarterly compliance review
- Access reviews and deprovisioning

