#!/usr/bin/env python3
"""
Script to apply permission system to all frontend list components
"""

import os
import re

def update_component_with_permissions(file_path, component_name, api_endpoint, app_label, model_name):
    """Update a component file with permission system"""
    print(f"Updating {component_name}...")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add imports if not present
        if 'usePermissionControl' not in content:
            # Add permission imports after existing imports
            import_pattern = r"(import useAuthStore from '@common/store/authStore';)"
            if re.search(import_pattern, content):
                content = re.sub(
                    import_pattern,
                    r"\1\nimport { usePermissionControl } from '../../../hooks/usePermissionControl';\nimport PermissionRequestModal from '../../../components/permissions/PermissionRequestModal';",
                    content
                )
        
        # Add django_user_type to useAuthStore destructuring
        auth_store_pattern = r"const \{ ([^}]+) \} = useAuthStore\(\);"
        if re.search(auth_store_pattern, content):
            content = re.sub(
                auth_store_pattern,
                lambda m: f"const {{ {m.group(1)}, django_user_type }} = useAuthStore();",
                content
            )
        
        # Add permission control hook
        if 'usePermissionControl' not in content:
            # Find where to add the permission control hook
            hook_pattern = r"(const \{ [^}]+ \} = useAuthStore\(\);)"
            if re.search(hook_pattern, content):
                permission_hook = """
  // Permission control
  const { executeWithPermission, showPermissionModal, permissionRequest, closePermissionModal, onPermissionRequestSuccess } = usePermissionControl({
    onPermissionGranted: () => fetchData()
  });"""
                content = re.sub(hook_pattern, rf"\1{permission_hook}", content)
        
        # Update edit handler
        edit_pattern = r"const handleEdit = [^;]+;"
        if not re.search(edit_pattern, content):
            # Add edit handler if it doesn't exist
            edit_handler = f"""
  const handleEdit = async (record) => {{
    // For non-adminusers, open edit modal directly
    if (django_user_type !== 'adminuser') {{
      setEditingItem(record);
      return;
    }}
    
    try {{
      // Check if user has active permission
      const response = await api.get('/api/v1/permissions/check/', {{
        params: {{
          permission_type: 'edit',
          object_id: record.id,
          app_label: '{app_label}',
          model: '{model_name}'
        }}
      }});
      
      if (response.data.has_permission) {{
        // User has permission, open edit modal directly
        setEditingItem(record);
      }} else {{
        // No permission, trigger permission request flow
        executeWithPermission(
          () => api.patch(`{api_endpoint}/${{record.id}}/`, {{}}),
          'edit {component_name.lower()}'
        ).then(() => {{
          setEditingItem(record);
        }}).catch((error) => {{
          if (error) {{
            console.error('Permission check failed:', error);
          }}
        }});
      }}
    }} catch (error) {{
      console.error('Error checking permission:', error);
      // Fallback to permission request flow
      executeWithPermission(
        () => api.patch(`{api_endpoint}/${{record.id}}/`, {{}}),
        'edit {component_name.lower()}'
      ).then(() => {{
        setEditingItem(record);
      }}).catch((error) => {{
        if (error) {{
          console.error('Permission check failed:', error);
        }}
      }});
    }}
  }};"""
            
            # Find where to insert the handler
            component_pattern = rf"const {component_name}: React\.FC = \(\) => \{{"
            if re.search(component_pattern, content):
                content = re.sub(
                    component_pattern,
                    rf"{component_pattern.replace('{', '{')} {edit_handler}",
                    content
                )
        
        # Update delete handler
        delete_pattern = r"const handleDelete = [^;]+;"
        if not re.search(delete_pattern, content):
            # Add delete handler if it doesn't exist
            delete_handler = f"""
  const handleDelete = async (record) => {{
    try {{
      if (django_user_type === 'adminuser') {{
        // Check if user has active permission
        try {{
          const response = await api.get('/api/v1/permissions/check/', {{
            params: {{
              permission_type: 'delete',
              object_id: record.id,
              app_label: '{app_label}',
              model: '{model_name}'
            }}
          }});
          
          if (response.data.has_permission) {{
            // User has permission, delete directly
            await api.delete(`{api_endpoint}/${{record.id}}/`);
          }} else {{
            // No permission, use permission flow
            await executeWithPermission(
              () => api.delete(`{api_endpoint}/${{record.id}}/`),
              'delete {component_name.lower()}'
            );
          }}
        }} catch (permError) {{
          // Fallback to permission flow
          await executeWithPermission(
            () => api.delete(`{api_endpoint}/${{record.id}}/`),
            'delete {component_name.lower()}'
          );
        }}
      }} else {{
        await api.delete(`{api_endpoint}/${{record.id}}/`);
      }}
      
      message.success('{component_name} deleted successfully');
      fetchData();
    }} catch (error) {{
      if (error) {{
        message.error('Failed to delete {component_name.lower()}');
      }}
    }}
  }};"""
            
            # Find where to insert the handler
            component_pattern = rf"const {component_name}: React\.FC = \(\) => \{{"
            if re.search(component_pattern, content):
                content = re.sub(
                    component_pattern,
                    rf"{component_pattern.replace('{', '{')} {delete_handler}",
                    content
                )
        
        # Add permission modal at the end
        if 'PermissionRequestModal' not in content:
            # Find the end of the component
            end_pattern = r"(\s+</[^>]+>\s+\);\s+};\s+export default [^;]+;)"
            if re.search(end_pattern, content):
                permission_modal = """
      
      {showPermissionModal && permissionRequest && (
        <PermissionRequestModal
          visible={showPermissionModal}
          onCancel={closePermissionModal}
          onSuccess={onPermissionRequestSuccess}
          permissionType={permissionRequest.permissionType}
          objectId={permissionRequest.objectId}
          contentType={permissionRequest.contentType}
          objectName={permissionRequest.objectName}
        />
      )}"""
                content = re.sub(end_pattern, rf"{permission_modal}\1", content)
        
        # Write back the modified content
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"  ✅ Successfully updated {component_name}")
        
    except Exception as e:
        print(f"  ❌ Error updating {component_name}: {e}")

def main():
    """Main function to update all components"""
    
    # Components to update (excluding chatbox and already updated ones)
    components = [
        {
            'name': 'ToolboxTalkList',
            'path': '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/frontedn/src/features/toolboxtalk/components/ToolboxTalkList.tsx',
            'api_endpoint': '/toolbox-talks',
            'app_label': 'tbt',
            'model_name': 'toolboxtalk'
        },
        {
            'name': 'SafetyObservationList',
            'path': '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/frontedn/src/features/safetyobservation/components/SafetyObservationList.tsx',
            'api_endpoint': '/safety-observations',
            'app_label': 'safetyobservation',
            'model_name': 'safetyobservation'
        },
        {
            'name': 'WorkerList',
            'path': '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/frontedn/src/features/worker/components/WorkerList.tsx',
            'api_endpoint': '/workers',
            'app_label': 'worker',
            'model_name': 'worker'
        },
        {
            'name': 'MomList',
            'path': '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/frontedn/src/features/mom/components/MomList.tsx',
            'api_endpoint': '/mom',
            'app_label': 'mom',
            'model_name': 'mom'
        },
        {
            'name': 'PermitList',
            'path': '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/frontedn/src/features/ptw/components/PermitList.tsx',
            'api_endpoint': '/permits',
            'app_label': 'ptw',
            'model_name': 'permit'
        },
        {
            'name': 'IncidentList',
            'path': '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/frontedn/src/features/incidentmanagement/components/IncidentList.tsx',
            'api_endpoint': '/incidents',
            'app_label': 'incidentmanagement',
            'model_name': 'incident'
        }
    ]
    
    for component in components:
        if os.path.exists(component['path']):
            update_component_with_permissions(
                component['path'],
                component['name'],
                component['api_endpoint'],
                component['app_label'],
                component['model_name']
            )
        else:
            print(f"⚠️  Component file not found: {component['path']}")
    
    print("\n🎉 Frontend permission system applied to all components!")

if __name__ == '__main__':
    main()