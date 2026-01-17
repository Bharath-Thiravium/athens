# Coverage Matrix (Endpoints + Consumers)

Legend:
- Tenant enforced? / Project enforced? / Collaboration read? / Cross-tenant write denied? / Tests?
- Values: PASS / FAIL / TBD / N/A

## Core Routes
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /admin/ | backend/backend/urls.py | N/A | N/A | N/A | N/A | TBD | Django admin |
| /health/ | backend/backend/urls.py | TBD | N/A | N/A | N/A | TBD | health_check |
| / (redirect to /admin/) | backend/backend/urls.py | N/A | N/A | N/A | N/A | N/A | RedirectView |

## Authentication (/authentication/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /authentication/ | backend/authentication/urls.py | TBD | N/A | N/A | N/A | TBD | index |
| /authentication/login/ | backend/authentication/urls.py | TBD | N/A | N/A | N/A | TBD | SecureCompatibleLoginAPIView |
| /authentication/login/legacy/ | backend/authentication/urls.py | TBD | N/A | N/A | N/A | TBD | CustomTokenObtainPairView |
| /authentication/login/tenant/ | backend/authentication/urls.py | TBD | N/A | N/A | N/A | TBD | TenantLoginAPIView |
| /authentication/token/refresh/ | backend/authentication/urls.py | TBD | N/A | N/A | N/A | TBD | TokenRefreshView |
| /authentication/logout/ | backend/authentication/urls.py | TBD | N/A | N/A | N/A | TBD | LogoutView |
| /authentication/project/create/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectCreateView |
| /authentication/project/list/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectListView |
| /authentication/project/update/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectUpdateView |
| /authentication/project/delete/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectDeleteView |
| /authentication/project/cleanup/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectCleanupView |
| /authentication/master-admin/projects/create/ | backend/authentication/urls.py | TBD | N/A | N/A | TBD | TBD | MasterAdminProjectCreateView |
| /authentication/master-admin/projects/create-admins/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | MasterAdminCreateProjectAdminsView |
| /authentication/master-admin/projects/<int:project_id>/admins/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | MasterAdminCreateProjectAdminsView |
| /authentication/master-admin/projects/admin/delete/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | MasterAdminDeleteProjectAdminView |
| /authentication/master-admin/reset-admin-password/ | backend/authentication/urls.py | TBD | N/A | N/A | TBD | TBD | MasterAdminResetAdminPasswordView |
| /authentication/master-admin/create/ | backend/authentication/urls.py | TBD | N/A | N/A | TBD | TBD | CreateMasterAdminView |
| /authentication/admin/user-by-username/<str:username>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | MasterAdminGetUserByUsernameView |
| /authentication/admin/reset-password/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectAdminResetPasswordView |
| /authentication/admin/list/<int:project_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectAdminListByProjectView |
| /authentication/projectadminuser/create/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectAdminUserCreateView |
| /authentication/projectadminuser/list/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectAdminUserListView |
| /authentication/projectadminuser/update/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectAdminUserUpdateView |
| /authentication/projectadminuser/delete/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectAdminUserDeleteView |
| /authentication/projectadminuser/reset-password/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ProjectAdminUserResetPasswordView |
| /authentication/userdetail/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UserDetailRetrieveUpdateView |
| /authentication/userdetail/approve/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UserDetailApproveView |
| /authentication/userdetail/pending/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | PendingUserDetailsForAdminView |
| /authentication/userdetail/pending/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UserDetailPendingView |
| /authentication/companydetail/ | backend/authentication/urls.py | TBD | N/A | N/A | TBD | TBD | CompanyDetailRetrieveUpdateView |
| /authentication/epcuser-list/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | EPCUserListAPIView |
| /authentication/project/<int:project_id>/contractor-company/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ContractorCompanyNameView |
| /authentication/epc-clientuser-list/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | EPCAndClientUserListAPIView |
| /authentication/all-adminusers/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AllAdminUsersListAPIView |
| /authentication/debug-contractors/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | DebugContractorListAPIView |
| /authentication/contractoruser-list/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | ContractorUsersListAPIView |
| /authentication/users-overview/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UsersByTypeOverviewAPIView |
| /authentication/master-admin/delete-admin-user/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | MasterAdminDeleteAdminUserView |
| /authentication/notifications/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationListView |
| /authentication/notifications/create/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationCreateView |
| /authentication/notifications/<int:pk>/read/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationMarkReadView |
| /authentication/notifications/mark-all-read/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationMarkAllReadView |
| /authentication/notifications/<int:pk>/delete/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationDeleteView |
| /authentication/notifications/unread-count/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationUnreadCountView |
| /authentication/notifications/preferences/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationPreferenceView |
| /authentication/notifications/broadcast/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | NotificationBroadcastView |
| /authentication/api/attendance/check-in/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | check_in |
| /authentication/api/attendance/check-out/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | check_out |
| /authentication/api/attendance/status/<int:project_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | get_attendance_status |
| /authentication/compare-faces/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | compare_faces_api |
| /authentication/test-face-recognition/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | test_face_recognition_setup |
| /authentication/user-face-info/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | get_user_face_info |
| /authentication/admin/me/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | CurrentAdminDetailView |
| /authentication/user/project/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | CurrentUserProjectView |
| /authentication/admin/detail/update/<str:usertype>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AdminDetailUpdateView |
| /authentication/admin/update/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AdminDetailUpdateByMasterView |
| /authentication/master-admin/ | backend/authentication/urls.py | TBD | N/A | N/A | TBD | TBD | MasterAdminView |
| /authentication/admin/pending/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AdminPendingDetailView |
| /authentication/admin/detail/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AdminDetailView |
| /authentication/admin/detail/update-by-master/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AdminDetailUpdateByMasterView |
| /authentication/admin/detail/approve/<int:user_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AdminDetailApproveView |
| /authentication/dashboard/overview/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | dashboard_overview |
| /authentication/admin/dashboard/consolidated/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | MenuManagementStatsView |
| /authentication/menu/dashboard/stats/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | MenuManagementStatsView |
| /authentication/company-data/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UnifiedCompanyDataView |
| /authentication/current-user-profile/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | CurrentUserProfileView |
| /authentication/project-menu-access/user_menu_access/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UserMenuAccessView |
| /authentication/modules/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UserMenuAccessView |
| /authentication/signature/template/data/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | signature_template_data_safe |
| /authentication/signature/template/preview/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | signature_template_preview_simple |
| /authentication/signature/preview/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | signature_preview |
| /authentication/signature/template/create/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | create_signature_template_simple |
| /authentication/signature/template/generate/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | generate_signature_template |
| /authentication/api/team-members/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | TeamMemberViewSet (router) |
| /authentication/api/team-members/<int:pk>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | TeamMemberViewSet (router) |
| /authentication/approval/status/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | UserApprovalStatusView |
| /authentication/admin/detail/approve/<int:admin_detail_id>/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | AdminDetailApprovalView |
| /authentication/admin/pending-details/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | PendingAdminDetailsView |
| /authentication/epc-logo-test/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | EPCLogoTestView |
| /authentication/induction-status/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | induction_status |
| /authentication/signature/save/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | save_signature |
| /authentication/signature/get/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | get_signature |
| /authentication/signature/sign-form/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | sign_form |
| /authentication/signature/get-form-signature/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | get_form_signature |
| /authentication/signature/log-print/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | log_print_action |
| /authentication/signature/request/ | backend/authentication/urls.py | TBD | TBD | N/A | TBD | TBD | signature_approval_urls.request_signature |
| /authentication/signature/request/approve/<int:request_id>/ | backend/authentication/signature_approval_urls.py | TBD | TBD | N/A | TBD | TBD | approve_signature |
| /authentication/signature/request/reject/<int:request_id>/ | backend/authentication/signature_approval_urls.py | TBD | TBD | N/A | TBD | TBD | reject_signature |
| /authentication/signature/request/worker-verify/ | backend/authentication/signature_approval_urls.py | TBD | TBD | N/A | TBD | TBD | mark_worker_verified |
| /authentication/signature/request/pending/ | backend/authentication/signature_approval_urls.py | TBD | TBD | N/A | TBD | TBD | get_signature_requests |

## Menu API (/api/menu/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/menu/simple/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | simple_menu_data |
| /api/menu/test/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | TestMenuView |
| /api/menu/user-menu/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | UserMenuAccessView |
| /api/menu/menu-modules/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | UserMenuAccessView |
| /api/menu/project-menu-access/by_project/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | UserMenuAccessView |
| /api/menu/projects/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | ProjectListView |
| /api/menu/categories/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | MenuCategoriesView |
| /api/menu/company-access/ | backend/authentication/menu_urls.py | TBD | TBD | N/A | TBD | TBD | CompanyMenuManagementView |

## Control Plane (/api/control-plane/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/control-plane/tenant-lookup/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantLookupAPIView |
| /api/control-plane/tenants/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantCompanyViewSet |
| /api/control-plane/tenants/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantCompanyViewSet |
| /api/control-plane/tenant-db-configs/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantDatabaseConfigViewSet |
| /api/control-plane/tenant-db-configs/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantDatabaseConfigViewSet |
| /api/control-plane/tenant-subscriptions/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantModuleSubscriptionViewSet |
| /api/control-plane/tenant-subscriptions/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantModuleSubscriptionViewSet |
| /api/control-plane/superadmins/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | SuperadminUserViewSet |
| /api/control-plane/superadmins/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | SuperadminUserViewSet |
| /api/control-plane/collaboration-projects/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | CollaborationProjectViewSet |
| /api/control-plane/collaboration-projects/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | CollaborationProjectViewSet |
| /api/control-plane/collaboration-memberships/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | CollaborationMembershipViewSet |
| /api/control-plane/collaboration-memberships/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | CollaborationMembershipViewSet |
| /api/control-plane/collaboration-policies/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | CollaborationSharePolicyViewSet |
| /api/control-plane/collaboration-policies/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | CollaborationSharePolicyViewSet |
| /api/control-plane/project-links/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | ProjectLinkViewSet |
| /api/control-plane/project-links/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | ProjectLinkViewSet |
| /api/control-plane/invitations/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantInvitationViewSet |
| /api/control-plane/invitations/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | TenantInvitationViewSet |
| /api/control-plane/audit-logs/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | AuditLogViewSet (read-only) |
| /api/control-plane/audit-logs/<int:pk>/ | backend/control_plane/urls.py | N/A | N/A | N/A | N/A | TBD | AuditLogViewSet (read-only) |

## Chatbox (/chatbox/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /chatbox/users/ | backend/chatbox/urls.py | PASS | PASS | N/A | PASS | TBD | UserListView |
| /chatbox/messages/ | backend/chatbox/urls.py | PASS | PASS | N/A | PASS | TBD | MessageListCreateView |
| /chatbox/read-receipts/ | backend/chatbox/urls.py | PASS | PASS | N/A | PASS | TBD | ReadReceiptView |
| /chatbox/typing-indicator/ | backend/chatbox/urls.py | PASS | PASS | N/A | PASS | TBD | TypingIndicatorView |
| /chatbox/notification-summary/ | backend/chatbox/urls.py | PASS | PASS | N/A | PASS | TBD | ChatNotificationSummaryView |
| /chatbox/download/<int:message_id>/ | backend/chatbox/urls.py | PASS | PASS | N/A | PASS | TBD | FileDownloadView |
| /chatbox/view/<int:message_id>/ | backend/chatbox/urls.py | PASS | PASS | N/A | PASS | TBD | FileViewView |

## Worker (/worker/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /worker/ | backend/worker/urls.py | PASS | PASS | N/A | PASS | TBD | WorkerViewSet (router) |
| /worker/<int:pk>/ | backend/worker/urls.py | PASS | PASS | N/A | PASS | TBD | WorkerViewSet (router) |
| /worker/check-permissions/ | backend/worker/urls.py | TBD | TBD | N/A | TBD | TBD | check_user_permissions |
| /worker/debug/ | backend/worker/urls.py | TBD | TBD | N/A | TBD | TBD | debug_worker_data |

## TBT (/tbt/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /tbt/users/list/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | user_list |
| /tbt/users/search/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | user_search |
| /tbt/attendance/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | submit_attendance |
| /tbt/trained-personnel/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | trained_personnel |
| /tbt/list/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | ToolboxTalkViewSet.list |
| /tbt/create/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | create_toolbox_talk |
| /tbt/update/<int:pk>/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | ToolboxTalkViewSet.update |
| /tbt/delete/<int:pk>/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | ToolboxTalkViewSet.destroy |
| /tbt/<int:pk>/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | ToolboxTalkViewSet.retrieve |
| /tbt/<int:pk>/attendance/ | backend/tbt/urls.py | PASS | PASS | N/A | PASS | TBD | ToolboxTalkViewSet.attendance |

## Induction (/induction/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /induction/ | backend/inductiontraining/urls.py | TBD | TBD | N/A | TBD | TBD | comprehensive_induction_endpoint |
| /induction/legacy/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | create_induction_post |
| /induction/<int:pk>/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | induction_detail |
| /induction/initiated-workers/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | initiated_workers |
| /induction/<int:pk>/attendance/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | attendance_view |
| /induction/<int:pk>/signatures/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | signatures_view |
| /induction/<int:pk>/auto-signature/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | auto_signature_request |
| /induction/<int:pk>/complete-attendance/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | complete_attendance_and_request_signatures |
| /induction/manage/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | manage_endpoint |
| /induction/manage/<int:pk>/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | manage_endpoint |
| /induction/manage/trained-personnel/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | manage_endpoint |
| /induction/api/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | InductionTrainingViewSet (router) |
| /induction/api/<int:pk>/ | backend/inductiontraining/urls.py | PASS | PASS | N/A | PASS | TBD | InductionTrainingViewSet (router) |

## Job Training (/jobtraining/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /jobtraining/create/ | backend/jobtraining/urls.py | PASS | PASS | N/A | PASS | TBD | create_job_training |
| /jobtraining/deployed-workers/ | backend/jobtraining/urls.py | PASS | PASS | N/A | PASS | TBD | JobTrainingViewSet.trained_personnel |
| /jobtraining/ | backend/jobtraining/urls.py | PASS | PASS | N/A | PASS | TBD | JobTrainingViewSet (router) |
| /jobtraining/<int:pk>/ | backend/jobtraining/urls.py | PASS | PASS | N/A | PASS | TBD | JobTrainingViewSet (router) |

## Manpower (/man/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /man/test/ | backend/manpower/urls.py | PASS | PASS | N/A | PASS | TBD | test_endpoint |
| /man/debug/ | backend/manpower/urls.py | PASS | PASS | N/A | PASS | TBD | debug_manpower_endpoint |
| /man/manpower/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | ManpowerEntryView |
| /man/manpower/individual/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | ManpowerEntryView |
| /man/manpower/<int:pk>/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | ManpowerEntryDetailView |
| /man/manpower/by-date/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | ManpowerEntryByDateView |
| /man/record/<int:pk>/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | IndividualManpowerEntryView |
| /man/work-types/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | WorkTypeView |
| /man/daily-summary/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | DailyManpowerSummaryView |
| /man/dashboard-stats/ | backend/manpower/urls.py | PASS | PASS | N/A | PASS | TBD | manpower_dashboard_stats |
| /man/consolidated-attendance/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | consolidated_attendance_view |
| /man/consolidated-summary/ | backend/manpower/urls.py | TBD | TBD | N/A | TBD | TBD | consolidated_attendance_summary |

## MOM (/api/v1/mom/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/mom/schedule/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomCreateView |
| /api/v1/mom/list/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomListView |
| /api/v1/mom/<int:pk>/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomUpdateView |
| /api/v1/mom/<int:pk>/delete/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomDeleteView |
| /api/v1/mom/<int:mom_id>/participants/<int:user_id>/response/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | ParticipantResponseView |
| /api/v1/mom/<int:mom_id>/response/<int:user_id>/accept/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | ParticipantAcceptView |
| /api/v1/mom/<int:mom_id>/response/<int:user_id>/reject/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | ParticipantRejectView |
| /api/v1/mom/<int:mom_id>/participants/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | ParticipantListView |
| /api/v1/mom/<int:pk>/live/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomLiveView |
| /api/v1/mom/<int:pk>/live/attendance/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomLiveAttendanceUpdateView |
| /api/v1/mom/<int:pk>/complete/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomCompleteView |
| /api/v1/mom/<int:pk>/participants/add/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MomAddParticipantsView |
| /api/v1/mom/<int:mom_id>/info/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | MeetingInfoView |
| /api/v1/mom/csrf-token/ | backend/mom/urls.py | TBD | N/A | N/A | N/A | TBD | CsrfTokenView |
| /api/v1/users/ | backend/mom/urls.py | TBD | TBD | N/A | TBD | TBD | UsersByDepartmentListView |

## Safety Observation (/api/v1/safetyobservation/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/safetyobservation/ | backend/safetyobservation/urls.py | PASS | PASS | N/A | PASS | TBD | SafetyObservationViewSet (router) |
| /api/v1/safetyobservation/<int:pk>/ | backend/safetyobservation/urls.py | PASS | PASS | N/A | PASS | TBD | SafetyObservationViewSet (router) |

## PTW (/api/v1/ptw/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/ptw/permit-types/ | backend/ptw/urls.py | PASS | N/A | N/A | PASS | TBD | PermitTypeViewSet (router) |
| /api/v1/ptw/hazards/ | backend/ptw/urls.py | PASS | N/A | N/A | PASS | TBD | HazardLibraryViewSet |
| /api/v1/ptw/workflow-templates/ | backend/ptw/urls.py | PASS | N/A | N/A | PASS | TBD | WorkflowTemplateViewSet |
| /api/v1/ptw/permits/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | PermitViewSet |
| /api/v1/ptw/permit-workers/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | PermitWorkerViewSet |
| /api/v1/ptw/permit-approvals/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | PermitApprovalViewSet |
| /api/v1/ptw/permit-extensions/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | PermitExtensionViewSet |
| /api/v1/ptw/permit-audits/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | PermitAuditViewSet |
| /api/v1/ptw/gas-readings/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | GasReadingViewSet |
| /api/v1/ptw/permit-photos/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | PermitPhotoViewSet |
| /api/v1/ptw/digital-signatures/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | DigitalSignatureViewSet |
| /api/v1/ptw/workflow-instances/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | WorkflowInstanceViewSet |
| /api/v1/ptw/system-integrations/ | backend/ptw/urls.py | PASS | N/A | N/A | PASS | TBD | SystemIntegrationViewSet |
| /api/v1/ptw/compliance-reports/ | backend/ptw/urls.py | PASS | N/A | N/A | PASS | TBD | ComplianceReportViewSet |
| /api/v1/ptw/sync-offline-data/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | sync_offline_data |
| /api/v1/ptw/qr-scan/<str:qr_code>/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | qr_scan_permit |
| /api/v1/ptw/mobile-permit/<int:permit_id>/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | mobile_permit_view |
| /api/v1/ptw/team-members/get_users_by_type_and_grade/ | backend/ptw/urls.py | PASS | PASS | N/A | PASS | TBD | get_users_by_type_and_grade |
| /api/v1/ptw/permits/<int:pk>/workflow/initiate/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | initiate_workflow |
| /api/v1/ptw/permits/<int:pk>/workflow/assign-verifier/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | assign_verifier |
| /api/v1/ptw/permits/<int:pk>/workflow/verify/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | verify_permit |
| /api/v1/ptw/permits/<int:pk>/workflow/assign-approver/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | assign_approver |
| /api/v1/ptw/permits/<int:pk>/workflow/approve/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | approve_permit |
| /api/v1/ptw/permits/<int:pk>/workflow/status/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | get_workflow_status |
| /api/v1/ptw/permits/<int:pk>/workflow/resubmit/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | resubmit_permit |
| /api/v1/ptw/workflow/verifiers/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | get_available_verifiers |
| /api/v1/ptw/workflow/approvers/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | get_available_approvers |
| /api/v1/ptw/workflow/my-tasks/ | backend/ptw/workflow_urls.py | TBD | TBD | N/A | TBD | TBD | get_my_workflow_tasks |
| /api/v1/ptw/permit-types/ (legacy) | backend/ptw/urls.py | TBD | TBD | N/A | TBD | TBD | PermitTypeViewSet.as_view |
| /api/v1/ptw/permits/ (legacy) | backend/ptw/urls.py | TBD | TBD | N/A | TBD | TBD | PermitViewSet.as_view |
| /api/v1/ptw/permits/<int:pk>/ (legacy) | backend/ptw/urls.py | TBD | TBD | N/A | TBD | TBD | PermitViewSet.as_view |
| /api/v1/ptw/permits/<int:pk>/verify/ | backend/ptw/urls.py | TBD | TBD | N/A | TBD | TBD | PermitViewSet.verify |
| /api/v1/ptw/permits/<int:pk>/approve/ | backend/ptw/urls.py | TBD | TBD | N/A | TBD | TBD | PermitViewSet.approve |
| /api/v1/ptw/permits/<int:pk>/reject/ | backend/ptw/urls.py | TBD | TBD | N/A | TBD | TBD | PermitViewSet.reject |

## Incident Management (/api/v1/incidentmanagement/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/incidentmanagement/incidents/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | IncidentViewSet |
| /api/v1/incidentmanagement/incidents/<int:pk>/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | IncidentViewSet |
| /api/v1/incidentmanagement/attachments/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | IncidentAttachmentViewSet |
| /api/v1/incidentmanagement/attachments/<int:pk>/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | IncidentAttachmentViewSet |
| /api/v1/incidentmanagement/cost-centers/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | IncidentCostCenterViewSet |
| /api/v1/incidentmanagement/learnings/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | IncidentLearningViewSet |
| /api/v1/incidentmanagement/8d-processes/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | EightDProcessViewSet |
| /api/v1/incidentmanagement/8d-teams/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | EightDTeamViewSet |
| /api/v1/incidentmanagement/8d-containment-actions/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | EightDContainmentActionViewSet |
| /api/v1/incidentmanagement/8d-root-causes/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | EightDRootCauseViewSet |
| /api/v1/incidentmanagement/8d-analysis-methods/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | EightDAnalysisMethodViewSet |
| /api/v1/incidentmanagement/8d-corrective-actions/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | EightDCorrectiveActionViewSet |
| /api/v1/incidentmanagement/8d-prevention-actions/ | backend/incidentmanagement/urls.py | PASS | PASS | N/A | PASS | TBD | EightDPreventionActionViewSet |

## Inspection (/api/v1/inspection/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/inspection/inspections/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | InspectionViewSet |
| /api/v1/inspection/inspections/<int:pk>/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | InspectionViewSet |
| /api/v1/inspection/inspection-items/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | InspectionItemViewSet |
| /api/v1/inspection/inspection-items/<int:pk>/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | InspectionItemViewSet |
| /api/v1/inspection/inspection-reports/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | InspectionReportViewSet |
| /api/v1/inspection/inspection-reports/<int:pk>/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | InspectionReportViewSet |
| /api/v1/inspection/ac-cable-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | ACCableInspectionFormViewSet |
| /api/v1/inspection/acdb-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | ACDBChecklistFormViewSet |
| /api/v1/inspection/ht-cable-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | HTCableChecklistFormViewSet |
| /api/v1/inspection/ht-precommission-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | HTPreCommissionFormViewSet |
| /api/v1/inspection/ht-precommission-template-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | HTPreCommissionTemplateFormViewSet |
| /api/v1/inspection/civil-work-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | CivilWorkChecklistFormViewSet |
| /api/v1/inspection/cement-register-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | CementRegisterFormViewSet |
| /api/v1/inspection/concrete-pour-card-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | ConcretePourCardFormViewSet |
| /api/v1/inspection/pcc-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | PCCChecklistFormViewSet |
| /api/v1/inspection/bar-bending-schedule-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | BarBendingScheduleFormViewSet |
| /api/v1/inspection/battery-charger-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | BatteryChargerChecklistFormViewSet |
| /api/v1/inspection/battery-ups-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | BatteryUPSChecklistFormViewSet |
| /api/v1/inspection/bus-duct-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | BusDuctChecklistFormViewSet |
| /api/v1/inspection/control-cable-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | ControlCableChecklistFormViewSet |
| /api/v1/inspection/control-room-audit-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | ControlRoomAuditChecklistFormViewSet |
| /api/v1/inspection/earthing-checklist-forms/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | EarthingChecklistFormViewSet |
| /api/v1/inspection/users/ | backend/inspection/urls.py | PASS | PASS | N/A | PASS | TBD | inspection_users |

## Permissions (/api/v1/permissions/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/permissions/request/ | backend/permissions/urls.py | PASS | PASS | N/A | PASS | TBD | request_permission |
| /api/v1/permissions/approve/<int:request_id>/ | backend/permissions/urls.py | PASS | PASS | N/A | PASS | TBD | approve_permission |
| /api/v1/permissions/my-requests/ | backend/permissions/urls.py | PASS | PASS | N/A | PASS | TBD | my_permission_requests |
| /api/v1/permissions/check/ | backend/permissions/urls.py | PASS | PASS | N/A | PASS | TBD | check_permission |
| /api/v1/permissions/escalate/ | backend/permissions/urls.py | PASS | PASS | N/A | PASS | TBD | escalate_item |

## System (/system/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /system/settings/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | SystemSettingsView |
| /system/logs/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | SystemLogsView |
| /system/logs/export/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | SystemLogsExportView |
| /system/backups/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | BackupListCreateView |
| /system/backups/<int:pk>/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | BackupDetailView |
| /system/backups/<int:pk>/restore/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | BackupRestoreView |
| /system/backups/<int:pk>/download/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | BackupDownloadView |
| /system/backups/upload/ | backend/system/urls.py | TBD | TBD | N/A | TBD | TBD | BackupUploadView |

## Environment (/api/v1/environment/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/environment/aspects/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | EnvironmentAspectViewSet |
| /api/v1/environment/generation/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | GenerationDataViewSet |
| /api/v1/environment/emission-factors/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | EmissionFactorViewSet |
| /api/v1/environment/ghg-activities/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | GHGActivityViewSet |
| /api/v1/environment/waste-manifests/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | WasteManifestViewSet |
| /api/v1/environment/biodiversity-events/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | BiodiversityEventViewSet |
| /api/v1/environment/policies/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | ESGPolicyViewSet |
| /api/v1/environment/grievances/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | GrievanceViewSet |
| /api/v1/environment/reports/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | ESGReportViewSet |
| /api/v1/environment/monitoring/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | EnvironmentalMonitoringViewSet |
| /api/v1/environment/carbon-footprint/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | CarbonFootprintViewSet |
| /api/v1/environment/water-management/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | WaterManagementViewSet |
| /api/v1/environment/energy-management/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | EnergyManagementViewSet |
| /api/v1/environment/environmental-incidents/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | EnvironmentalIncidentViewSet |
| /api/v1/environment/sustainability-targets/ | backend/environment/urls.py | PASS | PASS | N/A | PASS | TBD | SustainabilityTargetViewSet |

## Quality (/api/v1/quality/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/quality/standards/ | backend/quality/urls.py | PASS | N/A | N/A | PASS | TBD | QualityStandardViewSet |
| /api/v1/quality/templates/ | backend/quality/urls.py | PASS | PASS | N/A | PASS | TBD | QualityTemplateViewSet |
| /api/v1/quality/inspections/ | backend/quality/urls.py | PASS | PASS | N/A | PASS | TBD | QualityInspectionViewSet |
| /api/v1/quality/defects/ | backend/quality/urls.py | PASS | PASS | N/A | PASS | TBD | QualityDefectViewSet |
| /api/v1/quality/suppliers/ | backend/quality/urls.py | PASS | PASS | N/A | PASS | TBD | SupplierQualityViewSet |
| /api/v1/quality/metrics/ | backend/quality/urls.py | PASS | PASS | N/A | PASS | TBD | QualityMetricsViewSet |
| /api/v1/quality/alerts/ | backend/quality/urls.py | PASS | PASS | N/A | PASS | TBD | QualityAlertViewSet |

## Voice Translator (/api/v1/voice/)
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /api/v1/voice/translate/ | backend/voice_translator/urls.py | PASS | N/A | N/A | PASS | TBD | translate_text |
| /api/v1/voice/languages/ | backend/voice_translator/urls.py | PASS | N/A | N/A | PASS | TBD | supported_languages |

## WebSockets
| Endpoint/Consumer | Source | Tenant enforced? | Project enforced? | Collaboration read? | Cross-tenant write denied? | Tests? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ws/notifications/ | backend/authentication/routing.py | TBD | TBD | TBD | TBD | TBD | NotificationConsumer |
