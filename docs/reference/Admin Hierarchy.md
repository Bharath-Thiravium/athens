User Hierarchy & Types
1. Master Admin (master)
Highest level system administrator

Access: Complete system control

Responsibilities:

Manage all projects across the system

Create and manage all admin users

System settings and configuration

System logs and backup management

Full CRUD access to all modules

2. Project Admin (projectadmin)
Sub-types based on admin_type:

2.1 Client Admin (client)
Role: Client organization representative

Access: Full project management within their project scope

Responsibilities:

Manage project-specific users

Oversee all EHS activities for their project

Approve permits and safety observations

Generate reports and analytics

2.2 EPC Admin (epc)
Role: Engineering, Procurement & Construction contractor

Access: Full project management capabilities

Responsibilities:

Manage construction and engineering activities

Handle permit-to-work processes

Manage worker safety and training

Quality management oversight

2.3 Contractor Admin (contractor)
Role: Sub-contractor organization lead

Access: Project-specific management rights

Responsibilities:

Manage contractor workers and activities

Submit safety observations and incident reports

Handle training and compliance

Coordinate with client and EPC teams

3. Admin Users (adminuser)
Sub-types based on their creator's admin_type:

3.1 Client User (clientuser)
Role: Client organization staff

Access: Operational level access

Responsibilities:

Daily EHS operations

Worker management and attendance

Safety observations and incident reporting

Training coordination

3.2 EPC User (epcuser)
Role: EPC contractor staff

Access: Construction and engineering operations

Responsibilities:

Site operations management

Quality inspections

Permit applications and approvals

Environmental monitoring

3.3 Contractor User (contractoruser)
Role: Sub-contractor staff

Access: Limited operational access

Responsibilities:

Worker safety compliance

Basic reporting and documentation

Training participation

Equipment and material management

Module Access Matrix
Core Modules Available to All User Types:
Dashboard - Overview and analytics

Voice Translator - Multi-language communication

Training Management - Induction and job training

Safety Observation - Safety reporting and monitoring

Incident Management - Incident reporting and tracking

Permits to Work (PTW) - Work authorization system

Inspections - Quality and safety inspections

ESG Management - Environmental, Social, Governance

Quality Management - Quality control and assurance

Restricted Access Modules:
Master Admin Only:
System Settings

System Logs

Backup Management

Cross-project analytics

Project Admin Level:
User Management (create/edit admin users)

Advanced reporting and analytics

Project configuration

Approval workflows

Admin User Level:
Worker Management

Attendance tracking

Operational reporting

Day-to-day EHS activities

Permission System
Approval Workflow:
New users must complete profile details

Profiles require approval from higher-level users

Unapproved users have restricted menu access

Data Access Rules:
Users can only access data within their assigned project

Admin users can only manage workers they created

Project admins can view but not edit worker details

Master admin has cross-project visibility

ESG Specific Roles:
ESG Administrator

ESG Data Owner

ESG Auditor

Environmental Officer

Sustainability Manager

Key Features by User Type
Master Admin Features:
Multi-project dashboard

System-wide user management

Global analytics and reporting

System maintenance tools

Project Admin Features:
Project-specific dashboards

Team management

Comprehensive module access

Advanced reporting capabilities

Approval authority for permits and incidents

Admin User Features:
Operational dashboards

Worker and attendance management

Safety and quality reporting

Training coordination

Basic analytics

Security & Compliance:
Role-based access control (RBAC)

Digital signature templates

Audit trails for all actions

Secure file uploads and document management

Multi-level approval workflows

This hierarchical structure ensures proper segregation of duties while maintaining operational efficiency across different organizational levels in the EHS management system.
