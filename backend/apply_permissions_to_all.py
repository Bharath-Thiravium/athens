#!/usr/bin/env python3
"""
Script to apply permission decorators to all ViewSets in the project
"""

import os
import re
import sys

# Add the project directory to Python path
sys.path.append('/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/backend')

def apply_permissions_to_file(file_path, module_name):
    """Apply permission decorators to a specific file"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if permissions decorator is already imported
        if 'from permissions.decorators import require_permission' not in content:
            # Add import after other imports
            import_pattern = r'(from rest_framework[^\n]*\n)'
            if re.search(import_pattern, content):
                content = re.sub(
                    import_pattern,
                    r'\1from permissions.decorators import require_permission\n',
                    content,
                    count=1
                )
        
        # Find all ViewSet classes
        viewset_pattern = r'class (\w+ViewSet)\(.*?\):'
        viewsets = re.findall(viewset_pattern, content)
        
        for viewset in viewsets:
            
            # Add model attribute if not present
            model_pattern = rf'(class {viewset}\([^{{]*?\{{[^}}]*?)(\n    def|\n    @|\nclass|\Z)'
            if f'model = ' not in content:
                # Extract model name from ViewSet name (remove 'ViewSet' suffix)
                model_name = viewset.replace('ViewSet', '')
                model_line = f'\n    model = {model_name}  # Required for permission decorator'
                content = re.sub(
                    model_pattern,
                    rf'\1{model_line}\2',
                    content,
                    flags=re.DOTALL
                )
            
            # Add permission decorators to update, partial_update, destroy methods
            methods_to_decorate = [
                ('update', 'edit'),
                ('partial_update', 'edit'),
                ('destroy', 'delete')
            ]
            
            for method_name, permission_type in methods_to_decorate:
                # Check if method already has decorator
                decorated_pattern = rf'@require_permission\([\'\"]{permission_type}[\'\"]\)\s*def {method_name}'
                if not re.search(decorated_pattern, content):
                    # Look for the method definition
                    method_pattern = rf'(\s+)(def {method_name}\(self, request[^:]*?\):)'
                    if re.search(method_pattern, content):
                        # Add decorator
                        replacement = rf'\1@require_permission(\'{permission_type}\')\n\1\2\n\1    return super().{method_name}(request, *args, **kwargs)'
                        content = re.sub(method_pattern, replacement, content)
                    else:
                        # Add method if it doesn't exist
                        class_end_pattern = rf'(class {viewset}\([^{{]*?\{{.*?)(\n\nclass|\n@|\Z)'
                        method_code = f'''
    @require_permission('{permission_type}')
    def {method_name}(self, request, *args, **kwargs):
        return super().{method_name}(request, *args, **kwargs)
'''
                        content = re.sub(
                            class_end_pattern,
                            rf'\1{method_code}\2',
                            content,
                            flags=re.DOTALL
                        )
        
        # Write back the modified content
        with open(file_path, 'w') as f:
            f.write(content)
        
        
    except Exception as e:

        

        
        
        pass
        
        pass

def main():
    """Main function to apply permissions to all modules"""
    
    # List of modules to process (excluding chatbox as requested)
    modules_to_process = [
        'incidentmanagement',
        'manpower',
        'ptw',
        'inspection',  # Add inspection module
        # Already done: 'jobtraining', 'inductiontraining', 'safetyobservation', 'tbt', 'worker', 'mom'
    ]
    
    base_path = '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/backend'
    
    for module in modules_to_process:
        views_file = os.path.join(base_path, module, 'views.py')
        if os.path.exists(views_file):
            apply_permissions_to_file(views_file, module)
        else:
    

if __name__ == '__main__':
    main()