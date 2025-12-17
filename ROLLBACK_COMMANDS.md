# ROLLBACK COMMANDS

## Linux/Mac Recovery Commands

### Debug Scripts
```bash
cp archived/debug_scripts/test_api_connectivity.py .
cp archived/debug_scripts/security_verification.py .
cp archived/debug_scripts/test_auth_flow.html .
cp archived/debug_scripts/test_contractor_fix.py .
cp archived/debug_scripts/test_logo.html .
cp archived/debug_scripts/test_permit_creation.py .
cp archived/debug_scripts/test_permit_types_api.py .
cp archived/debug_scripts/check_permit_types.py .
cp archived/debug_scripts/test_login.py backend/
cp archived/debug_scripts/test_esg_implementation.py backend/
cp archived/debug_scripts/test_frontend_login.py backend/
cp archived/debug_scripts/test_rag_comprehensive.py backend/
cp archived/debug_scripts/check_master_admin.py backend/
cp archived/debug_scripts/clear_tokens.py backend/
cp archived/debug_scripts/reset_password.py backend/
cp archived/debug_scripts/fix_except_blocks.py backend/
cp archived/debug_scripts/fix_masteradmin_shell_commands.py backend/
```

### Batch Files
```bash
cp archived/batch_files/cleanup_project.sh .
cp archived/batch_files/create_master_admin.sh .
cp archived/batch_files/fix_issues.sh .
cp archived/batch_files/install_all_deps.sh .
cp archived/batch_files/install_complete.sh .
cp archived/batch_files/install_reports_dependencies.sh .
cp archived/batch_files/production_deploy.sh .
cp archived/batch_files/quick_start.sh .
cp archived/batch_files/run_project.sh .
cp archived/batch_files/setup_project.sh .
cp archived/batch_files/setup_venv_and_install.sh .
cp archived/batch_files/start_local_dev.sh .
cp archived/batch_files/start_server.sh .
cp archived/batch_files/test_cors.sh .
```

### Bridge Deploy
```bash
cp archived/bridge_deploy/apply_frontend_permissions.py .
cp archived/bridge_deploy/create_permit_types.py .
cp archived/bridge_deploy/apply_permissions_to_all.py backend/
cp archived/bridge_deploy/add_airline_permits.py backend/
cp archived/bridge_deploy/cleanup_permit_types.py backend/
cp archived/bridge_deploy/clear_old_ptw_notifications.py backend/
cp archived/bridge_deploy/create_admin.py backend/
cp archived/bridge_deploy/create_complete_dummy_data.py backend/
cp archived/bridge_deploy/create_master_admin.py backend/
cp archived/bridge_deploy/create_simple_demo_data.py backend/
cp archived/bridge_deploy/populate_all_modules_data.py backend/
cp archived/bridge_deploy/populate_demo_data.py backend/
cp archived/bridge_deploy/populate_permit_types.py backend/
cp archived/bridge_deploy/setup_rag.py backend/
```

### External Integration
```bash
cp archived/external_integration/Project_Information_Template.csv .
cp archived/external_integration/complete_ehs_system_video_prompt.json .
cp archived/external_integration/incident_management_video_prompt.json .
cp archived/external_integration/wordpress-plugin.zip .
cp archived/external_integration/esg1.txt .
cp archived/external_integration/esg2 .
cp archived/external_integration/esg2.txt .
cp archived/external_integration/25.2 backend/
cp archived/external_integration/Pip backend/
```

### Documentation (Sample - 85 files total)
```bash
cp archived/documentation/60_second_video_script.md .
cp archived/documentation/DEPLOYMENT_GUIDE.md .
cp archived/documentation/PROJECT_SPECIFICATIONS.md .
cp archived/documentation/BACKEND_SETUP_GUIDE.md backend/
cp archived/documentation/NOTIFICATION_SYSTEM_GUIDE.md backend/
# ... (and 80 more documentation files)
```

## Windows Recovery Commands

### Debug Scripts
```cmd
copy archived\debug_scripts\test_api_connectivity.py .
copy archived\debug_scripts\security_verification.py .
copy archived\debug_scripts\test_login.py backend\
# ... (continue pattern for all files)
```

## Complete Rollback (All Files)
```bash
# Linux/Mac
find archived/ -type f -exec sh -c 'cp "$1" "${1#archived/*/}"' _ {} \;

# Windows
for /r archived %i in (*) do copy "%i" .
```